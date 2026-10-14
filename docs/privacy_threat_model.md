# Privacy & Threat Model

## 1. Why Freelancers Need Local AI Bookkeeping

Independent developers, freelance designers, and consultants regularly handle receipts containing:
- Client names and confidential project codes.
- Full personal legal names, phone numbers, and residential billing addresses.
- Partial credit card digits and payment routing numbers.
- Travel itineraries, hotel locations, and dining timestamps.

Cloud receipt scanners require transmitting these documents to third-party proprietary servers, where they may be stored indefinitely, processed by third-party sub-processors, or indexed into training datasets.

PocketLedger AI guarantees that **your documents never leave your physical machine**.

## 2. Threat Vector Analysis & Mitigations

| Threat Vector | Potential Impact | PocketLedger AI Defense |
|---|---|---|
| **Cloud Exfiltration** | Third-party access to confidential invoices | Ollama runs locally on `127.0.0.1`. No external API keys are configured or needed. |
| **Path Traversal Attack** | Attacker fetches sensitive host files via `../` in file download endpoints | File serving endpoint canonicalizes filesystem paths and asserts that target resides inside the bounded `uploads/` directory. |
| **CSV Formula Injection** | Attacker uploads receipt with `=cmd|' /C calc'!A0` to execute arbitrary commands upon CSV export | `backend/export.py` prepends `'` to any cell beginning with `=`, `+`, `-`, `@`, `\t`, or `\r`. |
| **Model Hallucination** | LLM invents taxes, amounts, or vendor names | Strict prompt rules forbidding hallucination + deterministic math checks comparing subtotal + tax against total. |
| **Data Retention** | Old financial documents lingering on shared devices | One-click permanent data wipe (`/api/reset-data`) removes both SQLite records and local document files. |
| **CORS Exploitation** | Malicious browser tabs accessing local backend | CORS origins restricted to local development ports (`5173`, `3000`, `8000`). |

## 3. Local vs. Hosted Demo Distinction

- **Local Mode (Production Experience):** The full privacy-first product. All inference runs on your local CPU/GPU via Ollama. 100% offline and private.
- **Hosted Web Demos:** Frontends deployed to cloud hosts (such as Render or Vercel) **cannot** access a visitor's local Ollama instance due to browser sandbox boundaries. Hosted public demos must utilize synthetic sample documents and disclose that remote inference or pre-extracted mock fixtures are active. We never describe a hosted demo as "offline on-device" unless running locally.
