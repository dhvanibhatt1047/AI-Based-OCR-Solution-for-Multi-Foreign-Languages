"""
Orchestrator - runs every configured source independently, so one bad
source category never stops the whole run (roadmap Step 7). Prints a
per-source success/fail summary at the end (roadmap Step 8).

Run this file with:  python -m src.main
(run from the project root, transfusion-scraper/)
"""
import logging
from .sources import SOURCES
from .scrapers import wikipedia_scraper, static_scraper, playwright_scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

RUNNERS = {
    "api": wikipedia_scraper.run,
    "static": static_scraper.run,
    "playwright": playwright_scraper.run,
}


def main():
    summary = []
    for source_config in SOURCES:
        runner = RUNNERS.get(source_config["type"])
        if not runner:
            print(f"Skipping unknown source type: {source_config['type']}")
            continue

        print(f"\n=== Running source: {source_config['name']} ===")
        try:
            result = runner(source_config)
            summary.append(result)
        except Exception as e:
            # A source category crashing entirely must not kill the others.
            print(f"Source {source_config['name']} crashed entirely: {e}")
            summary.append({"source": source_config["name"], "success": 0, "failed": "crashed"})

    print("\n=== Run summary ===")
    for row in summary:
        print(f"{row['source']:30s} success={row['success']:<5} failed={row['failed']}")


if __name__ == "__main__":
    main()
