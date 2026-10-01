"""
Generic scraper for static (server-rendered) bilingual pages.
Handles government/NGO press-release style sources where Chinese and
English text sit in separate selectors on the same page.
"""
from ..fetch import resilient_get
from ..extract import decode_content, extract_paragraphs
from ..storage import save_pair, log_failure


def run(source_config):
    """Entry point called by main.py for any source with type == 'static'."""
    name = source_config["name"]
    success, failed = 0, 0

    for url in source_config["urls"]:
        result = resilient_get(url)
        if not result.ok:
            log_failure(name, url, result.reason)
            failed += 1
            continue

        html = decode_content(result.content)
        zh_paragraphs = extract_paragraphs(html, source_config["zh_selector"])
        en_paragraphs = extract_paragraphs(html, source_config["en_selector"])

        if not zh_paragraphs or not en_paragraphs:
            log_failure(name, url, "no_paragraphs_found")
            failed += 1
            continue

        zh_text = "\n".join(zh_paragraphs)
        en_text = "\n".join(en_paragraphs)
        save_pair(name, url, zh_text, en_text)
        success += 1

    return {"source": name, "success": success, "failed": failed}
