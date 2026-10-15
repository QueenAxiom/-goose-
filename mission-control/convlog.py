"""Append Mission Control chats to the NotebookLM conversation folder (secrets redacted)."""
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from export_conversations import redact  # noqa: E402

log = logging.getLogger("mission-control.convlog")

LABELS = {("ecc", "user"): "Alan", ("ecc", "assistant"): "ECC",
          ("axiom", "user"): "Alan", ("axiom", "assistant"): "Axiom"}
CHANNEL_TITLES = {"ecc": "Chat with ECC", "axiom": "Chat with Axiom"}


def log_turn(directory: "Path | None", channel: str, role: str, text: str) -> None:
    """Add one chat turn to this month's file. A None directory disables logging; failures never break chat."""
    if directory is None:
        return
    now = datetime.now(timezone.utc)
    path = Path(directory) / f"mission-control-chats-{now:%Y-%m}.md"
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        new_file = not path.exists()
        with path.open("a", encoding="utf-8") as fh:
            if new_file:
                fh.write(f"# Mission Control chats, {now:%Y-%m}\n\nChats typed in Mission Control (ECC and Axiom).\n\n")
            fh.write(f"### {now:%Y-%m-%d %H:%M} UTC, {CHANNEL_TITLES.get(channel, channel)}\n"
                     f"**{LABELS.get((channel, role), role)}:** {redact(text)}\n\n")
    except OSError:
        log.exception("could not write conversation log")
