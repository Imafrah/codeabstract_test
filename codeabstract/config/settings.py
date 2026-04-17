"""Application settings."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mappings.db"
KEY_PATH = DATA_DIR / "fernet.key"

DATA_DIR.mkdir(parents=True, exist_ok=True)

