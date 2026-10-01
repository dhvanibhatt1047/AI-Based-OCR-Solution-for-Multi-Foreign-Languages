"""
Central configuration for the scraper.
Change values here to tune politeness, retries, and paths.
Nothing else in the project should hardcode these numbers.
"""
from pathlib import Path

# --- Identify honestly (Step 6 of the resilience deep dive) ---
# Real projects put a real contact so a site owner can reach you instead of
# just blocking your IP blind. Replace the email before running for real.
USER_AGENT = "TransFusionAI-Scraper/1.0 (Student project; contact: shivanimunjani2007@gmail.com)"

# --- Politeness: delay range between every single request ---
MIN_DELAY = 1.5   # seconds
MAX_DELAY = 3.0   # seconds

# --- Resilience: retry behavior for transient failures only ---
MAX_RETRIES = 2          # bounded retries for 429 / timeout
REQUEST_TIMEOUT = 10      # seconds before a request counts as "timed out"
RETRY_BACKOFF_BASE = 2    # exponential backoff: 2s, 4s, ...

# --- Paths: everything writes under data/, nothing scattered elsewhere ---
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
LOG_DIR = BASE_DIR / "data" / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
