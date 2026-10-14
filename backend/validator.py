import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from dateutil import parser as date_parser

from backend.schemas import FREELANCE_CATEGORIES, ExtractedReceiptFields

CURRENCY_MAP = {
    "$": "USD",
    "USD": "USD",
    "US$": "USD",
    "€": "EUR",
    "EUR": "EUR",
    "£": "GBP",
    "GBP": "GBP",
    "₹": "INR",
    "INR": "INR",
    "¥": "JPY",
    "JPY": "JPY",
    "CAD": "CAD",
    "C$": "CAD",
    "AUD": "AUD",
    "A$": "AUD",
    "CHF": "CHF",
}

CATEGORY_KEYWORDS = {
    "Software & SaaS": ["software", "cloud", "aws", "gcp", "azure", "github", "gitlab", "vercel", "heroku", "openai", "anthropic", "figma", "notion", "slack", "zoom", "adobe", "domain", "hosting", "subscription", "api"],
    "Office Supplies": ["stationery", "paper", "pen", "desk", "staples", "officemax", "notebook", "printer ink", "cartridge"],
    "Hardware & Equipment": ["laptop", "monitor", "keyboard", "mouse", "headset", "apple", "dell", "lenovo", "macbook", "electronics", "cable", "adapter", "hard drive", "ssd"],
    "Travel & Lodging": ["hotel", "airbnb", "flight", "airline", "uber", "lyft", "taxi", "train", "amtrak", "parking", "toll", "rental car", "transit"],
    "Meals & Entertainment": ["coffee", "starbucks", "cafe", "restaurant", "dinner", "lunch", "breakfast", "bakery", "bistro", "bar", "food", "doordash", "ubereats"],
    "Professional Services": ["consulting", "legal", "accounting", "freelancer", "contractor", "design", "translation", "audit"],
    "Utilities": ["internet", "wifi", "broadband", "verizon", "at&t", "t-mobile", "electric", "power", "water", "phone"],
}

def normalize_currency(curr_raw: Optional[str], text_context: str = "") -> str:
    """Normalize raw currency symbol or text into standard 3-letter ISO code."""
    if not curr_raw:
        # Search text context for symbols
        if "€" in text_context:
            return "EUR"
        if "£" in text_context:
            return "GBP"
        if "₹" in text_context:
            return "INR"
        if "¥" in text_context:
            return "JPY"
        return "USD"

    cleaned = curr_raw.strip().upper()
    if cleaned in CURRENCY_MAP:
        return CURRENCY_MAP[cleaned]

    # Search for known symbols
    for sym, code in CURRENCY_MAP.items():
        if sym in cleaned:
            return code

    # Fallback to uppercase 3-letter alphanumeric or default USD
    match = re.search(r"[A-Z]{3}", cleaned)
    if match:
        return match.group(0)
    return "USD"

def parse_and_normalize_date(raw_date: Optional[str]) -> Tuple[Optional[str], Optional[str], List[str]]:
    """Parse date string into normalized YYYY-MM-DD format with integrity checks."""
    if not raw_date or not raw_date.strip():
        return None, None, ["Date missing from source document."]

    cleaned = raw_date.strip()
    warnings = []

    try:
        # Parse using dateutil
        parsed = date_parser.parse(cleaned, fuzzy=True, dayfirst=False)
        today = date.today()
        
        # Check if year is plausible
        if parsed.year < 2000 or parsed.year > today.year + 1:
            warnings.append(f"Parsed date {parsed.strftime('%Y-%m-%d')} has suspicious year ({parsed.year}).")

        # Future date check
        if parsed.date() > today:
            warnings.append(f"Transaction date {parsed.strftime('%Y-%m-%d')} is in the future.")

        normalized_iso = parsed.strftime("%Y-%m-%d")
        return normalized_iso, cleaned, warnings
    except Exception:
        # Try custom regex for common formats like 2026/09/12 or 12-09-2026
        match_iso = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", cleaned)
        if match_iso:
            y, m, d = match_iso.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}", cleaned, []

        return None, cleaned, [f"Could not reliably parse date '{cleaned}'."]

