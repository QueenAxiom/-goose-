"""Start/stop the Jarvis voice assistant from Mission Control."""
import logging
import subprocess
import sys
import threading
from pathlib import Path

log = logging.getLogger("mission-control.voice")

VOICE_DIR = Path(__file__).resolve().parent.parent / "voice"
STOP_WAIT_SECONDS = 5


class VoiceProcess:
    def __init__(self, popen=subprocess.Popen):
        self._popen = popen
        self._proc = None
        self._lock = threading.Lock()

    def running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def start(self) -> bool:
        """Launch Jarvis. Returns False if it was already running or failed to start."""
        with self._lock:
            if self.running():
                return False
            try:
                self._proc = self._popen([sys.executable, "jarvis.py"], cwd=VOICE_DIR)
            except OSError:
                log.exception("could not start jarvis")
                self._proc = None
                return False
            return True

    def stop(self) -> bool:
        with self._lock:
            if not self.running():
                return False
            self._proc.terminate()
            try:
                self._proc.wait(timeout=STOP_WAIT_SECONDS)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            return True
