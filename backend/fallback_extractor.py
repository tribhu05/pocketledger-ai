import re
from typing import Optional, List, Dict, Any
from backend.schemas import ExtractedReceiptFields, FREELANCE_CATEGORIES
from backend.validator import normalize_category, normalize_currency

GENERIC_HEADERS = {
    "receipt", "tax invoice", "invoice", "sales receipt", "bill", "payment receipt",
    "customer copy", "merchant copy", "order summary", "e-receipt", "cash receipt",
    "official receipt", "original receipt"
}

def extract_amounts_heuristic(text: str) -> Dict[str, Optional[float]]:
    """Scan text for Total, Subtotal, and Tax numbers using robust line-level keyword parsing."""
    res: Dict[str, Optional[float]] = {"subtotal": None, "tax": None, "total": None}
    lines = text.split("\n")

    def parse_float_from_line(line: str) -> Optional[float]:
        # Matches numbers like 1,234.50 or 44.00 or 14.85
        nums = re.findall(r"([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2}|[0-9]+\.[0-9]{2})", line)
        if nums:
            try:
                # Return the last monetary number on the line (typically the amount column)
                return float(nums[-1].replace(",", ""))
            except Exception:
                return None
        return None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()

        # Check for subtotal first so "subtotal" doesn't falsely trigger "total"
        if any(k in lower for k in ["subtotal", "sub-total", "net amount", "sub total"]):
            if res["subtotal"] is None:
                parsed = parse_float_from_line(stripped)
                if parsed is not None:
                    res["subtotal"] = parsed

        elif any(k in lower for k in ["sales tax", "vat", "gst", "hst", "tax"]):
            if res["tax"] is None:
                parsed = parse_float_from_line(stripped)
                if parsed is not None:
                    res["tax"] = parsed

        elif any(k in lower for k in ["grand total", "total due", "amount due", "balance due", "total amount", "total paid", "total:"]):
            if res["total"] is None:
                parsed = parse_float_from_line(stripped)
                if parsed is not None:
                    res["total"] = parsed

    # Second pass for bare "total" if not yet found
    if res["total"] is None:
        for line in reversed(lines):
            stripped = line.strip()
            lower = stripped.lower()
            if "subtotal" in lower or "sub-total" in lower:
                continue
            if "total" in lower:
                parsed = parse_float_from_line(stripped)
                if parsed is not None:
                    res["total"] = parsed
                    break

    return res


def extract_merchant_heuristic(text: str) -> Optional[str]:
    """Extract candidate merchant from prominent early non-empty lines."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:8]:
        cleaned = re.sub(r"[^\w\s&.,'-]", "", line).strip()
        if not cleaned:
            continue
        if cleaned.lower() in GENERIC_HEADERS:
            continue
        if len(cleaned) < 2 or len(cleaned) > 50:
            continue
        # Skip if looks like a date or invoice number
        if re.search(r"^\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}$", cleaned):
            continue
        if re.search(r"(?i)^(invoice|receipt|date|tel|phone|fax)", cleaned):
            continue
        return cleaned
    return None

def extract_invoice_number_heuristic(text: str) -> Optional[str]:
    """Extract invoice or order reference number."""
    pat = re.compile(r"(?i)(?:inv(?:oice)?|receipt|order|ref(?:erence)?)\s*(?:#|no\.?|num(?:ber)?|id)?\s*[:.-]?\s*([a-zA-Z0-9\-_]{3,25})")
    m = pat.search(text)
    if m:
        val = m.group(1).strip()
        if not val.lower() in {"date", "for", "the", "total", "subtotal"}:
            return val
    return None

def extract_date_heuristic(text: str) -> Optional[str]:
    """Find date string in text."""
    date_patterns = [
        r"(?i)(?:date[:\s]*)?(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",
        r"(?i)(?:date[:\s]*)?(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
        r"(?i)(?:date[:\s]*)?([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})",
        r"(?i)(?:date[:\s]*)?(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
    ]
    for p in date_patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()
    return None

def extract_document_type_heuristic(text: str) -> str:
    """Identify if document is an invoice or a receipt."""
    lower = text.lower()
    if "invoice" in lower or "bill to" in lower or "due date" in lower:
        return "invoice"
    return "receipt"

def extract_with_fallback(document_text: str) -> ExtractedReceiptFields:
    """
    Deterministic fallback parser for when Gemma is offline or unavailable.
    Explicitly labels active fallback.
    """
    warnings = ["Local fallback active: Gemma was unavailable during processing."]

    if not document_text or not document_text.strip():
        warnings.append("Empty document text.")
        return ExtractedReceiptFields(
            merchant=None,
            total=None,
            warnings=warnings
        )

    amounts = extract_amounts_heuristic(document_text)
    merchant = extract_merchant_heuristic(document_text)
    doc_type = extract_document_type_heuristic(document_text)
    inv_num = extract_invoice_number_heuristic(document_text)
    date_str = extract_date_heuristic(document_text)
    currency = normalize_currency(None, document_text)
    category = normalize_category(None, f"{merchant or ''} {document_text[:300]}")

    if not merchant:
        warnings.append("Fallback could not detect merchant name.")
    if amounts["total"] is None:
        warnings.append("Fallback could not identify grand total.")

    return ExtractedReceiptFields(
        merchant=merchant,
        document_type=doc_type,
        invoice_number=inv_num,
        transaction_date=date_str,
        raw_date=date_str,
        currency=currency,
        subtotal=amounts["subtotal"],
        tax=amounts["tax"],
        total=amounts["total"],
        category=category,
        payment_method=None,
        description=f"Extracted via deterministic fallback ({doc_type})",
        warnings=warnings
    )
