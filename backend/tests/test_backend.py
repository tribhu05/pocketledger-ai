import pytest
import pytest_asyncio
import json
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.database import init_db
from backend.validator import (
    reconcile_financial_amounts,
    parse_and_normalize_date,
    normalize_currency,
    normalize_category,
    validate_and_normalize_record,
)
from backend.schemas import ExtractedReceiptFields
from backend.export import sanitize_csv_cell, export_expenses_to_csv, export_summary_to_csv
from backend.fallback_extractor import extract_with_fallback

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_reconciliation_math():
    # 1. Matching amounts
    status, delta, warnings = reconcile_financial_amounts(10.00, 1.00, 11.00)
    assert status == "reconciled"
    assert delta == 0.0

    # 2. Tolerable rounding difference (within 0.05)
    status, delta, warnings = reconcile_financial_amounts(10.01, 1.01, 11.00)
    assert status == "reconciled"

    # 3. Mismatch
    status, delta, warnings = reconcile_financial_amounts(20.00, 2.00, 28.50)
    assert status == "mismatch"
    assert delta == 6.50
    assert any("differs from Total" in w for w in warnings)

    # 4. Missing total
    status, delta, warnings = reconcile_financial_amounts(15.00, 1.50, None)
    assert status == "mismatch"
    assert any("Total amount is missing" in w for w in warnings)

@pytest.mark.asyncio
async def test_date_normalization():
    # Valid date
    norm, raw, warnings = parse_and_normalize_date("2026-09-15")
    assert norm == "2026-09-15"

    # Common US format
    norm, raw, warnings = parse_and_normalize_date("09/15/2026")
    assert norm == "2026-09-15"

    # Written format
    norm, raw, warnings = parse_and_normalize_date("September 15, 2026")
    assert norm == "2026-09-15"

    # Missing date
    norm, raw, warnings = parse_and_normalize_date(None)
    assert norm is None
    assert len(warnings) > 0

@pytest.mark.asyncio
async def test_currency_normalization():
    assert normalize_currency("$") == "USD"
    assert normalize_currency("USD") == "USD"
    assert normalize_currency("€") == "EUR"
    assert normalize_currency("£") == "GBP"
    assert normalize_currency("₹") == "INR"
    assert normalize_currency(None, "Total: € 45.00") == "EUR"

@pytest.mark.asyncio
async def test_csv_injection_sanitization():
    # Dangerous formula prefixes
    assert sanitize_csv_cell("=CMD|' /C calc'!A0") == "'=CMD|' /C calc'!A0"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("-SOMEPAYLOAD") == "'-SOMEPAYLOAD"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("\tTabPrefix") == "'\tTabPrefix"
    
    # Safe text
    assert sanitize_csv_cell("Acme Corp") == "Acme Corp"
    assert sanitize_csv_cell(45.50) == "45.5"

@pytest.mark.asyncio
async def test_csv_export_multi_currency_segregation():
    records = [
        {
            "id": "1",
            "transaction_date": "2026-09-01",
            "merchant": "AWS",
            "document_type": "invoice",
            "invoice_number": "INV-1",
            "category": "Software & SaaS",
            "currency": "USD",
            "subtotal": 50.0,
            "tax": 0.0,
            "total": 50.0,
            "reconciliation_status": "reconciled",
            "status": "confirmed",
        },
        {
            "id": "2",
            "transaction_date": "2026-09-05",
            "merchant": "Hetzner",
            "document_type": "invoice",
            "invoice_number": "INV-2",
            "category": "Software & SaaS",
            "currency": "EUR",
            "subtotal": 40.0,
            "tax": 7.6,
            "total": 47.6,
            "reconciliation_status": "reconciled",
            "status": "confirmed",
        }
    ]
    csv_text = export_expenses_to_csv(records)
    assert "AWS" in csv_text
    assert "Hetzner" in csv_text
    assert "USD" in csv_text
    assert "EUR" in csv_text

    # Summary segregation
    summary_csv = export_summary_to_csv(records)
    # Check that USD and EUR are distinct rows, not mixed
    assert "USD" in summary_csv
    assert "EUR" in summary_csv
    assert "50.00" in summary_csv
    assert "47.60" in summary_csv

@pytest.mark.asyncio
async def test_deterministic_fallback():
    sample_text = """Acme Cloud Services
Invoice #AC-1002
Date: 2026-09-20
Subtotal: $40.00
Tax: $4.00
Total Due: $44.00"""

    extracted = extract_with_fallback(sample_text)
    assert extracted.total == 44.00
    assert extracted.subtotal == 40.00
    assert extracted.tax == 4.00
    assert extracted.merchant == "Acme Cloud Services"
    assert any("fallback active" in w.lower() for w in extracted.warnings)

@pytest.mark.asyncio
async def test_api_status_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "app_name" in data
        assert "ollama_connected" in data
        assert "database_connected" in data
        assert data["database_connected"] is True

@pytest.mark.asyncio
async def test_raw_text_upload_and_review_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Process receipt text
        payload = {
            "title": "Test Starbucks Receipt",
            "raw_text": "STARBUCKS #102\nDate: 2026-10-01\nCoffee $4.00\nTax $0.40\nTotal $4.40"
        }
        resp = await client.post("/api/documents/upload-raw-text", data=payload)
        assert resp.status_code == 200
        created = resp.json()
        assert created["id"] is not None
        assert created["status"] == "awaiting_review"
        assert created["total"] == 4.40

        expense_id = created["id"]

        # 2. Review and confirm
        review_update = {
            "merchant": "Starbucks Coffee",
            "total": 4.40,
            "status": "confirmed",
            "category": "Meals & Entertainment",
            "description": "Morning coffee before client call"
        }
        review_resp = await client.put(f"/api/documents/{expense_id}/review", json=review_update)
        assert review_resp.status_code == 200
        updated = review_resp.json()
        assert updated["status"] == "confirmed"
        assert updated["merchant"] == "Starbucks Coffee"
        assert len(updated["user_edits"]) > 0  # audit trail recorded!

        # 3. Check dashboard reflects confirmed spend
        dash_resp = await client.get("/api/dashboard")
        assert dash_resp.status_code == 200
        dash = dash_resp.json()
        assert dash["confirmed_count"] >= 1
        assert "USD" in dash["total_expenses_by_currency"]

        # 4. Delete record
        del_resp = await client.delete(f"/api/documents/{expense_id}")
        assert del_resp.status_code == 200
