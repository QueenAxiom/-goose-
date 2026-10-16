import tempfile
import unittest
from pathlib import Path
from unittest import mock

import control
import convlog
from store import Store

SITES = {"EverythingInternet.ca": {"live": "https://everythinginternet.ca", "staging": None}}


class FakePoster:
    def configured(self, platform):
        return True


class ConvLogTests(unittest.TestCase):
    def test_appends_redacted_turns_to_a_monthly_file(self):
        with tempfile.TemporaryDirectory() as d:
            convlog.log_turn(Path(d), "ecc", "user", "my key is sk-ant-api03-ABCDEFGH12345678")
            convlog.log_turn(Path(d), "ecc", "assistant", "noted")
            [f] = list(Path(d).glob("mission-control-chats-*.md"))
            text = f.read_text(encoding="utf-8")
            self.assertNotIn("ABCDEFGH12345678", text)
            self.assertIn("**Alan:**", text)
            self.assertIn("**ECC:** noted", text)

    def test_none_dir_disables_logging(self):
        convlog.log_turn(None, "ecc", "user", "hi")  # must not raise


class ChatAppTests(unittest.TestCase):
    def make_app(self, conv_dir=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return control.App("tok", SITES, Store(Path(tmp.name)), mock.Mock(), FakePoster(), conv_dir=conv_dir)

    def test_ecc_chat_stores_both_turns_and_reports_changed_files(self):
        app = self.make_app()
        with mock.patch("control.run_claude", return_value=(True, "Done, edited a.py")) as run, \
                mock.patch("control.files.snapshot", return_value={}), \
                mock.patch("control.files.changed_since", return_value=[{"path": "a.py", "status": "modified"}]):
            out = app.chat({"channel": "ecc", "message": "fix it"})
        self.assertEqual(out["reply"], "Done, edited a.py")
        self.assertEqual(out["files"], [{"path": "a.py", "status": "modified"}])
        self.assertEqual([m["role"] for m in app.store.chat_history("ecc")], ["user", "assistant"])
        self.assertTrue(run.call_args.kwargs.get("edits", True))

    def test_axiom_chat_cannot_edit_files_or_use_tools(self):
        app = self.make_app()
        with mock.patch("control.run_claude", return_value=(True, "Hi Alan")) as run:
            out = app.chat({"channel": "axiom", "message": "hello"})
        self.assertEqual(out["files"], [])
        self.assertFalse(run.call_args.kwargs["edits"])
        self.assertFalse(run.call_args.kwargs["tools"])

    def test_failed_reply_is_a_value_error_and_keeps_history_clean(self):
        app = self.make_app()
        with mock.patch("control.run_claude", return_value=(False, "Claude could not be run.")), \
                mock.patch("control.files.snapshot", return_value={}):
            with self.assertRaises(ValueError):
                app.chat({"channel": "ecc", "message": "hi"})
        self.assertEqual(app.store.chat_history("ecc"), [])

    def test_rejects_bad_channel_and_bad_message(self):
        app = self.make_app()
        for body in ({"channel": "bob", "message": "x"}, {"channel": "ecc", "message": "  "},
                     {"channel": "ecc", "message": "x" * (control.MAX_CHAT_CHARS + 1)}):
            with self.subTest(body=body), self.assertRaises(ValueError):
                app.chat(body)

    def test_chat_is_logged_to_conversation_folder(self):
        with tempfile.TemporaryDirectory() as conv:
            app = self.make_app(conv_dir=Path(conv))
            with mock.patch("control.run_claude", return_value=(True, "Hello")), \
                    mock.patch("control.files.snapshot", return_value={}), \
                    mock.patch("control.files.changed_since", return_value=[]):
                app.chat({"channel": "ecc", "message": "hi there"})
            [f] = list(Path(conv).glob("mission-control-chats-*.md"))
            self.assertIn("hi there", f.read_text(encoding="utf-8"))

    def test_history_and_clear(self):
        app = self.make_app()
        app.store.chat_append("ecc", "user", "hi")
        self.assertEqual(len(app.chat_history({"channel": "ecc"})["messages"]), 1)
        app.chat_clear({"channel": "ecc"})
        self.assertEqual(app.chat_history({"channel": "ecc"})["messages"], [])

    def test_file_read_delegates_and_maps_errors(self):
        app = self.make_app()
        with mock.patch("control.files.read_file", return_value={"path": "a", "content": "x", "diff": ""}):
            self.assertEqual(app.file_read({"path": "a"})["content"], "x")
        with mock.patch("control.files.read_file", side_effect=KeyError("a")):
            with self.assertRaises(KeyError):
                app.file_read({"path": "a"})

    def test_links_include_github_and_n8n(self):
        links = self.make_app().links_info()
        self.assertTrue(links["links"]["GitHub"].startswith("https://github.com/"))
        self.assertIn("n8n", links["links"]["n8n"])

    def test_links_include_email_and_godaddy(self):
        links = self.make_app().links_info()["links"]
        self.assertTrue(links["Email"].startswith("https://"))
        self.assertIn("godaddy.com", links["GoDaddy"])
        self.assertEqual(links["Grok"], "https://grok.com/")

    def test_model_channels_use_providers_not_claude_cli(self):
        app = self.make_app()
        with mock.patch("control.providers.ask", return_value=(True, "GPT says hi")) as ask, \
                mock.patch("control.run_claude") as cli:
            out = app.chat({"channel": "gpt", "message": "hello"})
        self.assertEqual(out, {"reply": "GPT says hi", "files": []})
        cli.assert_not_called()
        self.assertEqual(ask.call_args.args[0], "gpt")
        self.assertEqual([m["role"] for m in app.store.chat_history("gpt")], ["user", "assistant"])

    def test_history_reports_relay_mode_without_key_and_api_mode_with_key(self):
        app = self.make_app()
        with mock.patch("control.posting.load_env", return_value={}):
            out = app.chat_history({"channel": "gpt"})
        self.assertEqual(out["mode"], "relay")
        self.assertTrue(out["url"].startswith("https://"))
        with mock.patch("control.posting.load_env", return_value={"OPENAI_API_KEY": "k"}):
            self.assertEqual(app.chat_history({"channel": "gpt"})["mode"], "api")
        self.assertNotIn("mode", app.chat_history({"channel": "ecc"}))

    def test_relay_prompt_includes_history_and_ends_with_the_message(self):
        app = self.make_app()
        app.store.chat_append("claude", "user", "earlier")
        app.store.chat_append("claude", "assistant", "answer")
        prompt = app.chat_prompt({"channel": "claude", "message": "new question"})["prompt"]
        self.assertIn("Alan: earlier", prompt)
        self.assertTrue(prompt.endswith("Alan: new question"))

    def test_relay_record_saves_both_turns_and_logs_them(self):
        with tempfile.TemporaryDirectory() as conv:
            app = self.make_app(conv_dir=Path(conv))
            app.chat_record({"channel": "deepseek", "message": "q", "reply": "pasted answer"})
            self.assertEqual([m["text"] for m in app.store.chat_history("deepseek")], ["q", "pasted answer"])
            [f] = list(Path(conv).glob("mission-control-chats-*.md"))
            self.assertIn("**DeepSeek:** pasted answer", f.read_text(encoding="utf-8"))

    def test_relay_only_for_model_channels_and_needs_both_texts(self):
        app = self.make_app()
        for call, body in ((app.chat_prompt, {"channel": "ecc", "message": "x"}),
                           (app.chat_record, {"channel": "axiom", "message": "x", "reply": "y"}),
                           (app.chat_record, {"channel": "gpt", "message": "x", "reply": "  "}),
                           (app.chat_record, {"channel": "gpt", "message": "", "reply": "y"}),
                           (app.chat_record, {"channel": "gpt", "message": "x", "reply": "y" * (control.MAX_RELAY_REPLY_CHARS + 1)})):
            with self.subTest(body=body), self.assertRaises(ValueError):
                call(body)

    def test_unconfigured_model_is_a_value_error_and_keeps_history_clean(self):
        app = self.make_app()
        with mock.patch("control.posting.load_env", return_value={}):
            with self.assertRaises(ValueError):
                app.chat({"channel": "claude", "message": "hello"})
        self.assertEqual(app.store.chat_history("claude"), [])


class RunClaudeFlagsTests(unittest.TestCase):
    def test_default_keeps_accept_edits(self):
        done = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch("control.subprocess.run", return_value=done) as run:
            control.run_claude("hi")
        self.assertIn("acceptEdits", run.call_args.args[0])

    def test_read_only_mode_disables_edits_and_tools(self):
        done = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch("control.subprocess.run", return_value=done) as run:
            control.run_claude("hi", edits=False, tools=False)
        argv = run.call_args.args[0]
        self.assertNotIn("acceptEdits", argv)
        self.assertIn("--tools", argv)


if __name__ == "__main__":
    unittest.main()
