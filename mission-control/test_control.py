import unittest
from unittest import mock

import control

SITES = {"EverythingInternet.ca": {"live": "https://everythinginternet.ca", "staging": "https://1248767.us8.myftpupload.com"},
         "alangooding.ca": {"live": "https://alangooding.ca", "staging": None}}
TOKEN = "tok"
GOOD = {"site": "EverythingInternet.ca", "view": "staging", "prompt": "change the hero text", "token": TOKEN}


class ValidateTests(unittest.TestCase):
    def check(self, payload, host="127.0.0.1:8765", origin=None):
        return control.validate_request(payload, TOKEN, SITES, host, origin)

    def test_accepts_good_staging_request(self):
        self.assertIsNone(self.check(GOOD))

    def test_rejects_bad_token(self):
        self.assertIn("token", self.check({**GOOD, "token": "nope"}))

    def test_rejects_foreign_host_header(self):
        self.assertIn("host", self.check(GOOD, host="evil.com"))

    def test_rejects_foreign_origin(self):
        self.assertIn("origin", self.check(GOOD, origin="http://evil.com"))

    def test_accepts_same_origin(self):
        self.assertIsNone(self.check(GOOD, origin="http://127.0.0.1:8765"))

    def test_rejects_unknown_site(self):
        self.assertIn("site", self.check({**GOOD, "site": "other.com"}))

    def test_rejects_empty_or_huge_prompt(self):
        self.assertIn("prompt", self.check({**GOOD, "prompt": "  "}))
        self.assertIn("prompt", self.check({**GOOD, "prompt": "x" * 5000}))

    def test_live_requires_explicit_confirmation(self):
        self.assertIn("confirm", self.check({**GOOD, "view": "live"}))
        self.assertIsNone(self.check({**GOOD, "view": "live", "confirm_live": True}))

    def test_site_without_staging_cannot_use_staging(self):
        self.assertIn("staging", self.check({**GOOD, "site": "alangooding.ca"}))

    def test_rejects_non_dict_payload(self):
        self.assertIn("payload", self.check(["x"]))


class PromptTests(unittest.TestCase):
    def test_prompt_names_site_view_url_and_staging_rule(self):
        p = control.build_prompt(SITES["EverythingInternet.ca"], "EverythingInternet.ca", "staging", "do x")
        self.assertIn("EverythingInternet.ca", p)
        self.assertIn("1248767", p)
        self.assertIn("do x", p)

    def test_live_prompt_states_confirmed(self):
        p = control.build_prompt(SITES["EverythingInternet.ca"], "EverythingInternet.ca", "live", "do x")
        self.assertIn("confirmed", p.lower())


class RunTests(unittest.TestCase):
    def test_run_claude_sends_prompt_on_stdin(self):
        done = mock.Mock(returncode=0, stdout="done\n", stderr="")
        with mock.patch("control.subprocess.run", return_value=done) as run:
            self.assertEqual(control.run_claude("hello --flag"), (True, "done"))
        self.assertEqual(run.call_args.kwargs["input"], "hello --flag")
        self.assertNotIn("hello --flag", run.call_args.args[0])

    def test_run_claude_failure_is_a_fixed_message(self):
        with mock.patch("control.subprocess.run", side_effect=FileNotFoundError("C:/secret/path")):
            ok, msg = control.run_claude("hi")
        self.assertFalse(ok)
        self.assertNotIn("secret", msg)


class GuardTests(unittest.TestCase):
    def check(self, host="127.0.0.1:8765", origin=None, token=TOKEN):
        return control.guard(host, origin, token, TOKEN)

    def test_accepts_valid(self):
        self.assertIsNone(self.check())

    def test_rejects_bad_token_host_and_origin(self):
        self.assertIn("token", self.check(token="x"))
        self.assertIn("host", self.check(host="evil.com"))
        self.assertIn("origin", self.check(origin="http://evil.com"))

    def test_missing_token_is_rejected(self):
        self.assertIn("token", self.check(token=None))


class FakePoster:
    def __init__(self, configured=True):
        self._configured = configured
        self.published, self.deleted = [], []

    def configured(self, platform):
        return self._configured

    def publish(self, platform, text):
        self.published.append((platform, text))
        return {"post_id": "1_2"}

    def delete(self, platform, post_id):
        self.deleted.append((platform, post_id))


