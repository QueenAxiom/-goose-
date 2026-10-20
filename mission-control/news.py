"""Reuters headlines from the Google News RSS feed, newest first."""
import time
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_TEMPLATE = "https://news.google.com/rss/search?q=site:{domain}&hl=en-US&gl=US&ceid=US:en"
SOURCES = {"reuters": ("reuters.com", " - Reuters"), "ap": ("apnews.com", " - AP News")}
MAX_ITEMS = 10
CACHE_SECONDS = 3600
FETCH_TIMEOUT_SECONDS = 15

_cache = {}


def parse_feed(xml_text: str, suffix: str = "") -> list:
    """Return [{title, link, published (ISO, UTC)}] sorted newest first, capped at MAX_ITEMS."""
    items = []
    for item in ET.fromstring(xml_text).iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        try:
            when = parsedate_to_datetime(item.findtext("pubDate") or "")
        except (TypeError, ValueError):
            continue
        if not title or not link.startswith("http"):
            continue
        if suffix and title.endswith(suffix):
            title = title[: -len(suffix)]
        items.append({"title": title, "link": link, "published": when.isoformat()})
    items.sort(key=lambda i: i["published"], reverse=True)
    return items[:MAX_ITEMS]


def fetch_headlines(source: str = "reuters", now: float = None) -> list:
    domain, suffix = SOURCES[source]
    now = time.time() if now is None else now
    cached = _cache.get(source)
    if cached and now - cached["at"] < CACHE_SECONDS:
        return cached["items"]
    req = urllib.request.Request(FEED_TEMPLATE.format(domain=domain), headers={"User-Agent": "Mozilla/5.0 AxiomMissionControl"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
        items = parse_feed(resp.read().decode("utf-8"), suffix)
    _cache[source] = {"at": now, "items": items}
    return items
