import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import chat
import files
from store import Store


class PromptTests(unittest.TestCase):
    def test_ecc_prompt_includes_history_and_new_message(self):
        history = [{"role": "user", "text": "hi"}, {"role": "assistant", "text": "hello"}]
        p = chat.build_chat_prompt("ecc", history, "do the thing", persona="")
        self.assertIn("hi", p)
        self.assertIn("hello", p)
        self.assertTrue(p.rstrip().endswith("do the thing"))

    def test_history_is_trimmed_to_recent_turns(self):
        history = [{"role": "user", "text": f"msg {i}"} for i in range(50)]
        p = chat.build_chat_prompt("ecc", history, "now", persona="")
        self.assertIn("msg 49", p)
        self.assertNotIn("msg 0 ", p + " ")

    def test_axiom_prompt_carries_persona(self):
        p = chat.build_chat_prompt("axiom", [], "hello", persona="You are Axiom, Alan's partner.")
        self.assertIn("You are Axiom", p)

    def test_unknown_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            chat.build_chat_prompt("bob", [], "x", persona="")

    def test_load_persona_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("Axiom", chat.load_persona(Path(d) / "missing.md"))


class ChatStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.s = Store(Path(self._tmp.name))

    def test_append_and_read_back_per_channel(self):
        self.s.chat_append("ecc", "user", "hi")
        self.s.chat_append("axiom", "user", "yo")
        self.assertEqual([m["text"] for m in self.s.chat_history("ecc")], ["hi"])

    def test_history_is_capped(self):
        for i in range(250):
            self.s.chat_append("ecc", "user", f"m{i}")
        h = self.s.chat_history("ecc")
        self.assertEqual(len(h), 200)
        self.assertEqual(h[-1]["text"], "m249")

    def test_clear(self):
        self.s.chat_append("ecc", "user", "hi")
        self.s.chat_clear("ecc")
        self.assertEqual(self.s.chat_history("ecc"), [])


class FilesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.repo, check=True)
        (self.repo / "a.txt").write_text("one\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.repo, check=True)

    def test_changed_files_lists_modified_and_new(self):
        (self.repo / "a.txt").write_text("two\n", encoding="utf-8")
        (self.repo / "b.txt").write_text("new\n", encoding="utf-8")
        got = {f["path"]: f["status"] for f in files.changed_files(self.repo)}
        self.assertEqual(got, {"a.txt": "modified", "b.txt": "new"})

    def test_read_file_returns_content_and_diff(self):
        (self.repo / "a.txt").write_text("two\n", encoding="utf-8")
        out = files.read_file(self.repo, "a.txt")
        self.assertEqual(out["content"], "two\n")
        self.assertIn("-one", out["diff"])
        self.assertIn("+two", out["diff"])

    def test_read_untracked_file_diff_is_whole_file(self):
        (self.repo / "b.txt").write_text("new\n", encoding="utf-8")
        self.assertIn("+new", files.read_file(self.repo, "b.txt")["diff"])

    def test_path_traversal_is_refused(self):
        for bad in ("../outside.txt", "..\\outside.txt", "/etc/passwd", "C:/Windows/win.ini"):
            with self.subTest(path=bad), self.assertRaises(ValueError):
                files.read_file(self.repo, bad)

    def test_secret_and_internal_paths_are_refused(self):
        (self.repo / ".env").write_text("TOKEN=abc", encoding="utf-8")
        (self.repo / "mission-control").mkdir()
        (self.repo / "mission-control" / ".env").write_text("TOKEN=abc", encoding="utf-8")
        for bad in (".env", "mission-control/.env", ".git/config"):
            with self.subTest(path=bad), self.assertRaises(ValueError):
                files.read_file(self.repo, bad)

    def test_binary_and_huge_files_are_refused(self):
        (self.repo / "x.bin").write_bytes(b"\x00\x01\x02")
        (self.repo / "big.txt").write_text("x" * (files.MAX_FILE_BYTES + 1), encoding="utf-8")
        for bad in ("x.bin", "big.txt"):
            with self.subTest(path=bad), self.assertRaises(ValueError):
                files.read_file(self.repo, bad)

    def test_missing_file_is_key_error(self):
        with self.assertRaises(KeyError):
            files.read_file(self.repo, "nope.txt")

    def test_new_changes_since_snapshot(self):
        before = files.snapshot(self.repo)
        (self.repo / "b.txt").write_text("new\n", encoding="utf-8")
        (self.repo / "a.txt").write_text("two\n", encoding="utf-8")
        after = files.changed_since(self.repo, before)
        self.assertEqual({f["path"] for f in after}, {"a.txt", "b.txt"})

    def test_unchanged_dirty_files_are_not_reported(self):
        (self.repo / "a.txt").write_text("two\n", encoding="utf-8")
        before = files.snapshot(self.repo)
        self.assertEqual(files.changed_since(self.repo, before), [])


if __name__ == "__main__":
    unittest.main()
