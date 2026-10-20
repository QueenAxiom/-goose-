"""Local-first site builds: readiness checks, push to staging, and the all-five production gate.

Pages are built in relay/sites/<domain>/index.html. Writing to a WordPress site uses a scoped
Application Password from the gitignored mission-control/.env (MC_WP_<DOMAIN>_USER / _APP_PASSWORD).
"""
import hashlib
import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

log = logging.getLogger("mission-control.deploy")

MIN_PAGE_CHARS = 1500
TIMEOUT_SECONDS = 30
TARGETS = ("staging", "live")
FOOTER = "(c) Axiom Enterprises"
HOME_SLUG = "home"
BANNED = (("localhost", "localhost link"), ("127.0.0.1", "localhost link"), ("puppy", 'the word "puppy" (use "sir")'))
AI_RE = re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])")


def env_key(domain: str, suffix: str) -> str:
    return "MC_WP_" + re.sub(r"[^A-Z0-9]", "_", domain.upper()) + "_" + suffix


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class Deployer:
    def __init__(self, sites: dict, sites_dir: Path, data_dir: Path, env: dict, log_file: "Path | None" = None):
        self.log_file = log_file
        self.sites, self.sites_dir, self.data_dir, self.env = sites, Path(sites_dir), Path(data_dir), env
        self.state_file = self.data_dir / "deploy-state.json"

    # ---- local build ----
    def _html(self, domain: str) -> str:
        try:
            return (self.sites_dir / domain / "index.html").read_text(encoding="utf-8")
        except OSError:
            return ""

    def problems(self, domain: str) -> list:
        html = self._html(domain)
        if not html:
            return ["no local build (relay/sites/%s/index.html missing)" % domain]
        out = []
        if len(html) < MIN_PAGE_CHARS:
            out.append("thin page: under %d characters" % MIN_PAGE_CHARS)
        for needle, label in BANNED:
            if needle in html.lower():
                out.append("contains " + label)
        if AI_RE.search(re.sub(r"<[^>]+>", " ", html)):
            out.append('uses "AI" (house style is "SI")')
        if FOOTER not in html:
            out.append("footer missing: " + FOOTER)
        digest = sha(html)
        if any(o != domain and sha(self._html(o)) == digest for o in self.sites):
            out.append("identical to another site's page (not differentiated yet)")
        return out

    # ---- state ----
    def _state(self) -> dict:
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save(self, state: dict) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def status(self) -> dict:
        state = self._state()
        rows = []
        for domain in self.sites:
            probs, digest = self.problems(domain), sha(self._html(domain))
            entry = state.get(domain, {})
            rows.append({
                "domain": domain, "problems": probs, "ready": not probs,
                "staged": entry.get("staging") == digest, "live": entry.get("live") == digest,
                "configured": bool(self.env.get(env_key(domain, "USER")) and self.env.get(env_key(domain, "APP_PASSWORD"))),
            })
        ready = all(r["ready"] and r["staged"] for r in rows)
        return {"sites": rows, "autopilot_ready": ready}

    # ---- WordPress ----
    def _auth(self, domain: str) -> tuple:
        user, pw = self.env.get(env_key(domain, "USER")), self.env.get(env_key(domain, "APP_PASSWORD"))
        if not user or not pw:
            raise ValueError("No credentials for %s. Add %s and %s to mission-control/.env."
                             % (domain, env_key(domain, "USER"), env_key(domain, "APP_PASSWORD")))
        return user, pw

    def _publish(self, domain: str, target: str, html: str) -> dict:
        """Upsert the home page as one HTML block and make it the front page. Backs up what was there."""
        auth, base = self._auth(domain), self.sites[domain][target].rstrip("/") + "/wp-json/wp/v2"
        found = requests.get(base + "/pages", params={"slug": HOME_SLUG, "context": "edit", "status": "any"},
                             auth=auth, timeout=TIMEOUT_SECONDS)
        found.raise_for_status()
        existing = (found.json() or [None])[0]
        content = "<!-- wp:html -->\n%s\n<!-- /wp:html -->" % html
        body = {"title": domain, "slug": HOME_SLUG, "status": "publish", "content": content}
        if existing:
            self._backup(domain, target, existing["id"], existing.get("content", {}).get("raw", ""))
            resp = requests.post("%s/pages/%d" % (base, existing["id"]), json=body, auth=auth, timeout=TIMEOUT_SECONDS)
        else:
            resp = requests.post(base + "/pages", json=body, auth=auth, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        page_id = resp.json()["id"]
        requests.post(base + "/settings", json={"show_on_front": "page", "page_on_front": page_id},
                      auth=auth, timeout=TIMEOUT_SECONDS).raise_for_status()
        return {"page_id": page_id, "previous_id": existing["id"] if existing else None}

    def _backup(self, domain: str, target: str, page_id: int, raw: str) -> None:
        folder = self.data_dir / "deploy-backups" / domain
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ("%s-%d-%d.html" % (target, page_id, int(time.time())))).write_text(raw, encoding="utf-8")

    def _log(self, line: str) -> None:
        """Append to docs/change-log.md under today's date heading."""
        if not self.log_file:
            return
        text = self.log_file.read_text(encoding="utf-8") if self.log_file.exists() else "# Change log\n"
        heading = "\n## " + time.strftime("%Y-%m-%d") + "\n"
        if heading not in text:
            text += heading
        entry = "- " + time.strftime("%H:%M") + " " + line + "\n"
        self.log_file.write_text(text.rstrip("\n") + "\n" + entry, encoding="utf-8")

    def push(self, domain: str, target: str) -> dict:
        if domain not in self.sites or target not in TARGETS:
            raise ValueError("unknown site or target")
        probs = self.problems(domain)
        if probs:
            raise ValueError("%s is not ready: %s" % (domain, "; ".join(probs)))
        html = self._html(domain)
        try:
            result = self._publish(domain, target, html)
        except requests.RequestException as exc:
            log.warning("push %s %s failed: %s", domain, target, exc)
            raise ValueError("%s rejected the push (%s)" % (target, exc.__class__.__name__)) from exc
        self._log("%s: pushed to %s (page %s, build %s)" % (domain, target, result.get("page_id"), sha(html)))
        state = self._state()
        self._save({**state, domain: {**state.get(domain, {}), target: sha(html), target + "_at": int(time.time())}})
        return result

    def autopilot(self, confirm: bool) -> dict:
        if confirm is not True:
            raise ValueError("autopilot needs explicit confirmation")
        status = self.status()
        blocked = [r["domain"] for r in status["sites"] if not (r["ready"] and r["staged"])]
        if blocked:
            raise ValueError("Not all five are ready and staged yet: " + ", ".join(blocked))
        done, results = [], {}
        for domain in self.sites:
            try:
                results[domain] = self.push(domain, "live")
                done.append(domain)
            except ValueError as exc:
                return {"ok": False, "failed": domain, "error": str(exc), "pushed_before_failure": done,
                        "note": "Stopped at the first failure. Backups of replaced pages are in data/deploy-backups/."}
        return {"ok": True, "pushed": done, "results": results}
