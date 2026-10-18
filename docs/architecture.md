# PocketLedger AI — System Architecture & Technical Specification

> **"AI reads the document. Deterministic code checks the numbers. Humans approve the record."**

PocketLedger AI is engineered on a **local-first, privacy-by-design architecture**. It is specifically designed for freelancers, independent developers, and consultants who require automated receipt extraction without exposing sensitive financial invoices to third-party cloud AI vendors.

---

## 1. System Topology & Architectural Layers

The architecture is divided into five strictly decoupled layers with an enforced **On-Device Privacy Boundary**:

```mermaid
flowchart TB
    subgraph PRESENTATION["1. Client Presentation Layer (Browser)"]
        UI["React 19 + TypeScript + Vite SPA"]
        Dashboard["Dashboard & KPI Cards"]
        Inbox["Document Upload Inbox\n(Drag & Drop / PDF / Image / Text)"]
        ReviewModal["Split-Screen Review Canvas\n(Original Receipt vs. Extracted Fields)"]
        Ledger["Multi-Currency Ledger & Filter Search"]
        StatusPill["System Status & Mode Indicator\n(gemma2_local vs. deterministic_fallback)"]
    end

    subgraph GATEWAY["2. Application Gateway & API Layer (FastAPI)"]
        Router["FastAPI REST Router (:8000 / :10000)"]
        SecGuards["Path Traversal & Size Guards (<= 15 MB)"]
        Endpoints["Endpoints:\n• POST /api/upload\n• POST /api/review/{id}\n• GET /api/status\n• GET /api/export/csv\n• POST /api/load-demo"]
    end

    subgraph PIPELINE["3. Document Extraction Pipeline"]
        DocRouter{"MIME Type Detection"}
        PDFEngine["pypdf Digital Vector Extractor\n(Stripe, AWS, GitHub invoices)"]
        OCREngine["Tesseract OCR Engine\n(Scanned paper & camera receipts)"]
        TextNorm["Text Normalizer & Encoding Cleaner"]
    end

    subgraph PRIVACY_BOUNDARY["4. Intelligence & Privacy Boundary (100% On-Device)"]
        Dispatcher{"Model Dispatcher\n(Ollama Health Probe)"}
        
        subgraph LOCAL_MODE["Local Mode (Default)"]
            Ollama["Local Ollama Daemon (:11434)"]
            Gemma["Google Gemma 2B Instruct\n(gemma2:2b open-weight weights)"]
        end

        subgraph FALLBACK_MODE["Hosted Fallback Mode (Cloud Containers)"]
            Fallback["Deterministic Regex & Pattern Engine\n(Zero-friction evaluation on Render)"]
        end

        JSONParser["4-Stage Defensive JSON Recovery Parser\n1. Direct JSON Parse\n2. Markdown Fence Stripper\n3. Balanced Brace Extractor\n4. Pydantic Schema Coercion"]
    end

    subgraph VALIDATION["5. Deterministic Verification & Reconciliation"]
        DecimalEngine["Python Decimal Engine\nExact cent precision (No float drift)"]
        ReconcileRule["Reconciliation Math Check:\nExpected = Subtotal + Tax - Discount + Charges\nVariance Delta = |Stated - Expected|"]
        StatusClassifier{"Status Classifier"}
        Reconciled["Status: reconciled (Delta <= 0.05)"]
        Mismatch["Status: mismatch (Delta > 0.05)"]
        Unverified["Status: unverified (Missing Total)"]
        DateNorm["ISO-8601 Date Normalizer (YYYY-MM-DD)"]
        CurrNorm["ISO-4217 Currency Standardizer (USD, EUR, GBP, INR)"]
    end

    subgraph PERSISTENCE["6. Persistence, Audit & Defensive Export"]
        AuditDiff["Audit Trail & Field Diff Tracker\nRecords JSON diff of manual corrections"]
        SQLiteDB[("SQLite Database\npocketledger.db / :memory:")]
        CSVExport["Defensive CSV Generator\nMulti-currency segregation & formula injection guard"]
    end

    %% Wiring
    Inbox -->|Multipart Upload| Router
    Router --> SecGuards --> Endpoints
    Endpoints --> DocRouter
    DocRouter -->|application/pdf| PDFEngine --> TextNorm
    DocRouter -->|image/png, image/jpeg| OCREngine --> TextNorm
    TextNorm --> Dispatcher

    Dispatcher -->|Ollama Available| Ollama --> Gemma --> JSONParser
    Dispatcher -->|Ollama Offline| Fallback --> JSONParser

    JSONParser --> DecimalEngine
    DecimalEngine --> ReconcileRule --> StatusClassifier
    StatusClassifier --> Reconciled --> Endpoints
    StatusClassifier --> Mismatch --> Endpoints
    StatusClassifier --> Unverified --> Endpoints

    Endpoints --> AuditDiff --> SQLiteDB
    ReviewModal -->|Approve & Edit Diff| Endpoints
    Ledger -->|Query Records| Endpoints
    Endpoints --> CSVExport
    StatusPill -->|Probe Health| Endpoints
```

