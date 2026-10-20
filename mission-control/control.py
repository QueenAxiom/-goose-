"""Mission Control helper: serves the dashboard, status/sales APIs, and relays commands to Claude Code.

Run: python mission-control/control.py   (or start-mission-control.cmd)
Binds to 127.0.0.1 only. Every request needs the per-run token embedded in the page.
"""
import json
import logging
import os
import secrets
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import chat
import convlog
import files
import news
import next_action
import posting
import providers
import status
import weather
from store import COUNCIL_TOPICS, STATUSES, Store
from voice_ctl import VoiceProcess

log = logging.getLogger("mission-control")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
HOST = "127.0.0.1"
PORT = 8765
MAX_PROMPT_CHARS = 2000
MAX_BODY_BYTES = 80 * 1024
CLAUDE_TIMEOUT_SECONDS = 300
TOKEN_PLACEHOLDER = "__MC_TOKEN__"
TOKEN_HEADER = "X-MC-Token"
VIEWS = ("staging", "live")
POST_HISTORY_LIMIT = 50
UNDO_WINDOW_SECONDS = 300
DUPLICATE_WINDOW_SECONDS = 60
MAX_SAY_CHARS = 500
MAX_CHAT_CHARS = 4000
MAX_RELAY_REPLY_CHARS = 16000
CONVERSATIONS_DIR = Path(r"C:\Axiom Enterprises\conversations")
N8N_URL = "https://goldengoose.app.n8n.cloud"
EMAIL_URL = "https://mail.google.com/"
GODADDY_URL = "https://www.godaddy.com/"
GROK_URL = "https://grok.com/"
CHECKOUT_SITE = "EverythingInternet.ca"
DRAFTS_DOC = REPO / "docs" / "smb-outreach-drafts.md"
STATIC_FILES = {"/app.js": "application/javascript; charset=utf-8", "/style.css": "text/css; charset=utf-8",
                "/assets/sofia-day.webp": "image/webp", "/assets/sofia-pro.webp": "image/webp",
                "/assets/sofia-horned.webp": "image/webp"}


def load_sites(path: Path = HERE / "sites.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def guard(host: str, origin: "str | None", supplied_token: "str | None", token: str) -> "str | None":
    """Shared request checks: local host, same origin, correct token."""
    if host not in (f"{HOST}:{PORT}", f"localhost:{PORT}"):
        return "bad host"
    if origin is not None and origin not in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}"):
        return "bad origin"
    if not isinstance(supplied_token, str) or not secrets.compare_digest(supplied_token, token):
        return "bad token"
    return None


def validate_request(payload, token: str, sites: dict, host: str, origin: "str | None") -> "str | None":
    """Return an error message for a /ask payload, or None if acceptable."""
    if not isinstance(payload, dict):
        return "bad payload"
    error = guard(host, origin, payload.get("token"), token)
    if error:
        return error
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


def run_claude(prompt: str, edits: bool = True, tools: bool = True) -> "tuple[bool, str]":
    """Run Claude Code in the repo. Prompt goes on stdin; failures return a fixed message.

    edits=False drops the accept-edits permission; tools=False removes every tool (pure conversation).
    """
    argv = ["claude", "-p"]
    if edits:
        argv += ["--permission-mode", "acceptEdits"]
    if not tools:
        argv += ["--tools", ""]
    try:
        result = subprocess.run(
            argv, input=prompt, capture_output=True, text=True, encoding="utf-8",
            cwd=REPO, timeout=CLAUDE_TIMEOUT_SECONDS, shell=(os.name == "nt"),
        )
    except (subprocess.SubprocessError, OSError):
        log.exception("claude failed to run")
        return False, "Claude could not be run. Check the helper window."
    if result.returncode != 0:
        log.error("claude exited %s: %s", result.returncode, result.stderr[:500])
        return False, "Claude reported an error. Check the helper window."
    return True, result.stdout.strip() or "(no reply)"


