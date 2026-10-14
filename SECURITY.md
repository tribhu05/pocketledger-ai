# Security Policy

## Security Philosophy

PocketLedger AI was engineered from day zero around the core principle of **Zero-Knowledge Financial Privacy**. We believe financial records (receipts, client names, banking details, invoices) belong exclusively on the user's local device.

## Threat Model & Security Controls

### 1. Data Ingress & Local Inference Boundary
- **Network Isolation:** By default, PocketLedger AI binds exclusively to localhost interfaces (`127.0.0.1`).
- **No Third-Party Telemetry:** Document content, merchant names, invoice numbers, and monetary amounts are never sent to external AI providers, analytics platforms, or telemetry collectors.
- **Local Model Execution:** All LLM inference is directed to a local Ollama daemon hosting Google's open-weight Gemma 2B model on `http://localhost:11434`.

### 2. Path Traversal & Unsafe File Handling
- When a document is uploaded, the original filename is sanitized to strip path separators (`/`, `\`, `..`).
- A random UUID prefix is assigned to every stored file (`{uuid}_{sanitized_name}`).
- When serving files via `/api/documents/{id}/file`, the backend resolves the canonical filesystem path and strictly asserts that the target resides inside the trusted `uploads/` root directory. Requests referencing paths outside this directory return HTTP 403.

### 3. CSV Injection (Formula Injection) Defense
- Exporting financial data to CSV opens the risk of malicious formula execution in spreadsheet software (Microsoft Excel, LibreOffice Calc, Google Sheets).
- PocketLedger implements an automated cell sanitizer in `backend/export.py`. Any cell content starting with dangerous formula prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) is automatically prepended with a single quote (`'`), neutralizing executable payloads.

### 4. Upload Size and Type Restrictions
- Maximum upload size is strictly limited to 15 MB per file.
- Allowed MIME types and extensions are strictly restricted to `.png`, `.jpg`, `.jpeg`, `.webp`, and `.pdf`. Executable files and scripts are rejected with HTTP 400.

### 5. Data Erasure & Compliance
- Users can completely and permanently delete all records and uploaded source files at any time via the `/api/reset-data` endpoint or through the Settings & Privacy interface.

## Reporting a Vulnerability

If you discover a security vulnerability in PocketLedger AI, please do not file a public issue. Instead, submit a report via GitHub Private Vulnerability Reporting or email the maintainers directly.

We appreciate responsible disclosure and will respond within 48 hours.
