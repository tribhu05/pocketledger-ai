# Reviewer Demo Script — Test PocketLedger AI in Under 5 Minutes

Follow this quick walkthrough to test all features of PocketLedger AI locally.

---

## Prerequisites (1 minute)

1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```
2. Verify `gemma2:2b` is installed:
   ```bash
   ollama list
   ```
   *(If missing, run `ollama pull gemma2:2b`)*

---

## Step 1: Launch Application (1 minute)

### Terminal 1: Backend
```bash
# In project root:
.venv\Scripts\uvicorn backend.main:app --port 8000
# On Linux/macOS:
source .venv/bin/activate && uvicorn backend.main:app --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## Step 2: Instant Demo Exploration (1 minute)

1. On the **Dashboard**, click the button: **"Load Synthetic Demo Workspace"**.
2. Notice how 8 realistic freelance expenses across USD, EUR, and GBP populate instantly.
3. Observe the metric cards: Confirmed Spend separated by currency (e.g. `$172.43 USD`, `€54.74 EUR`, `£25.00 GBP`), Category Breakdown bars, and the "Needs Review" action badge.

---

## Step 3: Test Reconciliation & Audit Trail (1 minute)

1. Navigate to the **Ledger** tab.
2. Look for the receipt named **`[Demo] reconciliation-mismatch-bistro.png`** showing the amber **"Discrepancy"** warning badge.
3. Click on the row to open the **Review Screen**:
   - On the left: View the raw document evidence where Food Subtotal was $20.00, Tax was $2.00, but Total charged was $28.50 (due to tip).
   - On the right: Note the prominent warning:
     *`Reconciliation Mismatch: Subtotal (20.00) + Tax (2.00) = 22.00, which does not match Total (28.50). Discrepancy of 6.50.`*
   - Expand the **Audit Trail & Lineage History** accordion at the bottom to inspect the raw model JSON response.
   - Click **"Confirm & Approve Record"** to save your verified human confirmation.

---

## Step 4: Test CSV Export & Spreadsheet Security (30 seconds)

1. Click on the **Reports & CSV** tab.
2. Click **"Download Confirmed Expenses CSV"**.
3. Open the downloaded file:
   - Notice that columns are cleanly formatted with merchant, invoice number, and category.
   - Notice that multi-currency records are not lumped into misleading sums.
   - Any formulas or dangerous inputs are safely neutralized with single quotes (`'`) to protect spreadsheets.

---

## Step 5: Test Live Benchmark & Privacy Controls (30 seconds)

1. Navigate to the **Privacy & Status** tab.
2. Verify that **Ollama Runtime** and **AI Model (gemma2:2b)** show green connected status with the **100% On-Device** badge.
3. Click **"Run Live Benchmark"** to trigger live on-device evaluation across the synthetic test corpus and see real accuracy percentages.
4. Click **"Wipe All Records & Files"** to test the privacy deletion feature. The database and uploads directory will be wiped clean.
