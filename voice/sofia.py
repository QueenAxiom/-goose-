"""Sofia: say "Sofia, <question>" and she answers out loud as Claude.

Wake word is detected by transcribing speech segments with faster-whisper
(stopgap until a custom openWakeWord model exists). Replies come from the
Claude Code CLI run in the repo, so Sofia picks up CLAUDE.md and memory.

Run: python voice/sofia.py
"""
import json
import queue
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

REPO = Path(__file__).resolve().parent.parent
SAMPLE_RATE = 16000
CHUNK = 1600  # 100 ms
SPEECH_RMS = 450
END_SILENCE_CHUNKS = 8  # 0.8 s of quiet ends an utterance
MIN_CHUNKS = 5
MAX_CHUNKS = 300  # 30 s cap
FOLLOW_UP_WAIT_CHUNKS = 80  # 8 s to start speaking after "Sofia?"
WAKE_RE = re.compile(r"\b(sofia|sophia|sofie|sophie)\b[,.!?]*\s*", re.IGNORECASE)
WHISPER_SIZE = "base.en"
DATA_DIR = REPO / "voice" / "data"
LOCAL_MODEL_URL = "http://127.0.0.1:8000/v1/chat/completions"
LOCAL_MODEL = "olmoe-colibri"
PERSONA = (
    "You are Sofia, a spoken voice assistant for Alan Gooding at Axiom Enterprises. "
    "Your words are read aloud, so speech must be one to three short plain sentences: "
    "no markdown, lists, emoji or code. Be direct, warm and business-level, "
    "no tutorial hand-holding. If you do not know something, say so.\n"
    "Reply with ONLY a JSON object, no code fences: "
    '{"action": "none|add_task|save_note|draft", "text": "...", "speech": "..."}. '
    "add_task: text is the task. save_note: text is the note. "
    "draft: text is a one-line brief of what to draft (post, email, outreach). "
    "Use none for questions and chat. You can never publish, send, post, delete or "
    "spend money; if asked, say you can only save it as a task or draft for review. "
    "speech is what you say aloud, confirming what you did."
)


def rms(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))


def listen_utterance(audio_q: "queue.Queue[np.ndarray]", patience: int) -> np.ndarray | None:
    """Block until speech starts, record until it ends. None if nobody speaks."""
    chunks: list[np.ndarray] = []
    quiet, waited, started = 0, 0, False
    while True:
        chunk = audio_q.get()
        loud = rms(chunk) >= SPEECH_RMS
        if not started:
            waited += 1
            if loud:
                started = True
                chunks.append(chunk)
            elif patience and waited > patience:
                return None
            continue
        chunks.append(chunk)
        quiet = 0 if loud else quiet + 1
        if (quiet >= END_SILENCE_CHUNKS and len(chunks) > MIN_CHUNKS) or len(chunks) >= MAX_CHUNKS:
            return np.concatenate(chunks)


def transcribe(whisper: WhisperModel, audio: np.ndarray) -> str:
    segments, _ = whisper.transcribe(audio.astype(np.float32) / 32768.0, language="en")
    return " ".join(s.text.strip() for s in segments).strip()


def ask_claude(question: str) -> str:
    result = subprocess.run(
        ["claude", "-p", question, "--tools", "", "--append-system-prompt", PERSONA],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return "Sorry, I could not reach Claude."
    lines = [l for l in result.stdout.splitlines() if not l.startswith("⚠")]
    return "\n".join(lines).strip()


def parse_reply(raw: str) -> dict:
    """Claude should return JSON; fall back to treating the reply as plain speech."""
    start, end = raw.find("{"), raw.rfind("}")
    try:
        data = json.loads(raw[start:end + 1])
        return {"action": str(data.get("action", "none")),
                "text": str(data.get("text", "")),
                "speech": str(data.get("speech", "")) or "Done."}
    except (ValueError, TypeError):
        return {"action": "none", "text": "", "speech": raw or "I have nothing to add."}


def append_line(filename: str, line: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_DIR / filename, "a", encoding="utf-8") as f:
        f.write(f"- [{stamp}] {line}\n")


def draft_locally(brief: str) -> str:
    """First-pass drafts go to the free local model, never to Claude."""
    payload = json.dumps({"model": LOCAL_MODEL, "messages": [
        {"role": "system", "content": "Draft concise, on-brand copy for Axiom Enterprises: "
                                      "direct, warm, proudly Canadian, no hype or corporate jargon. "
                                      "Do not invent facts, prices or testimonials."},
        {"role": "user", "content": brief}]}).encode("utf-8")
    req = urllib.request.Request(LOCAL_MODEL_URL, payload, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    return body["choices"][0]["message"]["content"].strip()


def run_action(reply: dict) -> str:
    """Execute a whitelisted local action and return what Sofia should say."""
    action, text = reply["action"], reply["text"].strip()
    if action == "add_task" and text:
        append_line("tasks.md", text)
    elif action == "save_note" and text:
        append_line("notes.md", text)
    elif action == "draft" and text:
        try:
            draft = draft_locally(text)
        except (urllib.error.URLError, OSError, KeyError, ValueError):
            return "The local drafting model is not running. Start it and ask me again."
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        name = f"draft-{datetime.now():%Y%m%d-%H%M%S}.md"
        (DATA_DIR / name).write_text(f"Brief: {text}\n\n{draft}\n", encoding="utf-8")
        print(f"Saved voice/data/{name}")
    return reply["speech"]


def speak(text: str) -> None:
    print(f"Sofia: {text}")
    safe = text.replace("'", "''")
    subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"Add-Type -AssemblyName System.Speech; "
         f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')"],
        check=False,
    )


def drain(audio_q: "queue.Queue[np.ndarray]") -> None:
    while not audio_q.empty():
        audio_q.get_nowait()


def main() -> int:
    whisper = WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")
    audio_q: "queue.Queue[np.ndarray]" = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        audio_q.put(indata[:, 0].copy())

    print("Listening for 'Sofia'... (Ctrl+C to quit)")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=CHUNK, callback=on_audio):
        while True:
            audio = listen_utterance(audio_q, patience=0)
            text = transcribe(whisper, audio) if audio is not None else ""
            match = WAKE_RE.search(text)
            if not match:
                continue
            command = text[match.end():].strip()
            if not command:
                speak("Yes?")
                drain(audio_q)
                follow = listen_utterance(audio_q, patience=FOLLOW_UP_WAIT_CHUNKS)
                command = transcribe(whisper, follow) if follow is not None else ""
            if not command:
                continue
            print(f"You: {command}")
            speak(run_action(parse_reply(ask_claude(command))))
            drain(audio_q)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
