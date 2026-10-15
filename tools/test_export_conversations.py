import json
import tempfile
import unittest
from pathlib import Path

import export_conversations as ex


def entry(role, content, ts="2026-10-15T10:00:00.000Z", session="s1", **extra):
    return {"type": role, "timestamp": ts, "sessionId": session, "message": {"role": role, "content": content}, **extra}


class ExtractTextTests(unittest.TestCase):
    def test_string_content(self):
        self.assertEqual(ex.extract_text({"content": "hello"}), "hello")

    def test_block_content_keeps_only_text_blocks(self):
        msg = {"content": [{"type": "thinking", "thinking": "secret thoughts"}, {"type": "text", "text": "Answer"},
                           {"type": "tool_use", "name": "Bash", "input": {}}]}
        self.assertEqual(ex.extract_text(msg), "Answer")

    def test_tool_results_are_dropped(self):
        msg = {"content": [{"type": "tool_result", "content": "lots of output"}]}
        self.assertEqual(ex.extract_text(msg), "")

    def test_system_reminders_are_stripped(self):
        text = "Do it.<system-reminder>internal rules</system-reminder>"
        self.assertEqual(ex.extract_text({"content": text}), "Do it.")

    def test_non_dict_message_is_empty(self):
        self.assertEqual(ex.extract_text("oops"), "")


class RedactTests(unittest.TestCase):
    def test_redacts_common_secrets(self):
        raw = "key sk-ant-api03-ABCDEFGH12345678 and pk_live_ABCDEFGH1234 and Bearer abcdefghijklmnop1234"
        out = ex.redact(raw)
        for secret in ("ABCDEFGH12345678", "pk_live_ABCDEFGH1234", "abcdefghijklmnop1234"):
            self.assertNotIn(secret, out)
        self.assertIn("[REDACTED]", out)

    def test_leaves_normal_text_alone(self):
        self.assertEqual(ex.redact("Post to Facebook at 3pm"), "Post to Facebook at 3pm")


class SessionTests(unittest.TestCase):
    def test_session_markdown_has_title_date_and_turns(self):
        entries = [
            {"type": "ai-title", "aiTitle": "Voice setup", "sessionId": "s1"},
            entry("user", "Get voice working"),
            entry("assistant", [{"type": "text", "text": "On it."}], ts="2026-10-15T10:00:05.000Z"),
        ]
        md = ex.session_markdown(entries)
        self.assertIn("## Voice setup", md)
        self.assertIn("2026-10-15", md)
        self.assertIn("**Alan:** Get voice working", md)
        self.assertIn("**ECC:** On it.", md)

    def test_empty_turns_and_synthetic_are_skipped(self):
        entries = [entry("user", "Hi"), entry("assistant", [{"type": "tool_use", "name": "Bash"}]),
                   {**entry("assistant", [{"type": "text", "text": "No response requested."}]), "isSynthetic": True}]
        md = ex.session_markdown(entries)
        self.assertEqual(md.count("**ECC:**"), 0)

    def test_session_with_no_turns_returns_none(self):
        self.assertIsNone(ex.session_markdown([{"type": "mode"}]))

    def test_month_key_from_first_timestamp(self):
        self.assertEqual(ex.month_key([entry("user", "x", ts="2026-09-22T01:00:00Z")]), "2026-09")


class ExportTests(unittest.TestCase):
    def test_export_groups_sessions_by_month_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dst:
            def write(name, entries):
                (Path(src) / f"{name}.jsonl").write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")
            write("a", [entry("user", "September talk", ts="2026-09-22T10:00:00Z", session="a")])
            write("b", [entry("user", "October talk", ts="2026-10-15T10:00:00Z", session="b")])
            first = ex.export(Path(src), Path(dst))
            second = ex.export(Path(src), Path(dst))
            self.assertEqual(sorted(p.name for p in Path(dst).glob("*.md")),
                             ["axiom-conversations-2026-09.md", "axiom-conversations-2026-10.md"])
            self.assertEqual(first, second)
            self.assertIn("October talk", (Path(dst) / "axiom-conversations-2026-10.md").read_text(encoding="utf-8"))

    def test_bad_json_lines_are_skipped(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dst:
            (Path(src) / "a.jsonl").write_text("{broken\n" + json.dumps(entry("user", "ok")), encoding="utf-8")
            self.assertEqual(ex.export(Path(src), Path(dst))["sessions"], 1)


if __name__ == "__main__":
    unittest.main()
