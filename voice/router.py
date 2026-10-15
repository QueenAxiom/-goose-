"""Command router: wake word extraction, keyword routing, action dispatch."""
import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests

CONFIG_PATH = Path(__file__).with_name("routes.json")
REQUEST_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class Route:
    name: str
    keywords: tuple = ()
    action: str = "reply"
    target: str = ""


def extract_command(text, wake_words):
    """Return the text after the first wake word, or None if absent."""
    lowered = text.lower()
    for wake in wake_words:
        idx = lowered.find(wake.lower())
        if idx != -1:
            return text[idx + len(wake):].strip(" ,.!?:;")
    return None


def route(command, routes):
    """First route whose keyword appears in the command wins."""
    if not command.strip():
        return Route(name="empty", action="reply", target="Yes?")
    lowered = command.lower()
    for r in routes:
        if any(k in lowered for k in r.keywords):
            return r
    return Route(name="fallback", action="local_model")


def load_config(path=CONFIG_PATH):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    routes = tuple(
        Route(r["name"], tuple(r["keywords"]), r["action"], r.get("target", ""))
        for r in raw["routes"]
    )
    return {**raw, "routes": routes}


def dispatch(matched, command, config):
    """Execute a route's action and return the reply text. Errors become messages, not crashes."""
    try:
        if matched.action == "reply":
            return matched.target
        if matched.action == "webhook":
            resp = requests.post(matched.target, json={"command": command}, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            return f"{matched.name} triggered."
        if matched.action == "local_model":
            resp = requests.post(
                config["local_model_url"],
                json={"model": config["local_model"], "messages": [{"role": "user", "content": command}]},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"Unknown action: {matched.action}"
    except (requests.RequestException, KeyError, ValueError) as exc:
        return f"{matched.name} failed: {exc}"


def handle(text, config):
    """Full pipeline for one utterance. Returns reply text, or None if no wake word."""
    command = extract_command(text, config["wake_words"])
    if command is None:
        return None
    return dispatch(route(command, config["routes"]), command, config)
