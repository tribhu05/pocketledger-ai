import io
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageFilter
import pypdf
import pytesseract

from backend.config import settings, find_tesseract_binary

def get_ocr_engine_status() -> Dict[str, Any]:
    binary = find_tesseract_binary()
    available = binary is not None
    version = None
    if available:
        try:
            pytesseract.pytesseract.tesseract_cmd = binary
            version = str(pytesseract.get_tesseract_version())
        except Exception as e:
            available = False
            version = None

    return {
        "engine": "tesseract",
        "available": available,
        "binary_path": binary,
        "version": version,
        "pdf_engine_available": True,  # pypdf is installed
    }

def clean_extracted_text(text: str) -> str:
    """Normalize extracted text whitespace while preserving line structure."""
    if not text:
        return ""
    # Strip null characters and carriage returns
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading and trailing whitespace on lines
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()

def extract_text_from_pdf(file_path: Path) -> Dict[str, Any]:
    """Extract digital text from PDF using pypdf."""
    try:
        reader = pypdf.PdfReader(str(file_path))
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(page_text)
        
        full_text = clean_extracted_text("\n\n--- Page Break ---\n\n".join(extracted_pages))
        if full_text:
            return {
                "text": full_text,
                "method": "pdf_digital_extract",
                "success": True,
                "warnings": [],
            }
        else:
            return {
                "text": "",
                "method": "pdf_digital_extract",
                "success": False,
                "warnings": ["PDF contained no extractable digital text (scanned document)."],
            }
    except Exception as e:
        return {
            "text": "",
            "method": "pdf_digital_extract",
            "success": False,
            "warnings": [f"PDF parsing error: {str(e)}"],
        }

def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR character recognition."""
    # Convert to grayscale
    gray = image.convert("L")
    # Resize up if very small
    w, h = gray.size
    if w < 1000 or h < 1000:
        scale = max(1000 / w, 1000 / h)
        gray = gray.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.8)
    return enhanced

def extract_text_from_image(file_path: Path) -> Dict[str, Any]:
    """Extract text from image using local Tesseract OCR."""
    binary = find_tesseract_binary()
    if not binary:
        return {
            "text": "",
            "method": "tesseract_unavailable",
            "success": False,
            "warnings": [
                "Tesseract OCR executable was not found on this system. "
                "For PDF documents, native digital text extraction works automatically. "
                "To OCR camera receipt images, install Tesseract (see Settings > Troubleshooting)."
            ],
        }

    try:
        pytesseract.pytesseract.tesseract_cmd = binary
        with Image.open(file_path) as img:
            processed_img = preprocess_image_for_ocr(img)
            # PSM 6: Assume a single uniform block of text or PSM 4: Assume a single column of text of variable sizes
            config = "--psm 6"
            raw_text = pytesseract.image_to_string(processed_img, config=config)
            
            cleaned = clean_extracted_text(raw_text)
            if not cleaned:
                # Retry with default PSM
                raw_text = pytesseract.image_to_string(processed_img)
                cleaned = clean_extracted_text(raw_text)

            return {
                "text": cleaned,
                "method": "tesseract_ocr",
                "success": bool(cleaned),
                "warnings": [] if cleaned else ["OCR completed but no characters were detected."],
            }
    except Exception as e:
        return {
            "text": "",
            "method": "tesseract_ocr_error",
            "success": False,
            "warnings": [f"OCR execution failed: {str(e)}"],
        }

def extract_document_text(file_path: Path, mime_type: str) -> Dict[str, Any]:
    """Unified entrypoint for document text extraction."""
    if not file_path.exists():
        return {
            "text": "",
            "method": "file_not_found",
            "success": False,
            "warnings": ["Source file not found."],
        }

    ext = file_path.suffix.lower()
    if ext == ".pdf" or mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif ext in {".png", ".jpg", ".jpeg", ".webp"}:
        return extract_text_from_image(file_path)
    else:
        return {
            "text": "",
            "method": "unsupported_format",
            "success": False,
            "warnings": [f"Unsupported file format: {ext}"],
        }
