import csv
import io
from typing import List, Dict, Any

def sanitize_csv_cell(value: Any) -> str:
    """
    Prevent CSV Injection (Formula Injection):
    If a cell starts with =, +, -, @, \t, or \r, prepend a single quote (')
    to prevent execution in Excel, LibreOffice, or Google Sheets.
    """
    if value is None:
        return ""
    val_str = str(value)
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str

def export_expenses_to_csv(expenses: List[Dict[str, Any]]) -> str:
    """
    Generate CSV string of expenses with security sanitization and multi-currency clarity.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header
    headers = [
        "ID",
        "Transaction Date",
        "Merchant",
        "Document Type",
        "Invoice Number",
        "Category",
        "Currency",
        "Subtotal",
        "Tax",
        "Total",
        "Reconciliation Status",
        "Review Status",
        "Payment Method",
        "Description",
        "Extraction Mode",
        "Source File",
    ]
    writer.writerow(headers)

    for exp in expenses:
        row = [
            sanitize_csv_cell(exp.get("id")),
            sanitize_csv_cell(exp.get("transaction_date") or ""),
            sanitize_csv_cell(exp.get("merchant") or ""),
            sanitize_csv_cell(exp.get("document_type") or ""),
            sanitize_csv_cell(exp.get("invoice_number") or ""),
            sanitize_csv_cell(exp.get("category") or ""),
            sanitize_csv_cell(exp.get("currency") or "USD"),
            f"{exp['subtotal']:.2f}" if exp.get("subtotal") is not None else "",
            f"{exp['tax']:.2f}" if exp.get("tax") is not None else "",
            f"{exp['total']:.2f}" if exp.get("total") is not None else "",
            sanitize_csv_cell(exp.get("reconciliation_status") or ""),
            sanitize_csv_cell(exp.get("status") or ""),
            sanitize_csv_cell(exp.get("payment_method") or ""),
            sanitize_csv_cell(exp.get("description") or ""),
            sanitize_csv_cell(exp.get("extraction_mode") or ""),
            sanitize_csv_cell(exp.get("source_filename") or ""),
        ]
        writer.writerow(row)

    return output.getvalue()

def export_summary_to_csv(expenses: List[Dict[str, Any]]) -> str:
    """
    Generate grouped summary by Month, Category, and Currency.
    Never lumps mixed currencies together.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    writer.writerow(["Month (YYYY-MM)", "Category", "Currency", "Record Count", "Total Amount"])

    # Aggregate by (month, category, currency)
    aggregates: Dict[tuple, Dict[str, Any]] = {}
    for exp in expenses:
        # Only aggregate confirmed records with valid totals
        if exp.get("total") is None:
            continue

        raw_date = exp.get("transaction_date") or "Unknown"
        month = raw_date[:7] if len(raw_date) >= 7 and "-" in raw_date else "Unknown"
        category = exp.get("category") or "Other"
        currency = exp.get("currency") or "USD"

        key = (month, category, currency)
        if key not in aggregates:
            aggregates[key] = {"count": 0, "total": 0.0}
        aggregates[key]["count"] += 1
        aggregates[key]["total"] += float(exp["total"])

    for (m, cat, curr), data in sorted(aggregates.items(), key=lambda x: (x[0][0], x[0][1])):
        writer.writerow([
            sanitize_csv_cell(m),
            sanitize_csv_cell(cat),
            sanitize_csv_cell(curr),
            data["count"],
            f"{data['total']:.2f}",
        ])

    return output.getvalue()
