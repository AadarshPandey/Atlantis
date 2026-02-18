# Stores your API keys and the GPS coordinates of the zones you monitor.

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── API Keys ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")

# ── Directory Paths ──────────────────────────────────────────────────────────
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ── Monitoring Zone (Caribbean Sea – matches sample imagery) ─────────────────
MONITORING_ZONE = {
    "name": "Caribbean Restricted Artisanal Zone",
    "center_lat": 13.5,
    "center_lon": -67.0,
    "bbox": {
        "min_lat": 10.0,
        "max_lat": 17.0,
        "min_lon": -70.0,
        "max_lon": -62.0,
    },
}

# ── Dummy Credentials (for demonstration only) ──────────────────────────────
SENTINEL_API_USER = "demo_user"
SENTINEL_API_PASS = "demo_password"
AIS_STREAM_TOKEN = "demo_ais_token_000"
