"""Command router: wake word extraction, keyword routing, action dispatch."""
import json
import logging
import os
import re
import subprocess
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

log = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).with_name("routes.json")
REQUEST_TIMEOUT_SECONDS = 30
LOCAL_MODEL_TIMEOUT_SECONDS = 180  # olmoe-colibri runs ~2 tokens/s
LOCAL_MODEL_MAX_TOKENS = 60
CLAUDE_TIMEOUT_SECONDS = 120
MAX_REPLY_CHARS = 600
VALID_ACTIONS = ("reply", "webhook", "local_model", "claude")
ALLOWED_HOSTS = ("localhost", "127.0.0.1")
SECRET_HEADER = "X-Axiom-Secret"
SECRET_ENV = "AXIOM_WEBHOOK_SECRET"
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
SPOKEN_STYLE_PROMPT = (
    "You are Jarvis, a spoken assistant for Alan at Axiom Enterprises. Reply in one to "
    "three short plain sentences, no markdown or lists. Be direct and warm. "
    "If you do not know, say so."
)


@dataclass(frozen=True)
class Route:
    name: str
    keywords: tuple = ()
    action: str = "reply"
    target: str = ""


@lru_cache(maxsize=None)
def _phrase_re(phrase: str) -> "re.Pattern[str]":
    return re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)


def extract_command(text: str, wake_words: tuple) -> "str | None":
    """Return the text after a wake word that opens the utterance, else None."""
    stripped = text.lstrip()
    for wake in wake_words:
        match = _phrase_re(wake).match(stripped)
        if match:
            return stripped[match.end():].strip(" ,.!?:;")
    return None


def route(command: str, routes: tuple) -> Route:
    """First route whose keyword appears as a whole phrase in the command wins."""
    if not command.strip():
        return Route(name="empty", action="reply", target="Yes?")
    for r in routes:
        if any(_phrase_re(k).search(command) for k in r.keywords):
            return r
    return Route(name="fallback", action="local_model")


def sanitize_reply(text: str) -> str:
    """Strip ANSI/control characters and cap length before speaking or printing."""
    cleaned = CONTROL_RE.sub("", ANSI_RE.sub("", text))
    return cleaned[:MAX_REPLY_CHARS]


def _is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.hostname in ALLOWED_HOSTS


def load_config(path: Path = CONFIG_PATH) -> dict:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not raw.get("wake_words"):
        raise ValueError("wake_words must not be empty")
    if not _is_local_url(raw["local_model_url"]):
        raise ValueError("local_model_url must point at localhost")
    routes = tuple(
        Route(r["name"], tuple(r["keywords"]), r["action"], r.get("target", ""))
        for r in raw["routes"]
    )
    for r in routes:
        if r.action not in VALID_ACTIONS:
            raise ValueError(f"route {r.name!r}: unknown action {r.action!r}")
        if r.action == "webhook" and not _is_local_url(r.target):
            raise ValueError(f"route {r.name!r}: webhook must point at localhost")
    return {**raw, "routes": routes}


def _run_action(matched: Route, command: str, config: dict) -> str:
    if matched.action == "reply":
        return matched.target
    if matched.action == "webhook":
        secret = os.environ.get(SECRET_ENV, "")
        resp = requests.post(
            matched.target,
            json={"command": command},
            headers={SECRET_HEADER: secret} if secret else {},
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
        resp.raise_for_status()
        return f"{matched.name} triggered."
    if matched.action == "local_model":
        resp = requests.post(
            config["local_model_url"],
            json={
                "model": config["local_model"],
                "max_tokens": LOCAL_MODEL_MAX_TOKENS,
                "messages": [
                    {"role": "system", "content": SPOKEN_STYLE_PROMPT},
                    {"role": "user", "content": command},
                ],
            },
            timeout=LOCAL_MODEL_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    if matched.action == "claude":
        result = subprocess.run(
            ["claude", "-p", "--tools", "", "--strict-mcp-config",
             "--append-system-prompt", SPOKEN_STYLE_PROMPT],
            input=command, capture_output=True, text=True, encoding="utf-8",
            timeout=CLAUDE_TIMEOUT_SECONDS, shell=(os.name == "nt"),
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude exited {result.returncode}")
        return result.stdout.strip() or "Claude had nothing to add."
    raise ValueError(f"unknown action {matched.action!r}")


def dispatch(matched: Route, command: str, config: dict) -> str:
    """Execute a route's action and return a safe reply. Failures become a fixed message."""
    try:
        return sanitize_reply(_run_action(matched, command, config))
    except (requests.RequestException, subprocess.SubprocessError, OSError,
            LookupError, TypeError, AttributeError, ValueError, RuntimeError):
        log.exception("route %s failed", matched.name)
        return f"{matched.name} failed."


SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")
SSE_PREFIX = "data: "
SSE_DONE = "[DONE]"


def iter_sentences(tokens):
    """Group a token stream into sentences, yielding each as soon as it completes."""
    buffer = ""
    for token in tokens:
        buffer += token
        *done, buffer = SENTENCE_END_RE.split(buffer)
        yield from (s.strip() for s in done if s.strip())
    if buffer.strip():
        yield buffer.strip()


def _stream_tokens(command: str, config: dict):
    with requests.post(
        config["local_model_url"],
        json={
            "model": config["local_model"],
            "max_tokens": LOCAL_MODEL_MAX_TOKENS,
            "stream": True,
            "messages": [
                {"role": "system", "content": SPOKEN_STYLE_PROMPT},
                {"role": "user", "content": command},
            ],
        },
        timeout=LOCAL_MODEL_TIMEOUT_SECONDS,
        allow_redirects=False,
        stream=True,
    ) as resp:
        resp.raise_for_status()
        for raw in resp.iter_lines():
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            if not line.startswith(SSE_PREFIX) or line[len(SSE_PREFIX):] == SSE_DONE:
                continue
            delta = json.loads(line[len(SSE_PREFIX):])["choices"][0]["delta"]
            yield delta.get("content") or ""


def handle_stream(text: str, config: dict):
    """Like handle(), but yields the reply sentence by sentence so speech can start early."""
    command = extract_command(text, config["wake_words"])
    if command is None:
        return
    matched = route(command, config["routes"])
    if matched.action != "local_model":
        yield dispatch(matched, command, config)
        return
    try:
        for sentence in iter_sentences(_stream_tokens(command, config)):
            yield sanitize_reply(sentence)
    except (requests.RequestException, OSError, LookupError, TypeError, AttributeError, ValueError):
        log.exception("route %s failed", matched.name)
        yield f"{matched.name} failed."


def handle(text: str, config: dict) -> "str | None":
    """Full pipeline for one utterance. Returns reply text, or None if no wake word."""
    command = extract_command(text, config["wake_words"])
    if command is None:
        return None
    return dispatch(route(command, config["routes"]), command, config)
