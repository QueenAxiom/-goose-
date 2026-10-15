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


if __name__ == "__main__":
    unittest.main()