COUNCIL_ANGLES = ("Factual reviewer: are the premises true? What is unverified?",
                  "Senior engineer: what is the simplest approach that works, and what breaks?",
                  "Security and risk: what could go wrong or leak?",
                  "Consistency reviewer: does it conflict with Axiom's earlier decisions (docs/decisions-log.md)?",
                  "Redundancy checker: is any of this already built or unnecessary?")


def build_council_package(question: dict) -> str:
    """Copy-paste package for an outside model: the question, context and the required reply format."""
    reviewer = COUNCIL_TOPICS.get(question["topic"], "/autoplan")
    return (
        f"Question for the Axiom Enterprises council (asked by {question['asked_by']}, topic: {question['topic']}).\n\n"
        f"{question['question']}\n\n"
        "Context: Axiom Enterprises runs EmpoweredAtHome.com, EverythingInternet.ca and SchmucksDebate.com; "
        "goal is first customers for a $499 website + automation offer for Canadian small businesses. "
        "Rules: say \"SI\", never \"AI\"; keep it practical; flag risks but don't stall.\n\n"
        f"Suggested in-repo reviewer: {reviewer}\n\n"
        "Reply with: VERDICT: AGREE, CHANGES or NEEDS-INFO, then your reasoning in under 200 words."
    )


def build_council_prompt(question: dict) -> str:
    angles = "\n".join(f"- {a}" for a in COUNCIL_ANGLES)
    return (
        f"Council question from {question['asked_by']} (topic: {question['topic']}): {question['question']}\n\n"
        f"Answer it from these angles, briefly, then give one clear recommendation:\n{angles}\n"
        "Check docs/decisions-log.md before contradicting an earlier decision. Do not change any files or sites."
    )


def voice_reply(text: str) -> str:
    """Run text through the Jarvis router (wake word implied) and return the full reply."""
    voice_dir = str(REPO / "voice")
    if voice_dir not in sys.path:
        sys.path.insert(0, voice_dir)
    import router  # noqa: E402  (lives in voice/, imported lazily so tests don't need it)

    config = router.load_config()
    sentences = list(router.handle_stream(f"{config['wake_words'][0]} {text}", config))
    return " ".join(sentences) or "No reply."


