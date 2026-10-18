---
title: "Your Freelance Receipts Are Private. Why Does Your AI Bookkeeper Need to Upload Them?"
published: true
tags: devchallenge, hf26challenge, ai, opensource
cover_image: https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/hero_banner.png
canonical_url: https://github.com/tribhu05/pocketledger-ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

# Your Freelance Receipts Are Private. Why Does Your AI Bookkeeper Need to Upload Them?

Imagine spending an entire evening organizing AWS invoices, GitHub subscriptions, travel receipts, and software bills before a tax deadline.

You could manually copy every date, merchant, currency, subtotal, and tax amount into a spreadsheet. Or you could upload those documents to a cloud-based AI service and let it extract the information.

But what if those invoices contain confidential client details?

As a freelance developer, I wanted to explore a third option: **an expense assistant that uses open-weight AI locally, verifies financial arithmetic with deterministic code, and leaves the final decision to the user.**

That's why I built **PocketLedger AI** for the Hacktoberfest Side Hustle challenge.

The principle behind the project is simple:

**AI reads the document. Deterministic code checks the numbers. Humans approve the record.**

## Demo: PocketLedger AI in 50 seconds

{% youtube Uk_9aB7Z0xo %}

🎥 **[Watch the YouTube demo](https://youtu.be/Uk_9aB7Z0xo)**

🌐 [Try the hosted application](https://pocketledger-ai.onrender.com)

💻 [Explore the source code on GitHub](https://github.com/tribhu05/pocketledger-ai)

{% github tribhu05/pocketledger-ai %}

### The End-to-End Workflow in Action

![PocketLedger AI interactive workflow walkthrough](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/pocketledger-workflow.gif)

![PocketLedger AI dashboard](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/01_dashboard.png)

The application brings together document extraction, financial reconciliation, a review workflow, a searchable expense ledger, and CSV exports.

The hosted demo uses a deterministic fallback when local Ollama inference is unavailable. For the full open-weight AI workflow, run PocketLedger on your own machine with Ollama and Gemma.

## What I built

PocketLedger AI is designed for freelancers, independent developers, consultants, and side-hustlers who need to organize recurring expenses without turning bookkeeping into another time-consuming project.

The application supports:

- **PDF and image ingestion:** Extract embedded text from digital PDFs with `pypdf` and use local Tesseract OCR for supported receipt images.
- **Open-weight AI extraction:** Run Google's Gemma 2B Instruct model through Ollama in the local configuration.
- **Structured output validation:** Parse and validate extracted fields before they enter the financial workflow.
- **Deterministic reconciliation:** Calculate expected totals and flag discrepancies.
- **Human-in-the-loop review:** Edit extracted fields and approve records explicitly.
- **Local persistence:** Store records in SQLite in the local workflow.
- **Multi-currency expense reporting:** Keep USD, EUR, GBP, INR, and other supported currencies distinct instead of combining unlike amounts.
- **Defensive CSV exports:** Apply safeguards against spreadsheet formula injection.

This is not intended to replace an accountant or a full accounting platform. It focuses on one specific job: turning messy expense documents into reviewable, organized records.

## How I built it

The stack includes Python, FastAPI, Pydantic, React, TypeScript, Vite, SQLite, `pypdf`, Tesseract OCR, Ollama, and Gemma 2B Instruct.

The processing pipeline is:

```text
PDF / Receipt Image
        |
        v
Local Text Extraction
pypdf / Tesseract OCR
        |
        v
Gemma 2B via Ollama
        |
        v
Structured Field Validation
        |
        v
Deterministic Reconciliation
        |
        v
Human Review and Approval
        |
        v
SQLite Ledger
        |
        v
CSV Export
```

### 1. Local document extraction

Digital PDFs and photographed receipts present different challenges.

For PDFs containing embedded text, PocketLedger uses `pypdf` to extract the text directly. For supported image-based receipts, it uses Tesseract OCR with image preprocessing.

![PocketLedger AI document upload inbox](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/02_inbox.png)

The extracted text is passed into the next stage. Keeping document parsing separate from semantic extraction makes the pipeline easier to inspect and test.

### 2. Gemma 2B through Ollama

The local workflow uses the model identifier:

`gemma2:2b`

Ollama serves the model through the local runtime, and PocketLedger asks it to extract structured fields such as merchant, document type, date, currency, subtotal, tax, discount, additional charges, and total.

The extractor requests JSON output and validates the response against a Pydantic schema:

```python
# System prompt enforcing strict structured extraction in backend/gemma_extractor.py
GEMMA_SYSTEM_PROMPT = """You are PocketLedger AI, a precise financial document extraction engine for freelancers.
Extract key expense fields from the provided receipt or invoice text.
Output MUST be a valid JSON object matching this exact schema:

{
  "merchant": "string or null - Name of business/vendor. NEVER guess or invent.",
  "document_type": "receipt | invoice | other",
  "invoice_number": "string or null - Invoice/receipt reference number if present",
  "transaction_date": "string or null - Date formatted as YYYY-MM-DD",
  "currency": "string - 3-letter currency code (USD, EUR, GBP, CAD, INR, etc.)",
  "subtotal": "number or null - Pre-tax amount",
  "tax": "number or null - Tax/VAT/GST amount",
  "discount": "number or null - Discount, coupon, or promotional reduction if explicitly present",
  "additional_charges": "number or null - Tips, service fees, or delivery surcharge if explicitly present",
  "total": "number or null - Grand total amount",
  "category": "one of: Software & SaaS, Office Supplies, Hardware & Equipment, Travel & Lodging, Meals & Entertainment, Professional Services, Utilities, Other",
  "warnings": ["array of specific warning strings if any value was missing or illegible"]
}"""
```

The extractor requests JSON output and validates the response against a Pydantic schema. Its parsing layer also handles common malformed-response cases, including JSON wrapped in Markdown or preceded by conversational text.

A schema does not make a model infallible. A syntactically valid response can still contain a wrong date or amount, which is why extraction and financial validation are separate stages.

### 3. Financial correctness: don't let the LLM do the accounting

This is one of the most important engineering decisions in PocketLedger AI.

Language models can misread numbers, omit discounts, or produce inconsistent totals. I don't want a plausible-looking AI response to be treated as verified financial arithmetic.

PocketLedger calculates:

$$\text{Expected Total} = \text{Subtotal} + \text{Tax} - \text{Discount} + \text{Additional Charges}$$
$$\Delta = |\text{Stated Total} - \text{Expected Total}|$$

The implementation uses Python's `Decimal` for monetary normalization and arithmetic, eliminating binary floating-point drift (such as `0.1 + 0.2 = 0.30000000000000004`), with a configured rounding tolerance of ₹0.05 or the equivalent in the relevant currency:

```python
# Actual implementation from backend/validator.py
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def to_money_decimal(val: Optional[Any]) -> Optional[Decimal]:
    """Convert monetary value to exact 2-decimal Decimal to eliminate IEEE-754 drift."""
    if val is None:
        return None
    try:
        val_str = f"{val:.2f}" if isinstance(val, float) else str(val).strip()
        return Decimal(val_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return None

def reconcile_financial_amounts(
    subtotal: Optional[float],
    tax: Optional[float],
    total: Optional[float],
    discount: Optional[float] = 0.0,
    additional_charges: Optional[float] = 0.0,
    tolerance: float = 0.05
) -> Tuple[str, Optional[float], List[str]]:
    warnings: List[str] = []

    if total is None:
        warnings.append("Critical: Total amount is missing or could not be determined.")
        return "mismatch", None, warnings

    total_dec = to_money_decimal(total)
    d_dec = to_money_decimal(discount) or Decimal("0.00")
    c_dec = to_money_decimal(additional_charges) or Decimal("0.00")

    if subtotal is not None:
        s_dec = to_money_decimal(subtotal)
        t_dec = to_money_decimal(tax) or Decimal("0.00")
        
        expected_dec = (s_dec + t_dec - d_dec + c_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        diff_dec = (total_dec - expected_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        abs_diff = abs(diff_dec)

        if abs_diff <= Decimal(str(tolerance)):
            return "reconciled", 0.0, warnings
        else:
            msg = (
                f"Reconciliation mismatch: Subtotal ({s_dec}) + Tax ({t_dec}) - "
                f"Discount ({d_dec}) + Charges ({c_dec}) = Expected ({expected_dec}) vs "
                f"Stated Total ({total_dec}), Difference: {abs_diff}."
            )
            warnings.append(msg)
            return "mismatch", float(diff_dec), warnings

    return "unverified", None, []
```

For example:

| Field | Amount |
|---|---:|
| Subtotal | ₹2,300.00 |
| GST (18%) | ₹414.00 |
| Promotional Discount | ₹114.00 |
| Additional Charges | ₹0.00 |
| **Expected total** | **₹2,600.00** |
| **Stated total** | **₹2,600.00** |
| **Reconciliation Status** | **Reconciled ($\Delta = 0.00$)** |

The calculation is:

`₹2,300 + ₹414 − ₹114 = ₹2,600`

When the calculated total differs from the stated total beyond the configured tolerance, the record is flagged with an amber warning banner. Missing totals also trigger a review requirement instead of being silently accepted.

![PocketLedger AI reconciliation and review](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/04_review_modal.png)

### 4. Human review and audit history

Extracted information should not become a trusted expense record just because a model returned valid JSON.

PocketLedger lets users inspect the original document alongside extracted fields, correct values, and approve the record. The backend records field edits in a JSON diff so users can inspect what changed during review:

```json
{
  "user_edits": {
    "merchant": { "old": "AMZN MKTP", "new": "Amazon Web Services" },
    "category": { "old": "Other", "new": "Software & SaaS" }
  }
}
```

This makes the workflow transparent: users see the extracted information, investigate discrepancies, and decide what should be saved.

### 5. Multi-currency reporting and CSV safety

Freelancers often pay for tools in several currencies. Adding `$50 USD` and `€40 EUR` into a single total would produce a meaningless result without an exchange-rate conversion.

![PocketLedger AI multi-currency expense ledger](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/03_ledger.png)

PocketLedger's summary export groups records strictly by month, category, and currency.

The project also implements defensive handling for CSV cells beginning with characters such as `=`, `+`, `-`, `@`, tabs, and carriage returns. In spreadsheet software like Microsoft Excel or LibreOffice, these characters can execute dynamic data exchange (DDE) formulas:

```python
# Actual implementation from backend/export.py
def sanitize_csv_cell(val: Any) -> Any:
    if val is None:
        return ""
    val_str = str(val).strip()
    # Neutralize spreadsheet formula injection prefixes
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str
```

![PocketLedger AI CSV reports export](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/05_reports_csv.png)

This safeguard is intended to reduce formula-injection risk; it should not be understood as a guarantee against every spreadsheet security issue.

## Technical execution: what I actually tested

I wanted the engineering evidence to go beyond screenshots and a demo video. Here is the actual automated test execution across the repository:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
collected 16 items

backend/tests/test_backend.py::test_reconciliation_math PASSED           [  6%]
backend/tests/test_backend.py::test_record_validation_backward_compatibility PASSED [ 12%]
backend/tests/test_backend.py::test_date_normalization PASSED            [ 18%]
backend/tests/test_backend.py::test_currency_normalization PASSED        [ 25%]
backend/tests/test_backend.py::test_csv_injection_sanitization PASSED    [ 31%]
backend/tests/test_backend.py::test_csv_export_multi_currency_segregation PASSED [ 37%]
backend/tests/test_backend.py::test_deterministic_fallback PASSED        [ 43%]
backend/tests/test_backend.py::test_api_status_endpoint PASSED           [ 50%]
backend/tests/test_backend.py::test_raw_text_upload_and_review_workflow PASSED [ 56%]
backend/tests/test_backend.py::test_discount_reconciliation_workflow PASSED [ 62%]
backend/tests/test_backend.py::test_exact_decimal_arithmetic_drift_prevention PASSED [ 68%]
backend/tests/test_backend.py::test_currency_anomaly_detection PASSED    [ 75%]
backend/tests/test_backend.py::test_schema_currency_string_coercion PASSED [ 81%]
backend/tests/test_backend.py::test_gemma_json_parser_robustness PASSED  [ 87%]
backend/tests/test_backend.py::test_synthetic_scenarios_reconciliation PASSED [ 93%]
backend/tests/test_backend.py::test_formula_injection_defense_suite PASSED [100%]

============================= 16 passed in 10.34s =============================

✓ src/test/App.test.tsx (7 tests) 1189ms
Test Files  1 passed (1)
     Tests  7 passed (7)
```

| Test suite | Reported result | What is verified |
|---|---:|---|
| **Backend — Pytest** | **16 passed, 0 failed** | Decimal reconciliation math, discount & surcharge logic, date parsing, currency symbol mapping, CSV injection fuzzing, multi-currency export segregation, API status probe, review diff audit, and JSON parser recovery. |
| **Frontend — Vitest** | **7 passed, 0 failed** | Status indicator pill, dashboard metric cards, ledger search filtering, CSV export triggers, pricing validation survey, split-screen review modal, and reconciliation display. |
| **Total automated tests** | **23 passed, 0 failed** | 100% pass rate across entire codebase. |

These are automated tests of defined behavior, not proof that every possible invoice will be processed correctly.

**[Read the full technical evidence report in the repository](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/technical-evidence-report.md)**

## Benchmark results — and what they mean

PocketLedger's documentation describes two different synthetic evaluations, so I keep their results separate.

### Local Gemma benchmark

The documented local Gemma benchmark used eight synthetic receipts and invoices on an AMD Ryzen 3 7320U system with 8 GB RAM, using local Ollama inference.

| Field | Reported result |
|---|---:|
| Merchant name | 8/8 correct |
| Total amount | 8/8 correct |
| Currency | 8/8 correct |
| Document type | 8/8 correct |
| Transaction date | 7/8 correct |
| Average processing time | 34.1 seconds per document |

The date miss involved a European-style date that required additional care. The benchmark also demonstrates a practical trade-off: local inference can offer more control over processing, but it can be slower on modest CPU hardware.

### Deterministic fallback benchmark (10 synthetic scenarios)

A separate benchmark evaluated the fallback parser against ten synthetic expense documents built into the application (`GET /api/benchmark`):

| Document / Scenario | Type | Currency | Extracted Total | Stated Total | Reconciled? |
|---|---|---|---:|---:|:---:|
| `aws-cloud-invoice-sep2026.pdf` | Digital Cloud Bill | USD | $42.18 | $42.18 | Yes |
| `starbucks-client-meeting.png` | Photo Cafe Receipt | USD | $14.85 | $14.85 | Yes |
| `github-pro-subscription.pdf` | Digital SaaS Receipt | USD | $48.00 | $48.00 | Yes |
| `staples-design-sketchbooks.jpg` | Photo Office Receipt | USD | $32.40 | $32.40 | Yes |
| `hetzner-cloud-europe.pdf` | Digital European Hosting | EUR | €54.74 | €54.74 | Yes |
| `heathrow-express-transit.png` | Digital Transit Ticket | GBP | £25.00 | £25.00 | Yes |
| `reconciliation-mismatch-bistro.png` | Photo Restaurant Receipt | USD | $28.50 | $28.50 | **Mismatch (+$6.50 tip)** |
| `illegible-taxi-receipt.png` | Smudged Taxi Slip | USD | null | null | **Flagged (missing total)** |
| `indian-gst-tech-solutions.pdf` | Digital Consulting Invoice | INR | ₹2,600.00 | ₹2,600.00 | Yes (₹114 discount) |
| `express-courier-surcharge.pdf` | Shipping Invoice | USD | $64.00 | $64.00 | Yes ($10 surcharge) |

Across the 10 documents, the fallback achieved 100% extraction accuracy for merchant, total, currency, and document type, and 90% for transaction date, with an average fallback latency of **0.58 milliseconds per document**.

These results describe the particular synthetic test set, not general accuracy on arbitrary real-world invoices. The fallback is also not the same as Gemma inference: it uses deterministic heuristics rather than the open-weight model.

**The lesson is that model extraction quality, arithmetic correctness, and processing speed are different measurements.** They need to be evaluated separately.

[Read the benchmark report in the repository](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/benchmark_report.md)

## Local AI versus the hosted demo

The local and hosted configurations serve different purposes.

In the local configuration, the application can use Ollama and Gemma on the user's machine, with local document processing and SQLite persistence.

The Render deployment currently reports that Ollama and OCR are unavailable and that the application is using `deterministic_fallback`. This makes the hosted version useful for exploring the interface and fallback workflow, but it is not proof that Gemma is running on Render.

![PocketLedger AI system status and privacy inspector](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/06_system_status.png)

You can verify this directly via the live Render endpoint (`GET https://pocketledger-ai.onrender.com/api/status`):

```json
{
  "app_name": "PocketLedger AI",
  "version": "1.0.0",
  "environment": "production",
  "ollama_connected": false,
  "gemma_available": false,
  "current_mode": "deterministic_fallback",
  "database_connected": true
}
```

This distinction matters because I don't want a reviewer to confuse a working web demo with a local model benchmark.

For the local AI workflow, the repository documents how to install Ollama, pull `gemma2:2b`, configure the backend, and launch the React frontend.

**[Follow the setup instructions in the repository](https://github.com/tribhu05/pocketledger-ai)**

## Why open innovation matters

Open-weight AI isn't just a technical detail in PocketLedger. It changes the trade-offs available to the person using it.

### 1. More control over where documents are processed

Invoices can contain customer names, billing details, addresses, and information covered by client confidentiality requirements.

Running the configured inference workflow locally can reduce the need to send document contents to an external AI inference API. Users still need to consider their own device security, application configuration, backups, and other services, but local inference gives them a meaningful choice.

### 2. Less dependence on per-request AI pricing

After the model is downloaded, local inference does not require a paid cloud inference API for each extraction. That can make the economics more predictable for a small tool aimed at independent professionals.

The trade-off is local compute: the model needs disk space, memory, and suitable hardware, and processing may be slower than a hosted service.

### 3. The freedom to inspect and adapt the system

The code is released under the MIT License, and the local workflow uses an open-weight model through Ollama. Developers can inspect the extraction pipeline, change prompts, experiment with compatible models, and adapt the validation logic.

For a specialized task such as financial extraction, that freedom is valuable. The model is not the entire product: the surrounding validation rules, review workflow, and data handling matter just as much.

**Open innovation makes it possible to choose the trade-off instead of being locked into one provider's API, pricing, and runtime.**

## My first user: Nitu tested PocketLedger AI

I wanted to see how the project performed for someone other than its creator.

I shared PocketLedger AI with Nitu, a freelance developer working with US clients. He described spending around two hours manually transcribing AWS receipts and invoice PDFs, and explained why cloud-based document scanners were a concern for work involving client confidentiality.

He installed Ollama and tried the local workflow with **six receipts and an Indian SaaS invoice**.

His initial feedback was encouraging:

> “Honestly, this is pretty impressive! The receipts were processed well, and I really like that everything runs locally.”

He also offered to test more invoices and report edge cases or accuracy issues over the following days.

![First-user feedback on PocketLedger AI](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/nitu_feedback.png)

*Initial feedback from Nitu after testing PocketLedger AI.*

### What I learned from the experience

- **The problem is practical:** Transcribing receipts and invoices can consume valuable time.
- **Local processing is meaningful:** The ability to run inference locally matters to users who are careful about confidential client documents.
- **More testing is essential:** Six receipts and one SaaS invoice are an encouraging start, not a comprehensive accuracy benchmark.
- **The next improvements should be evidence-driven:** More invoice layouts, date formats, discounts, currencies, and ambiguous totals need testing.

I'm grateful to Nitu for trying an early version and offering to continue testing it. His feedback reinforced the need to keep improving extraction reliability and reconciliation rather than claiming that every receipt will work perfectly.

## Could this become a side hustle?

The initial audience is freelancers and independent developers who manage recurring software subscriptions, hosting bills, travel expenses, and client invoices.

My pricing hypothesis is a **$29 one-time purchase** for a packaged desktop edition, potentially including automatic receipt-folder monitoring and customizable tax categories.

The project also includes an in-app survey asking testers how they currently organize receipts, whether they would pay for an automated desktop version, and which features failed during testing.

This is an experiment, not validated demand. Nitu's feedback is encouraging, but it does not establish willingness to pay, and I am not claiming paying customers.

Before commercializing the product, I would prioritize reliable extraction, easier installation, clear review workflows, and more comprehensive tests.

## What failed, and what I'd build next

Building the project has highlighted several trade-offs:

- **CPU latency:** The documented Gemma benchmark averages 34.1 seconds per document on the tested hardware.
- **Document quality:** Faded or ambiguous receipts still require human verification.
- **Date ambiguity:** Numerical dates can be interpreted differently across regions.
- **Setup friction:** Users must install Ollama and download the model to use the local inference path.

The next steps are to improve installation, expand test coverage across document formats, investigate extraction edge cases, and explore an automatic local folder watcher.

I'd rather make a focused workflow dependable than claim to automate every accounting task.

## Code and project links

- **GitHub:** [PocketLedger AI](https://github.com/tribhu05/pocketledger-ai)
- **Hosted demo:** [Try the application](https://pocketledger-ai.onrender.com)
- **YouTube demo:** [Watch the 50-second walkthrough](https://youtu.be/Uk_9aB7Z0xo)
- **Technical evidence:** [Test results and architecture](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/technical-evidence-report.md)
- **Benchmark report:** [Synthetic evaluation results](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/benchmark_report.md)

PocketLedger AI is released under the MIT License.

## Your turn

**Would you trust a local AI expense assistant with your receipts? What would you need to see before using it for your own freelance bookkeeping?**

I'd especially appreciate feedback on the reconciliation workflow, the local-versus-hosted distinction, and the edge cases a financial extraction tool should handle.

If you're a freelancer or independent developer willing to test an early version, I'd love to hear what works, what fails, and which features would genuinely save you time.

Thanks for reading!

*Built with Python, FastAPI, React, TypeScript, SQLite, Ollama, and Google's open-weight Gemma model.*