class AppPostTests(unittest.TestCase):
    def make_app(self, poster=None):
        import tempfile
        from pathlib import Path
        from store import Store
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return control.App(TOKEN, SITES, Store(Path(tmp.name)), mock.Mock(), poster or FakePoster())

    def test_post_publishes_logs_and_returns_flags(self):
        app = self.make_app()
        out = app.post({"platform": "facebook", "text": "Hello world"})
        self.assertEqual(app.poster.published, [("facebook", "Hello world")])
        self.assertEqual(out["post"]["post_id"], "1_2")
        self.assertTrue(out["flags"])  # no email / site
        self.assertEqual(len(app.store.posts()), 1)

    def test_post_validation_error_is_value_error(self):
        with self.assertRaises(ValueError):
            self.make_app().post({"platform": "facebook", "text": "  "})

    def test_post_when_not_configured_is_value_error_and_logs_nothing(self):
        app = self.make_app(FakePoster(configured=False))
        with self.assertRaises(ValueError):
            app.post({"platform": "facebook", "text": "hi"})
        self.assertEqual(app.store.posts(), [])

    def test_duplicate_within_window_is_refused(self):
        app = self.make_app()
        app.post({"platform": "facebook", "text": "Same"})
        with self.assertRaises(ValueError):
            app.post({"platform": "facebook", "text": "same "})
        self.assertEqual(len(app.poster.published), 1)

    def test_undo_deletes_remote_and_marks_record(self):
        app = self.make_app()
        rec = app.post({"platform": "facebook", "text": "Oops"})["post"]
        app.undo({"id": rec["id"]})
        self.assertEqual(app.poster.deleted, [("facebook", "1_2")])
        self.assertTrue(app.store.posts()[0]["deleted"])

    def test_undo_unknown_id_is_key_error(self):
        with self.assertRaises(KeyError):
            self.make_app().undo({"id": "nope"})

    def test_preflight_returns_flags_without_posting(self):
        app = self.make_app()
        out = app.preflight({"platform": "facebook", "text": "hi"})
        self.assertTrue(out["flags"])
        self.assertEqual(app.poster.published, [])


class AppSayTests(unittest.TestCase):
    def test_say_rejects_blank_and_overlong_text(self):
        import tempfile
        from pathlib import Path
        from store import Store
        with tempfile.TemporaryDirectory() as tmp:
            app = control.App(TOKEN, SITES, Store(Path(tmp)), mock.Mock(), FakePoster())
            with self.assertRaises(ValueError):
                app.say({"text": " "})
            with self.assertRaises(ValueError):
                app.say({"text": "x" * 1000})

    def test_say_returns_router_reply(self):
        import tempfile
        from pathlib import Path
        from store import Store
        with tempfile.TemporaryDirectory() as tmp:
            app = control.App(TOKEN, SITES, Store(Path(tmp)), mock.Mock(), FakePoster())
            with mock.patch("control.voice_reply", return_value="Voice router online."):
                self.assertEqual(app.say({"text": "status"}), {"reply": "Voice router online."})

class CouncilTests(unittest.TestCase):
    def make_app(self):
        import tempfile
        from pathlib import Path
        from store import Store
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return control.App(TOKEN, SITES, Store(Path(tmp.name)), mock.Mock(), FakePoster())

    def test_ask_then_info_lists_question_with_suggested_reviewer(self):
        app = self.make_app()
        app.council_ask({"question": "Is the checkout safe?", "asked_by": "Alan", "topic": "engineering"})
        info = app.council_info()
        self.assertEqual(info["questions"][0]["reviewer"], "/plan-eng-review")
        self.assertTrue(info["asked_today"])

    def test_package_contains_question_context_and_reply_format(self):
        q = {"question": "Raise price?", "asked_by": "Alan", "topic": "strategy"}
        pkg = control.build_council_package(q)
        self.assertIn("Raise price?", pkg)
        self.assertIn("VERDICT", pkg)

    def test_ecc_answer_is_stored_with_source(self):
        app = self.make_app()
        q = app.council_ask({"question": "Raise price?", "asked_by": "Alan", "topic": "strategy"})["question"]
        with mock.patch("control.run_claude", return_value=(True, "Hold at $499.")):
            out = app.council_ecc({"id": q["id"]})
        self.assertEqual(out["question"]["answer"], "Hold at $499.")
        self.assertEqual(out["question"]["answer_source"], "ECC")

    def test_ecc_failure_is_value_error_and_leaves_question_open(self):
        app = self.make_app()
        q = app.council_ask({"question": "x?", "asked_by": "Alan", "topic": "general"})["question"]
        with mock.patch("control.run_claude", return_value=(False, "Claude could not be run.")):
            with self.assertRaises(ValueError):
                app.council_ecc({"id": q["id"]})
        self.assertEqual(app.store.questions()[0]["status"], "open")

    def test_manual_answer_recorded(self):
        app = self.make_app()
        q = app.council_ask({"question": "x?", "asked_by": "Axiom", "topic": "general"})["question"]
        app.council_answer({"id": q["id"], "answer": "Do it.", "source": "GPT"})
        self.assertEqual(app.store.questions()[0]["answer_source"], "GPT")

