"""Voice loop. Text mode works with no extra deps; audio mode needs
openwakeword + sounddevice + faster-whisper (pip install them to enable)."""
import sys

from router import handle, load_config


def text_loop(config):
    print(f"Text mode. Say one of {config['wake_words']} then a command. Ctrl+C to quit.")
    for line in sys.stdin:
        reply = handle(line.strip(), config)
        if reply is not None:
            print(f"> {reply}")


def audio_loop(config):
    import numpy as np
    import sounddevice as sd
    from faster_whisper import WhisperModel
    from openwakeword.model import Model

    rate, chunk, listen_seconds = 16000, 1280, 5
    wake = Model(wakeword_models=["hey_jarvis"])  # stock model; swap for a custom "hey axiom" model
    stt = WhisperModel("base.en", compute_type="int8")
    print("Listening. Say the wake word, then your command.")
    with sd.InputStream(samplerate=rate, channels=1, dtype="int16", blocksize=chunk) as stream:
        while True:
            frame, _ = stream.read(chunk)
            if max(wake.predict(frame[:, 0]).values()) < 0.5:
                continue
            audio, _ = stream.read(rate * listen_seconds)
            segments, _ = stt.transcribe(audio[:, 0].astype(np.float32) / 32768.0)
            command = " ".join(s.text for s in segments).strip()
            reply = handle(f"{config['wake_words'][0]} {command}", config)
            print(f"> {command!r} -> {reply}")
            wake.reset()


def main():
    config = load_config()
    if "--audio" in sys.argv:
        audio_loop(config)
    else:
        text_loop(config)


if __name__ == "__main__":
    main()
