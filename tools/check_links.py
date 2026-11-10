"""Check the Axiom sites for broken links and bad redirects, then write a report.

Usage: python tools/check_links.py [site-url ...] [--max-pages N] [--out report.md]

With no URLs it checks EmpoweredAtHome.com, EverythingInternet.ca and SchmucksDebate.com.
Crawls each site's own pages (same host only), checks every link and image it finds,
including external ones, and writes a Markdown report. Read-only: it only sends GET/HEAD.
Exit code is 1 when anything is broken, so it can run from n8n or a scheduled task.
"""
import argparse
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

DEFAULT_SITES = [
    "https://empoweredathome.com/",
    "https://everythinginternet.ca/",
    "https://schmucksdebate.com/",
]
USER_AGENT = "AxiomLinkChecker/1.0 (+https://everythinginternet.ca)"
TIMEOUT_SECONDS = 15
MAX_REDIRECTS = 10
DEFAULT_MAX_PAGES = 200
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "sms:")
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "Claude outputs" / "link-report.md"


class LinkParser(HTMLParser):
    """Collects href/src targets from a page."""

    ATTRS = {"a": "href", "link": "href", "img": "src", "script": "src", "iframe": "src", "source": "src"}

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        wanted = self.ATTRS.get(tag)
        for name, value in attrs:
            if name == wanted and value and value.strip():
                self.links.append(value.strip())


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def request_once(url: str, method: str):
    """One request with no redirect following. Returns (status, location, content_type, body)."""
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with OPENER.open(req, timeout=TIMEOUT_SECONDS) as resp:
            ctype = resp.headers.get("Content-Type", "")
            body = resp.read() if method == "GET" and "html" in ctype else b""
            return resp.status, None, ctype, body
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location"), e.headers.get("Content-Type", ""), b""


def fetch(url: str, want_body: bool):
    """Follow redirects by hand so every hop is recorded.

    Returns dict: status, final_url, hops (list of (status, url)), body, error.
    Tries HEAD first for non-pages; falls back to GET when a server rejects HEAD.
    """
    hops, current = [], url
    for _ in range(MAX_REDIRECTS + 1):
        try:
            method = "GET" if want_body else "HEAD"
            status, location, ctype, body = request_once(current, method)
            if method == "HEAD" and status in (403, 405, 501):
                status, location, ctype, body = request_once(current, "GET")
        except Exception as e:  # DNS, TLS, timeout, refused
            return {"status": None, "final_url": current, "hops": hops, "body": b"", "error": str(e) or type(e).__name__}
        if 300 <= status < 400 and location:
            hops.append((status, current))
            current = urljoin(current, location)
            continue
        return {"status": status, "final_url": current, "hops": hops, "body": body, "error": None}
    return {"status": None, "final_url": current, "hops": hops, "body": b"", "error": "too many redirects"}


def normalize(link: str, base: str) -> "str | None":
    if link.lower().startswith(SKIP_SCHEMES) or link.startswith("#"):
        return None
    url, _ = urldefrag(urljoin(base, link))
    return url if urlparse(url).scheme in ("http", "https") else None


def same_site(url: str, root: str) -> bool:
    strip = lambda h: (h or "").lower().removeprefix("www.")
    return strip(urlparse(url).hostname) == strip(urlparse(root).hostname)


def redirect_problems(url: str, result: dict) -> "list[str]":
    """Why a redirect chain is worth fixing, or [] if it's fine."""
    hops = result["hops"]
    if not hops:
        return []
    problems = []
    if len(hops) > 1:
        problems.append(f"{len(hops)} hops (link straight to the final URL)")
    if urlparse(url).scheme == "https" and urlparse(result["final_url"]).scheme == "http":
        problems.append("redirects from https to http")
    if any(code == 302 or code == 307 for code, _ in hops):
        problems.append("temporary redirect (302/307); use 301 if permanent")
    return problems


def check_site(root: str, max_pages: int, fetcher=fetch) -> dict:
    """Crawl one site. Returns results per checked URL and the pages each URL appears on."""
    results, found_on = {}, defaultdict(set)
    queue, queued = [root], {root}
    pages_crawled = 0
    while queue:
        url = queue.pop(0)
        internal = same_site(url, root)
        crawl = internal and pages_crawled < max_pages
        result = fetcher(url, want_body=crawl)
        results[url] = result
        if not crawl or result["status"] != 200 or not result["body"]:
            continue
        if not same_site(result["final_url"], root):
            continue
        pages_crawled += 1
        parser = LinkParser()
        parser.feed(result["body"].decode("utf-8", errors="replace"))
        for raw in parser.links:
            link = normalize(raw, result["final_url"])
            if not link:
                continue
            found_on[link].add(url)
            if link not in queued:
                queued.add(link)
                queue.append(link)
    return {"root": root, "results": results, "found_on": found_on, "pages_crawled": pages_crawled}


def is_broken(result: dict) -> bool:
    return result["error"] is not None or result["status"] is None or result["status"] >= 400


def build_report(sites: "list[dict]", now: "datetime | None" = None) -> "tuple[str, int]":
    """Markdown report and the total count of broken links."""
    now = now or datetime.now()
    lines = ["# Link check report", "", f"Run: {now:%Y-%m-%d %H:%M}", ""]
    total_broken = 0
    summary = ["| Site | Pages crawled | Links checked | Broken | Redirect issues |", "|---|---|---|---|---|"]
    body = []
    for site in sites:
        results, found_on = site["results"], site["found_on"]
        broken = sorted(u for u, r in results.items() if is_broken(r))
        redirects = sorted((u, p) for u, r in results.items() if not is_broken(r) for p in [redirect_problems(u, r)] if p)
        total_broken += len(broken)
        host = urlparse(site["root"]).hostname
        summary.append(f"| {host} | {site['pages_crawled']} | {len(results)} | {len(broken)} | {len(redirects)} |")

        body += [f"## {host}", ""]
        if not broken and not redirects:
            body += ["No problems found.", ""]
            continue
        if broken:
            body += ["### Broken", "", "| Link | Problem | Found on |", "|---|---|---|"]
            for u in broken:
                r = results[u]
                problem = r["error"] or f"HTTP {r['status']}"
                pages = ", ".join(sorted(found_on.get(u, [])))[:300] or "(start page)"
                body.append(f"| {u} | {problem} | {pages} |")
            body.append("")
        if redirects:
            body += ["### Redirects to fix", "", "| Link | Ends at | Issue | Found on |", "|---|---|---|---|"]
            for u, problems in redirects:
                pages = ", ".join(sorted(found_on.get(u, [])))[:300] or "(start page)"
                body.append(f"| {u} | {results[u]['final_url']} | {'; '.join(problems)} | {pages} |")
            body.append("")
    return "\n".join(lines + summary + [""] + body), total_broken


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sites", nargs="*", default=DEFAULT_SITES)
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="pages to crawl per site")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)

    checked = []
    for root in args.sites:
        print(f"Checking {root} ...", flush=True)
        checked.append(check_site(root, args.max_pages))
    report, broken = build_report(checked)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"{broken} broken link(s). Report: {args.out}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
