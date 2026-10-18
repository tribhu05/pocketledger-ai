---
title: "Your Freelance Receipts Are Private. Why Does Your AI Bookkeeper Need to Upload Them?"
published: true
tags: devchallenge, hf26challenge, ai, opensource
cover_image: https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/hero_banner.png
canonical_url: https://github.com/tribhu05/pocketledger-ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

# Your Freelance Receipts Are Private. Why Does Your AI Bookkeeper Need to Upload Them?

It is Sunday night before a quarterly tax deadline. You open a folder full of AWS invoices, SaaS subscriptions, coffee receipts, and hardware bills.

You have two choices:
1. **Spend hours manually copying** dates, vendor names, and tax totals into spreadsheets.
2. **Upload them to a cloud AI scanner**—and hand confidential client names, NDA project codes, billing rates, and payment card hints over to third-party servers.

As an independent software developer, I wanted a third option: **an expense assistant that runs open-weight AI locally, verifies financial arithmetic with deterministic code, and leaves final approval in human hands.**

That is why I built **PocketLedger AI**.

> **"AI reads the document. Deterministic code checks the numbers. Humans approve the record."**

---

## 🎥 50-Second Demo & Real-Product Walkthrough

{% youtube Uk_9aB7Z0xo %}

- 🎥 **[Watch the 50-Second YouTube Demo](https://youtu.be/Uk_9aB7Z0xo)**
- 🌐 **[Try the Hosted App on Render](https://pocketledger-ai.onrender.com)**
- 💻 **[GitHub Repository (MIT)](https://github.com/tribhu05/pocketledger-ai)**

{% github tribhu05/pocketledger-ai %}

### 1. Document Ingestion & Local Gemma Extraction
Drop digital PDFs or receipt photos into the local inbox. Google's Gemma 2B Instruct processes the text locally via Ollama into typed JSON without sending a single byte over the internet:

![PocketLedger AI Ingestion and Split-Screen Review](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/pocketledger-extraction-review.gif)

---

## 🏗️ Architecture: How It Works

Instead of trusting a Large Language Model to do financial accounting, PocketLedger divides responsibilities strictly:

```text
Receipt PDF / Image 
       │
       ▼
Local OCR (pypdf / Tesseract) ──► Raw Text
       │
       ▼
Local Gemma 2B (Ollama)      ──► Structured Fields (Vendor, Date, Amounts)
       │
       ▼
Deterministic Python Engine  ──► Math Check (Expected Total = Subtotal + Tax - Discount + Charges)
       │
       ▼
Human-in-the-Loop Review     ──► Split-Screen Approval & Diff Audit Trail
       │
       ▼
Local SQLite Ledger          ──► Multi-Currency Segregation & Injection-Safe CSV Export
```

### Financial Correctness: Decimal Math over LLM Guesswork

Language models can hallucinate numbers, overlook discounts, or force inconsistent subtotals to match. PocketLedger enforces a strict mathematical rule in `backend/validator.py` using Python's `Decimal` to eliminate binary floating-point drift:

$$\text{Expected Total} = \text{Subtotal} + \text{Tax} - \text{Discount} + \text{Additional Charges}$$
$$\Delta = |\text{Stated Total} - \text{Expected Total}|$$

```python
# Actual implementation from backend/validator.py
def reconcile_financial_amounts(
    subtotal: Optional[float],
    tax: Optional[float],
    total: Optional[float],
    discount: Optional[float] = 0.0,
    additional_charges: Optional[float] = 0.0,
    tolerance: float = 0.05
) -> Tuple[str, Optional[float], List[str]]:
    if total is None:
        return "mismatch", None, ["Total is missing or ambiguous."]

    total_dec = to_money_decimal(total)
    s_dec = to_money_decimal(subtotal)
    t_dec = to_money_decimal(tax) or Decimal("0.00")
    d_dec = to_money_decimal(discount) or Decimal("0.00")
    c_dec = to_money_decimal(additional_charges) or Decimal("0.00")

    if s_dec is not None:
        expected_dec = (s_dec + t_dec - d_dec + c_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        diff_dec = (total_dec - expected_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        if abs(diff_dec) <= Decimal(str(tolerance)):
            return "reconciled", 0.0, []
        return "mismatch", float(diff_dec), [f"Discrepancy: {abs(diff_dec)}"]

    return "unverified", None, []
```

If the stated total differs from the calculated total beyond the cent-level rounding tolerance ($0.05$), the record is flagged with an amber warning banner. The user inspects the original document side-by-side before approving:

![PocketLedger AI Split-Screen Review and Reconciliation Screen](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/04_review_modal.png)

---

## 📊 Ledger, Multi-Currency Segregation & Safe CSV Export

Freelancers often pay for software and hosting across multiple currencies. Adding `$50 USD` and `€40 EUR` together produces an accounting disaster. PocketLedger groups records strictly by `(Month, Category, Currency)`.

Furthermore, cells exported to CSV are protected against **formula injection** (`=CMD|`, `@SUM`, `+`, `-`) by automatically prepending `'`:

![PocketLedger AI Multi-Currency Ledger and Reports](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/pocketledger-ledger-export.gif)

```python
# Neutralizing spreadsheet injection in backend/export.py
def sanitize_csv_cell(val: Any) -> Any:
    val_str = str(val).strip() if val is not None else ""
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str
```

---

## 🧪 Verified Engineering Proof

I wanted all technical claims to be backed by verifiable code and automated tests rather than marketing claims:

### Automated Test Suite Execution
```text
$ pytest backend/tests/test_backend.py -v
============================= 16 passed in 10.34s =============================
- test_reconciliation_math [PASSED]
- test_exact_decimal_arithmetic_drift_prevention [PASSED]
- test_discount_reconciliation_workflow [PASSED]
- test_currency_anomaly_detection [PASSED]
- test_schema_currency_string_coercion [PASSED]
- test_gemma_json_parser_robustness [PASSED]
- test_synthetic_scenarios_reconciliation [PASSED]
- test_formula_injection_defense_suite [PASSED]
... (8 additional integration tests passed)

$ npm test -- --run (frontend)
============================= 7 passed in 1.19s ===============================
Total: 23 passed, 0 failed (100% pass rate)
```

### Compact Benchmark Comparison

Evaluated on an AMD Ryzen 3 7320U (4-core, 8 GB RAM) across real-world synthetic freelancer receipts:

| Evaluation Dimension | Local Gemma 2B (`gemma2:2b`) | Deterministic Fallback Engine | Verification Scope |
|---|:---:|:---:|---|
| **Merchant Name** | **100%** (8 / 8) | **100%** (10 / 10) | Extracts vendor name ignoring visual noise |
| **Total Amount** | **100%** (8 / 8) | **100%** (10 / 10) | Preserves `null` on smudged receipts |
| **Currency Detection** | **100%** (8 / 8) | **100%** (10 / 10) | Identifies $, €, £, ₹ correctly |
| **Document Type** | **100%** (8 / 8) | **100%** (10 / 10) | Differentiates invoices from receipts |
| **Transaction Date** | **87.5%** (7 / 8) | **90%** (9 / 10) | Normalizes to ISO-8601 (`YYYY-MM-DD`) |
| **Average Latency** | **34.1 seconds** | **0.58 milliseconds** | Local open-weight AI vs instant regex heuristic |
| **Data Egress** | **0 Bytes** (100% Local) | **0 Bytes** (100% Local) | Zero third-party network transmission |

---

## 🌐 Local Mode vs. Hosted Demo: Complete Transparency

To ensure hackathon judges can test the interface immediately without installing Ollama, a live demo is deployed to Render. Here is the exact difference between environments:

| Dimension | Local Mode (Workstation) | Hosted Mode (Render Cloud) |
|---|---|---|
| **Inference Engine** | Local Google Gemma 2B via Ollama | Deterministic Heuristic Fallback |
| **Privacy Boundary** | 100% On-Device (Zero Network Egress) | Ephemeral Cloud Container |
| **Reconciliation Math** | Python `Decimal` Engine | Python `Decimal` Engine |
| **Review & Audit** | Full split-screen with diff tracking | Full split-screen with diff tracking |
| **Persistence** | Persistent SQLite (`pocketledger.db`) | In-memory SQLite database |
| **Status Declaration** | Shows `gemma2_local` badge | Shows `deterministic_fallback` badge |

You can verify this live via the production health endpoint:

```json
// GET https://pocketledger-ai.onrender.com/api/status
{
  "app_name": "PocketLedger AI",
  "environment": "production",
  "ollama_connected": false,
  "gemma_available": false,
  "current_mode": "deterministic_fallback",
  "database_connected": true
}
```

---

## 👤 Real User Testing: How Nitu Improved the Math

I shared PocketLedger AI with **Nitu**, a freelance developer who handles international client billings:

![First User Feedback from Tester Nitu](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/nitu_feedback.png)

Nitu immediately caught an edge case: Indian GST invoices explicitly separate subtotal, GST, and promotional discounts:
> *Subtotal ₹2,300 + GST ₹414 − Discount ₹114 = ₹2,600 Total*

In early versions, the formula only added subtotal and tax, triggering a false mismatch. Thanks to Nitu's real-world test, I updated `backend/validator.py` to natively support discounts and additional charges, adding automated regression tests to guarantee exact ₹0.00 variance.

---

## 💼 The Side Hustle Thesis & What’s Next

- **Target Audience:** Freelancers, independent contractors, and solo founders with confidential client NDAs.
- **Hypothetical Pricing:** A **$29 one-time purchase** for a zero-dependency native desktop app with an automated folder-drop watcher (`watchdog`).
- **Next Roadmap Milestones:** Local folder-sync daemon and mobile camera companion over local LAN.

---

## 💬 Your Turn

**Would you trust an open-weight local AI assistant to organize your freelance tax receipts? What features would you need to see before adopting it for your quarterly taxes?**

I’d love to hear your thoughts, feedback, and financial edge cases in the comments below!

*Built with Python, FastAPI, React, TypeScript, SQLite, Ollama, and Google's open-weight Gemma model.*
