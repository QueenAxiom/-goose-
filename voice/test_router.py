import unittest
import json
import subprocess
import tempfile
from pathlib import Path
from unittest import mock

import requests

from router import (extract_command, route, Route, dispatch, load_config, sanitize_reply,
                    iter_sentences, handle_stream)

ROUTES = (
    Route(name="status", keywords=("status", "what's running"), action="reply", target="All systems nominal."),
    Route(name="backup", keywords=("backup", "back up"), action="webhook", target="http://localhost:5678/webhook/backup"),
)


class ExtractCommandTests(unittest.TestCase):
    def test_returns_command_after_wake_word(self):
        self.assertEqual(extract_command("Hey Axiom, run a backup", ("hey axiom",)), "run a backup")

    def test_returns_none_without_wake_word(self):
        self.assertIsNone(extract_command("run a backup", ("hey axiom",)))

    def test_wake_word_alone_returns_empty_string(self):
        self.assertEqual(extract_command("hey axiom", ("hey axiom",)), "")

    def test_ignores_wake_word_mid_sentence(self):
        self.assertIsNone(extract_command("ok so hey axiom status please", ("hey axiom",)))

    def test_ignores_wake_word_inside_another_word(self):
        self.assertIsNone(extract_command("jarvisson run a backup", ("jarvis",)))

    def test_longer_wake_word_listed_first_is_consumed_whole(self):
        self.assertEqual(extract_command("hey jarvis status", ("hey jarvis", "jarvis")), "status")


class RouteTests(unittest.TestCase):
    def test_matches_keyword(self):
        self.assertEqual(route("please back up the docs", ROUTES).name, "backup")

    def test_first_match_wins(self):
        self.assertEqual(route("status of backup", ROUTES).name, "status")

    def test_falls_back_to_local_model(self):
        r = route("tell me a joke", ROUTES)
        self.assertEqual((r.name, r.action), ("fallback", "local_model"))

    def test_empty_command_falls_back_to_reply(self):
        self.assertEqual(route("", ROUTES).action, "reply")

    def test_keyword_needs_word_boundary(self):
        self.assertEqual(route("statuses everywhere", ROUTES).name, "fallback")

    def test_ask_claude_beats_other_keywords(self):
        routes = (Route("claude", ("ask claude",), "claude"),) + ROUTES
        self.assertEqual(route("ask claude about the backup status", routes).name, "claude")


CFG = {"local_model_url": "http://127.0.0.1:8000/v1/chat/completions", "local_model": "m"}


class DispatchTests(unittest.TestCase):
    def test_webhook_sends_secret_and_blocks_redirects(self):
        with mock.patch.dict("os.environ", {"AXIOM_WEBHOOK_SECRET": "s3"}),                 mock.patch("router.requests.post") as post:
            dispatch(ROUTES[1], "backup", CFG)
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["headers"]["X-Axiom-Secret"], "s3")
        self.assertFalse(kwargs["allow_redirects"])

    def test_webhook_failure_does_not_leak_url(self):
        with mock.patch("router.requests.post", side_effect=requests.ConnectionError("http://secret/url")):
            reply = dispatch(ROUTES[1], "backup", CFG)
        self.assertNotIn("secret", reply)

    def test_empty_model_choices_do_not_crash(self):
        resp = mock.Mock(json=lambda: {"choices": []})
        with mock.patch("router.requests.post", return_value=resp):
            self.assertIn("failed", dispatch(Route("fallback", action="local_model"), "hi", CFG))

    def test_null_model_content_does_not_crash(self):
        resp = mock.Mock(json=lambda: {"choices": [{"message": {"content": None}}]})
        with mock.patch("router.requests.post", return_value=resp):
            self.assertIn("failed", dispatch(Route("fallback", action="local_model"), "hi", CFG))

    def test_claude_gets_prompt_on_stdin_not_argv(self):
        done = subprocess.CompletedProcess([], 0, stdout="ok\n")
        with mock.patch("router.subprocess.run", return_value=done) as run:
            self.assertEqual(dispatch(Route("claude", action="claude"), "--evil", CFG), "ok")
        self.assertNotIn("--evil", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["input"], "--evil")

    def test_missing_claude_binary_does_not_crash(self):
        with mock.patch("router.subprocess.run", side_effect=FileNotFoundError):
            self.assertIn("failed", dispatch(Route("claude", action="claude"), "hi", CFG))


