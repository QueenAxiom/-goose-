import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import posting
import scheduler
from store import Store

NOW = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)


class FakePoster:
    def __init__(self, fail_with=None):
        self.published, self.fail_with = [], fail_with

    def configured(self, platform):
        return True

    def publish(self, platform, text):
        if self.fail_with:
            raise self.fail_with
        self.published.append((platform, text))
        return {"post_id": f"1_{len(self.published)}"}


class PlanScheduleTests(unittest.TestCase):
    def test_spreads_items_evenly_across_the_day(self):
        times = scheduler.plan_schedule(4, NOW, per_day=24)  # one per hour
        self.assertEqual([t - NOW for t in times], [timedelta(hours=h) for h in range(4)])

    def test_750_a_day_is_about_one_every_115_seconds(self):
        times = scheduler.plan_schedule(3, NOW, per_day=750)
        self.assertAlmostEqual((times[1] - times[0]).total_seconds(), 86400 / 750, places=3)

    def test_rejects_non_positive_rate(self):
        with self.assertRaises(ValueError):
            scheduler.plan_schedule(3, NOW, per_day=0)


class QueueStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = Store(Path(self._tmp.name))

    def test_enqueue_many_creates_queued_items(self):
        items = self.store.enqueue_many([("facebook", "A", NOW.isoformat()), ("facebook", "B", NOW.isoformat())])
        self.assertEqual([i["status"] for i in items], ["queued", "queued"])
        self.assertEqual(len(self.store.queue()), 2)

    def test_enqueue_rejects_blank_text(self):
        with self.assertRaises(ValueError):
            self.store.enqueue_many([("facebook", "  ", NOW.isoformat())])

    def test_settings_default_and_update(self):
        self.assertFalse(self.store.settings()["paused"])
        self.store.update_settings({"paused": True, "daily_cap": 750})
        s = self.store.settings()
        self.assertEqual((s["paused"], s["daily_cap"]), (True, 750))

    def test_settings_reject_bad_values(self):
        with self.assertRaises(ValueError):
            self.store.update_settings({"daily_cap": -5})
        with self.assertRaises(ValueError):
            self.store.update_settings({"daily_cap": "lots"})

    def test_cancel_marks_item_cancelled(self):
        item = self.store.enqueue_many([("facebook", "A", NOW.isoformat())])[0]
        self.store.update_queue_item(item["id"], {"status": "cancelled"})
        self.assertEqual(self.store.queue()[0]["status"], "cancelled")


class TickTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = Store(Path(self._tmp.name))

    def queue(self, n, due=NOW - timedelta(minutes=1), platform="facebook"):
        return self.store.enqueue_many([(platform, f"post {i}", due.isoformat()) for i in range(n)])

    def test_posts_due_items_and_logs_history_for_undo(self):
        self.queue(1)
        poster = FakePoster()
        scheduler.Scheduler(self.store, poster).tick(NOW)
        self.assertEqual(poster.published, [("facebook", "post 0")])
        self.assertEqual(self.store.queue()[0]["status"], "posted")
        self.assertEqual(len(self.store.posts()), 1)

    def test_future_items_wait(self):
        self.queue(1, due=NOW + timedelta(hours=1))
        poster = FakePoster()
        scheduler.Scheduler(self.store, poster).tick(NOW)
        self.assertEqual(poster.published, [])

    def test_only_one_post_per_platform_per_tick(self):
        self.queue(3)
        poster = FakePoster()
        scheduler.Scheduler(self.store, poster).tick(NOW)
        self.assertEqual(len(poster.published), 1)

    def test_kill_switch_stops_everything(self):
        self.queue(1)
        self.store.update_settings({"paused": True})
        poster = FakePoster()
        scheduler.Scheduler(self.store, poster).tick(NOW)
        self.assertEqual(poster.published, [])

    def test_daily_cap_is_respected(self):
        self.store.update_settings({"daily_cap": 2})
        self.queue(5)
        poster = FakePoster()
        sched = scheduler.Scheduler(self.store, poster)
        for i in range(5):
            sched.tick(NOW + timedelta(seconds=i))
        self.assertEqual(len(poster.published), 2)

    def test_rate_limit_pauses_that_platform_and_keeps_item_queued(self):
        self.queue(2)
        poster = FakePoster(fail_with=posting.PostingError("slow down", rate_limited=True))
        sched = scheduler.Scheduler(self.store, poster)
        sched.tick(NOW)
        self.assertEqual([i["status"] for i in self.store.queue()], ["queued", "queued"])
        self.assertIsNotNone(sched.paused_until("facebook"))
        poster.fail_with = None
        sched.tick(NOW + timedelta(minutes=5))  # still inside the pause
        self.assertEqual(poster.published, [])
        sched.tick(NOW + scheduler.RATE_LIMIT_PAUSE + timedelta(minutes=1))
        self.assertEqual(len(poster.published), 1)

    def test_repeated_errors_fail_the_item_and_move_on(self):
        self.queue(2)
        poster = FakePoster(fail_with=posting.PostingError("bad token"))
        sched = scheduler.Scheduler(self.store, poster)
        for i in range(scheduler.MAX_ATTEMPTS):
            sched.tick(NOW + timedelta(seconds=i))
        statuses = [i["status"] for i in self.store.queue()]
        self.assertEqual(statuses[0], "failed")
        self.assertIn("bad token", self.store.queue()[0]["error"])

    def test_unconfigured_platform_is_left_alone(self):
        self.queue(1)
        poster = FakePoster()
        poster.configured = lambda platform: False
        scheduler.Scheduler(self.store, poster).tick(NOW)
        self.assertEqual(self.store.queue()[0]["status"], "queued")


class RateLimitDetectionTests(unittest.TestCase):
    def test_graph_rate_limit_codes_are_flagged(self):
        from unittest import mock
        resp = mock.Mock(status_code=400, json=lambda: {"error": {"message": "Too many calls", "code": 4}})
        with mock.patch("posting.requests.post", return_value=resp):
            with self.assertRaises(posting.PostingError) as ctx:
                posting.Poster(env={"MC_FB_PAGE_ID": "1", "MC_FB_PAGE_TOKEN": "t"}).publish("facebook", "x")
        self.assertTrue(ctx.exception.rate_limited)


if __name__ == "__main__":
    unittest.main()
