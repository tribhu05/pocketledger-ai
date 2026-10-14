import os
import shutil
from pathlib import Path
from typing import Optional, Set
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PocketLedger AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "local"
    DEBUG: bool = False

    # Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DATABASE_PATH: Path = BASE_DIR / "pocketledger.db"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}"

    # File limits & security
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}

    # Ollama / Gemma AI Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    GEMMA_MODEL: str = os.getenv("GEMMA_MODEL", "gemma2:2b")
    OLLAMA_TIMEOUT_SECONDS: float = 60.0

    # OCR Configuration
    TESSERACT_CMD: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def find_tesseract_binary() -> Optional[str]:
    """Auto-detect Tesseract executable across standard paths."""
    if settings.TESSERACT_CMD and os.path.exists(settings.TESSERACT_CMD):
        return settings.TESSERACT_CMD
    
    # Check PATH
    which_tess = shutil.which("tesseract")
    if which_tess:
        return which_tess

    # Standard Windows paths
    win_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for p in win_paths:
        if os.path.exists(p):
            return p

    # Standard Linux / macOS paths
    nix_paths = ["/usr/bin/tesseract", "/usr/local/bin/tesseract", "/opt/homebrew/bin/tesseract"]
    for p in nix_paths:
        if os.path.exists(p):
            return p

    return None
