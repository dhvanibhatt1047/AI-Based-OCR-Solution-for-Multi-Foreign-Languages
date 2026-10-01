# TransFusion AI — bilingual scraper

## Setup (run once)

```bash
cd transfusion-scraper
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium     # downloads the browser binary Playwright drives
```

## Configure

1. Open `src/config.py` and put a real contact email in `USER_AGENT`.
2. Open `src/sources.py` and fill in real URLs + CSS selectors for the
   `static` and `playwright` sources, after inspecting the real site's HTML
   in your browser's DevTools (see the source-analysis checklist).

## Run

```bash
python -m src.main
```

Run from the project root (the folder containing `src/`), not from inside
`src/` itself — the relative imports (`from . import config`) require it.

## Output

- `data/raw/<source_name>.jsonl` — one JSON object per line: zh_text,
  en_text, url, source, timestamp.
- `data/logs/failures.log` — every skipped URL with its failure reason,
  tab-separated: source, url, reason.

## Project layout

```
transfusion-scraper/
├── requirements.txt
├── README.md
├── data/
│   ├── raw/            # scraped output, one .jsonl per source
│   └── logs/           # failures.log
└── src/
    ├── config.py        # all tunable settings: delays, retries, paths
    ├── fetch.py          # resilient_get() - the A3 request wrapper
    ├── extract.py         # HTML -> clean paragraph text
    ├── sources.py          # registry: what to scrape and how
    ├── storage.py           # all disk writes go through here
    ├── main.py               # orchestrator, run this
    └── scrapers/
        ├── wikipedia_scraper.py    # Wikipedia API (type: "api")
        ├── static_scraper.py       # requests+BS4 (type: "static")
        └── playwright_scraper.py   # JS-rendered (type: "playwright")
```
