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

You could manually copy every merchant, date, currency, subtotal, and tax amount into a spreadsheet. Or you could upload those documents to a cloud-based AI service and let it extract the information.

But what if those invoices contain confidential client details?

As a freelance developer, I wanted to explore a third option: **an expense assistant that can use open-weight AI locally, verify financial arithmetic with deterministic code, and leave the final decision to the user.**

That's why I built **PocketLedger AI** for the Hacktoberfest Side Hustle challenge.

The idea behind it is simple:

> **AI reads the document. Code checks the numbers. Humans approve the record.**

---

## 🎥 Try It Yourself: 50-Second Demo & Live Links

{% youtube Uk_9aB7Z0xo %}

- 🎥 **[Watch the 50-second demo](https://youtu.be/Uk_9aB7Z0xo)**
- 🌐 **[Open the hosted application](https://pocketledger-ai.onrender.com/)**
- 💻 **[Explore the source code on GitHub](https://github.com/tribhu05/pocketledger-ai)**

{% github tribhu05/pocketledger-ai %}

### Watch the Ingestion, Local Gemma Extraction & Split-Screen Review in Action:

![PocketLedger AI Ingestion and Review Workflow](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/pocketledger-extraction-review.gif)

The hosted demo currently uses deterministic fallback parsing because Ollama and OCR are unavailable in that deployment. It demonstrates the interface and fallback workflow; it does not demonstrate Gemma inference running on Render. The local configuration is the way to explore the Ollama-powered workflow.

![PocketLedger AI Dashboard](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/01_dashboard.png)

---

## What I Built

PocketLedger AI is an AI-assisted expense management tool designed for freelancers, independent developers, consultants, and side-hustlers who want to organize receipts without turning bookkeeping into another time-consuming project.

It focuses on a specific workflow: converting expense documents into structured, reviewable financial records.

The application supports:

- **PDF and image ingestion:** Extract embedded text from digital PDFs using `pypdf` and process supported receipt images using Tesseract OCR.
- **Open-weight AI extraction:** Run Gemma 2B Instruct through Ollama in the local configuration.
- **Structured validation:** Validate extracted fields before they enter the financial workflow.
- **Financial reconciliation:** Calculate expected totals and flag discrepancies.
- **Human review:** Inspect, edit, and explicitly approve extracted records.
- **Local persistence:** Store records in SQLite in the local workflow.
- **Multi-currency reporting:** Keep supported currencies separate instead of adding unlike amounts together.
- **Safer CSV exports:** Apply safeguards against spreadsheet formula injection.

This is not an attempt to replace an accountant or build a complete accounting platform. It is a focused assistant for the repetitive first step of bookkeeping: getting information out of receipts and into organized records.

---

## Who Might Pay for It?

The initial audience is freelancers and independent professionals who regularly handle software subscriptions, hosting bills, travel expenses, and client invoices.

For someone who processes receipts every week, reducing repetitive data entry while retaining control over financial records could be valuable. Whether the tool saves enough time to justify payment is something I still need to validate with more users.

---

## How I Built It

PocketLedger AI combines a conventional web application with a local open-weight model and deterministic financial rules.

The stack includes Python, FastAPI, Pydantic, React, TypeScript, Vite, SQLite, `pypdf`, Tesseract OCR, Ollama, and Gemma 2B Instruct.

The intended processing pipeline is:

```text
PDF / Receipt Image
        │
        ▼
Local Text Extraction (pypdf / Tesseract OCR)
        │
        ▼
Gemma 2B via Local Ollama
        │
        ▼
Structured Field Validation (Pydantic)
        │
        ▼
Deterministic Financial Checks (Decimal Math)
        │
        ▼
Human Review and Approval (Split-Screen Diff)
        │
        ▼
SQLite Ledger & Safe CSV Export
```

### 1. Extracting information from documents

Digital PDFs and photographed receipts require different approaches.

For PDFs containing embedded text, PocketLedger uses `pypdf`. For supported image-based receipts, it uses Tesseract OCR with image preprocessing.

Separating text extraction from semantic extraction makes it easier to inspect and test each stage independently.

### 2. Using Gemma through Ollama

The local model identifier is `gemma2:2b`.

Ollama serves the model through the local runtime. PocketLedger asks it to extract structured fields such as merchant, document type, transaction date, currency, subtotal, tax, discount, additional charges, and total.

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

The extraction layer requests JSON and validates the response against a Pydantic schema. Its parser also handles common malformed-response cases, such as JSON wrapped in Markdown or preceded by conversational text.

However, valid JSON does not guarantee correct information. A model can return a plausible but incorrect date or amount, so financial validation must be a separate step.

### 3. Keeping financial arithmetic deterministic

I didn't want an LLM's plausible-looking answer to become the source of truth for financial calculations.

PocketLedger's reconciliation rule is:

> **Expected Total = Subtotal + Tax − Discount + Additional Charges**  
> **Difference = |Stated Total − Expected Total|**

The implementation uses Python's `Decimal` for monetary arithmetic and a configured rounding tolerance of ₹0.05, or the equivalent amount in the relevant currency:

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
| GST | ₹414.00 |
| Discount | ₹114.00 |
| **Expected total** | **₹2,600.00** |
| **Stated total** | **₹2,600.00** |
| **Reconciliation Status** | **Reconciled (Difference = 0.00)** |

The arithmetic is straightforward:

`₹2,300 + ₹414 − ₹114 = ₹2,600`

When the calculated and stated totals differ beyond the configured tolerance, the record is flagged for review rather than silently accepted:

![PocketLedger AI Split-Screen Review and Reconciliation Screen](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/04_review_modal.png)

This check cannot prove that the original receipt was read correctly. It provides a separate consistency check on the extracted numbers.

### 4. Keeping humans in control

Extracted data should not become a trusted expense record simply because the model returned valid JSON.

PocketLedger lets users inspect extracted fields, correct values, and approve records explicitly. The backend also records field edits in a JSON diff so changes made during review can be inspected:

```json
{
  "user_edits": {
    "merchant": { "old": "AMZN MKTP", "new": "Amazon Web Services" },
    "category": { "old": "Other", "new": "Software & SaaS" }
  }
}
```

The goal is not to eliminate human judgment. It is to make repetitive work easier while preserving a clear review step.

### 5. Handling currencies and CSV exports

Adding `$50 USD` and `€40 EUR` into a single total would be misleading without exchange-rate conversion.

![PocketLedger AI Multi-Currency Ledger and Reports](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/pocketledger-ledger-export.gif)

PocketLedger's summary export groups records by month, category, and currency rather than treating different currencies as interchangeable.

The project also applies defensive handling to CSV cells beginning with characters such as `=`, `+`, `-`, `@`, tabs, and carriage returns. Spreadsheet applications may interpret some such cells as formulas:

```python
# Neutralizing spreadsheet injection in backend/export.py
def sanitize_csv_cell(val: Any) -> Any:
    if val is None:
        return ""
    val_str = str(val).strip()
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str
```

This reduces a known risk but is not a guarantee against every spreadsheet security issue.

---

## Technical Evidence: What I Actually Tested

The project's technical evidence report records these automated test results:

```text
$ pytest backend/tests/test_backend.py -v
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

$ npm test -- --run (frontend)
✓ src/test/App.test.tsx (7 tests) 1189ms
Test Files  1 passed (1)
     Tests  7 passed (7)
```

| Test suite | Reported result | What is verified |
|---|---:|---|
| **Backend — Pytest** | **16 passed, 0 failed** | Reconciliation math, discount & surcharge logic, Decimal drift elimination, date/currency normalization, CSV injection fuzzing, multi-currency export segregation, API status probe, review diff audit, and JSON parser recovery. |
| **Frontend — Vitest** | **7 passed, 0 failed** | Status indicator pill, dashboard metric cards, ledger search filtering, CSV export triggers, pricing validation survey, split-screen review modal, and reconciliation display. |
| **Total** | **23 passed, 0 failed** | 100% pass rate across entire codebase. |

The reported backend coverage includes reconciliation, discount handling, Decimal arithmetic, date and currency normalization, CSV sanitization, fallback parsing, API status, review workflows, and JSON parsing.

The frontend tests cover selected interface behavior, including dashboard metrics, ledger filtering, CSV export interactions, the review modal, and reconciliation display.

Passing automated tests does not establish that every possible receipt will be processed correctly.

- **[Read the full technical evidence report in the repository](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/technical-evidence-report.md)**
- **[Inspect the project and setup instructions](https://github.com/tribhu05/pocketledger-ai)**

---

## What the Benchmarks Show

The project documents two separate synthetic evaluations. They should not be interpreted as a controlled head-to-head comparison:

| Evaluation Dimension | Local Gemma 2B Evaluation | Deterministic Fallback Evaluation | Context & Notes |
|---|:---:|:---:|---|
| **Hardware / Runtime** | AMD Ryzen 3 7320U (8 GB RAM) via Ollama | Local Python process (regex heuristic) | Local open-weight inference vs regex parser |
| **Test Corpus** | 8 synthetic receipts/invoices | 10 synthetic receipts/invoices | Diverse real-world freelancer expense scenarios |
| **Merchant Name** | **8/8 correct** (100%) | **10/10 correct** (100%) | Extracts business name ignoring visual noise |
| **Total Amount** | **8/8 correct** (100%) | **10/10 correct** (100%) | Preserves `null` on smudged receipts |
| **Currency** | **8/8 correct** (100%) | **10/10 correct** (100%) | Maps $, €, £, ₹ to standard ISO codes |
| **Document Type** | **8/8 correct** (100%) | **10/10 correct** (100%) | Differentiates invoices from receipts |
| **Transaction Date** | **7/8 correct** (87.5%) | **9/10 correct** (90%) | The date miss involved European-style dates |
| **Average Processing Time** | **34.1 seconds** per document | **0.58 milliseconds** per document | Local compute trade-off vs instant heuristic |

The local evaluation shows that local extraction was feasible on the tested hardware, but processing was relatively slow. One date was misinterpreted, illustrating why review remains necessary.

The fallback parser uses deterministic heuristics rather than Gemma. Its results come from a small, specific synthetic test set and should not be generalized to arbitrary invoices.

These evaluations measure different approaches under different test conditions. They do not prove that either approach achieves the same accuracy on real customer documents.

The engineering lesson is that extraction quality, arithmetic consistency, and processing speed are separate problems. A useful expense assistant needs to address all three.

**[Read the benchmark report in the repository](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/benchmark_report.md)**

---

## Local AI Versus the Hosted Demo

The local and hosted configurations serve different purposes:

| Dimension | Local Mode (Workstation) | Hosted Demo (Render Cloud) |
|---|---|---|
| **Inference Engine** | Local Google Gemma 2B via Ollama | Deterministic Heuristic Fallback |
| **Privacy Boundary** | 100% On-Device (Zero Network Egress) | Ephemeral Cloud Container |
| **Reconciliation Math** | Python `Decimal` Engine | Python `Decimal` Engine |
| **Review & Audit** | Full split-screen with diff tracking | Full split-screen with diff tracking |
| **Persistence** | Persistent SQLite (`pocketledger.db`) | In-memory SQLite database |
| **Status Declaration** | Shows `gemma2_local` badge | Shows `deterministic_fallback` badge |

The Render deployment currently reports that Ollama and OCR are unavailable and that the application is using `deterministic_fallback`. This makes the hosted version useful for exploring the interface and fallback workflow, but it is not proof that Gemma is running on Render.

![PocketLedger AI System Status and Privacy Inspector](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/06_system_status.png)

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

---

## Why Does Open Innovation Matter?

Open-weight AI is central to this project because it gives users another option for processing sensitive financial documents.

### 1. More control over document processing
Invoices may contain customer names, billing details, addresses, and information covered by confidentiality agreements.

Running the configured inference workflow locally can reduce the need to send document contents to an external AI inference API. Local execution does not automatically make an entire computer secure, but it gives users more control over where inference takes place.

### 2. Less dependence on paid inference APIs
After downloading the model, local inference does not require a paid cloud inference API for every extraction. This can make costs more predictable for a small application.

There are trade-offs: local inference uses the user's hardware, consumes memory and disk space, and can be slower on modest machines.

### 3. Freedom to inspect and adapt
The project is released under the MIT License, and the local workflow uses an open-weight Gemma model through Ollama.

Developers can inspect the extraction pipeline, adapt prompts, experiment with compatible models, and improve the validation and review logic.

The model is only one component of the system. The surrounding code determines how extracted data is checked, presented, stored, and exported.

Open innovation makes these choices possible: developers can inspect the implementation and users can choose a processing setup that better fits their needs.

---

## My First User: Nitu Tested PocketLedger AI

I wanted to see how PocketLedger AI performed for someone other than its creator.

Nitu, a freelance developer working with US clients, tried the local workflow after describing how time-consuming it was to transcribe AWS receipts and invoice PDFs.

He tested six receipts and an Indian SaaS invoice using the local Ollama setup.

His initial feedback was:

> “Honestly, this is pretty impressive! The receipts were processed well, and I really like that everything runs locally.”

He also offered to test more invoices and report edge cases.

![First-User Feedback on PocketLedger AI](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/nitu_feedback.png)

*Initial feedback from Nitu after testing PocketLedger AI.*

### What I learned
- Receipt transcription is a concrete, repetitive problem.
- Local inference can be an important consideration for people handling confidential documents.
- A handful of successful documents is an encouraging start, not proof of broad reliability.
- Additional testing needs to cover different layouts, date formats, currencies, discounts, and ambiguous totals.

I'm grateful that Nitu took the time to test an early version. His feedback encourages me to keep improving extraction reliability and the review workflow instead of claiming that every receipt will work perfectly.

---

## Prize Categories

### Primary Category: Side Hustle
PocketLedger AI was built specifically for the **Side Hustle** prompt. It tackles a concrete administrative pain point experienced by independent developers, freelancers, and solo consultants: organizing sensitive receipts and business expenses without sacrificing client confidentiality or paying expensive monthly accounting SaaS fees.

### Partner Category: Best Use of Render
PocketLedger AI is entered for the **Best Use of Render** prize track:

- **Live Production Deployment:** [https://pocketledger-ai.onrender.com](https://pocketledger-ai.onrender.com)
- **Declarative Infrastructure Blueprint:** The deployment is managed via [`render.yaml`](https://github.com/tribhu05/pocketledger-ai/blob/master/render.yaml) with continuous deployment, health check routing (`/api/status`), and configured environment variables.
- **Unified Multi-Stage Docker Architecture:** The Render service runs a multi-stage Docker build that compiles the React 19 / TypeScript frontend, installs system-level Tesseract OCR (`tesseract-ocr`, `libtesseract-dev`), bundles the FastAPI backend, and serves the entire unified application on a single web service.
- **Cloud-Resilient Fallback Design:** In a cloud container environment where a local Ollama daemon is absent, the application detects the host environment and activates its deterministic heuristic fallback parser. This guarantees that hackathon judges and evaluators have zero setup friction—they can immediately test document intake, reconciliation math, review editing, and CSV export without needing to configure or download local LLM weights.

---

## Could This Become a Side Hustle?

My initial pricing hypothesis is a **$29 one-time purchase** for a packaged desktop edition, potentially including easier installation, local receipt-folder monitoring, and customizable tax categories.

That is a hypothesis, not a validated price. I have not established that users will pay for it.

Before asking people to buy it, I would focus on:
- **Reliable onboarding:** Make installing the application and local model straightforward.
- **Better extraction coverage:** Test more document layouts, date formats, currencies, and edge cases.
- **A dependable review workflow:** Make errors and discrepancies easy to identify and correct.
- **Real user validation:** Recruit more freelancers, observe their workflows, and test willingness to pay before committing to a pricing model.

The goal is to build something useful enough that a freelancer would choose it over a spreadsheet—not to add AI for its own sake.

---

## What I'd Build Next

The current project has highlighted several limitations:
- Local Gemma inference averaged 34.1 seconds per document in the documented test environment.
- Faded, unusual, or ambiguous receipts still need human verification.
- Numerical dates can be interpreted differently across regions.
- Installing Ollama and downloading a model introduces setup friction.
- The hosted demo's fallback mode does not demonstrate the local Gemma workflow.

My next steps would be to simplify installation, expand the test corpus, improve error handling, and explore an automatic local folder watcher.

I'd rather make one expense workflow dependable than claim to automate every accounting task.

---

## Project Links

- **Source code:** [PocketLedger AI on GitHub](https://github.com/tribhu05/pocketledger-ai)
- **Live demo:** [Try PocketLedger AI](https://pocketledger-ai.onrender.com/)
- **Video demo:** [Watch the 50-second walkthrough](https://youtu.be/Uk_9aB7Z0xo)
- **Technical evidence:** [Test report](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/technical-evidence-report.md)
- **Benchmark details:** [Synthetic evaluation report](https://github.com/tribhu05/pocketledger-ai/blob/master/docs/benchmark_report.md)

PocketLedger AI is released under the MIT License.

---

## Your Turn

**Would you trust a local AI expense assistant with your receipts? What would you need to see before using one for your freelance bookkeeping?**

I'd especially appreciate feedback on the reconciliation workflow, the local-versus-hosted distinction, and the edge cases a financial extraction tool should handle.

If you're a freelancer or independent developer willing to test an early version, I'd love to hear what works, what fails, and which features would genuinely save you time.

Thanks for reading!

*Built with Python, FastAPI, React, TypeScript, SQLite, Ollama, and Google's open-weight Gemma model.*