class SanitizeTests(unittest.TestCase):
    def test_strips_control_and_ansi_and_caps_length(self):
        out = sanitize_reply("hi[31m red" + "x" * 2000)
        self.assertNotIn("", out)
        self.assertNotIn("", out)
        self.assertLessEqual(len(out), 600)


class LoadConfigTests(unittest.TestCase):
    def _load(self, data):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            return load_config(p)

    def test_rejects_unknown_action(self):
        bad = {"wake_words": ["x"], "local_model_url": CFG["local_model_url"], "local_model": "m",
               "routes": [{"name": "a", "keywords": ["a"], "action": "rm_rf"}]}
        with self.assertRaises(ValueError):
            self._load(bad)

    def test_rejects_non_local_webhook(self):
        bad = {"wake_words": ["x"], "local_model_url": CFG["local_model_url"], "local_model": "m",
               "routes": [{"name": "a", "keywords": ["a"], "action": "webhook", "target": "http://169.254.169.254/"}]}
        with self.assertRaises(ValueError):
            self._load(bad)

    def test_rejects_empty_wake_words(self):
        with self.assertRaises(ValueError):
            self._load({"wake_words": [], "local_model_url": CFG["local_model_url"], "local_model": "m", "routes": []})

    def test_shipped_config_is_valid(self):
        self.assertTrue(load_config()["routes"])


class StreamingTests(unittest.TestCase):
    def test_iter_sentences_yields_each_sentence_as_it_completes(self):
        tokens = ["Hello", " there.", " How", " are", " you?", " Fine"]
        self.assertEqual(list(iter_sentences(iter(tokens))), ["Hello there.", "How are you?", "Fine"])

    def _stream_response(self, tokens):
        lines = [("data: " + json.dumps({"choices": [{"delta": {"content": t}}]})).encode() for t in tokens]
        lines += [b"", b"data: [DONE]"]
        return mock.MagicMock(iter_lines=lambda: iter(lines), __enter__=lambda s: s, __exit__=lambda *a: False)

    def test_handle_stream_speaks_model_sentences_incrementally(self):
        cfg = {**CFG, "wake_words": ("jarvis",), "routes": ()}
        with mock.patch("router.requests.post", return_value=self._stream_response(["Hi.", " Bye."])):
            self.assertEqual(list(handle_stream("jarvis tell me something", cfg)), ["Hi.", "Bye."])

    def test_handle_stream_yields_nothing_without_wake_word(self):
        cfg = {**CFG, "wake_words": ("jarvis",), "routes": ROUTES}
        self.assertEqual(list(handle_stream("status", cfg)), [])

    def test_handle_stream_non_model_route_yields_single_reply(self):
        cfg = {**CFG, "wake_words": ("jarvis",), "routes": ROUTES}
        self.assertEqual(list(handle_stream("jarvis status", cfg)), ["All systems nominal."])

    def test_handle_stream_model_failure_yields_fixed_message(self):
        cfg = {**CFG, "wake_words": ("jarvis",), "routes": ()}
        with mock.patch("router.requests.post", side_effect=requests.ConnectionError("http://secret")):
            out = list(handle_stream("jarvis hi", cfg))
        self.assertEqual(out, ["fallback failed."])

class FallbackActionTests(unittest.TestCase):
    def test_route_uses_configured_fallback_action(self):
        r = route("tell me anything", ROUTES, fallback_action="claude")
        self.assertEqual((r.name, r.action), ("fallback", "claude"))

    def test_default_fallback_stays_local_model(self):
        self.assertEqual(route("tell me anything", ROUTES).action, "local_model")

    def test_handle_stream_routes_free_speech_to_claude_when_configured(self):
        cfg = {**CFG, "wake_words": ("jarvis",), "routes": ROUTES, "fallback_action": "claude"}
        done = subprocess.CompletedProcess([], 0, stdout="Sure thing.\n")
        with mock.patch("router.subprocess.run", return_value=done):
            self.assertEqual(list(handle_stream("jarvis what should I do today", cfg)), ["Sure thing."])

    def _load(self, fallback):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps({"wake_words": ["x"], "local_model_url": CFG["local_model_url"], "local_model": "m",
                                     "fallback_action": fallback, "routes": []}), encoding="utf-8")
            return load_config(p)

    def test_load_config_accepts_claude_fallback(self):
        self.assertEqual(self._load("claude")["fallback_action"], "claude")

    def test_load_config_rejects_dangerous_fallback(self):
        with self.assertRaises(ValueError):
            self._load("webhook")


if __name__ == "__main__":
    unittest.main()
