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

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def to_money_decimal(val: Optional[Any]) -> Optional[Decimal]:
    """Convert monetary value to exact 2-decimal-place Decimal to avoid IEEE 754 drift."""
    if val is None:
        return None
    try:
        # If float, round to string first to avoid 0.30000000000000004
        if isinstance(val, float):
            import math
            if math.isnan(val) or math.isinf(val):
                return None
            val_str = f"{val:.2f}"
        else:
            val_str = str(val).strip()
        return Decimal(val_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return None

def detect_currency_anomalies(text_context: str, chosen_currency: str) -> List[str]:
    """Detect if multiple contradictory currency symbols appear in document text."""
    warnings: List[str] = []
    found_symbols = []
    if "€" in text_context:
        found_symbols.append("EUR (€)")
    if "£" in text_context:
        found_symbols.append("GBP (£)")
    if "₹" in text_context:
        found_symbols.append("INR (₹)")
    if "¥" in text_context:
        found_symbols.append("JPY (¥)")
    if "$" in text_context and not any(k in text_context for k in ["US$", "C$", "A$"]):
        found_symbols.append("USD ($)")

    unique_symbols = list(dict.fromkeys(found_symbols))
    if len(unique_symbols) > 1:
        warnings.append(
            f"Multiple conflicting currency symbols detected in document ({', '.join(unique_symbols)}). "
            f"Assigned '{chosen_currency}' — please verify."
        )
    return warnings

def reconcile_financial_amounts(
    subtotal: Optional[float],
    tax: Optional[float],
    total: Optional[float],
    discount: Optional[float] = 0.0,
    additional_charges: Optional[float] = 0.0,
    tolerance: float = 0.05
) -> Tuple[str, Optional[float], List[str]]:
    """
    Perform deterministic math reconciliation using exact Decimal arithmetic:
    Expected Total = Subtotal + Tax - Discount + Additional Charges
    (with configurable currency rounding tolerance, default 0.05).
    """
    warnings: List[str] = []

    if total is None:
        warnings.append("Critical: Total amount is missing or could not be determined.")
        return "mismatch", None, warnings

    total_dec = to_money_decimal(total)
    if total_dec is None:
        warnings.append("Critical: Stated total is malformed or non-numeric.")
        return "mismatch", None, warnings

    if total_dec < Decimal("0.00"):
        warnings.append(f"Negative total amount detected ({float(total_dec):.2f}). Please verify if refund or credit memo.")

    d_dec = to_money_decimal(discount) if discount is not None else Decimal("0.00")
    if d_dec is None:
        d_dec = Decimal("0.00")
    if d_dec < Decimal("0.00"):
        warnings.append(f"Negative discount detected ({float(d_dec):.2f}). Discount should be non-negative.")

    c_dec = to_money_decimal(additional_charges) if additional_charges is not None else Decimal("0.00")
    if c_dec is None:
        c_dec = Decimal("0.00")
    if c_dec < Decimal("0.00"):
        warnings.append(f"Negative additional charges detected ({float(c_dec):.2f}).")

    if subtotal is not None:
        sub_dec = to_money_decimal(subtotal)
        if sub_dec is None:
            warnings.append("Subtotal amount is malformed or non-numeric.")
            return "unverified", None, warnings

        t_dec = to_money_decimal(tax) if tax is not None else Decimal("0.00")
        if t_dec is None:
            t_dec = Decimal("0.00")

        # Decimal formula: expected = subtotal + tax - discount + additional_charges
        expected_total_dec = sub_dec + t_dec - d_dec + c_dec
        diff_dec = total_dec - expected_total_dec
        abs_diff_dec = abs(diff_dec)

        tol_dec = Decimal(str(tolerance)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        breakdown_msg = (
            f"Breakdown: Subtotal ({float(sub_dec):.2f}) + Tax ({float(t_dec):.2f}) - "
            f"Discount ({float(d_dec):.2f}) + Additional Charges ({float(c_dec):.2f}) = "
            f"Expected Total ({float(expected_total_dec):.2f}) vs Stated Total ({float(total_dec):.2f}), "
            f"Difference: {float(abs_diff_dec):.2f}"
        )

        if abs_diff_dec <= tol_dec:
            if tax is None and d_dec == Decimal("0.00") and c_dec == Decimal("0.00"):
                warnings.append("Zero or missing tax reconciled with total.")
            return "reconciled", 0.0, warnings
        else:
            msg = f"Reconciliation mismatch: {breakdown_msg}. Please review source receipt."
            warnings.append(msg)
            return "mismatch", float(diff_dec), warnings

    warnings.append("Subtotal missing; cannot perform full arithmetic reconciliation.")
    return "unverified", None, warnings

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

    # 3. Currency normalization & anomaly checks
    norm_currency = normalize_currency(raw.currency, raw_ocr_text)
    curr_warnings = detect_currency_anomalies(raw_ocr_text, norm_currency)
    warnings.extend(curr_warnings)

    # 4. Amounts sanitization via safe money conversion
    sub_dec = to_money_decimal(raw.subtotal)
    tax_dec = to_money_decimal(raw.tax)
    disc_dec = to_money_decimal(raw.discount) if raw.discount is not None else Decimal("0.00")
    if disc_dec is None:
        disc_dec = Decimal("0.00")
    chg_dec = to_money_decimal(raw.additional_charges) if raw.additional_charges is not None else Decimal("0.00")
    if chg_dec is None:
        chg_dec = Decimal("0.00")
    tot_dec = to_money_decimal(raw.total)

    subtotal = float(sub_dec) if sub_dec is not None else None
    tax = float(tax_dec) if tax_dec is not None else None
    discount = float(disc_dec)
    additional_charges = float(chg_dec)
    total = float(tot_dec) if tot_dec is not None else None

    # 5. Math Reconciliation with Decimal engine
    rec_status, rec_delta, rec_warnings = reconcile_financial_amounts(
        subtotal=subtotal,
        tax=tax,
        total=total,
        discount=discount,
        additional_charges=additional_charges,
    )
    warnings.extend(rec_warnings)

    # 6. Category normalization
    norm_category = normalize_category(raw.category, f"{merchant or ''} {raw.description or ''} {raw_ocr_text}")

    # 7. Overall review status
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
        "discount": discount,
        "additional_charges": additional_charges,
        "total": total,
        "category": norm_category,
        "payment_method": raw.payment_method.strip() if raw.payment_method else None,
        "description": raw.description.strip() if raw.description else None,
        "status": status,
        "reconciliation_status": rec_status,
        "reconciliation_delta": rec_delta,
        "warnings": unique_warnings,
    }
