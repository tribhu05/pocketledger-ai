import json
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, List, Optional
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, select, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from backend.config import settings

Base = declarative_base()

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False, default=0)

    # Core Financial Fields
    merchant = Column(String(255), nullable=True)
    document_type = Column(String(50), nullable=False, default="receipt")
    invoice_number = Column(String(100), nullable=True)
    transaction_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    raw_date = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=False, default="USD")
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    category = Column(String(100), nullable=False, default="Other")
    payment_method = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)

    # Workflow & Review State
    status = Column(String(50), nullable=False, default="awaiting_review")  # awaiting_review, confirmed, rejected
    reconciliation_status = Column(String(50), nullable=False, default="unverified")  # reconciled, mismatch, unverified
    reconciliation_delta = Column(Float, nullable=True)
    extraction_mode = Column(String(50), nullable=False, default="gemma2:2b")  # gemma2:2b, deterministic_fallback, manual
    
    # Audit Trail & Lineage
    warnings = Column(Text, nullable=False, default="[]")  # JSON list
    raw_ocr_text = Column(Text, nullable=True)
    raw_model_response = Column(Text, nullable=True)
    user_edits = Column(Text, nullable=False, default="{}")  # JSON dict

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        parsed_warnings = []
        if self.warnings:
            try:
                parsed_warnings = json.loads(self.warnings)
            except Exception:
                parsed_warnings = [self.warnings]

        parsed_user_edits = {}
        if self.user_edits:
            try:
                parsed_user_edits = json.loads(self.user_edits)
            except Exception:
                parsed_user_edits = {}

        return {
            "id": self.id,
            "source_filename": self.source_filename,
            "stored_filename": self.stored_filename,
            "mime_type": self.mime_type,
            "file_size_bytes": self.file_size_bytes,
            "merchant": self.merchant,
            "document_type": self.document_type,
            "invoice_number": self.invoice_number,
            "transaction_date": self.transaction_date,
            "raw_date": self.raw_date,
            "currency": self.currency,
            "subtotal": self.subtotal,
            "tax": self.tax,
            "total": self.total,
            "category": self.category,
            "payment_method": self.payment_method,
            "description": self.description,
            "status": self.status,
            "reconciliation_status": self.reconciliation_status,
            "reconciliation_delta": self.reconciliation_delta,
            "extraction_mode": self.extraction_mode,
            "warnings": parsed_warnings,
            "raw_ocr_text": self.raw_ocr_text,
            "raw_model_response": self.raw_model_response,
            "user_edits": parsed_user_edits,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
