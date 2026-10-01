"""
For JS-rendered (SPA) pages that requests + BeautifulSoup can't see, because
the real content only appears after client-side JavaScript runs.
Same politeness and resilience principles, adapted to a browser context.
"""
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from ..extract import extract_paragraphs
from ..storage import save_pair, log_failure
from .. import config


def run(source_config):
    """Entry point called by main.py for any source with type == 'playwright'."""
    name = source_config["name"]
    success, failed = 0, 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=config.USER_AGENT)
        page = context.new_page()

        for url in source_config["urls"]:
            time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))
            try:
                page.goto(url, timeout=config.REQUEST_TIMEOUT * 1000)
                html = page.content()
            except PWTimeout:
                log_failure(name, url, "timeout")
                failed += 1
                continue
            except Exception as e:
                log_failure(name, url, str(e))
                failed += 1
                continue

            zh_paragraphs = extract_paragraphs(html, source_config["zh_selector"])
            en_paragraphs = extract_paragraphs(html, source_config["en_selector"])

            if not zh_paragraphs or not en_paragraphs:
                log_failure(name, url, "no_paragraphs_found")
                failed += 1
                continue

            save_pair(name, url, "\n".join(zh_paragraphs), "\n".join(en_paragraphs))
            success += 1

        browser.close()

    return {"source": name, "success": success, "failed": failed}
