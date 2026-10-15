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


if __name__ == "__main__":
    unittest.main()
