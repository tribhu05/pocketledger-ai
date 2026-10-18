# About PocketLedger AI

> **"Your receipts. Your records. Your data stays yours."**

**PocketLedger AI** is an open-source, privacy-first bookkeeping assistant designed specifically for freelancers, independent software engineers, consultants, and solo creators.

---

## 🎯 The Mission

Freelancers often spend hours each tax season transcribing messy receipts and invoices into spreadsheets. Traditional solutions force an unacceptable dilemma:
- **Manual Data Entry:** Tedious, slow, and prone to transcription errors.
- **Cloud AI Bookkeeping:** Uploads sensitive client invoices, home addresses, hourly rates, and banking details to proprietary cloud APIs.

**PocketLedger AI solves this by keeping intelligence local and validation deterministic.**

---

## 💡 The Core Philosophy

```
AI reads the document.  ──▶  Deterministic code checks the numbers.  ──▶  Humans approve the record.
```

1. **Local Open-Weight AI:** Text extraction is powered by Google's **Gemma 2B Instruct** running on-device through Ollama. No document images or parsed amounts ever leave your machine.
2. **Deterministic Financial Math:** Extracted figures are verified using exact Python `Decimal` arithmetic. The engine calculates `Expected Total = Subtotal + Tax - Discount + Surcharges` and flags discrepancies rather than hallucinating or silently accepting bad math.
3. **Human-in-the-Loop Review:** An intuitive split-screen review modal gives users full inspection rights and tracks all edits in an immutable JSON diff trail.
4. **Defensive CSV & Multi-Currency Segregation:** Totals are segregated by currency (USD, EUR, GBP, INR) to prevent invalid math, and CSV exports neutralize formula injection vulnerabilities.

---

## 👥 Who Is This For?

- **Freelance Developers & Designers:** Managing dozens of billable tools across multiple clients under strict NDAs.
- **Independent Consultants:** Who need itemized expense categorization for Schedule C or VAT/GST filing.
- **Privacy-Conscious Professionals:** Lawyers, doctors, and financial contractors whose ethics rules prevent uploading records to third-party AI APIs.

---

## 🚀 Live Demo & Repository Resources

* **GitHub Repository:** [https://github.com/tribhu05/pocketledger-ai](https://github.com/tribhu05/pocketledger-ai)
* **Live Hosted Demo:** [https://pocketledger-ai.onrender.com](https://pocketledger-ai.onrender.com)
* **50-Second Video Demo:** [Watch on YouTube](https://youtu.be/Uk_9aB7Z0xo)
* **Hacktoberfest Week 2 Submission:** [Read on DEV.to](docs/devto-hacktoberfest-week2-final.md)
* **Technical Evidence & Test Audit:** [View Report](docs/technical-evidence-report.md)
* **Synthetic Benchmark:** [View Benchmark](docs/benchmark_report.md)
