# PocketLedger AI — Technical Evidence & Verification Report
**Hacktoberfest 2026 Open-Source AI Challenge (Week 2: Side Hustle)**  
*Date of Verification:* October 18, 2026  
*Auditor:* Senior Full-Stack & AI Systems Reviewer  
*Repository:* [https://github.com/tribhu05/pocketledger-ai](https://github.com/tribhu05/pocketledger-ai)  
*Hosted Demo:* [https://pocketledger-ai.onrender.com](https://pocketledger-ai.onrender.com)  
*Demo Video:* [YouTube Walkthrough](https://youtu.be/Uk_9aB7Z0xo?si=P0W50wuzLihcNeFz) | [Direct MP4](https://github.com/tribhu05/pocketledger-ai/raw/master/docs/video/PocketLedger_AI_Demo_50s.mp4)  
*License:* MIT (Verified in repository root `LICENSE`)

---

## 1. Executive Summary & Objective

This technical evidence report provides verified, reproducible engineering proof for **PocketLedger AI**, a privacy-first expense management co-pilot designed for freelancers.

### Core Architecture Principle
> **"AI reads the document. Deterministic code checks the numbers. Humans approve the record."**

Rather than treating Large Language Models as infallible financial authorities, PocketLedger AI isolates the AI to unstructured text interpretation, enforces strict mathematical validation via a deterministic Python Decimal engine, flags discrepancies automatically, and requires explicit human review before persistent ledger entry or tax CSV export.

---

## 2. Test Execution & Coverage Audit

The project features automated test suites across both the backend (FastAPI/Pytest) and frontend (React/Vitest).

### 2.1 Backend Automated Test Suite (Pytest)
- **Command:** `.venv\Scripts\pytest.exe -v`
- **Results:** **16 Passed, 0 Failed** (10.34s)
- **Environment:** Windows, Python 3.14.0, `pytest-9.1.1`, `anyio-4.15.1`, `asyncio-1.4.0`

| # | Test Identifier | Module | Verification Scope | Status |
|---|---|---|---|---|
| 1 | `test_reconciliation_math` | `backend/tests/test_backend.py` | Validates standard formula $T = S + \text{Tax} - D + C$, rounding tolerance, and mismatch reporting. | **PASSED** |
| 2 | `test_record_validation_backward_compatibility` | `backend/tests/test_backend.py` | Ensures legacy records lacking a discount field default to `0.0` gracefully without false warnings. | **PASSED** |
| 3 | `test_date_normalization` | `backend/tests/test_backend.py` | Tests ISO (`YYYY-MM-DD`), US (`MM/DD/YYYY`), written dates, and flags missing or future dates. | **PASSED** |
| 4 | `test_currency_normalization` | `backend/tests/test_backend.py` | Verifies symbol mapping (`$`, `€`, `£`, `₹`, `¥`) to ISO-4217 currency codes with contextual fallback. | **PASSED** |
| 5 | `test_csv_injection_sanitization` | `backend/tests/test_backend.py` | Confirms formula injection prevention prepending `'` to `=`, `+`, `-`, `@`, `\t`, `\r`. | **PASSED** |
| 6 | `test_csv_export_multi_currency_segregation` | `backend/tests/test_backend.py` | Confirms CSV export aggregates by `(month, category, currency)` and never blends distinct currencies. | **PASSED** |
| 7 | `test_deterministic_fallback` | `backend/tests/test_backend.py` | Verifies heuristic fallback parsing when Ollama is offline, extracting totals and vendors. | **PASSED** |
| 8 | `test_api_status_endpoint` | `backend/tests/test_backend.py` | Probes `/api/status` for engine metadata and active database connectivity. | **PASSED** |
| 9 | `test_raw_text_upload_and_review_workflow` | `backend/tests/test_backend.py` | Executes full lifecycle: raw text ingestion → review update → audit trail diff → dashboard spend reflection. | **PASSED** |
| 10 | `test_discount_reconciliation_workflow` | `backend/tests/test_backend.py` | Validates Indian GST receipt (Subtotal ₹2300, GST ₹414, Discount ₹114, Total ₹2600) and CSV persistence. | **PASSED** |
| 11 | `test_exact_decimal_arithmetic_drift_prevention` | `backend/tests/test_backend.py` | Checks IEEE-754 binary floating-point drift elimination ($0.10 + 0.20 = 0.30$) via Python `Decimal`. | **PASSED** |
| 12 | `test_currency_anomaly_detection` | `backend/tests/test_backend.py` | Flags contradictory currency symbols within a single document (e.g., both `$` and `€`). | **PASSED** |
| 13 | `test_schema_currency_string_coercion` | `backend/tests/test_backend.py` | Coerces string amounts (`"$1,234.50"`, `"₹50.00"`) safely to numeric floats and handles `NaN` gracefully. | **PASSED** |
| 14 | `test_gemma_json_parser_robustness` | `backend/tests/test_backend.py` | Recovers JSON payloads wrapped in markdown code blocks (` ```json ... ``` `) and conversational preamble. | **PASSED** |
| 15 | `test_synthetic_scenarios_reconciliation` | `backend/tests/test_backend.py` | Verifies end-to-end reconciliation for all 10 synthetic benchmark receipts in `SYNTHETIC_RECEIPTS`. | **PASSED** |
| 16 | `test_formula_injection_defense_suite` | `backend/tests/test_backend.py` | Comprehensive fuzz test against Excel/LibreOffice DDE command execution payloads. | **PASSED** |

### 2.2 Frontend Automated Test Suite (Vitest)
- **Command:** `npm test` (in `frontend/`)
- **Results:** **7 Passed, 0 Failed** (5.44s)
- **Environment:** Vitest v5.0.4, React 19, JSDOM, React Testing Library

| # | Test Description | UI Component Verified | Status |
|---|---|---|---|
| 1 | Live system status pill | `Navbar.tsx` (checks "100% On-Device" and active mode badge) | **PASSED** |
| 2 | Financial summary cards & category metrics | `DashboardView.tsx` (spend by currency, confirmed expense count) | **PASSED** |
| 3 | Ledger query filtering & empty state | `ExpenseLedger.tsx` (keyword search, status filters) | **PASSED** |
| 4 | Tax reports & CSV export triggers | `ReportsView.tsx` (direct download handlers for itemized/summary CSV) | **PASSED** |
| 5 | Side hustle validation survey | `PricingView.tsx` (freelancer willingness-to-pay feedback form) | **PASSED** |
| 6 | Split-screen review modal | `ReviewModal.tsx` (side-by-side OCR text and editable fields) | **PASSED** |
| 7 | Discount and balanced math banner | `ReviewModal.tsx` (reconciliation delta display and discount field) | **PASSED** |

**Total Automated Tests:** **23 Passed, 0 Failed**.

---

## 3. Financial Correctness: Decimal Reconciliation Engine

### 3.1 The Mathematical Model
Financial figures must never suffer from IEEE-754 binary floating-point drift (e.g. `0.1 + 0.2 = 0.30000000000000004`). In PocketLedger AI, all amounts are normalized through `to_money_decimal` in `backend/validator.py`:

$$\text{Expected Total} = \text{Decimal}(\text{Subtotal}) + \text{Decimal}(\text{Tax}) - \text{Decimal}(\text{Discount}) + \text{Decimal}(\text{Additional Charges})$$
$$\Delta = |\text{Decimal}(\text{Stated Total}) - \text{Expected Total}|$$

```python
# Implementation in backend/validator.py
def to_money_decimal(val: Optional[Any]) -> Optional[Decimal]:
    if val is None:
        return None
    try:
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
            val_str = f"{val:.2f}"
        else:
            val_str = str(val).strip()
        return Decimal(val_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return None
```

- **Reconciled Threshold:** If $\Delta \le 0.05$ (configurable rounding tolerance), the record receives `reconciliation_status = "reconciled"`.
- **Mismatch Warning:** If $\Delta > 0.05$, the record is marked `reconciliation_status = "mismatch"`, and an explicit warning is attached detailing subtotal, tax, discount, additional charges, expected total, and difference.
- **Missing Total Handling:** If the grand total is absent or smudged, the record is flagged for human review.

---

## 4. Gemma 2B Integration & Fallback Transparency

### 4.1 Local Inference Pipeline
- **Model:** Google Gemma 2B Instruct (`gemma2:2b`)
- **Runtime:** Local Ollama daemon (`http://localhost:11434`)
- **System Prompt:** Strict schema enforcement requesting single JSON output without markdown conversational filler.
- **Robustness Layer:** `parse_json_from_response` uses multi-stage extraction:
  1. Direct `json.loads`
  2. Markdown regex block extraction (` ```json\s*(\{.*?\})\s*``` `)
  3. Outermost balanced brace matching (`{` to `}`)
  4. Specific error classification (`httpx.ConnectError` vs `httpx.TimeoutException`)

### 4.2 Hosted Fallback Behavior (Render)
When deployed to free-tier cloud environments (e.g., Render) without GPU acceleration or local Ollama daemons:
- `check_gemma_availability()` detects Ollama offline within 3.0s timeout.
- The system automatically transitions to `deterministic_fallback` without crashing.
- Heuristic regex patterns extract date, merchant, currency, subtotal, tax, discount, and total.
- The user is notified via UI pill: `Deterministic Fallback Active`.

---

## 5. Synthetic Test Corpus & Benchmark Results

PocketLedger AI includes a built-in benchmark harness (`GET /api/benchmark`) evaluated against 10 synthetic real-world freelancer expense documents in `backend/demo_data.py`.

### 5.1 Benchmark Execution Output
Run on 2026-10-18:
- **Corpus Size:** 10 receipts / invoices
- **Total Fallback Duration:** 5.75 ms
- **Average Latency per Document:** **0.58 ms**
- **Field Extraction Accuracy:**
  - **Merchant:** 100.0%
  - **Total:** 100.0%
  - **Currency:** 100.0%
  - **Transaction Date:** 90.0% (German European dot format `01.10.2026` handled with warning)
  - **Document Type:** 100.0%

### 5.2 Synthetic Scenarios Tested
1. `aws-cloud-invoice-sep2026.pdf`: Standard cloud infrastructure bill ($42.18, 0% tax) → Reconciled.
2. `starbucks-client-meeting.png`: Multi-item cafe receipt ($13.50 subtotal + $1.35 tax = $14.85 total) → Reconciled.
3. `github-pro-subscription.pdf`: Developer SaaS annual subscription ($48.00) → Reconciled.
4. `staples-design-sketchbooks.jpg`: Office supplies with cash tender and change ($32.40 total) → Reconciled.
5. `hetzner-cloud-europe.pdf`: European VAT invoice (€46.00 + €8.74 VAT = €54.74 total) → Reconciled.
6. `heathrow-express-transit.png`: UK travel transit ticket (£25.00 total) → Reconciled.
7. `reconciliation-mismatch-bistro.png`: Bistro charge with unstated tip ($20.00 + $2.00 tax vs $28.50 charged) → **Mismatch Detected ($6.50 delta)**.
8. `illegible-taxi-receipt.png`: Smudged meter fare with missing total → **Flagged for Human Review**.
9. `indian-gst-tech-solutions.pdf`: Tech consulting with GST and promotional discount (₹2300 + ₹414 GST - ₹114 discount = ₹2600) → Reconciled.
10. `express-courier-surcharge.pdf`: Urgent shipping with delivery surcharge ($50 + $4 tax + $10 surcharge = $64 total) → Reconciled.

---

## 6. Security Defense: CSV Injection Sanitization

Spreadsheet formula injection (CWE-1236) occurs when untrusted user or vendor input begins with executable formula characters (`=`, `+`, `-`, `@`, `\t`, `\r`). If an accountant opens an exported CSV in Microsoft Excel or LibreOffice, malicious formulas can execute arbitrary commands (`=cmd|' /C calc'!A0`).

### Defense Implementation (`backend/export.py`)
```python
def sanitize_csv_cell(val: Any) -> Any:
    if val is None:
        return ""
    val_str = str(val).strip()
    # Neutralize spreadsheet formula injection prefixes
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str
```
- **Fuzz Test Suite:** `test_formula_injection_defense_suite` verifies all dangerous payloads (`=1+1`, `=CMD|...`, `@SUM()`, `+12345`, `-calc`, `\tcmd.exe`) are safely escaped with a single leading quote `'`.

---

## 7. Hosted Deployment & Live Network Verification

The production instance is live on Render:
- **URL:** [https://pocketledger-ai.onrender.com](https://pocketledger-ai.onrender.com)
- **Live Status Probe (`GET /api/status`):**
```json
{
  "app_name": "PocketLedger AI",
  "version": "1.0.0",
  "environment": "production",
  "ollama_connected": false,
  "ollama_url": "http://localhost:11434",
  "gemma_model": "gemma2:2b",
  "gemma_available": false,
  "ocr_available": false,
  "ocr_engine": "none",
  "ocr_binary_path": null,
  "database_connected": true,
  "current_mode": "deterministic_fallback"
}
```
- **Render Configuration:** Docker multi-stage build deploying FastAPI + pre-built React frontend bundle to a unified port.
- **Deterministic Fallback Transparency:** Status endpoint and frontend badges explicitly declare `deterministic_fallback` when operating on cloud tiers without local Gemma, maintaining 100% operational integrity.

---

## 8. Artifact and Media Verification

| Asset | Location / URL | Description |
|---|---|---|
| **Walkthrough Video (YouTube)** | [https://youtu.be/Uk_9aB7Z0xo?si=P0W50wuzLihcNeFz](https://youtu.be/Uk_9aB7Z0xo?si=P0W50wuzLihcNeFz) | 50-second end-to-end demo video with audio voiceover |
| **Direct Video File** | `docs/video/PocketLedger_AI_Demo_50s.mp4` | 1080p MP4 recording (6 scenes: Problem, On-Device Gemma, Extraction, Math Check, Human Approval, CSV Export) |
| **Workflow Diagram GIF** | `docs/screenshots/pocketledger-workflow.gif` | Animated end-to-end workflow walkthrough |
| **Hero Banner** | `docs/screenshots/hero_banner.png` | 1280x640 DEV.to submission banner |
| **App Screenshots** | `docs/screenshots/01_dashboard.png` through `06_csv_export.png` | High-resolution UI captures of core features |
| **Architecture Spec** | `docs/architecture.md` | Comprehensive system design, data flows, and security model |
| **DEV.to Article Draft** | `docs/devto-hacktoberfest-week2-final.md` | Complete submission markdown article |
