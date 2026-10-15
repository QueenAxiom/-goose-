"""Export every Claude Code conversation to NotebookLM-ready markdown, one file per month.

Usage: python tools/export_conversations.py [source_dir] [dest_dir]

Defaults read this project's Claude Code sessions and write to
C:\\Axiom Enterprises\\conversations. Safe to re-run: files are rewritten from scratch.
Upload the files to NotebookLM (or put them in a Google Drive folder and add them as Drive
sources, then press Sync). Secrets are redacted before anything is written.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_SOURCE = Path.home() / ".claude" / "projects" / "C--Users-DELL-axiom-enterprises"
DEFAULT_DEST = Path(r"C:\Axiom Enterprises\conversations")
OWNER_LABEL, ASSISTANT_LABEL = "Alan", "ECC"
REDACTED = "[REDACTED]"

REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
    re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{8,}"),
    re.compile(r"\bpk_(?:live|test)_[A-Za-z0-9]{8,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
    re.compile(r"\bEAA[A-Za-z0-9]{40,}"),
    re.compile(r"(?i)(MC_FB_PAGE_TOKEN|api[_-]?key|secret|password|token)\s*[=:]\s*\S{8,}"),
]


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(REDACTED, text)
    return text


def extract_text(message) -> str:
    """The human-readable text of a transcript message; tool calls, results and thinking are dropped."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, list):
        content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    if not isinstance(content, str):
        return ""
    return REMINDER_RE.sub("", content).strip()


def _title(entries: list) -> str:
    return next((e["aiTitle"] for e in entries if e.get("type") == "ai-title" and e.get("aiTitle")), "Untitled conversation")


def _is_turn(entry: dict) -> bool:
    msg = entry.get("message")
    return (entry.get("type") in ("user", "assistant") and isinstance(msg, dict)
            and not entry.get("isSidechain") and not entry.get("isSynthetic") and msg.get("model") != "<synthetic>")


def _timestamps(entries: list) -> list:
    return sorted(e["timestamp"] for e in entries if e.get("timestamp") and _is_turn(e))


def month_key(entries: list) -> str:
    stamps = _timestamps(entries)
    return stamps[0][:7] if stamps else "undated"


def session_markdown(entries: list) -> "str | None":
    """One conversation as markdown, or None if it has no readable turns."""
    turns = []
    for e in entries:
        if not _is_turn(e):
            continue
        text = redact(extract_text(e["message"]))
        if text:
            label = OWNER_LABEL if e["type"] == "user" else ASSISTANT_LABEL
            turns.append(f"**{label}:** {text}")
    if not turns:
        return None
    stamps = _timestamps(entries)
    when = f"{stamps[0][:10]} {stamps[0][11:16]} UTC" if stamps else "undated"
    return f"## {_title(entries)}\n*{when}*\n\n" + "\n\n".join(turns) + "\n"


def _read_entries(path: Path) -> list:
    entries = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    return entries


def export(source: Path, dest: Path) -> dict:
    """Write one markdown file per month. Returns counts so repeat runs can be compared."""
    by_month = defaultdict(list)
    for path in sorted(Path(source).glob("*.jsonl")):
        entries = _read_entries(path)
        md = session_markdown(entries)
        if md:
            by_month[month_key(entries)].append((_timestamps(entries)[0], md))
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for month, sessions in by_month.items():
        body = "\n---\n\n".join(md for _, md in sorted(sessions))
        header = f"# Axiom Enterprises conversations, {month}\n\nAlan's conversations with ECC (Claude Code). Newest sessions last.\n\n"
        (dest / f"axiom-conversations-{month}.md").write_text(header + body, encoding="utf-8")
    return {"months": len(by_month), "sessions": sum(len(s) for s in by_month.values())}


def main(argv: list) -> int:
    source = Path(argv[0]) if argv else DEFAULT_SOURCE
    dest = Path(argv[1]) if len(argv) > 1 else DEFAULT_DEST
    result = export(source, dest)
    print(f"Exported {result['sessions']} conversations into {result['months']} monthly files in {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
