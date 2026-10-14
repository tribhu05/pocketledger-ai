# Contributing to PocketLedger AI

Thank you for your interest in contributing to PocketLedger AI! We are building a privacy-first, on-device expense assistant for freelancers, independent developers, and creators.

## Principles

1. **Privacy First:** We never introduce code that sends document images, parsed financial amounts, or personally identifiable information to third-party cloud APIs by default.
2. **Honesty & Transparency:** Never disguise heuristic or deterministic fallbacks as neural model output. Every status indicator must truthfully reflect whether Gemma or a fallback processed a document.
3. **Deterministic Verification:** AI output must always be validated by strict deterministic business rules (e.g. subtotal + tax = total math reconciliation).
4. **Reproducible Code:** All features must include unit or integration tests that pass in CI.

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- [Ollama](https://ollama.ai) with `gemma2:2b` (`ollama pull gemma2:2b`)
- (Optional) [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for camera photo OCR.

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/pocketledger-ai.git
cd pocketledger-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend tests
python -m pytest backend/tests/test_backend.py -v

# Start FastAPI server
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# Run frontend tests
npx vitest run

# Run linter
npm run lint

# Start Vite dev server
npm run dev
```

## Pull Request Guidelines
- Ensure all tests pass (`pytest` and `vitest`).
- If adding a new extraction field, update the Pydantic schema in `backend/schemas.py`, TypeScript interface in `frontend/src/types.ts`, and test fixtures in `backend/demo_data.py`.
- Adhere to the code of conduct.
