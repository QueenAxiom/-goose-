"""Mission Control helper: serves the dashboard and relays commands to Claude Code.

Run: python mission-control/control.py   (or start-mission-control.cmd)
Binds to 127.0.0.1 only. Every command needs the per-run token embedded in the page.
"""
import json
import logging
import os
import secrets
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

log = logging.getLogger("mission-control")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
HOST = "127.0.0.1"
PORT = 8765
MAX_PROMPT_CHARS = 2000
MAX_BODY_BYTES = 16 * 1024
CLAUDE_TIMEOUT_SECONDS = 300
TOKEN_PLACEHOLDER = "__MC_TOKEN__"
VIEWS = ("staging", "live")


def load_sites(path: Path = HERE / "sites.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_request(payload, token: str, sites: dict, host: str, origin: "str | None") -> "str | None":
    """Return an error message, or None if the request is acceptable."""
    if not isinstance(payload, dict):
        return "bad payload"
    if host not in (f"{HOST}:{PORT}", f"localhost:{PORT}"):
        return "bad host"
    if origin is not None and origin not in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}"):
        return "bad origin"
    if not secrets.compare_digest(str(payload.get("token", "")), token):
        return "bad token"
    site = sites.get(payload.get("site"))
    if site is None:
        return "unknown site"
    view = payload.get("view")
    if view not in VIEWS:
        return "bad view"
    if view == "staging" and not site.get("staging"):
        return "this site has no staging"
    if view == "live" and payload.get("confirm_live") is not True:
        return "live changes need explicit confirm_live"
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > MAX_PROMPT_CHARS:
        return f"prompt must be 1-{MAX_PROMPT_CHARS} characters"
    return None


def build_prompt(site: dict, name: str, view: str, request: str) -> str:
    url = site[view]
    if view == "staging":
        rule = "This is STAGING. Make the change here only; do not touch the live site."
    else:
        rule = "Alan has confirmed this change for the LIVE site. Keep it minimal and report exactly what changed."
    return f"Mission Control request for {name} ({view}, {url}). {rule}\n\nRequest: {request.strip()}"


def run_claude(prompt: str) -> "tuple[bool, str]":
    """Run Claude Code in the repo. Prompt goes on stdin; failures return a fixed message."""
    try:
        result = subprocess.run(
            ["claude", "-p", "--permission-mode", "acceptEdits"],
            input=prompt, capture_output=True, text=True, encoding="utf-8",
            cwd=REPO, timeout=CLAUDE_TIMEOUT_SECONDS, shell=(os.name == "nt"),
        )
    except (subprocess.SubprocessError, OSError):
        log.exception("claude failed to run")
        return False, "Claude could not be run. Check the helper window."
    if result.returncode != 0:
        log.error("claude exited %s: %s", result.returncode, result.stderr[:500])
        return False, "Claude reported an error. Check the helper window."
    return True, result.stdout.strip() or "(no reply)"


def make_handler(token: str, sites: dict):
    page = (HERE / "index.html").read_text(encoding="utf-8").replace(TOKEN_PLACEHOLDER, token)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj: dict) -> None:
            self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

        def do_GET(self):
            if self.path == "/":
                self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            elif self.path == "/sites.json":
                self._json(200, sites)
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/ask":
                return self._json(404, {"error": "not found"})
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                return self._json(413, {"error": "too large"})
            try:
                payload = json.loads(self.rfile.read(length))
            except ValueError:
                return self._json(400, {"error": "bad json"})
            error = validate_request(payload, token, sites, self.headers.get("Host", ""), self.headers.get("Origin"))
            if error:
                return self._json(403, {"error": error})
            site_name = payload["site"]
            prompt = build_prompt(sites[site_name], site_name, payload["view"], payload["prompt"])
            log.info("ask %s (%s): %s", site_name, payload["view"], payload["prompt"][:200])
            ok, reply = run_claude(prompt)
            self._json(200 if ok else 502, {"ok": ok, "reply": reply})

        def log_message(self, fmt, *args):
            log.info(fmt, *args)

    return Handler


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    token = secrets.token_urlsafe(24)
    server = ThreadingHTTPServer((HOST, PORT), make_handler(token, load_sites()))
    print(f"Mission Control: http://{HOST}:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
