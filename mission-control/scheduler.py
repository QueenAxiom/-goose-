"""Promotion scheduler: drains the post queue on a steady clock, per-platform caps, auto-pause on throttling."""
import logging
import threading
import time
from datetime import datetime, timedelta, timezone

import posting

log = logging.getLogger("mission-control.scheduler")

SECONDS_PER_DAY = 86400
TICK_SECONDS = 20
MAX_ATTEMPTS = 3
RATE_LIMIT_PAUSE = timedelta(minutes=60)


def plan_schedule(count: int, start: datetime, per_day: int) -> list:
    """Evenly spaced due-times for `count` posts at `per_day` posts per day."""
    if per_day <= 0:
        raise ValueError("per_day must be positive")
    interval = SECONDS_PER_DAY / per_day
    return [start + timedelta(seconds=interval * i) for i in range(count)]


def _is_today(iso: str, now: datetime) -> bool:
    return bool(iso) and datetime.fromisoformat(iso).date() == now.date()


class Scheduler:
    def __init__(self, store, poster):
        self._store, self._poster = store, poster
        self._paused_until: dict = {}
        self._lock = threading.Lock()

    def paused_until(self, platform: str) -> "datetime | None":
        return self._paused_until.get(platform)

    def _posted_today(self, platform: str, now: datetime) -> int:
        return sum(q["status"] == "posted" and q["platform"] == platform and _is_today(q["posted_at"], now)
                   for q in self._store.queue())

    def _due(self, now: datetime) -> dict:
        """Earliest due queued item per platform."""
        first: dict = {}
        for item in sorted(self._store.queue(), key=lambda q: q["due"]):
            if item["status"] == "queued" and datetime.fromisoformat(item["due"]) <= now:
                first.setdefault(item["platform"], item)
        return first

    def tick(self, now: "datetime | None" = None) -> int:
        """Post at most one item per platform. Returns how many went out."""
        now = now or datetime.now(timezone.utc)
        settings = self._store.settings()
        if settings["paused"]:
            return 0
        sent = 0
        with self._lock:
            for platform, item in self._due(now).items():
                if not self._poster.configured(platform):
                    continue
                pause = self._paused_until.get(platform)
                if pause and now < pause:
                    continue
                if self._posted_today(platform, now) >= settings["daily_cap"]:
                    continue
                sent += self._send(platform, item, now)
        return sent

    def _send(self, platform: str, item: dict, now: datetime) -> int:
        try:
            result = self._poster.publish(platform, item["text"])
        except posting.PostingError as exc:
            if exc.rate_limited:
                self._paused_until[platform] = now + RATE_LIMIT_PAUSE
                log.warning("%s throttled; pausing until %s", platform, self._paused_until[platform])
                return 0
            attempts = item["attempts"] + 1
            failed = attempts >= MAX_ATTEMPTS
            self._store.update_queue_item(item["id"], {"attempts": attempts, "error": str(exc),
                                                       "status": "failed" if failed else "queued"})
            log.warning("%s post failed (%d/%d): %s", platform, attempts, MAX_ATTEMPTS, exc)
            return 0
        self._store.update_queue_item(item["id"], {"status": "posted", "post_id": result["post_id"], "posted_at": now.isoformat()})
        self._store.add_post({"platform": platform, "text": item["text"], "post_id": result["post_id"]})
        return 1

    def run_forever(self, stop: threading.Event) -> None:
        while not stop.is_set():
            try:
                self.tick()
            except Exception:  # keep the loop alive; one bad tick must not end promotion
                log.exception("scheduler tick crashed")
            stop.wait(TICK_SECONDS)