class App:
    """Everything the HTTP handler needs: config, store, voice process, poster."""

    def __init__(self, token: str, sites: dict, store: Store, voice: VoiceProcess, poster: "posting.Poster",
                 scheduler=None, conv_dir: "Path | None" = None):
        self.token, self.sites, self.store, self.voice, self.poster = token, sites, store, voice, poster
        self.scheduler, self.conv_dir = scheduler, conv_dir

    def chat_history(self, body: dict) -> dict:
        channel = str(body.get("channel", ""))
        if channel not in chat.CHANNELS:
            raise ValueError("unknown channel")
        out = {"messages": self.store.chat_history(channel)}
        if channel in chat.MODEL_CHANNELS:
            api = providers.configured(channel, posting.load_env())
            out.update(mode="api" if api else "relay", url=providers.RELAY_URLS[channel])
        return out

    def _relay_channel(self, body: dict) -> str:
        channel = str(body.get("channel", ""))
        if channel not in chat.MODEL_CHANNELS:
            raise ValueError("paste relay is only for GPT, DeepSeek and Claude")
        return channel

    @staticmethod
    def _relay_text(value, limit: int, what: str) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f"{what} must be 1-{limit} characters")
        return value.strip()

    def chat_prompt(self, body: dict) -> dict:
        """Prompt to paste into the model's own website (free paste relay)."""
        channel = self._relay_channel(body)
        message = self._relay_text(body.get("message"), MAX_CHAT_CHARS, "message")
        return {"prompt": chat.build_chat_prompt(channel, self.store.chat_history(channel), message, chat.load_persona())}

    def chat_record(self, body: dict) -> dict:
        """Save Alan's message and the reply he pasted back from the model's website."""
        channel = self._relay_channel(body)
        message = self._relay_text(body.get("message"), MAX_CHAT_CHARS, "message")
        reply = self._relay_text(body.get("reply"), MAX_RELAY_REPLY_CHARS, "reply")
        for role, text in (("user", message), ("assistant", reply)):
            self.store.chat_append(channel, role, text)
            convlog.log_turn(self.conv_dir, channel, role, text)
        return {"ok": True}

    def chat_clear(self, body: dict) -> dict:
        channel = str(body.get("channel", ""))
        if channel not in chat.CHANNELS:
            raise ValueError("unknown channel")
        self.store.chat_clear(channel)
        return {"ok": True}

    def chat(self, body: dict) -> dict:
        """One chat turn. ECC may edit files in the repo (and reports which); Axiom only talks."""
        channel, message = str(body.get("channel", "")), body.get("message")
        if channel not in chat.CHANNELS:
            raise ValueError("unknown channel")
        if not isinstance(message, str) or not message.strip() or len(message) > MAX_CHAT_CHARS:
            raise ValueError(f"message must be 1-{MAX_CHAT_CHARS} characters")
        message = message.strip()
        is_ecc = channel == "ecc"
        prompt = chat.build_chat_prompt(channel, self.store.chat_history(channel), message, chat.load_persona())
        before = files.snapshot(REPO) if is_ecc else {}
        if channel in chat.MODEL_CHANNELS:
            ok, reply = providers.ask(channel, prompt, posting.load_env())
        else:
            ok, reply = run_claude(prompt, edits=is_ecc, tools=is_ecc)
        if not ok:
            raise ValueError(reply)
        changed = files.changed_since(REPO, before) if is_ecc else []
        for role, text in (("user", message), ("assistant", reply)):
            self.store.chat_append(channel, role, text)
            convlog.log_turn(self.conv_dir, channel, role, text)
        return {"reply": reply, "files": changed}

    def files_info(self) -> dict:
        return {"files": files.changed_files(REPO)}

    def file_read(self, body: dict) -> dict:
        return files.read_file(REPO, str(body.get("path", "")))

    def links_info(self) -> dict:
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO, capture_output=True,
                                text=True, encoding="utf-8").stdout.strip()
        github = remote[:-4] if remote.endswith(".git") else remote
        return {"links": {"GitHub": github, "n8n": N8N_URL, "Email": EMAIL_URL, "GoDaddy": GODADDY_URL, "Grok": GROK_URL}}

    def news_info(self) -> dict:
        return {"items": news.fetch_headlines("reuters")}

    def weather_info(self) -> dict:
        return {"cities": weather.fetch_all()}

    def news_ap_info(self) -> dict:
        return {"items": news.fetch_headlines("ap")}

    def posts_info(self) -> dict:
        platforms = [{**p, "configured": self.poster.configured(p["id"])} for p in posting.platform_info()]
        return {"platforms": platforms, "posts": self.store.posts()[:POST_HISTORY_LIMIT], "undo_seconds": UNDO_WINDOW_SECONDS}

    def preflight(self, body: dict) -> dict:
        return {"flags": posting.preflight(str(body.get("platform", "")), str(body.get("text", "")))}

    def post(self, body: dict) -> dict:
        platform, text = str(body.get("platform", "")), body.get("text", "")
        error = posting.validate_post(platform, text)
        if error:
            raise ValueError(error)
        if not self.poster.configured(platform):
            raise ValueError(f"{platform} isn't set up yet. Add MC_FB_PAGE_ID and MC_FB_PAGE_TOKEN to mission-control/.env, then restart.")
        if self.store.recent_duplicate(platform, text, DUPLICATE_WINDOW_SECONDS):
            raise ValueError("That exact post went out less than a minute ago. Undo it first if you want to repost.")
        try:
            result = self.poster.publish(platform, text.strip())
        except posting.PostingError as exc:
            raise ValueError(str(exc)) from None
        record = self.store.add_post({"platform": platform, "text": text.strip(), "post_id": result["post_id"]})
        log.info("posted to %s (%s)", platform, result["post_id"])
        return {"post": record, "flags": posting.preflight(platform, text)}

    def post_multi(self, body: dict) -> dict:
        """Post the same text to every checked platform. Each platform succeeds or fails on its own."""
        requested = body.get("platforms")
        if requested is None and body.get("platform"):
            requested = [body["platform"]]
        platforms = list(dict.fromkeys(str(p) for p in (requested or [])))
        if not platforms:
            raise ValueError("Tick at least one place to post to.")
        text = body.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("post is empty")
        results = []
        for platform in platforms:
            try:
                results.append({"platform": platform, "ok": True, **self.post({"platform": platform, "text": text})})
            except ValueError as exc:
                results.append({"platform": platform, "ok": False, "error": str(exc)})
        return {"results": results}

    def undo(self, body: dict) -> dict:
        record = next((p for p in self.store.posts() if p["id"] == str(body.get("id", ""))), None)
        if record is None:
            raise KeyError("post")
        try:
            self.poster.delete(record["platform"], record["post_id"])
        except posting.PostingError as exc:
            raise ValueError(str(exc)) from None
        self.store.mark_post_deleted(record["id"])
        log.info("undid post %s", record["post_id"])
        return {"ok": True}

    def _facts(self) -> dict:
        now = datetime.now(timezone.utc)
        sites_status = status.check_all_sites(self.sites)
        down = [f"{name} ({view})" for name, views in sites_status.items() for view, r in views.items() if not r.get("up")]
        git = status.git_summary(REPO)
        questions = self.store.questions()
        today = now.date().isoformat()
        checkout = self.sites.get(CHECKOUT_SITE, {})
        return {
            "asked_today": self.store.asked_today(), "dismissed_today": self.store.dismissed_today(),
            "open_questions": sum(q["status"] == "open" for q in questions),
            "fb_configured": self.poster.configured("facebook"),
            "leads": self.store.leads(),
            "approved_templates": sum(a.get("approved", False) for a in self.store.approvals().values()),
            "posts_today": sum(p["created"].startswith(today) and not p["deleted"] for p in self.store.posts()),
            "sites_down": down,
            "uncommitted": git.get("uncommitted", 0), "unpushed": git.get("unpushed", 0),
            "manual_done": self.store.next_done(), "snoozed": self.store.snoozed_today(),
            "staging_checkout": (checkout.get("staging") or checkout.get("live", "")).rstrip("/") + "/checkout/",
            "now": now,
        }

    def next_plan(self) -> dict:
        """Dispatcher view: the next stop, the rest of the route, and what has been delivered today."""
        facts = self._facts()
        everything = next_action.candidates(facts)
        snapshot = self.store.merge_route([(a["key"], a["title"]) for a in everything if a["id"] != "idle"])
        remaining = {a["key"] for a in everything}
        snoozed = {a["key"] for a in everything if a["id"] in facts["snoozed"]}
        delivered = [s for s in snapshot if s["key"] not in remaining]
        skipped = [s for s in snapshot if s["key"] in snoozed]
        return {**next_action.plan(facts), "delivered": delivered, "skipped": skipped,
                "total_stops": len(snapshot), "stop_number": len(delivered) + len(skipped) + 1}

    def next_done(self, body: dict) -> dict:
        self.store.mark_next_done(str(body.get("id", "")))
        return {"ok": True}

    def next_skip(self, body: dict) -> dict:
        self.store.snooze(str(body.get("id", "")))
        return {"ok": True}

    def next_doubt(self, body: dict) -> dict:
        """Prefill a council question about a suggested step; the human decides whether to submit it."""
        match = next((a for a in next_action.candidates(self._facts()) if a["id"] == str(body.get("id", ""))), None)
        if match is None:
            raise ValueError("that step isn't suggested right now")
        return {"draft": f'Mission Control suggested my next step: "{match["title"]}" (reason given: {match["why"]}). '
                         "Is this the right thing to do next, or should something else come first?"}

    def council_info(self) -> dict:
        questions = [{**q, "reviewer": COUNCIL_TOPICS.get(q["topic"], "/autoplan"), "package": build_council_package(q)}
                     for q in self.store.questions()]
        return {
            "questions": questions,
            "topics": {k: v for k, v in COUNCIL_TOPICS.items()},
            "asked_today": self.store.asked_today(),
            "dismissed_today": self.store.dismissed_today(),
        }

    def council_ask(self, body: dict) -> dict:
        return {"question": self.store.add_question(body)}

    def council_answer(self, body: dict) -> dict:
        source = str(body.get("source") or "Alan")
        return {"question": self.store.answer_question(str(body.get("id", "")), str(body.get("answer", "")), source)}

    def council_delete(self, body: dict) -> dict:
        self.store.delete_question(str(body.get("id", "")))
        return {"ok": True}

    def council_dismiss(self, body: dict) -> dict:
        self.store.dismiss_today()
        return {"ok": True}

    def council_ecc(self, body: dict) -> dict:
        """Have ECC (Claude Code) give the council's answer. Uses the Claude plan, so it is an explicit action."""
        question = next((q for q in self.store.questions() if q["id"] == str(body.get("id", ""))), None)
        if question is None:
            raise KeyError("question")
        ok, reply = run_claude(build_council_prompt(question))
        if not ok:
            raise ValueError(reply)
        return {"question": self.store.answer_question(question["id"], reply, "ECC")}

    def say(self, body: dict) -> dict:
        """Type-to-Jarvis for noisy rooms: same router as the voice loop, text in, text out."""
        text = body.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_SAY_CHARS:
            raise ValueError(f"say 1-{MAX_SAY_CHARS} characters")
        return {"reply": voice_reply(text.strip())}

    def system_status(self) -> dict:
        checkout = self.sites.get(CHECKOUT_SITE, {})
        with ThreadPoolExecutor(max_workers=2) as pool:  # site and Stripe probes are independent, so overlap them
            sites_job = pool.submit(status.check_all_sites, self.sites)
            stripe_job = pool.submit(status.stripe_modes, checkout)
        return {
            "sites": sites_job.result(),
            "stripe": stripe_job.result(),
            "git": status.git_summary(REPO),
            "backup": status.backup_summary(REPO),
            "voice": {"running": self.voice.running()},
        }

    def sales(self) -> dict:
        try:
            templates = status.parse_templates(DRAFTS_DOC.read_text(encoding="utf-8"))
        except OSError:
            templates = []
        approvals = self.store.approvals()
        return {
            "scoreboard": self.store.scoreboard(),
            "leads": self.store.leads(),
            "templates": [{**t, "approved": approvals.get(t["id"], {}).get("approved", False)} for t in templates],
            "statuses": list(STATUSES),
        }

    def lead_action(self, body: dict) -> dict:
        action = body.get("action")
        if action == "add":
            return {"lead": self.store.add_lead(body)}
        if action == "update":
            return {"lead": self.store.update_lead(str(body.get("id", "")), body)}
        if action == "delete":
            self.store.delete_lead(str(body.get("id", "")))
            return {"ok": True}
        raise ValueError("unknown action")

    def voice_action(self, body: dict) -> dict:
        action = body.get("action")
        if action == "start":
            return {"changed": self.voice.start(), "running": self.voice.running()}
        if action == "stop":
            return {"changed": self.voice.stop(), "running": self.voice.running()}
        raise ValueError("unknown action")


