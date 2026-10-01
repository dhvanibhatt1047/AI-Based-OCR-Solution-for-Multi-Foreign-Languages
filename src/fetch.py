"""
The resilient request wrapper - this is the code that implements A3 from the
roadmap: classify failures, retry transient ones a bounded number of times,
skip permanent ones, and never let one bad URL stop the run.

Every network call in this project should go through resilient_get().
Never call requests.get() directly anywhere else in the codebase.
"""
import time
import random
import logging
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

from . import config

logger = logging.getLogger("fetch")


class FetchResult:
    """
    Wraps the outcome of a fetch attempt so calling code never has to guess
    what happened - it just checks .ok and reads .reason if it failed.
    """
    def __init__(self, ok, url, status_code=None, content=None, reason=None):
        self.ok = ok
        self.url = url
        self.status_code = status_code
        self.content = content
        # reason is one of: "blocked_or_missing", "unexpected_status",
        # "connection_error", "retries_exhausted", or an exception message
        self.reason = reason


def polite_delay():
    """Randomized pause before every request so traffic doesn't look scripted."""
    time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))


def resilient_get(url, session=None):
    """
    Fetch a URL with classification, bounded retries, and graceful skipping.
    This function NEVER raises - it always returns a FetchResult, whether
    the request succeeded or failed, so the caller's loop never crashes.
    """
    session = session or requests.Session()
    headers = {"User-Agent": config.USER_AGENT}

    attempt = 0
    while attempt <= config.MAX_RETRIES:
        try:
            polite_delay()
            resp = session.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)

            # --- Step 3: classify the response, don't just catch blindly ---
            if resp.status_code == 200:
                return FetchResult(ok=True, url=url, status_code=200, content=resp.content)

            if resp.status_code in (403, 404):
                # Permanent failure - skip immediately, never retry, never
                # attempt to work around it. This is the access-control line.
                logger.warning("[SKIP] %s -> %s", url, resp.status_code)
                return FetchResult(ok=False, url=url, status_code=resp.status_code,
                                    reason="blocked_or_missing")

            if resp.status_code == 429:
                # Transient - worth a bounded retry with backoff.
                attempt += 1
                wait = config.RETRY_BACKOFF_BASE ** attempt
                logger.info("[RATE-LIMITED] %s -> retrying in %ss (%s/%s)",
                            url, wait, attempt, config.MAX_RETRIES)
                time.sleep(wait)
                continue

            logger.warning("[SKIP] %s -> unexpected status %s", url, resp.status_code)
            return FetchResult(ok=False, url=url, status_code=resp.status_code,
                                reason="unexpected_status")

        except Timeout:
            attempt += 1
            wait = config.RETRY_BACKOFF_BASE ** attempt
            logger.info("[TIMEOUT] %s -> retrying in %ss (%s/%s)",
                        url, wait, attempt, config.MAX_RETRIES)
            time.sleep(wait)
            continue

        except ConnectionError:
            # Total connection failure - skip immediately, no retry.
            logger.warning("[SKIP] %s -> connection error", url)
            return FetchResult(ok=False, url=url, reason="connection_error")

        except RequestException as e:
            logger.warning("[SKIP] %s -> %s", url, e)
            return FetchResult(ok=False, url=url, reason=str(e))

    logger.warning("[SKIP] %s -> retries exhausted", url)
    return FetchResult(ok=False, url=url, reason="retries_exhausted")
