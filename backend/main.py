import json
import os
import shutil
import uuid
import re
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy import select, func, desc, asc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings, find_tesseract_binary
from backend.database import init_db, get_db, Expense
from backend.ocr import extract_document_text, get_ocr_engine_status
from backend.extractor import process_document_text
from backend.gemma_extractor import check_gemma_availability, extract_with_gemma
from backend.fallback_extractor import extract_with_fallback
from backend.validator import validate_and_normalize_record, reconcile_financial_amounts
from backend.schemas import (
    ExpenseResponse,
    ReviewUpdateRequest,
    SystemStatusResponse,
    DashboardSummaryResponse,
    ExtractedReceiptFields,
)
from backend.export import export_expenses_to_csv, export_summary_to_csv
from backend.demo_data import SYNTHETIC_RECEIPTS

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Privacy-first freelance expense assistant powered by local Gemma open-weight AI.",
    lifespan=lifespan,
)

# Restrict CORS to local development origins and Render deployment domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sanitize_filename(name: str) -> str:
    """Strip dangerous characters to prevent path traversal."""
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", Path(name).name)
    return cleaned or "receipt"

# -------------------------------------------------------------
# System Status & Health
# -------------------------------------------------------------
@app.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status():
    ocr_status = get_ocr_engine_status()
    gemma_ready, gemma_info = await check_gemma_availability()

    current_mode = "gemma2_local" if gemma_ready else "deterministic_fallback"

    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        ollama_connected=gemma_ready or ("Ollama is running" in str(gemma_info)),
        ollama_url=settings.OLLAMA_BASE_URL,
        gemma_model=settings.GEMMA_MODEL,
        gemma_available=gemma_ready,
        ocr_available=ocr_status["available"],
        ocr_engine=ocr_status["engine"],
        ocr_binary_path=ocr_status["binary_path"],
        database_connected=True,
        current_mode=current_mode,
    )

