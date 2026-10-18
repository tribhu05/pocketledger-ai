## Prize Categories

### Primary Category: Side Hustle
PocketLedger AI was built specifically for the **Side Hustle** prompt. It tackles a concrete administrative pain point experienced by independent developers, freelancers, and solo consultants: organizing sensitive receipts and business expenses without sacrificing client confidentiality or paying expensive monthly accounting SaaS fees.

### Sponsor Category: Google Gemma / Open-Source AI
PocketLedger AI is entered for the **Gemma / Open-Source AI** track:

- **Local Gemma 2B Inference Engine:** The application integrates Google's open-weight **Gemma 2B Instruct** (`gemma2:2b`) model running entirely on-device through the local Ollama REST API (`POST http://localhost:11434/api/generate`). Sensitive client invoices, addresses, and billing amounts never leave the developer's laptop.
- **Strict Structured Schema:** Prompt instructions constrain Gemma 2B to output validated financial entities (merchant, transaction date, subtotal, tax, discount, surcharge, total, currency, and freelance category).
- **Defensive Multi-Stage Parsing:** Small open-weight models sometimes wrap JSON in conversational markdown or trailing text. PocketLedger includes a 4-stage JSON recovery parser in `backend/gemma_extractor.py` and automated Pydantic coercion.

![PocketLedger AI Gemma Integration Proof](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/gemma_integration_proof.png)

#### Gemma Integration & Prompt Schema (`backend/gemma_extractor.py`)

```python
# System prompt constraining Google Gemma 2B to valid financial schema
GEMMA_SYSTEM_PROMPT = """You are PocketLedger AI, a precise financial document extraction engine for freelancers.
Extract key expense fields from the provided receipt or invoice text.
Output MUST be a valid JSON object matching this exact schema:

{
  "merchant": "string or null - Name of business/vendor. NEVER guess or invent.",
  "document_type": "receipt | invoice | other",
  "invoice_number": "string or null",
  "transaction_date": "string or null - Date formatted as YYYY-MM-DD",
  "currency": "string - 3-letter currency code (USD, EUR, GBP, CAD, INR, etc.)",
  "subtotal": "number or null - Pre-tax amount",
  "tax": "number or null - Tax/VAT/GST amount",
  "discount": "number or null - Explicit discount or promo deduction",
  "additional_charges": "number or null - Tips, service fees, or surcharge",
  "total": "number or null - Grand total amount",
  "category": "one of: Software & SaaS, Cloud & Hosting, Hardware, Travel, Meals, Office Supplies, Advertising, Professional Services, Other"
}

CRITICAL RULES:
1. NEVER invent, hallucinate, or assume missing values. If not visible, use null.
2. Monetary fields MUST be numeric (or null), never strings.
3. Output ONLY valid JSON. Do not wrap in markdown or commentary."""
```

#### Verified Automated Test Suite (`backend/tests/test_backend.py`)

```text
$ pytest backend/tests/test_backend.py -k gemma -v
backend/tests/test_backend.py::test_schema_currency_string_coercion PASSED   [ 50%]
backend/tests/test_backend.py::test_gemma_json_parser_robustness     PASSED   [100%]
============================= 2 passed in 1.42s =============================
```

### Partner Category: Best Use of Render
PocketLedger AI is entered for the **Best Use of Render** prize track:

- **Live Production Deployment:** [https://pocketledger-ai.onrender.com](https://pocketledger-ai.onrender.com)
- **Declarative Blueprint (`render.yaml`):** Continuous deployment with automated health check probes on `/api/status`.
- **Zero-Friction Evaluation:** Hackathon judges can test the full ingest, reconciliation, review, and export workflow instantly with zero local setup.

![PocketLedger AI Render Deployment Proof](https://raw.githubusercontent.com/tribhu05/pocketledger-ai/master/docs/screenshots/render_deployment_proof.png)

#### Infrastructure as Code: Declarative `render.yaml` Blueprint

```yaml
services:
  - type: web
    name: pocketledger-ai
    runtime: docker
    plan: free
    region: oregon
    healthCheckPath: /api/status
    envVars:
      - key: PORT
        value: 10000
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        value: sqlite:///:memory:
```

#### Unified Multi-Stage `Dockerfile`

```dockerfile
# Stage 1: Build Frontend (React 19 + TypeScript + Vite)
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend + Static Asset Serving
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr libtesseract-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
EXPOSE 10000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

#### Cloud-Resilient Architecture
In cloud environments where a local Ollama daemon is absent, the backend gracefully activates its deterministic regex/heuristic fallback parser. Evaluators get immediate, reliable document intake and financial reconciliation without configuration overhead.
