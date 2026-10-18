import json
import re
import time
from typing import Dict, Any, Tuple, Optional
import httpx
from pydantic import ValidationError

from backend.config import settings
from backend.schemas import ExtractedReceiptFields, FREELANCE_CATEGORIES

GEMMA_SYSTEM_PROMPT = f"""You are PocketLedger AI, a precise financial document extraction engine for freelancers.
Extract key expense fields from the provided receipt or invoice text.
Output MUST be a valid JSON object matching this exact schema:

{{
  "merchant": "string or null - Name of business/vendor. NEVER guess or invent.",
  "document_type": "receipt | invoice | other",
  "invoice_number": "string or null - Invoice/receipt reference number if present",
  "transaction_date": "string or null - Date formatted as YYYY-MM-DD",
  "raw_date": "string or null - Exact date text from document",
  "currency": "string - 3-letter currency code (USD, EUR, GBP, CAD, INR, etc.)",
  "subtotal": "number or null - Pre-tax amount",
  "tax": "number or null - Tax/VAT/GST amount",
  "discount": "number or null - Discount, coupon, or promotional reduction if explicitly present on document (positive number)",
  "additional_charges": "number or null - Tips, service fees, or delivery surcharge if explicitly present on document",
  "total": "number or null - Grand total amount",
  "category": "one of: {', '.join(FREELANCE_CATEGORIES)}",
  "payment_method": "string or null - e.g. Visa 1234, Cash, Bank Transfer",
  "description": "string or null - 1-line summary of goods/services",
  "warnings": ["array of specific warning strings if any value was missing or illegible"]
}}

CRITICAL RULES:
1. NEVER invent, hallucinate, or assume missing values. If not visible in text, use null.
2. The subtotal, tax, discount, additional_charges, and total fields MUST be numeric (or null), never strings.
3. If total amount is ambiguous, report null and add a note in warnings.
4. Output ONLY valid JSON. Do not wrap in markdown or commentary."""

def parse_json_from_response(raw_text: str) -> Dict[str, Any]:
    """Parse JSON payload from model response, handling markdown blocks or conversational preamble."""
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty model response")

    # 1. Try direct parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # 2. Extract ```json ... ``` code blocks
    code_block_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw_text)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Extract outermost balanced braces { ... }
    first_brace = raw_text.find("{")
    last_brace = raw_text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = raw_text[first_brace : last_brace + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 4. Clean backticks and try again
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

async def check_gemma_availability() -> Tuple[bool, Optional[str]]:
    """Check if Ollama server is running and the Gemma model is available."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Match gemma2:2b or configured model
                target = settings.GEMMA_MODEL.lower()
                for m in models:
                    if target in m.lower():
                        return True, m
                # If specific model tag not exact, check if any gemma is loaded
                for m in models:
                    if "gemma" in m.lower():
                        return True, m
                return False, f"Ollama is running, but Gemma model '{settings.GEMMA_MODEL}' not found. Available: {models}"
            return False, f"Ollama returned HTTP status {resp.status_code}"
    except httpx.ConnectError:
        return False, f"Ollama connection refused at {settings.OLLAMA_BASE_URL}. Ensure Ollama daemon is active."
    except httpx.TimeoutException:
        return False, f"Ollama health check timed out at {settings.OLLAMA_BASE_URL}."
    except Exception as e:
        return False, f"Could not connect to Ollama at {settings.OLLAMA_BASE_URL}: {str(e)}"

async def extract_with_gemma(document_text: str) -> Tuple[ExtractedReceiptFields, str, float]:
    """
    Extract structured fields using Gemma running on local Ollama instance.
    Returns (ExtractedReceiptFields, raw_json_response, duration_ms).
    """
    if not document_text or not document_text.strip():
        empty_res = ExtractedReceiptFields(
            merchant=None,
            total=None,
            warnings=["No document text provided for extraction."]
        )
        return empty_res, "{}", 0.0

    prompt = f"{GEMMA_SYSTEM_PROMPT}\n\nDocument Text:\n\"\"\"\n{document_text}\n\"\"\""

    payload = {
        "model": settings.GEMMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,  # Low temperature for strict structured extraction
            "num_predict": 768,
        }
    }

    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if response.status_code != 200:
                raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")

            res_json = response.json()
            raw_text = res_json.get("response", "").strip()
    except httpx.ConnectError as ce:
        raise RuntimeError(f"Connection refused to Ollama at {settings.OLLAMA_BASE_URL}. Run 'ollama serve'.") from ce
    except httpx.TimeoutException as te:
        raise RuntimeError(f"Ollama inference timed out after {settings.OLLAMA_TIMEOUT_SECONDS}s.") from te

    # Parse and validate JSON against Pydantic schema
    try:
        parsed_dict = parse_json_from_response(raw_text)
        validated = ExtractedReceiptFields(**parsed_dict)
        return validated, raw_text, duration_ms
    except (json.JSONDecodeError, ValueError) as jde:
        raise ValueError(f"Gemma produced non-parseable JSON: {raw_text[:200]}") from jde
    except ValidationError as ve:
        raise ValueError(f"Gemma JSON failed schema validation: {ve.errors()}") from ve