# -------------------------------------------------------------
# Document Upload & Processing
# -------------------------------------------------------------
@app.post("/api/documents/upload", response_model=List[ExpenseResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    created_expenses = []

    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Check content and size
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB"
            )

        # Save to disk safely
        safe_orig_name = sanitize_filename(file.filename or "receipt")
        unique_stored_name = f"{uuid.uuid4()}_{safe_orig_name}"
        saved_path = settings.UPLOAD_DIR / unique_stored_name
        saved_path.write_bytes(content)

        # Step 1: Text extraction (OCR or PDF)
        ocr_res = extract_document_text(saved_path, file.content_type or "")
        doc_text = ocr_res.get("text", "")
        ocr_warnings = ocr_res.get("warnings", [])

        # Step 2: Extraction (Gemma or Fallback) + Validation
        extraction_out = await process_document_text(doc_text)
        rec = extraction_out["record"]

        # Merge warnings
        combined_warnings = list(dict.fromkeys(ocr_warnings + rec["warnings"]))

        # Build database entity
        expense = Expense(
            id=str(uuid.uuid4()),
            source_filename=file.filename or safe_orig_name,
            stored_filename=unique_stored_name,
            mime_type=file.content_type or "application/octet-stream",
            file_size_bytes=len(content),
            merchant=rec["merchant"],
            document_type=rec["document_type"],
            invoice_number=rec["invoice_number"],
            transaction_date=rec["transaction_date"],
            raw_date=rec["raw_date"],
            currency=rec["currency"],
            subtotal=rec["subtotal"],
            tax=rec["tax"],
            discount=rec.get("discount", 0.0),
            additional_charges=rec.get("additional_charges", 0.0),
            total=rec["total"],
            category=rec["category"],
            payment_method=rec["payment_method"],
            description=rec["description"],
            status=rec["status"],
            reconciliation_status=rec["reconciliation_status"],
            reconciliation_delta=rec["reconciliation_delta"],
            extraction_mode=extraction_out["extraction_mode"],
            warnings=json.dumps(combined_warnings),
            raw_ocr_text=doc_text,
            raw_model_response=extraction_out["raw_model_response"],
            user_edits=json.dumps({}),
        )

        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        created_expenses.append(ExpenseResponse(**expense.to_dict()))

    return created_expenses

@app.post("/api/documents/upload-raw-text", response_model=ExpenseResponse)
async def upload_raw_text(
    title: str = Form("Pasted Receipt Text"),
    raw_text: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Directly process raw receipt or invoice text."""
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    unique_stored_name = f"{uuid.uuid4()}_pasted.txt"
    saved_path = settings.UPLOAD_DIR / unique_stored_name
    saved_path.write_text(raw_text, encoding="utf-8")

    extraction_out = await process_document_text(raw_text)
    rec = extraction_out["record"]

    expense = Expense(
        id=str(uuid.uuid4()),
        source_filename=f"{title}.txt",
        stored_filename=unique_stored_name,
        mime_type="text/plain",
        file_size_bytes=len(raw_text.encode("utf-8")),
        merchant=rec["merchant"],
        document_type=rec["document_type"],
        invoice_number=rec["invoice_number"],
        transaction_date=rec["transaction_date"],
        raw_date=rec["raw_date"],
        currency=rec["currency"],
        subtotal=rec["subtotal"],
        tax=rec["tax"],
        discount=rec.get("discount", 0.0),
        additional_charges=rec.get("additional_charges", 0.0),
        total=rec["total"],
        category=rec["category"],
        payment_method=rec["payment_method"],
        description=rec["description"],
        status=rec["status"],
        reconciliation_status=rec["reconciliation_status"],
        reconciliation_delta=rec["reconciliation_delta"],
        extraction_mode=extraction_out["extraction_mode"],
        warnings=json.dumps(rec["warnings"]),
        raw_ocr_text=raw_text,
        raw_model_response=extraction_out["raw_model_response"],
        user_edits=json.dumps({}),
    )

    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return ExpenseResponse(**expense.to_dict())

# -------------------------------------------------------------
# Document Ledger & Retrieval
# -------------------------------------------------------------
@app.get("/api/documents", response_model=List[ExpenseResponse])
async def list_expenses(
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    currency: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "transaction_date",
    order: str = "desc",
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense)

    if search:
        s_pat = f"%{search.strip()}%"
        query = query.where(
            (Expense.merchant.ilike(s_pat)) |
            (Expense.description.ilike(s_pat)) |
            (Expense.invoice_number.ilike(s_pat)) |
            (Expense.source_filename.ilike(s_pat))
        )

    if status and status != "all":
        query = query.where(Expense.status == status)

    if category and category != "all":
        query = query.where(Expense.category == category)

    if currency and currency != "all":
        query = query.where(Expense.currency == currency)

    if start_date:
        query = query.where(Expense.transaction_date >= start_date)

    if end_date:
        query = query.where(Expense.transaction_date <= end_date)

    # Sorting
    sort_column = Expense.transaction_date
    if sort_by == "total":
        sort_column = Expense.total
    elif sort_by == "merchant":
        sort_column = Expense.merchant
    elif sort_by == "created_at":
        sort_column = Expense.created_at

    if order.lower() == "asc":
        query = query.order_by(asc(sort_column).nulls_last())
    else:
        query = query.order_by(desc(sort_column).nulls_last())

    query = query.offset(offset).limit(limit)
    res = await db.execute(query)
    items = res.scalars().all()
    return [ExpenseResponse(**item.to_dict()) for item in items]

@app.get("/api/documents/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Expense).where(Expense.id == expense_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Expense not found.")
    return ExpenseResponse(**item.to_dict())

@app.get("/api/documents/{expense_id}/file")
async def get_document_file(expense_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Expense).where(Expense.id == expense_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Expense not found.")

    file_path = (settings.UPLOAD_DIR / item.stored_filename).resolve()
    # Path traversal defense: ensure resolved path is inside UPLOAD_DIR
    if not str(file_path).startswith(str(settings.UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File no longer exists on disk.")

    return FileResponse(
        path=str(file_path),
        filename=item.source_filename,
        media_type=item.mime_type
    )

# -------------------------------------------------------------
# Review, Edit & Confirm
# -------------------------------------------------------------
@app.put("/api/documents/{expense_id}/review", response_model=ExpenseResponse)
async def review_and_update_expense(
    expense_id: str,
    update: ReviewUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Expense).where(Expense.id == expense_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Expense not found.")

    # Record diff in user_edits audit log
    existing_edits = {}
    if item.user_edits:
        try:
            existing_edits = json.loads(item.user_edits)
        except Exception:
            existing_edits = {}

    changes = {}
    for field in [
        "merchant", "document_type", "invoice_number", "transaction_date",
        "currency", "subtotal", "tax", "discount", "additional_charges", "total", "category",
        "payment_method", "description"
    ]:
        new_val = getattr(update, field)
        if new_val is not None:
            old_val = getattr(item, field)
            if new_val != old_val:
                changes[field] = {"old": old_val, "new": new_val}
                setattr(item, field, new_val)

    if changes:
        existing_edits[datetime.now().isoformat()] = changes
        item.user_edits = json.dumps(existing_edits)

    # Re-run reconciliation on newly edited amounts
    rec_status, rec_delta, rec_warnings = reconcile_financial_amounts(
        item.subtotal, item.tax, item.total,
        discount=item.discount,
        additional_charges=item.additional_charges
    )
    item.reconciliation_status = rec_status
    item.reconciliation_delta = rec_delta

    # Parse and update warnings
    curr_warnings = []
    if item.warnings:
        try:
            curr_warnings = json.loads(item.warnings)
        except Exception:
            curr_warnings = []

    # Filter out old reconciliation mismatch warnings and add new ones
    curr_warnings = [w for w in curr_warnings if not w.startswith("Reconciliation")]
    curr_warnings.extend(rec_warnings)
    item.warnings = json.dumps(curr_warnings)

    item.status = update.status

    await db.commit()
    await db.refresh(item)
    return ExpenseResponse(**item.to_dict())

@app.delete("/api/documents/{expense_id}")
async def delete_expense(expense_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Expense).where(Expense.id == expense_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Expense not found.")

    # Remove file from disk
    file_path = settings.UPLOAD_DIR / item.stored_filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    await db.delete(item)
    await db.commit()
    return {"success": True, "message": f"Deleted expense {expense_id}."}

@app.post("/api/documents/{expense_id}/retry", response_model=ExpenseResponse)
async def retry_extraction(expense_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Expense).where(Expense.id == expense_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Expense not found.")

    if not item.raw_ocr_text:
        file_path = settings.UPLOAD_DIR / item.stored_filename
        ocr_res = extract_document_text(file_path, item.mime_type)
        item.raw_ocr_text = ocr_res.get("text", "")

    extraction_out = await process_document_text(item.raw_ocr_text)
    rec = extraction_out["record"]

    item.merchant = rec["merchant"]
    item.document_type = rec["document_type"]
    item.invoice_number = rec["invoice_number"]
    item.transaction_date = rec["transaction_date"]
    item.currency = rec["currency"]
    item.subtotal = rec["subtotal"]
    item.tax = rec["tax"]
    item.discount = rec.get("discount", 0.0)
    item.additional_charges = rec.get("additional_charges", 0.0)
    item.total = rec["total"]
    item.category = rec["category"]
    item.payment_method = rec["payment_method"]
    item.description = rec["description"]
    item.status = rec["status"]
    item.reconciliation_status = rec["reconciliation_status"]
    item.reconciliation_delta = rec["reconciliation_delta"]
    item.extraction_mode = extraction_out["extraction_mode"]
    item.raw_model_response = extraction_out["raw_model_response"]
    item.warnings = json.dumps(rec["warnings"])

    await db.commit()
    await db.refresh(item)
    return ExpenseResponse(**item.to_dict())

# -------------------------------------------------------------
# Dashboard Statistics
# -------------------------------------------------------------
@app.get("/api/dashboard", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    # Fetch all records
    res = await db.execute(select(Expense))
    items = res.scalars().all()

    receipts_count = len(items)
    awaiting_review_count = sum(1 for i in items if i.status == "awaiting_review")
    confirmed_count = sum(1 for i in items if i.status == "confirmed")
    rejected_count = sum(1 for i in items if i.status == "rejected")

    # Total expenses segregated by currency
    total_by_curr: Dict[str, float] = {}
    for i in items:
        if i.status == "confirmed" and i.total is not None:
            c = i.currency or "USD"
            total_by_curr[c] = round(total_by_curr.get(c, 0.0) + float(i.total), 2)

    # Category breakdown (for confirmed)
    cat_map: Dict[str, Dict[str, Any]] = {}
    for i in items:
        if i.status == "confirmed" and i.total is not None:
            cat = i.category or "Other"
            if cat not in cat_map:
                cat_map[cat] = {"category": cat, "count": 0, "amount": 0.0}
            cat_map[cat]["count"] += 1
            cat_map[cat]["amount"] = round(cat_map[cat]["amount"] + float(i.total), 2)

    cat_breakdown = sorted(cat_map.values(), key=lambda x: x["amount"], reverse=True)

    # Monthly trend
    month_map: Dict[str, Dict[str, Any]] = {}
    for i in items:
        if i.status == "confirmed" and i.total is not None:
            d = i.transaction_date or "Unknown"
            m = d[:7] if len(d) >= 7 and "-" in d else "Unknown"
            if m not in month_map:
                month_map[m] = {"month": m, "count": 0, "amount": 0.0}
            month_map[m]["count"] += 1
            month_map[m]["amount"] = round(month_map[m]["amount"] + float(i.total), 2)

    month_trend = sorted(month_map.values(), key=lambda x: x["month"])

    # Recent transactions
    recent_query = select(Expense).order_by(desc(Expense.created_at)).limit(5)
    recent_res = await db.execute(recent_query)
    recent_items = recent_res.scalars().all()

    return DashboardSummaryResponse(
        total_expenses_by_currency=total_by_curr,
        receipts_count=receipts_count,
        awaiting_review_count=awaiting_review_count,
        confirmed_count=confirmed_count,
        rejected_count=rejected_count,
        category_breakdown=cat_breakdown,
        monthly_trend=month_trend,
        recent_transactions=[ExpenseResponse(**i.to_dict()) for i in recent_items],
    )

# -------------------------------------------------------------
# Reports & CSV Export
# -------------------------------------------------------------
@app.get("/api/export/csv")
async def export_csv(
    status: Optional[str] = None,
    currency: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense)
    if status and status != "all":
        query = query.where(Expense.status == status)
    if currency and currency != "all":
        query = query.where(Expense.currency == currency)

    res = await db.execute(query.order_by(desc(Expense.transaction_date)))
    items = [i.to_dict() for i in res.scalars().all()]
    csv_data = export_expenses_to_csv(items)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pocketledger_expenses.csv"}
    )

@app.get("/api/export/summary-csv")
async def export_summary_csv(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Expense).where(Expense.status == "confirmed"))
    items = [i.to_dict() for i in res.scalars().all()]
    csv_data = export_summary_to_csv(items)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pocketledger_monthly_summary.csv"}
    )

# -------------------------------------------------------------
# Privacy: Complete Data Reset
# -------------------------------------------------------------
@app.post("/api/reset-data")
async def reset_all_data(db: AsyncSession = Depends(get_db)):
    """Wipes all expenses from database and removes all uploaded document files."""
    # Delete database rows
    await db.execute(delete(Expense))
    await db.commit()

    # Clear uploads folder
    removed_files = 0
    if settings.UPLOAD_DIR.exists():
        for f in settings.UPLOAD_DIR.iterdir():
            if f.is_file():
                try:
                    f.unlink()
                    removed_files += 1
                except Exception:
                    pass

    return {
        "success": True,
        "message": f"All records and {removed_files} uploaded files were permanently deleted."
    }

# -------------------------------------------------------------
# Synthetic Demo Seed Workspace
# -------------------------------------------------------------
@app.post("/api/demo/seed")
async def seed_demo_workspace(db: AsyncSession = Depends(get_db)):
    """Seed synthetic sample documents for testing without requiring user personal files."""
    created = []
    for item in SYNTHETIC_RECEIPTS:
        exp_id = str(uuid.uuid4())
        unique_name = f"demo_{uuid.uuid4()}_{item['source_filename']}"
        file_path = settings.UPLOAD_DIR / unique_name
        file_path.write_text(item["raw_ocr_text"], encoding="utf-8")

        # Run extraction
        extraction_out = await process_document_text(item["raw_ocr_text"])
        rec = extraction_out["record"]

        # If it was an intentional mismatch demo receipt, retain the mismatch status
        # Most demo receipts start as confirmed or awaiting_review
        status = "awaiting_review" if rec["reconciliation_status"] == "mismatch" or rec["total"] is None else "confirmed"

        expense = Expense(
            id=exp_id,
            source_filename=f"[Demo] {item['source_filename']}",
            stored_filename=unique_name,
            mime_type=item["mime_type"],
            file_size_bytes=len(item["raw_ocr_text"].encode("utf-8")),
            merchant=rec["merchant"] or item["expected"]["merchant"],
            document_type=rec["document_type"] or item["expected"]["document_type"],
            invoice_number=rec["invoice_number"] or item["expected"]["invoice_number"],
            transaction_date=rec["transaction_date"] or item["expected"]["transaction_date"],
            raw_date=rec["raw_date"],
            currency=rec["currency"] or item["expected"]["currency"],
            subtotal=rec["subtotal"] if rec["subtotal"] is not None else item["expected"]["subtotal"],
            tax=rec["tax"] if rec["tax"] is not None else item["expected"]["tax"],
            discount=rec.get("discount", 0.0),
            additional_charges=rec.get("additional_charges", 0.0),
            total=rec["total"] if rec["total"] is not None else item["expected"]["total"],
            category=rec["category"] or item["expected"]["category"],
            payment_method=rec["payment_method"] or item["expected"]["payment_method"],
            description=f"Synthetic demo receipt ({rec['category']})",
            status=status,
            reconciliation_status=rec["reconciliation_status"],
            reconciliation_delta=rec["reconciliation_delta"],
            extraction_mode=extraction_out["extraction_mode"],
            warnings=json.dumps(rec["warnings"]),
            raw_ocr_text=item["raw_ocr_text"],
            raw_model_response=extraction_out["raw_model_response"],
            user_edits=json.dumps({}),
        )
        db.add(expense)
        created.append(expense)

    await db.commit()
    return {"success": True, "count": len(created), "message": "Demo receipts successfully loaded."}

# -------------------------------------------------------------
# Live Model Benchmark Endpoint
# -------------------------------------------------------------
@app.get("/api/benchmark")
async def run_benchmark():
    """
    Evaluates both Gemma 2B and Deterministic Fallback on the synthetic test corpus.
    Measures field-level extraction accuracy, amount accuracy, and latency.
    """
    gemma_ready, gemma_info = await check_gemma_availability()

    results: Dict[str, Any] = {
        "model_name": settings.GEMMA_MODEL if gemma_ready else "Gemma Offline",
        "gemma_available": gemma_ready,
        "corpus_size": len(SYNTHETIC_RECEIPTS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gemma": {"total_time_ms": 0.0, "avg_time_ms": 0.0, "field_accuracy": {}, "cases": []},
        "fallback": {"total_time_ms": 0.0, "avg_time_ms": 0.0, "field_accuracy": {}, "cases": []},
    }

    fields_to_track = ["merchant", "total", "currency", "transaction_date", "document_type"]

    # 1. Fallback Benchmark
    fb_correct = {f: 0 for f in fields_to_track}
    start_fb_total = time.perf_counter()
    for item in SYNTHETIC_RECEIPTS:
        text = item["raw_ocr_text"]
        exp = item["expected"]

        t0 = time.perf_counter()
        fb_extracted = extract_with_fallback(text)
        fb_valid = validate_and_normalize_record(fb_extracted, raw_ocr_text=text)
        dt = (time.perf_counter() - t0) * 1000

        # Field matching
        case_scores = {}
        for f in fields_to_track:
            match = False
            if exp[f] is None and fb_valid[f] is None:
                match = True
            elif exp[f] is not None and fb_valid[f] is not None:
                if f == "total":
                    match = abs(float(exp[f]) - float(fb_valid[f])) <= 0.05
                elif f == "merchant":
                    match = (str(exp[f]).lower() in str(fb_valid[f]).lower()) or (str(fb_valid[f]).lower() in str(exp[f]).lower())
                else:
                    match = str(exp[f]).lower() == str(fb_valid[f]).lower()
            case_scores[f] = match
            if match:
                fb_correct[f] += 1

        results["fallback"]["cases"].append({
            "source": item["source_filename"],
            "duration_ms": round(dt, 2),
            "scores": case_scores,
            "extracted_total": fb_valid["total"],
            "expected_total": exp["total"],
        })

    fb_total_time = (time.perf_counter() - start_fb_total) * 1000
    results["fallback"]["total_time_ms"] = round(fb_total_time, 2)
    results["fallback"]["avg_time_ms"] = round(fb_total_time / len(SYNTHETIC_RECEIPTS), 2)
    results["fallback"]["field_accuracy"] = {
        f: round((count / len(SYNTHETIC_RECEIPTS)) * 100, 1) for f, count in fb_correct.items()
    }

    # 2. Gemma Benchmark (if available)
    if gemma_ready:
        gemma_correct = {f: 0 for f in fields_to_track}
        start_gemma_total = time.perf_counter()
        for item in SYNTHETIC_RECEIPTS:
            text = item["raw_ocr_text"]
            exp = item["expected"]

            t0 = time.perf_counter()
            try:
                gemma_extracted, raw_json, _ = await extract_with_gemma(text)
                gemma_valid = validate_and_normalize_record(gemma_extracted, raw_ocr_text=text)
                dt = (time.perf_counter() - t0) * 1000

                case_scores = {}
                for f in fields_to_track:
                    match = False
                    if exp[f] is None and gemma_valid[f] is None:
                        match = True
                    elif exp[f] is not None and gemma_valid[f] is not None:
                        if f == "total":
                            match = abs(float(exp[f]) - float(gemma_valid[f])) <= 0.05
                        elif f == "merchant":
                            match = (str(exp[f]).lower() in str(gemma_valid[f]).lower()) or (str(gemma_valid[f]).lower() in str(exp[f]).lower())
                        else:
                            match = str(exp[f]).lower() == str(gemma_valid[f]).lower()
                    case_scores[f] = match
                    if match:
                        gemma_correct[f] += 1

                results["gemma"]["cases"].append({
                    "source": item["source_filename"],
                    "duration_ms": round(dt, 2),
                    "scores": case_scores,
                    "extracted_total": gemma_valid["total"],
                    "expected_total": exp["total"],
                })
            except Exception as e:
                results["gemma"]["cases"].append({
                    "source": item["source_filename"],
                    "error": str(e),
                    "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
                    "scores": {f: False for f in fields_to_track},
                })

        gemma_total_time = (time.perf_counter() - start_gemma_total) * 1000
        results["gemma"]["total_time_ms"] = round(gemma_total_time, 2)
        results["gemma"]["avg_time_ms"] = round(gemma_total_time / len(SYNTHETIC_RECEIPTS), 2)
        results["gemma"]["field_accuracy"] = {
            f: round((count / len(SYNTHETIC_RECEIPTS)) * 100, 1) for f, count in gemma_correct.items()
        }
    else:
        results["gemma"]["status"] = "Not yet measured (Gemma offline)"

    return results

# Serve production frontend if built
dist_dir = settings.BASE_DIR / "frontend" / "dist"
if dist_dir.exists():
    from starlette.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
