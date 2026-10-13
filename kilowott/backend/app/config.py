import os
from datetime import date


def _load_dotenv():
    """Tiny .env loader so the API key can stay out of source code."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(path):
        with open(path) as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crm.db")

# Optional free-tier API key. If not set, the app uses deterministic dummy drafts.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Free-tier model used by the OpenAI-compatible provider.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

REFERENCE_DATE = os.getenv("REFERENCE_DATE")  # YYYY-MM-DD


def reference_date():
    if REFERENCE_DATE:
        return date.fromisoformat(REFERENCE_DATE)
    return date.today()