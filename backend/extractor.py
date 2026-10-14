import json
import logging
import time
from typing import Dict, Any, Tuple

from backend.config import settings
from backend.gemma_extractor import check_gemma_availability, extract_with_gemma
from backend.fallback_extractor import extract_with_fallback
from backend.validator import validate_and_normalize_record
from backend.schemas import ExtractedReceiptFields

logger = logging.getLogger(__name__)

async def process_document_text(document_text: str) -> Dict[str, Any]:
    """
    Main extraction pipeline:
    1. Try Gemma 2B local inference via Ollama.
    2. Fall back to deterministic heuristic parsing if Gemma is unavailable.
    3. Run deterministic validation, date normalization, and financial reconciliation.
    4. Return verified structured record.
    """
    gemma_ready, gemma_info = await check_gemma_availability()
    mode = "deterministic_fallback"
    raw_response = "{}"
    start_time = time.perf_counter()
    duration_ms = 0.0

    raw_fields: ExtractedReceiptFields

    if gemma_ready:
        try:
            raw_fields, raw_response, duration_ms = await extract_with_gemma(document_text)
            mode = settings.GEMMA_MODEL
        except Exception as e:
            logger.warning(f"Gemma extraction failed, activating fallback: {e}")
            raw_fields = extract_with_fallback(document_text)
            raw_fields.warnings.append(f"Gemma error: {str(e)[:100]}. Switched to deterministic fallback.")
            raw_response = json.dumps(raw_fields.model_dump(), default=str)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            mode = "deterministic_fallback"
    else:
        logger.info(f"Ollama/Gemma offline ({gemma_info}). Using deterministic fallback.")
        raw_fields = extract_with_fallback(document_text)
        raw_response = json.dumps(raw_fields.model_dump(), default=str)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        mode = "deterministic_fallback"

    # Deterministic validation and reconciliation pass
    validated_record = validate_and_normalize_record(raw_fields, raw_ocr_text=document_text)

    return {
        "record": validated_record,
        "extraction_mode": mode,
        "raw_model_response": raw_response,
        "duration_ms": duration_ms,
        "gemma_used": (mode == settings.GEMMA_MODEL),
    }
