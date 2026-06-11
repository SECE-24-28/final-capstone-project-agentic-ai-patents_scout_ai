import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

# App Configurations
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
PATENTSVIEW_API_KEY = os.getenv("PATENTSVIEW_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://patentscout:patentscout_pass@localhost:5432/patentscout_db")
OPENALEX_API_EMAIL = os.getenv("OPENALEX_API_EMAIL")

# Vector Database Configurations
CHROMA_DB_DIR = str(BASE_DIR / "backend" / "chroma_db")
