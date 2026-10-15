"""Read-only status probes for Mission Control: sites, Stripe mode, git, backups, templates."""
import logging
import re
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

log = logging.getLogger("mission-control.status")

FETCH_TIMEOUT_SECONDS = 10
MAX_FETCH_BYTES = 2_000_000
STRIPE_CACHE_SECONDS = 60
STRIPE_KEY_RE = re.compile(r"pk_(test|live)_[A-Za-z0-9]{8,}")
TEMPLATE_HEAD_RE = re.compile(r"^## (Email (\d+)[^\n]*)$", re.MULTILINE)
USER_AGENT = "AxiomMissionControl/1.0"

_stripe_cache: dict = {}


def default_fetch(url: str) -> "tuple[int, dict, str]":
    """GET a URL. Returns (status, headers, body-text). Caller passes only trusted URLs."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
            body = resp.read(MAX_FETCH_BYTES).decode("utf-8", errors="replace")
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), ""


def detect_stripe_mode(html: str) -> str:
    modes = {m.group(1) for m in STRIPE_KEY_RE.finditer(html)}
    if modes == {"test"}:
        return "test"
    if modes == {"live"}:
        return "live"
    return "mixed" if modes else "unknown"


def frame_allowed(headers: dict) -> bool:
    lowered = {k.lower(): v.lower() for k, v in headers.items()}
    if lowered.get("x-frame-options", "").strip() in ("deny", "sameorigin"):
        return False
    csp = lowered.get("content-security-policy", "")
    return "frame-ancestors" not in csp or "frame-ancestors *" in csp


def check_site(url: str, fetch=default_fetch) -> dict:
    started = time.perf_counter()
    try:
        code, headers, _ = fetch(url)
    except (OSError, ValueError):
        log.warning("site check failed for %s", url)
        return {"up": False, "status": None, "ms": None, "frame_ok": True}
    return {
        "up": code < 500,
        "status": code,
        "ms": round((time.perf_counter() - started) * 1000),
        "frame_ok": frame_allowed(headers),
    }


def stripe_mode_for(base_url: str, fetch=default_fetch, now=time.monotonic) -> str:
    """Stripe test/live mode as exposed by the site's checkout page (cached briefly)."""
    cached = _stripe_cache.get(base_url)
    if cached and now() - cached[0] < STRIPE_CACHE_SECONDS:
        return cached[1]
    try:
        _, _, body = fetch(base_url.rstrip("/") + "/checkout/")
        mode = detect_stripe_mode(body)
    except (OSError, ValueError):
        mode = "unknown"
    _stripe_cache[base_url] = (now(), mode)
    return mode


def check_all_sites(sites: dict, fetch=default_fetch) -> dict:
    jobs = [(name, view, url) for name, s in sites.items() for view, url in s.items() if url]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda j: check_site(j[2], fetch), jobs))
    out: dict = {name: {} for name in sites}
    for (name, view, _), result in zip(jobs, results):
        out[name][view] = result
    return out


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                            encoding="utf-8", timeout=15)
    return result.stdout.strip()


def git_summary(repo: Path) -> dict:
    try:
        dirty = [l for l in _git(repo, "status", "--porcelain").splitlines() if l]
        return {
            "branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
            "last_commit": _git(repo, "log", "-1", "--format=%h %s (%cr)"),
            "unpushed": len(_git(repo, "log", "@{u}..", "--oneline").splitlines()),
            "uncommitted": len(dirty),
        }
    except (subprocess.SubprocessError, OSError):
        log.exception("git summary failed")
        return {"error": "git unavailable"}


def backup_summary(repo: Path) -> dict:
    log_path = repo / "automation" / "backup-docs-to-drive.log"
    try:
        lines = [l for l in log_path.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    except OSError:
        return {"last_line": None}
    return {"last_line": lines[-1][:300] if lines else None}


def parse_templates(markdown: str) -> list:
    """Split the outreach drafts doc into one entry per '## Email N' section."""
    heads = list(TEMPLATE_HEAD_RE.finditer(markdown))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(markdown)
        body = re.split(r"^## (?!Email )", markdown[m.end():end], maxsplit=1, flags=re.MULTILINE)[0]
        out.append({"id": f"email-{m.group(2)}", "title": m.group(1).strip(), "body": body.strip()})
    return out
