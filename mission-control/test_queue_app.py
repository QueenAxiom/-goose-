import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import control
import scheduler
from store import Store

SITES = {"EverythingInternet.ca": {"live": "https://everythinginternet.ca", "staging": None}}


class FakePoster:
    def configured(self, platform):
        return True

    def publish(self, platform, text):
        return {"post_id": "1_1"}


@unittest.skip("Queue wiring is paused until Alan has read the platform rules (docs/platform-compliance.md)")
class QueueAppTests(unittest.TestCase):
    def make_app(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = Store(Path(tmp.name))
        poster = FakePoster()
        return control.App("tok", SITES, store, mock.Mock(), poster, scheduler.Scheduler(store, poster))

    def test_add_splits_blocks_and_queues_each_text_for_each_platform(self):
        app = self.make_app()
        with mock.patch("control.posting.PLATFORMS", {**control.posting.PLATFORMS, "threads": ("Threads", True, "")}):
            out = app.queue_add({"platforms": ["facebook", "threads"], "text": "One\n\nTwo\n\nThree", "per_day": 750})
        self.assertEqual(out["queued"], 6)
        self.assertEqual(len(app.store.queue()), 6)

    def test_add_spaces_posts_by_rate(self):
        app = self.make_app()
        app.queue_add({"platforms": ["facebook"], "text": "A\n\nB", "per_day": 24})
        a, b = (datetime.fromisoformat(q["due"]) for q in app.store.queue())
        self.assertAlmostEqual((b - a).total_seconds(), 3600, places=0)

    def test_add_rejects_empty_unticked_unavailable_and_bad_rate(self):
        app = self.make_app()
        for body in (
            {"platforms": [], "text": "A", "per_day": 10},
            {"platforms": ["facebook"], "text": "  \n\n  ", "per_day": 10},
            {"platforms": ["linkedin"], "text": "A", "per_day": 10},
            {"platforms": ["facebook"], "text": "A", "per_day": 0},
        ):
            with self.subTest(body=body), self.assertRaises(ValueError):
                app.queue_add(body)

    def test_add_caps_batch_size(self):
        app = self.make_app()
        text = "\n\n".join(["x"] * (control.MAX_QUEUE_BATCH + 1))
        with self.assertRaises(ValueError):
            app.queue_add({"platforms": ["facebook"], "text": text, "per_day": 10})

    def test_info_reports_counts_settings_and_posted_today(self):
        app = self.make_app()
        app.queue_add({"platforms": ["facebook"], "text": "A\n\nB", "per_day": 10})
        info = app.queue_info()
        self.assertEqual(info["counts"]["queued"], 2)
        self.assertFalse(info["settings"]["paused"])
        self.assertIn("facebook", info["posted_today"])

    def test_settings_pause_and_cap(self):
        out = self.make_app().queue_settings({"paused": True, "daily_cap": 100})
        self.assertEqual((out["settings"]["paused"], out["settings"]["daily_cap"]), (True, 100))

    def test_cancel_and_clear(self):
        app = self.make_app()
        app.queue_add({"platforms": ["facebook"], "text": "A\n\nB", "per_day": 10})
        app.queue_cancel({"id": app.store.queue()[0]["id"]})
        self.assertEqual(app.store.queue()[0]["status"], "cancelled")
        self.assertEqual(app.queue_clear({})["removed"], 1)


if __name__ == "__main__":
    unittest.main()
