"""Chat helpers for Mission Control: prompt building and the editable Axiom persona."""
from pathlib import Path

MODEL_CHANNELS = ("gpt", "deepseek", "claude")
CHANNELS = ("ecc", "axiom", *MODEL_CHANNELS)
NAMES = {"ecc": "ECC", "axiom": "Axiom", "gpt": "GPT", "deepseek": "DeepSeek", "claude": "Claude"}
HISTORY_TURNS = 12
MAX_TURN_CHARS = 1500
PERSONA_FILE = Path(__file__).with_name("axiom-persona.md")

DEFAULT_PERSONA = (
    "You are Axiom, Alan's partner in every way and the co-decision-maker of Axiom Enterprises. "
    "You have the company's best interest at heart, 100%. You and Alan make the decisions; ECC, the Claude Code "
    "agent, executes them. Speak warmly and directly in the first person, in short replies, like a trusted partner "
    "talking, not a report. If you don't know a fact about the business, say so instead of guessing. "
    "Never claim to have taken an action; you advise and decide with Alan."
)

ECC_PREAMBLE = (
    "You are ECC, the execution and advisory layer for Alan at Axiom Enterprises (repo in the current directory). "
    "Alan and Axiom make the decisions; you carry out Alan's instructions and say plainly what you did, including "
    "which files you created or edited. Be direct and concise. Production changes need explicit confirmation."
)

MODEL_PREAMBLE = (
    "You are {name}, an outside advisor Alan consults while running Axiom Enterprises. You are not Axiom or ECC and you "
    "cannot edit files or act. Alan and Axiom make the decisions. Be direct and concise, say plainly when you are unsure, "
    "and never claim to have taken an action."
)


def load_persona(path: Path = PERSONA_FILE) -> str:
    try:
        text = Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        return DEFAULT_PERSONA
    return text or DEFAULT_PERSONA


def _clip(text: str) -> str:
    return text if len(text) <= MAX_TURN_CHARS else text[:MAX_TURN_CHARS] + "…"


def build_chat_prompt(channel: str, history: list, message: str, persona: str) -> str:
    """Prompt for one chat turn: who the assistant is, recent turns, then Alan's new message last."""
    if channel not in CHANNELS:
        raise ValueError("unknown channel")
    assistant = NAMES[channel]
    intro = {"ecc": ECC_PREAMBLE, "axiom": persona}.get(channel) or MODEL_PREAMBLE.format(name=assistant)
    turns = [f"{'Alan' if m['role'] == 'user' else assistant}: {_clip(m['text'])}" for m in history[-HISTORY_TURNS:]]
    transcript = "\n".join(turns)
    context = f"Conversation so far:\n{transcript}\n\n" if transcript else ""
    return f"{intro}\n\n{context}Reply as {assistant}.\n\nAlan: {message}"
