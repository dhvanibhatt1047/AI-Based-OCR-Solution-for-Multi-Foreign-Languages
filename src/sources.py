"""
Source registry - the single place that defines WHAT to scrape and HOW.

Add a new source by adding an entry here; the scraper modules read from
this list. Never hardcode a URL inside scraper logic - it belongs here.

"type" tells main.py which scraper module handles this source:
    "api"        -> scrapers/wikipedia_scraper.py
    "static"     -> scrapers/static_scraper.py  (requests + BeautifulSoup)
    "playwright" -> scrapers/playwright_scraper.py  (JS-rendered pages)
"""

SOURCES = [
    {
        "name": "wikipedia",
        "type": "api",
        # Seed article titles to pull zh/en pairs for via the langlinks API.
        # Expand this list as far as you want - it's the easiest source to scale.
        "seed_titles": [
            "Artificial intelligence",
            "Climate change",
            "Great Wall of China",
            "World War II",
            "Machine learning",
            "Photosynthesis",
            "Solar System",
            "Ancient Egypt",
            "Renewable energy",
            "Human brain",
            "Internet",
            "World Health Organization",
            "United Nations",
            "Silk Road",
            "Beijing",
            "Shanghai",
            "Confucius",
            "Chinese New Year",
            "Traditional Chinese medicine",
            "Great Barrier Reef",
        ],
    },
    {
        "name": "example_gov_bilingual",
        "type": "static",
        # Fill these in with real bilingual government/NGO press-release URLs
        # AFTER you've done the source analysis (Step A1) on the real site -
        # the selectors below are placeholders until you inspect real HTML.
        "urls": [],
        "zh_selector": "div.content-zh",
        "en_selector": "div.content-en",
    },
    {
        "name": "example_js_rendered_site",
        "type": "playwright",
        "urls": [],
        "zh_selector": "div.zh-text",
        "en_selector": "div.en-text",
    },
]