---

## 2. End-to-End Processing Sequence

The sequence diagram illustrates how a receipt flows from raw upload to verified storage:

```mermaid
sequenceDiagram
    autonumber
    actor User as Freelancer / User
    participant Frontend as React 19 Frontend
    participant API as FastAPI Backend
    participant Ingest as Extraction Engine (PDF/OCR)
    participant Ollama as Local Ollama (Gemma 2B)
    participant Validator as Python Decimal Validator
    participant DB as SQLite Database

    User->>Frontend: Uploads receipt (PDF / Image)
    Frontend->>API: POST /api/upload (multipart/form-data)
    API->>API: Sanitize filename & verify path safety
    API->>Ingest: Extract document text
    Ingest-->>API: Normalized raw text
    
    alt Ollama daemon is active
        API->>Ollama: POST /api/generate (format: "json", temperature: 0.1)
        Ollama-->>API: Raw JSON response
    else Ollama daemon offline / Cloud container
        API->>API: Execute deterministic heuristic fallback
    end

    API->>API: 4-stage JSON parser & Pydantic schema validation
    API->>Validator: Reconcile amounts (Subtotal, Tax, Discount, Charges, Total)
    Validator->>Validator: Expected = Subtotal + Tax - Discount + Charges
    Validator-->>API: Status (reconciled | mismatch | unverified) + warnings

    API->>DB: Store pending record with raw text & extraction payload
    DB-->>API: Record ID
    API-->>Frontend: Return ExtractedReceipt object

    Frontend->>User: Display split-screen review modal
    User->>Frontend: Edits merchant/category & clicks "Confirm & Approve"
    Frontend->>API: POST /api/review/{id} (edits, user_notes)
    API->>API: Compute JSON diff ({old_val, new_val})
    API->>DB: Mark status = "confirmed", persist audit diff
    DB-->>API: OK
    API-->>Frontend: Updated record
    Frontend->>User: Display confirmed record in Ledger
```

---

## 3. Financial Document State Machine

Every document ingested by PocketLedger AI transitions through strict lifecycle states:

```mermaid
stateDiagram-v2
    [*] --> Ingested: File Uploaded
    Ingested --> Extracted: Text Extracted (pypdf / Tesseract)
    
    state Extraction_Routing {
        Extracted --> Gemma_Inference: Ollama Online
        Extracted --> Deterministic_Fallback: Ollama Offline
        Gemma_Inference --> Schema_Validated: 4-Stage JSON Recovery
        Deterministic_Fallback --> Schema_Validated: Regex Extraction
    }

    state Reconciliation_Engine {
        Schema_Validated --> Reconciled: Delta <= 0.05
        Schema_Validated --> Mismatch: Delta > 0.05
        Schema_Validated --> Unverified: Total is null
    }

    state Human_Review {
        Reconciled --> Pending_Review
        Mismatch --> Pending_Review: Flagged with Arithmetic Warning
        Unverified --> Pending_Review: Flagged with Missing Total Warning
        
        Pending_Review --> Confirmed: User Approves (Records Field Diff)
        Pending_Review --> Discarded: User Deletes Record
    }

    Confirmed --> Exportable: Available in Multi-Currency CSV
    Discarded --> [*]
    Exportable --> [*]
```