class NextActionAppTests(unittest.TestCase):
    def make_app(self, git=None):
        import tempfile
        from pathlib import Path
        from store import Store
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        app = control.App(TOKEN, SITES, Store(Path(tmp.name)), mock.Mock(), FakePoster())
        app.voice.running.return_value = False
        return app

    def patched(self):
        return mock.patch.multiple(
            "control.status",
            check_all_sites=mock.Mock(return_value={"EverythingInternet.ca": {"live": {"up": True}, "staging": {"up": True}},
                                                    "alangooding.ca": {"live": {"up": True}}}),
            git_summary=mock.Mock(return_value={"uncommitted": 0, "unpushed": 0}),
        )

    def test_first_action_today_is_council_checkin(self):
        with self.patched():
            out = self.make_app().next_plan()
        self.assertEqual(out["now"]["id"], "council-checkin")

    def test_done_advances_to_next_action(self):
        app = self.make_app()
        with self.patched():
            app.council_dismiss({})
            self.assertEqual(app.next_plan()["now"]["id"], "pay-link")
            app.next_done({"id": "pay-link"})
            self.assertEqual(app.next_plan()["now"]["id"], "test-purchase")

    def test_skip_snoozes_the_action(self):
        app = self.make_app()
        with self.patched():
            app.next_skip({"id": "council-checkin"})
            self.assertNotEqual(app.next_plan()["now"]["id"], "council-checkin")

    def test_down_site_is_reported(self):
        app = self.make_app()
        down = {"EverythingInternet.ca": {"live": {"up": False}, "staging": {"up": True}}}
        with mock.patch("control.status.check_all_sites", return_value=down),                 mock.patch("control.status.git_summary", return_value={"uncommitted": 0, "unpushed": 0}):
            app.council_dismiss({})
            self.assertEqual(app.next_plan()["now"]["id"], "site-down")

    def test_doubt_creates_council_question_prefilled(self):
        app = self.make_app()
        with self.patched():
            out = app.next_doubt({"id": "pay-link"})
        self.assertIn("Stripe Payment Link", out["draft"])

class RouteProgressTests(unittest.TestCase):
    def test_route_progress_counts_delivered_stops(self):
        import tempfile
        from pathlib import Path
        from store import Store
        with tempfile.TemporaryDirectory() as tmp:
            app = control.App(TOKEN, SITES, Store(Path(tmp)), mock.Mock(), FakePoster())
            app.voice.running.return_value = False
            ok_sites = {"EverythingInternet.ca": {"live": {"up": True}, "staging": {"up": True}}}
            git = {"uncommitted": 0, "unpushed": 0}
            with mock.patch("control.status.check_all_sites", return_value=ok_sites),                     mock.patch("control.status.git_summary", return_value=git):
                first = app.next_plan()
                self.assertEqual((first["stop_number"], first["delivered"]), (1, []))
                total = first["total_stops"]
                app.council_dismiss({})  # delivers the council check-in stop
                second = app.next_plan()
                self.assertEqual(second["stop_number"], 2)
                self.assertEqual(second["delivered"][0]["title"], "Daily council check-in")
                self.assertEqual(second["total_stops"], total)

class MultiPostTests(unittest.TestCase):
    def make_app(self, poster=None):
        import tempfile
        from pathlib import Path
        from store import Store
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return control.App(TOKEN, SITES, Store(Path(tmp.name)), mock.Mock(), poster or FakePoster())

    def test_posts_to_every_checked_platform_and_reports_each(self):
        app = self.make_app()
        with mock.patch("control.posting.PLATFORMS", {**control.posting.PLATFORMS, "threads": ("Threads", True, "")}):
            out = app.post_multi({"platforms": ["facebook", "threads"], "text": "Hello"})
        self.assertEqual([(r["platform"], r["ok"]) for r in out["results"]], [("facebook", True), ("threads", True)])
        self.assertEqual(len(app.store.posts()), 2)

    def test_one_platform_failing_does_not_stop_the_others(self):
        class Flaky(FakePoster):
            def publish(self, platform, text):
                if platform == "facebook":
                    raise control.posting.PostingError("Facebook is down")
                return super().publish(platform, text)

        app = self.make_app(Flaky())
        with mock.patch("control.posting.PLATFORMS", {**control.posting.PLATFORMS, "threads": ("Threads", True, "")}):
            out = app.post_multi({"platforms": ["facebook", "threads"], "text": "Hello"})
        by = {r["platform"]: r for r in out["results"]}
        self.assertFalse(by["facebook"]["ok"])
        self.assertIn("down", by["facebook"]["error"])
        self.assertTrue(by["threads"]["ok"])

    def test_no_platforms_checked_is_an_error(self):
        with self.assertRaises(ValueError):
            self.make_app().post_multi({"platforms": [], "text": "Hello"})

    def test_blank_text_is_an_error_before_anything_is_sent(self):
        app = self.make_app()
        with self.assertRaises(ValueError):
            app.post_multi({"platforms": ["facebook"], "text": "  "})
        self.assertEqual(app.poster.published, [])

    def test_duplicate_platforms_are_posted_once(self):
        app = self.make_app()
        app.post_multi({"platforms": ["facebook", "facebook"], "text": "Once"})
        self.assertEqual(len(app.poster.published), 1)

    def test_legacy_single_platform_field_still_works(self):
        app = self.make_app()
        out = app.post_multi({"platform": "facebook", "text": "Legacy"})
        self.assertTrue(out["results"][0]["ok"])


if __name__ == "__main__":
    unittest.main()
