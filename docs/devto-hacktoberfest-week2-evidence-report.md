# PocketLedger AI — Technical Audit & Evidence Report
**Hacktoberfest 2026 Open-Source AI Challenge (Week 2: Side Hustle)**  
*Audit Date:* October 18, 2026  
*Auditor:* AI Engineering Pair & Open-Source Auditor  
*Repository:* [https://github.com/tribhu05/pocketledger-ai](https://github.com/tribhu05/pocketledger-ai)  
*Hosted Demo:* [https://pocketledger-ai.onrender.com](https://pocketledger-ai.onrender.com)  

---

## 1. Executive Summary

This report establishes verifiable engineering proof for **PocketLedger AI**, an expense-management co-pilot designed for freelancers. The core technical premise is:
> **"AI reads the document. Deterministic code checks the numbers. Humans approve the record."**

Every claim presented in the accompanying DEV.to submission (`docs/devto-hacktoberfest-week2-final.md`) has been checked against local source code, automated test executions, live network probes, and media file inspections.

---

## 2. Automated Test Suite Execution

### 2.1 Backend Test Suite (Pytest)
- **Command:** `.venv\Scripts\pytest.exe -v`
- **Result:** **10 Passed, 0 Failed, 1 Warning** (10.90 seconds)
- **Environment:** Windows, Python 3.14.0, pytest 9.1.1, anyio 4.15.1, asyncio 1.4.0

| Test Name | File | Verified Behavior | Status |
|---|---|---|---|
| `test_reconciliation_math` | `backend/tests/test_backend.py` | Validates math formula with discounts, additional charges, rounding tolerance (0.05), and flags mismatches with exact delta. | **PASSED** |
| `test_record_validation_backward_compatibility` | `backend/tests/test_backend.py` | Ensures legacy records lacking a discount default gracefully to `0.0` without false reconciliation errors. | **PASSED** |
| `test_date_normalization` | `backend/tests/test_backend.py` | Parses ISO, US (`MM/DD/YYYY`), written month formats, and flags missing or future dates. | **PASSED** |
| `test_currency_normalization` | `backend/tests/test_backend.py` | Maps `$`, `€`, `£`, `₹`, `¥` to ISO-4217 currency codes with contextual text fallback. | **PASSED** |
| `test_csv_injection_sanitization` | `backend/tests/test_backend.py` | Neutralizes formula injection by prepending `'` to cells starting with `=`, `+`, `-`, `@`, `\t`, `\r`. | **PASSED** |
| `test_csv_export_multi_currency_segregation` | `backend/tests/test_backend.py` | Confirms summary CSV aggregates by `(month, category, currency)` and never blends currencies into meaningless blended sums. | **PASSED** |
| `test_deterministic_fallback` | `backend/tests/test_backend.py` | Validates regex heuristic fallback parsing when Ollama is offline, extracting totals and vendors. | **PASSED** |
| `test_api_status_endpoint` | `backend/tests/test_backend.py` | Verifies `/api/status` returns application metadata and confirms active SQLite database connection. | **PASSED** |
| `test_raw_text_upload_and_review_workflow` | `backend/tests/test_backend.py` | Executes full lifecycle: raw text ingestion → review update → audit trail diff generation → dashboard spend reflection → deletion. | **PASSED** |
| `test_discount_reconciliation_workflow` | `backend/tests/test_backend.py` | Tests Indian GST discount receipt (Subtotal ₹2300, GST ₹414, Discount ₹114, Total ₹2600) and verifies CSV export. | **PASSED** |

*Note on Warning:* One Pydantic v2 deprecation warning (`Support for class-based config is deprecated, use ConfigDict instead` in `backend/config.py`). Non-breaking.

---

### 2.2 Frontend Test Suite (Vitest)
- **Command:** `npm test -- --run` (in `frontend/`)
- **Result:** **7 Passed, 0 Failed** (1 test file, 1.47s test runtime)
- **Test File:** `frontend/src/test/App.test.tsx`
- **Environment:** Vitest v5.0.4, React Testing Library, JSDOM

| Test Description | Verified UI Behavior | Status |
|---|---|---|
| `renders navbar and displays live on-device Gemma status` | Confirms navigation bar, branding, and "100% On-Device" status pill. | **PASSED** |
| `renders dashboard with confirmed expense metrics` | Checks financial overview metrics, category breakdown, and total amounts. | **PASSED** |
| `navigates to ledger and filters by search query` | Tests search input and empty-state messaging upon filtering non-matching strings. | **PASSED** |
| `navigates to reports view and verifies CSV export links` | Verifies export tabs and presence of confirmed expenses and summary download buttons. | **PASSED** |
| `navigates to pricing and displays honest side hustle experiment` | Validates pricing tier display and presence of the freelancer validation survey form. | **PASSED** |
| `opens review modal and displays editable financial fields` | Confirms modal opens with populated vendor, total, and split-screen inputs. | **PASSED** |
| `displays discount field and balanced reconciliation banner` | Validates review modal renders discount input and "Reconciliation Balanced" banner. | **PASSED** |

---

## 3. Mathematical Reconciliation Engine Proof

### 3.1 The Equation
Implemented in `backend/validator.py`:
$$\text{Expected Total} = \text{round}(\text{Subtotal} + \text{Tax} - \text{Discount} + \text{Additional Charges}, 2)$$
$$\text{Difference} = |\text{Stated Total} - \text{Expected Total}|$$

- **Reconciled Condition:** $\text{Difference} \le 0.05$ (accounts for floating-point cent differences and cash rounding).
- **Mismatch Condition:** $\text{Difference} > 0.05$ or missing Stated Total.

### 3.2 Real Test Cases Verified
1. **Balanced Case (Standard):**
   - Subtotal: `$42.18`, Tax: `$0.00`, Total: `$42.18`
   - Expected: `$42.18`, Difference: `$0.00` → `reconciled`
2. **Balanced Case with Discount (Indian GST):**
   - Subtotal: `₹2300.00`, GST: `₹414.00`, Discount: `₹114.00`, Stated Total: `₹2600.00`
   - Expected: $2300 + 414 - 114 = 2600$, Difference: `₹0.00` → `reconciled`
3. **Discrepancy Case (Unstated Tip or Price Creep):**
   - Subtotal: `$2300.00`, Tax: `$414.00`, Discount: `$114.00`, Stated Total: `$2714.00`
   - Expected: `$2600.00`, Difference: `$114.00` → `mismatch`
   - Generated Warning:
     `Reconciliation mismatch: Breakdown: Subtotal (2300.00) + Tax (414.00) - Discount (114.00) + Additional Charges (0.00) = Expected Total (2600.00) vs Stated Total (2714.00), Difference: 114.00. Please review source receipt.`

---

## 4. Security & Defensive Engineering Proof

### 4.1 CSV Formula Injection Neutralization
- Implemented in `backend/export.py` (`sanitize_csv_cell`).
- Threat Vector: Malicious merchants embedding spreadsheet formulas (`=cmd|' /C calc'!A0`, `@SUM()`, `+12345`) into vendor names or descriptions to execute code when an accountant opens the exported CSV in Excel or LibreOffice.
- Sanitization Routine:
  ```python
  if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
      return f"'{val_str}"
  ```
- Verified: Both unit tests and export endpoints confirm formula prefixes are safely escaped with a leading single quote (`'`).

### 4.2 Multi-Currency Segregation
- Freelancers frequently bill international clients in USD, EUR, GBP, and INR.
- Naive financial tools sum these into a single dollar total, distorting accounting books.
- Verified: `export_summary_to_csv()` groups strictly by `(Month, Category, Currency)`. A `$50.00` USD expense and a `€40.00` EUR expense generate two distinct summary rows.

---

## 5. Architectural Runtime Verification: Local vs Hosted

### 5.1 Local Workstation Verification
- **Model:** `gemma2:2b` (Google Gemma 2B Instruct, 4-bit quantized, 1.63 GB on disk).
- **Runtime:** Ollama daemon (`http://localhost:11434`).
- **Benchmark Hardware:** AMD Ryzen 3 7320U (4 Cores, 8 Threads), 8 GB RAM, Integrated Radeon 610M Graphics.
- **Measured Latency:** Average 34.1 seconds per receipt on CPU.
- **Privacy Boundary:** 100% of tokens remain inside local memory; zero internet requests generated during inference.

### 5.2 Hosted Demo Verification (Render)
- **URL:** `https://pocketledger-ai.onrender.com`
- **Probe Date:** October 18, 2026, 16:19 UTC
- **HTTP Response:** `HTTP/1.1 200 OK`, Server: Cloudflare, Origin: Uvicorn
- **Live `/api/status` Payload:**
  ```json
  {
    "app_name": "PocketLedger AI",
    "version": "1.0.0",
    "environment": "production",
    "ollama_connected": false,
    "ollama_url": "http://localhost:11434",
    "gemma_model": "gemma2:2b",
    "gemma_available": false,
    "ocr_available": true,
    "ocr_engine": "tesseract",
    "ocr_binary_path": "/usr/bin/tesseract",
    "database_connected": true,
    "current_mode": "deterministic_fallback"
  }
  ```
- **Comparison Table:**

| Feature | Local Mode (Workstation) | Hosted Mode (Render Demo) |
|---|---|---|
| **AI Extraction Engine** | Google Gemma 2B via Ollama | Deterministic Regex Fallback |
| **Privacy Guarantee** | 100% On-Device (Zero Egress) | Ephemeral Container (Render Cloud) |
| **OCR Capability** | Tesseract OCR + pypdf | Tesseract OCR (`/usr/bin/tesseract`) + pypdf |
| **Math Reconciliation** | Deterministic Equation ($\le 0.05$) | Deterministic Equation ($\le 0.05$) |
| **Human Review Screen** | Full Interactive Split-Screen | Full Interactive Split-Screen |
| **Persistence** | Persistent Local SQLite (`pocketledger.db`) | In-Memory / Ephemeral SQLite |
| **CSV Export** | Formula-Sanitized Multi-Currency | Formula-Sanitized Multi-Currency |
| **Intended Purpose** | Production Freelance Use | Public Evaluation & Evaluator Walkthrough |

---

## 6. Demo Video & Visual Asset Audit

### 6.1 Demo Video Verification
- **File:** `docs/video/PocketLedger_AI_Demo_50s.mp4`
- **Duration:** Exactly **50.00 seconds** (Verified via FFprobe).
- **Video Stream:** H.264 (High), 1920×1080 @ 30 fps, progressive, 857 kbps bitrate.
- **Audio Stream:** AAC stereo, 44,100 Hz, 193 kbps bitrate.
- **Audio Mastering:** Narrated with `en-US-AndrewNeural`, processed through studio EQ (high-pass filter at 120 Hz, presence shelf boost +4 dB at 3.5 kHz, dynamic compression ratio 3:1). Background ambient pad ducked to -29 dB whisper.
- **Subtitles:** Burned-in synchronized subtitles matching the six storyboard scenes.
- **Delivery:** GitHub streamable link provided in the article.

### 6.2 Screenshot & GIF Verification
All visual assets correspond to genuine application interfaces and are committed in `docs/screenshots/`:
- `hero_banner.png`: 1200×636 (100:53 ratio), dark charcoal background, crisp typography, verified badge.
- `pocketledger-workflow.gif` / `pocketledger_demo.gif`: 481 KB, 1080×675 animated workflow walkthrough.
- `01_dashboard.png`: Financial overview with multi-currency summary and recent activity.
- `02_inbox.png`: Document Inbox showing receipt upload cards and status badges.
- `03_ledger.png`: Searchable, filterable expense ledger with category and reconciliation columns.
- `04_review_modal.png`: Split-screen review screen displaying extracted values and reconciliation state.
- `05_reports_csv.png`: Reporting tab with CSV download options.
- `06_system_status.png`: Privacy and model health dashboard showing on-device status.
- `nitu_feedback.png`: Authentic WhatsApp feedback from tester Nitu.

---

## 7. Known Limitations & Honest Disclosures

1. **CPU Latency:** On low-power 4-core laptops without dedicated GPUs, local Gemma 2B inference takes ~34 seconds per receipt. It is designed for background batch processing, not instantaneous chatbot streaming.
2. **Setup Friction:** Local execution requires installing Ollama and pulling `gemma2:2b` (1.63 GB).
3. **Non-Latin Scripts:** Tested primarily on Latin-character receipts (English, German, French, Spanish). Non-Latin script accuracy is unmeasured.
4. **Thermal Paper Degradation:** Badly smudged or faded thermal receipts may fail OCR and default to manual entry.