---

## 4. Key Architectural Safeguards

### 4.1. IEEE 754 Floating-Point Drift Elimination
Binary floating-point types (`float` in Python/JavaScript) cannot precisely represent decimal currency fractions:
```python
# The standard float hazard:
0.1 + 0.2 == 0.30000000000000004  # False!
```
In PocketLedger AI, all calculations in [`backend/validator.py`](../backend/validator.py) use Python's built-in `Decimal` with fixed 2-place quantizing:

$$\text{Expected Total} = \text{Subtotal} + \text{Tax} - \text{Discount} + \text{Additional Charges}$$
$$\Delta = |\text{Stated Total} - \text{Expected Total}|$$

A configured tolerance of `0.05` accounts for minor cent-rounding variances across regional tax laws without masking legitimate discrepancies.

### 4.2. 4-Stage Defensive JSON Recovery
Small open-weight LLMs (such as 2B parameter models) occasionally output conversational preamble or markdown code fences even when requested to output strict JSON. Rather than crashing, [`backend/gemma_extractor.py`](../backend/gemma_extractor.py) executes a 4-tier recovery cascade:
1. **Direct Parse:** Attempts `json.loads(raw_text)`.
2. **Markdown Fence Stripping:** Regex isolates ````json { ... } ```` blocks.
3. **Outer Balanced Braces:** Finds first `{` and last `}` to isolate valid JSON objects.
4. **Pydantic Type Coercion:** Strips currency symbols (`$1,234.50` → `1234.50`) and treats `NaN`/unreadable values as `None`.

### 4.3. Anti-CSV Injection Defense
Spreadsheet software (Microsoft Excel, LibreOffice Calc, Apple Numbers, Google Sheets) interprets cells starting with formula trigger symbols as executable expressions. Malicious receipt text containing `=cmd|' /C calc'!A0` or `-2+3+cmd|...` poses a serious risk to freelancers opening downloaded CSVs.

PocketLedger AI implements formula neutralization in [`backend/export.py`](../backend/export.py):
```python
def sanitize_csv_cell(val: Any) -> Any:
    if val is None:
        return ""
    val_str = str(val).strip()
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str
```
Every potentially malicious cell is prefixed with a single quote (`'`), forcing spreadsheet software to treat the contents strictly as plaintext.

### 4.4. Multi-Currency Segregation
Adding `100 USD + 100 EUR + 100 GBP` without exchange rate conversion results in corrupt tax reporting. PocketLedger's reporting engine automatically partitions summary data by currency code:
```text
Tax Summary by Currency:
  • USD: $1,420.50 (Tax: $122.10)
  • EUR: €340.00   (VAT: €64.60)
  • GBP: £85.20    (VAT: £14.20)
  • INR: ₹2,600.00 (GST: ₹414.00)
```

---

## 5. Technology Stack Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | React | 19.x | Component-driven UI and responsive review modal |
| **Frontend Language** | TypeScript | 5.x | Strict type safety synchronized with backend schemas |
| **Bundler & Build** | Vite | 5.x | Instant HMR development and optimized production bundles |
| **Styling & Icons** | Tailwind CSS & Lucide | 3.x / Latest | High-contrast dark/light accessible financial interface |
| **Backend Framework** | FastAPI | 0.115+ | High-performance asynchronous REST API |
| **Python Runtime** | Python | 3.11 / 3.14 | Modern async/await and native `Decimal` engine |
| **AI Model** | Google Gemma 2B Instruct | `gemma2:2b` | Open-weight on-device entity extraction |
| **Local Inference Host** | Ollama | 0.3+ | Local model serving with low-temperature JSON formatting |
| **Text Extraction** | `pypdf` & `pytesseract` | Latest | Dual digital-PDF and OCR raster image processing |
| **Database** | SQLite | 3.x | Persistent local storage (`pocketledger.db`) |
| **Containerization** | Docker | Multi-stage | Single-container deployment (Vite dist + FastAPI + Tesseract) |
| **Cloud Hosting** | Render | Blueprint | Continuous deployment via `render.yaml` with health probes |
