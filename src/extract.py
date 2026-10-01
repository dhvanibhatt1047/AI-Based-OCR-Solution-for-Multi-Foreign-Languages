"""
Turns raw HTML bytes into clean paragraph-level text.
This is A4 from the roadmap: strip noise, pull real content only.
"""
import chardet
from bs4 import BeautifulSoup


def decode_content(raw_bytes, declared_encoding=None):
    """
    Decode raw response bytes to text safely.
    Chinese sites are inconsistent about encoding (UTF-8 vs GBK/GB2312).
    We trust chardet's detection of the actual bytes over whatever the
    server's HTTP header claims, because the header is sometimes wrong.
    """
    detected = chardet.detect(raw_bytes)["encoding"] or "utf-8"
    encoding = detected
    try:
        return raw_bytes.decode(encoding, errors="replace")
    except (LookupError, UnicodeDecodeError):
        return raw_bytes.decode("utf-8", errors="replace")


def extract_paragraphs(html, content_selector=None):
    """
    Extract clean paragraph text from HTML.

    content_selector: a CSS selector narrowing to the real content area,
        e.g. "div.content-zh". Find this by inspecting the page in your
        browser's DevTools before adding the source to sources.py.
        If None, falls back to searching the whole page for <p> tags.
    """
    soup = BeautifulSoup(html, "lxml")

    # Strip obvious non-content noise before extracting anything.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "ins"]):
        tag.decompose()
    for tag in soup.select(".ad, .advertisement, .nav, .navigation, .sidebar"):
        tag.decompose()

    scope = soup.select_one(content_selector) if content_selector else soup
    if scope is None:
        return []

    paragraphs = [p.get_text(strip=True) for p in scope.find_all("p")]
    # Drop fragments too short to be real sentences (nav labels, etc.)
    return [p for p in paragraphs if len(p) > 10]
