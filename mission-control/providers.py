"""Outside-model chat for Mission Control: GPT, DeepSeek and Claude. Keys come from .env, never the page."""
import json
import logging
import urllib.request

log = logging.getLogger("mission-control.providers")

TIMEOUT_SECONDS = 120
MAX_REPLY_TOKENS = 1024
ANTHROPIC_VERSION = "2023-06-01"

PROVIDERS = {
    "gpt": {"name": "GPT", "env_key": "OPENAI_API_KEY", "model_env": "MC_GPT_MODEL", "model": "gpt-4o",
            "url": "https://api.openai.com/v1/chat/completions", "style": "openai"},
    "deepseek": {"name": "DeepSeek", "env_key": "DEEPSEEK_API_KEY", "model_env": "MC_DEEPSEEK_MODEL", "model": "deepseek-chat",
                 "url": "https://api.deepseek.com/chat/completions", "style": "openai"},
    "claude": {"name": "Claude", "env_key": "ANTHROPIC_API_KEY", "model_env": "MC_CLAUDE_MODEL", "model": "claude-sonnet-5-5",
               "url": "https://api.anthropic.com/v1/messages", "style": "anthropic"},
}


RELAY_URLS = {"gpt": "https://chatgpt.com/", "deepseek": "https://chat.deepseek.com/",
              "claude": "https://claude.ai/new"}


def _key(channel: str, env: dict) -> str:
    return str(env.get(PROVIDERS[channel]["env_key"], "")).strip()


def configured(channel: str, env: dict) -> bool:
    return channel in PROVIDERS and bool(_key(channel, env))


def _request(channel: str, prompt: str, env: dict) -> urllib.request.Request:
    p, key = PROVIDERS[channel], _key(channel, env)
    model = str(env.get(p["model_env"], "")).strip() or p["model"]
    messages = [{"role": "user", "content": prompt}]
    if p["style"] == "anthropic":
        body = {"model": model, "max_tokens": MAX_REPLY_TOKENS, "messages": messages}
        headers = {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}
    else:
        body = {"model": model, "messages": messages}
        headers = {"Authorization": f"Bearer {key}"}
    headers["Content-Type"] = "application/json"
    return urllib.request.Request(p["url"], data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")


def _extract(channel: str, payload: dict) -> str:
    if PROVIDERS[channel]["style"] == "anthropic":
        return "".join(b.get("text", "") for b in payload["content"] if b.get("type") == "text").strip()
    return payload["choices"][0]["message"]["content"].strip()


def ask(channel: str, prompt: str, env: dict) -> "tuple[bool, str]":
    """One reply from an outside model. Failures return a fixed, key-free message."""
    p = PROVIDERS[channel]
    if not configured(channel, env):
        return False, f"{p['name']} isn't set up yet. Add {p['env_key']} to mission-control/.env, then restart."
    try:
        with urllib.request.urlopen(_request(channel, prompt, env), timeout=TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read())
        return True, _extract(channel, payload) or "(no reply)"
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        log.exception("%s request failed", p["name"])
        return False, f"{p['name']} could not be reached or replied badly. Check the helper window."
