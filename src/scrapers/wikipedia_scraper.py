"""
Wikipedia is best handled through its official API, not raw HTML scraping -
it's faster, gives clean structured data, and is exactly what the site
wants automated tools to use instead of hitting rendered pages.
"""
import requests
from ..fetch import polite_delay
from ..storage import save_pair, log_failure

API_URL = "https://{lang}.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "TransFusionAI-Scraper/1.0 (Student project; contact: shivanimunjani2007@gmail.com)"}


def get_extract(title, lang):
    """Fetch the plain-text extract of one article in one language."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json",
    }
    resp = requests.get(API_URL.format(lang=lang), params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("extract", "")


def get_langlink_title(title, target_lang="zh"):
    """Find the Chinese-Wikipedia title that corresponds to an English title."""
    params = {
        "action": "query",
        "prop": "langlinks",
        "titles": title,
        "lllang": target_lang,
        "format": "json",
    }
    resp = requests.get(API_URL.format(lang="en"), params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    langlinks = page.get("langlinks", [])
    return langlinks[0]["*"] if langlinks else None


def run(source_config):
    """Entry point called by main.py for any source with type == 'api'."""
    name = source_config["name"]
    success, failed = 0, 0

    for en_title in source_config["seed_titles"]:
        polite_delay()
        zh_title = get_langlink_title(en_title)
        if not zh_title:
            log_failure(name, en_title, "no_zh_langlink")
            failed += 1
            continue

        try:
            en_text = get_extract(en_title, "en")
            zh_text = get_extract(zh_title, "zh")
            if en_text and zh_text:
                save_pair(name, f"en:{en_title}|zh:{zh_title}", zh_text, en_text)
                success += 1
            else:
                log_failure(name, en_title, "empty_extract")
                failed += 1
        except requests.RequestException as e:
            log_failure(name, en_title, str(e))
            failed += 1

    return {"source": name, "success": success, "failed": failed}
