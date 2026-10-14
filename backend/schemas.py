from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

FREELANCE_CATEGORIES = [
    "Software & SaaS",
    "Office Supplies",
    "Hardware & Equipment",
    "Travel & Lodging",
    "Meals & Entertainment",
    "Professional Services",
    "Utilities",
    "Other",
]

class ExtractedReceiptFields(BaseModel):
    """Raw structured fields extracted from Gemma or Fallback."""
    merchant: Optional[str] = Field(None, description="Name of the business/merchant/vendor. Never invent names.")
    document_type: str = Field("receipt", description="Either 'receipt', 'invoice', or 'other'.")
    invoice_number: Optional[str] = Field(None, description="Invoice, order, or receipt reference ID if present.")
    transaction_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format if identifiable.")
    raw_date: Optional[str] = Field(None, description="Exact date text as seen in document.")
    currency: str = Field("USD", description="3-letter currency code (e.g. USD, EUR, GBP, CAD, INR).")
    subtotal: Optional[float] = Field(None, description="Monetary subtotal before tax.")
    tax: Optional[float] = Field(None, description="Monetary tax/VAT/GST amount.")
    total: Optional[float] = Field(None, description="Monetary grand total.")
    category: str = Field("Other", description="Expense category from standard taxonomy.")
    payment_method: Optional[str] = Field(None, description="Payment method or card hint if present.")
    description: Optional[str] = Field(None, description="Brief 1-line description of goods/services purchased.")
    warnings: List[str] = Field(default_factory=list, description="Specific warnings about illegible or missing fields.")

class ReviewUpdateRequest(BaseModel):
    """Payload sent by human reviewer to update/confirm an expense."""
    merchant: Optional[str] = None
    document_type: Optional[str] = None
    invoice_number: Optional[str] = None
    transaction_date: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None
    status: Literal["awaiting_review", "confirmed", "rejected"] = "confirmed"

class ExpenseResponse(BaseModel):
    id: str
    source_filename: str
    stored_filename: str
    mime_type: str
    file_size_bytes: int
    merchant: Optional[str]
    document_type: str
    invoice_number: Optional[str]
    transaction_date: Optional[str]
    raw_date: Optional[str]
    currency: str
    subtotal: Optional[float]
    tax: Optional[float]
    total: Optional[float]
    category: str
    payment_method: Optional[str]
    description: Optional[str]
    status: str
    reconciliation_status: str
    reconciliation_delta: Optional[float]
    extraction_mode: str
    warnings: List[str]
    raw_ocr_text: Optional[str]
    raw_model_response: Optional[str]
    user_edits: Dict[str, Any]
    created_at: Optional[str]
    updated_at: Optional[str]

class SystemStatusResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    ollama_connected: bool
    ollama_url: str
    gemma_model: str
    gemma_available: bool
    ocr_available: bool
    ocr_engine: str
    ocr_binary_path: Optional[str]
    database_connected: bool
    current_mode: str  # "gemma2_local", "deterministic_fallback"

class DashboardSummaryResponse(BaseModel):
    total_expenses_by_currency: Dict[str, float]
    receipts_count: int
    awaiting_review_count: int
    confirmed_count: int
    rejected_count: int
    category_breakdown: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]
    recent_transactions: List[ExpenseResponse]
