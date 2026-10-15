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
import threading
import winsound
from collections import deque

import numpy as np
import openwakeword
import requests
import sounddevice as sd
from faster_whisper import WhisperModel
from openwakeword.model import Model

from endpointing import Endpointer, noise_floor, threshold_for
from router import handle_stream, load_config

WAKE_MODEL = "hey_jarvis"
WAKE_THRESHOLD = 0.5
SAMPLE_RATE = 16000
CHUNK = 1280  # 80 ms, the frame size openWakeWord expects
END_QUIET_CHUNKS = 10  # ~0.8 s of quiet after speech ends the command
ONSET_LIMIT_CHUNKS = 50  # ~4 s to start speaking after the wake word before giving up
MAX_CHUNKS = 150  # ~12 s hard cap on one command
NOISE_WINDOW_CHUNKS = 62  # ~5 s of recent audio used to judge room noise
BEEP_HZ, BEEP_MS = 880, 120
WHISPER_SIZE = "base.en"
LOCAL_WARMUP_TIMEOUT_SECONDS = 180


def chunk_rms(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))


def record_command(audio_q: "queue.Queue[np.ndarray]", threshold: float) -> np.ndarray:
    """Record until the speaker finishes, using a threshold tuned to the room's noise."""
    ep = Endpointer(threshold, END_QUIET_CHUNKS, ONSET_LIMIT_CHUNKS, MAX_CHUNKS)
    chunks = []
    while True:
        chunk = audio_q.get()
        chunks.append(chunk)
        if ep.feed(chunk_rms(chunk)) == "done":
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


def warm_local_model(config: dict) -> None:
    """Fire one tiny request at startup so the first real answer isn't a cold start."""
    try:
        requests.post(config["local_model_url"], timeout=LOCAL_WARMUP_TIMEOUT_SECONDS,
                      json={"model": config["local_model"], "max_tokens": 1,
                            "messages": [{"role": "user", "content": "hi"}]})
    except requests.RequestException:
        pass


def main() -> int:
    openwakeword.utils.download_models([WAKE_MODEL])
    wake = Model(wakeword_models=[WAKE_MODEL], inference_framework="onnx")
    whisper = WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")
    config = load_config()
    threading.Thread(target=warm_local_model, args=(config,), daemon=True).start()
    audio_q: "queue.Queue[np.ndarray]" = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_q.put(indata[:, 0].copy())

    print("Listening for 'Hey Jarvis'... (Ctrl+C to quit)")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=CHUNK, callback=on_audio):
        recent_rms: "deque[float]" = deque(maxlen=NOISE_WINDOW_CHUNKS)
        while True:
            chunk = audio_q.get()
            recent_rms.append(chunk_rms(chunk))
            if wake.predict(chunk).get(WAKE_MODEL, 0) < WAKE_THRESHOLD:
                continue
            wake.reset()
            threshold = threshold_for(noise_floor(list(recent_rms)))
            winsound.Beep(BEEP_HZ, BEEP_MS)  # tells you it is listening
            while not audio_q.empty():
                audio_q.get_nowait()  # drop the beep and the wake phrase itself
            print(f"Jarvis: listening (speech threshold {threshold:.0f})")
            text = transcribe(whisper, record_command(audio_q, threshold))
            print(f"Heard: {text or '(nothing)'}")
            if text:
                # Speak each sentence as the model produces it; generation continues while we talk.
                for sentence in handle_stream(f"{config['wake_words'][0]} {text}", config):
                    speak(sentence)
            else:
                speak("Sorry, I didn't catch that.")
            while not audio_q.empty():
                audio_q.get_nowait()
            recent_rms.clear()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