def make_handler(app: App):
    page = (HERE / "index.html").read_text(encoding="utf-8").replace(TOKEN_PLACEHOLDER, app.token)
    static = {path: ((HERE / path.lstrip("/")).read_bytes(), ctype) for path, ctype in STATIC_FILES.items()}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj: dict) -> None:
            self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

        def _guard(self, supplied_token=None) -> bool:
            token = supplied_token if supplied_token is not None else self.headers.get(TOKEN_HEADER)
            error = guard(self.headers.get("Host", ""), self.headers.get("Origin"), token, app.token)
            if error:
                self._json(403, {"error": error})
            return error is None

        def _read_json(self):
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                self._json(413, {"error": "too large"})
                return None
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                self._json(400, {"error": "bad json"})
                return None
            if not isinstance(body, dict):
                self._json(400, {"error": "bad payload"})
                return None
            return body

        def do_GET(self):
            if self.path == "/":
                return self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            if self.path in static:
                body, ctype = static[self.path]
                return self._send(200, body, ctype)
            if self.path == "/sites.json":
                return self._json(200, app.sites)
            getters = {"/api/status": app.system_status, "/api/sales": app.sales, "/api/posts": app.posts_info,
               "/api/council": app.council_info,
               "/api/next": app.next_plan,
               "/api/files": app.files_info, "/api/links": app.links_info, "/api/news": app.news_info,
               "/api/news-ap": app.news_ap_info, "/api/weather": app.weather_info}
            if self.path in getters:
                if not self._guard():
                    return
                return self._json(200, getters[self.path]())
            self._json(404, {"error": "not found"})

        def do_POST(self):
            body = self._read_json()
            if body is None:
                return
            if self.path == "/ask":
                return self._ask(body)
            handlers = {
                "/api/leads": app.lead_action,
                "/api/voice": app.voice_action,
                "/api/post": app.post_multi,
                "/api/post/undo": app.undo,
                "/api/preflight": app.preflight,
                "/api/say": app.say,
                "/api/council/ask": app.council_ask,
                "/api/council/answer": app.council_answer,
                "/api/council/delete": app.council_delete,
                "/api/council/dismiss": app.council_dismiss,
                "/api/council/ecc": app.council_ecc,
                "/api/chat": app.chat,
                "/api/chat/history": app.chat_history,
                "/api/chat/prompt": app.chat_prompt,
                "/api/chat/record": app.chat_record,
                "/api/chat/clear": app.chat_clear,
                "/api/files/read": app.file_read,
                "/api/next/done": app.next_done,
                "/api/next/skip": app.next_skip,
                "/api/next/doubt": app.next_doubt,
                "/api/money": lambda b: app.store.set_money(b.get("mrr"), b.get("cash")) or {"ok": True},
                "/api/approval": lambda b: app.store.set_approval(str(b.get("id", "")), b.get("approved") is True) or {"ok": True},
            }
            handler = handlers.get(self.path)
            if handler is None:
                return self._json(404, {"error": "not found"})
            if not self._guard():
                return
            try:
                self._json(200, handler(body))
            except KeyError:
                self._json(404, {"error": "not found"})
            except ValueError as exc:
                self._json(400, {"error": str(exc)})

        def _ask(self, body: dict) -> None:
            error = validate_request(body, app.token, app.sites, self.headers.get("Host", ""), self.headers.get("Origin"))
            if error:
                return self._json(403, {"error": error})
            site_name = body["site"]
            prompt = build_prompt(app.sites[site_name], site_name, body["view"], body["prompt"])
            log.info("ask %s (%s): %s", site_name, body["view"], body["prompt"][:200])
            ok, reply = run_claude(prompt)
            self._json(200 if ok else 502, {"ok": ok, "reply": reply})

        def log_message(self, fmt, *args):
            log.info(fmt, *args)

    return Handler


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    app = App(secrets.token_urlsafe(24), load_sites(), Store(HERE / "data"), VoiceProcess(), posting.Poster(),
              conv_dir=CONVERSATIONS_DIR)
    server = ThreadingHTTPServer((HOST, PORT), make_handler(app))
    print(f"Mission Control: http://{HOST}:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        app.voice.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
