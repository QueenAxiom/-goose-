"""Direct posting from Mission Control. Facebook Page is the only live rail today."""
import logging
import os
import re
from pathlib import Path

import requests

log = logging.getLogger("mission-control.posting")

GRAPH_BASE = "https://graph.facebook.com/v21.0"
REQUEST_TIMEOUT_SECONDS = 20
MAX_POST_CHARS = 5000
CONTACT_EMAIL = "rise@empoweredathome.com"
SITE_NAMES = ("empoweredathome.com", "everythinginternet.ca", "schmucksdebate.com")
POST_ID_RE = re.compile(r"^[0-9_]+$")
ENV_FILE = Path(__file__).with_name(".env")

# platform -> (label, available, reason when unavailable)
PLATFORMS = {
    "facebook": ("Facebook — EverythingInternet.ca Page", True, ""),
    "linkedin": ("LinkedIn", False, "Company Page posting is blocked: the LinkedIn developer app only supports personal posting."),
    "threads": ("Threads", False, "No Threads credential yet (app secret and threads_content_publish permission still needed)."),
}
RECOMMENDED_CHARS = {"facebook": 500}


class PostingError(Exception):
    """A posting failure whose message is safe to show the user."""


def parse_env(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def load_env(path: Path = ENV_FILE) -> dict:
    """Process env plus the optional gitignored mission-control/.env (process env wins)."""
    try:
        file_env = parse_env(path.read_text(encoding="utf-8"))
    except OSError:
        file_env = {}
    return {**file_env, **os.environ}


def platform_info() -> list:
    return [{"id": pid, "label": label, "available": ok, "reason": reason}
            for pid, (label, ok, reason) in PLATFORMS.items()]


def validate_post(platform: str, text: str) -> "str | None":
    if platform not in PLATFORMS:
        return "unknown platform"
    if not PLATFORMS[platform][1]:
        return f"{platform} is not available: {PLATFORMS[platform][2]}"
    if not isinstance(text, str) or not text.strip():
        return "post is empty"
    if len(text) > MAX_POST_CHARS:
        return f"post is too long (max {MAX_POST_CHARS} characters)"
    return None


def preflight(platform: str, text: str) -> list:
    """Compliance flags from docs/platform-compliance.md. Warnings only; they never block a post."""
    lowered = text.lower()
    flags = []
    if CONTACT_EMAIL not in lowered:
        flags.append(f"No contact email ({CONTACT_EMAIL})")
    if not any(site in lowered for site in SITE_NAMES):
        flags.append("No site mentioned (EmpoweredAtHome.com / EverythingInternet.ca / SchmucksDebate.com)")
    limit = RECOMMENDED_CHARS.get(platform)
    if limit and len(text) > limit:
        flags.append(f"Longer than the recommended {limit} characters for {platform}")
    return flags


class Poster:
    def __init__(self, env: "dict | None" = None):
        self._env = load_env() if env is None else env

    def configured(self, platform: str) -> bool:
        return platform == "facebook" and bool(self._env.get("MC_FB_PAGE_ID") and self._env.get("MC_FB_PAGE_TOKEN"))

    def _facebook_creds(self) -> "tuple[str, str]":
        if not self.configured("facebook"):
            raise PostingError("Facebook isn't set up yet. Add MC_FB_PAGE_ID and MC_FB_PAGE_TOKEN to mission-control/.env.")
        return self._env["MC_FB_PAGE_ID"], self._env["MC_FB_PAGE_TOKEN"]

    @staticmethod
    def _graph_error(resp) -> str:
        try:
            message = resp.json().get("error", {}).get("message", "")
        except ValueError:
            message = ""
        return f"Facebook rejected the request ({resp.status_code}): {message[:200] or 'no details'}"

    def publish(self, platform: str, text: str) -> dict:
        if platform != "facebook":
            raise PostingError(f"{platform} posting isn't available.")
        page_id, token = self._facebook_creds()
        try:
            resp = requests.post(f"{GRAPH_BASE}/{page_id}/feed", data={"message": text, "access_token": token},
                                 timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException:
            log.exception("facebook publish failed")
            raise PostingError("Could not reach Facebook. Nothing was posted.") from None
        if resp.status_code != 200:
            raise PostingError(self._graph_error(resp))
        post_id = resp.json().get("id")
        if not post_id:
            raise PostingError("Facebook returned no post id; check the Page before retrying.")
        return {"post_id": post_id}

    def delete(self, platform: str, post_id: str) -> None:
        if platform != "facebook":
            raise PostingError(f"{platform} posting isn't available.")
        if not POST_ID_RE.match(post_id or ""):
            raise PostingError("Invalid post id.")
        _, token = self._facebook_creds()
        try:
            resp = requests.delete(f"{GRAPH_BASE}/{post_id}", headers={"Authorization": f"OAuth {token}"},
                                   timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException:
            log.exception("facebook delete failed")
            raise PostingError("Could not reach Facebook. The post was not removed.") from None
        if resp.status_code != 200:
            raise PostingError(self._graph_error(resp))
