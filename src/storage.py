"""
Everything that writes to disk lives here. Scrapers call save_pair() and
log_failure() - they never open files themselves. Keeps storage format
changes (e.g. switching to Postgres later) to one file.
"""
import json
from datetime import datetime, timezone
from . import config


def save_pair(source_name, url, zh_text, en_text, meta=None):
    """Append one scraped zh/en pair to that source's JSONL file."""
    path = config.RAW_DIR / f"{source_name}.jsonl"
    record = {
        "source": source_name,
        "url": url,
        "zh_text": zh_text,
        "en_text": en_text,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "meta": meta or {},
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_failure(source_name, url, reason):
    """Append a failed URL to the shared failure log (roadmap Step 8)."""
    path = config.LOG_DIR / "failures.log"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{source_name}\t{url}\t{reason}\n")
