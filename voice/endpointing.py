"""Speech endpointing: decide when a spoken command starts and ends, adapting to room noise."""

MIN_THRESHOLD = 400  # loudness (RMS) below which nothing counts as speech, even in a silent room
NOISE_MARGIN = 2.5  # speech must be this many times louder than the room's noise floor
NOISE_PERCENTILE = 0.2  # the quiet fifth of recent audio approximates the noise floor


def noise_floor(recent_rms: list) -> float:
    """Estimate room noise from recent chunk loudness, ignoring speech-like bursts."""
    if not recent_rms:
        return 0
    ordered = sorted(recent_rms)
    return ordered[int(len(ordered) * NOISE_PERCENTILE)]


def threshold_for(floor: float) -> float:
    return max(MIN_THRESHOLD, floor * NOISE_MARGIN)


class Endpointer:
    """Feed one loudness value per audio chunk; it reports waiting, speaking or done.

    It waits through leading silence (up to onset_limit chunks), then ends after
    end_quiet quiet chunks following speech, or at max_chunks no matter what.
    """

    def __init__(self, threshold: float, end_quiet: int, onset_limit: int, max_chunks: int):
        self._threshold, self._end_quiet = threshold, end_quiet
        self._onset_limit, self._max_chunks = onset_limit, max_chunks
        self._count = 0
        self._quiet = 0
        self.heard_speech = False

    def feed(self, rms: float) -> str:
        self._count += 1
        loud = rms >= self._threshold
        if loud:
            self.heard_speech = True
            self._quiet = 0
        elif self.heard_speech:
            self._quiet += 1
        if self._count >= self._max_chunks:
            return "done"
        if not self.heard_speech:
            return "done" if self._count >= self._onset_limit else "waiting"
        return "done" if self._quiet >= self._end_quiet else "speaking"
