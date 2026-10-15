"""Jarvis: say "Hey Jarvis", speak a command, hear the answer.

Wake word (openWakeWord) and speech-to-text (faster-whisper) run locally. Commands go
through router.py: keyword routes first (n8n webhooks, "ask Claude"), then the local
olmoe-colibri model. Claude is only used when you say "ask Claude".

Run from the voice folder: python jarvis.py
"""
import os
import queue
import subprocess
import sys

import numpy as np
import openwakeword
import sounddevice as sd
from faster_whisper import WhisperModel
from openwakeword.model import Model

from router import handle, load_config

WAKE_MODEL = "hey_jarvis"
WAKE_THRESHOLD = 0.5
SAMPLE_RATE = 16000
CHUNK = 1280  # 80 ms, the frame size openWakeWord expects
SILENCE_RMS = 500
SILENCE_CHUNKS = 15  # ~1.2 s of quiet ends the command
MAX_CHUNKS = 375  # ~30 s hard cap
WHISPER_SIZE = "base.en"


def record_command(audio_q: "queue.Queue[np.ndarray]") -> np.ndarray:
    chunks, quiet = [], 0
    while len(chunks) < MAX_CHUNKS:
        chunk = audio_q.get()
        chunks.append(chunk)
        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
        quiet = quiet + 1 if rms < SILENCE_RMS else 0
        if quiet >= SILENCE_CHUNKS and len(chunks) > SILENCE_CHUNKS:
            break
    return np.concatenate(chunks)


def transcribe(whisper: WhisperModel, audio: np.ndarray) -> str:
    segments, _ = whisper.transcribe(audio.astype(np.float32) / 32768.0, language="en", vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()


def speak(text: str) -> None:
    print(f"Jarvis: {text}")
    # Text travels via an env var, never inside the PowerShell command string.
    subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Add-Type -AssemblyName System.Speech; "
         "(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak($env:JARVIS_SAY)"],
        check=False, env={**os.environ, "JARVIS_SAY": text},
    )


def main() -> int:
    openwakeword.utils.download_models([WAKE_MODEL])
    wake = Model(wakeword_models=[WAKE_MODEL], inference_framework="onnx")
    whisper = WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")
    config = load_config()
    audio_q: "queue.Queue[np.ndarray]" = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_q.put(indata[:, 0].copy())

    print("Listening for 'Hey Jarvis'... (Ctrl+C to quit)")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=CHUNK, callback=on_audio):
        while True:
            scores = wake.predict(audio_q.get())
            if scores.get(WAKE_MODEL, 0) < WAKE_THRESHOLD:
                continue
            wake.reset()
            print("Jarvis: yes?")
            text = transcribe(whisper, record_command(audio_q))
            print(f"Heard: {text or '(nothing)'}")
            if text:
                speak(handle(f"{config['wake_words'][0]} {text}", config) or "Sorry, I missed that.")
            while not audio_q.empty():
                audio_q.get_nowait()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