def normalize_category(category_raw: Optional[str], text_context: str = "") -> str:
    """Normalize category to standard Freelance Taxonomy."""
    if category_raw and category_raw in FREELANCE_CATEGORIES:
        return category_raw

    # Match against taxonomy names loosely
    if category_raw:
        low_cat = category_raw.lower()
        for cat in FREELANCE_CATEGORIES:
            if cat.lower() in low_cat or low_cat in cat.lower():
                return cat

    # Keyword search in context
    context_lower = f"{category_raw or ''} {text_context}".lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in context_lower:
                return cat

    return "Other"

def reconcile_financial_amounts(
    subtotal: Optional[float],
    tax: Optional[float],
    total: Optional[float]
) -> Tuple[str, Optional[float], List[str]]:
    """
    Perform deterministic math reconciliation on monetary totals.
    subtotal + tax == total (with tolerance 0.05).
    """
    warnings: List[str] = []

    if total is None:
        warnings.append("Critical: Total amount is missing or could not be determined.")
        return "mismatch", None, warnings

    if total < 0:
        warnings.append(f"Negative total amount detected ({total:.2f}). Please verify if refund or credit memo.")

    if subtotal is not None and tax is not None:
        calc_total = round(subtotal + tax, 2)
        diff = round(total - calc_total, 2)
        abs_diff = abs(diff)

        if abs_diff <= 0.05:
            return "reconciled", 0.0, warnings
        else:
            msg = (
                f"Reconciliation mismatch: Subtotal ({subtotal:.2f}) + Tax ({tax:.2f}) = {calc_total:.2f}, "
                f"which differs from Total ({total:.2f}) by {abs_diff:.2f}. Please review source receipt."
            )
            warnings.append(msg)
            return "mismatch", diff, warnings

    if subtotal is not None and tax is None:
        # If subtotal == total, tax is likely 0
        if round(abs(subtotal - total), 2) <= 0.05:
            return "reconciled", 0.0, ["Zero or missing tax reconciled with total."]
        else:
            return "unverified", None, ["Subtotal present but tax not specified; amounts unverified."]

    return "unverified", None, []

def validate_and_normalize_record(
    raw: ExtractedReceiptFields,
    raw_ocr_text: str = ""
) -> Dict[str, Any]:
    """Complete validation pass ensuring strict deterministic guarantees."""
    warnings: List[str] = list(raw.warnings)

    # 1. Merchant check
    merchant = raw.merchant.strip() if raw.merchant else None
    if not merchant:
        warnings.append("Merchant/Vendor name could not be identified.")

    # 2. Date parsing
    date_to_parse = raw.transaction_date or raw.raw_date
    norm_date, raw_date_out, date_warnings = parse_and_normalize_date(date_to_parse)
    warnings.extend(date_warnings)

    # 3. Currency normalization
    norm_currency = normalize_currency(raw.currency, raw_ocr_text)

    # 4. Amounts sanitization
    subtotal = round(float(raw.subtotal), 2) if raw.subtotal is not None else None
    tax = round(float(raw.tax), 2) if raw.tax is not None else None
    total = round(float(raw.total), 2) if raw.total is not None else None

    # 5. Math Reconciliation
    rec_status, rec_delta, rec_warnings = reconcile_financial_amounts(subtotal, tax, total)
    warnings.extend(rec_warnings)

    # 6. Category normalization
    norm_category = normalize_category(raw.category, f"{merchant or ''} {raw.description or ''} {raw_ocr_text}")

    # 7. Overall review status
    # Must remain awaiting_review until confirmed by human
    status = "awaiting_review"

    # Deduplicate warnings
    unique_warnings = list(dict.fromkeys(warnings))

    return {
        "merchant": merchant,
        "document_type": raw.document_type or "receipt",
        "invoice_number": raw.invoice_number.strip() if raw.invoice_number else None,
        "transaction_date": norm_date,
        "raw_date": raw_date_out,
        "currency": norm_currency,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "category": norm_category,
        "payment_method": raw.payment_method.strip() if raw.payment_method else None,
        "description": raw.description.strip() if raw.description else None,
        "status": status,
        "reconciliation_status": rec_status,
        "reconciliation_delta": rec_delta,
        "warnings": unique_warnings,
    }
