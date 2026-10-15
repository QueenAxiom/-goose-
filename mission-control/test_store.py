import tempfile
import unittest
from pathlib import Path

import store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.s = store.Store(Path(self._tmp.name))

    def test_add_lead_returns_new_lead_and_persists(self):
        lead = self.s.add_lead({"business": "Acme Plumbing", "contact": "Pat", "email": "pat@acme.ca"})
        self.assertEqual(lead["status"], "new")
        self.assertEqual([l["business"] for l in self.s.leads()], ["Acme Plumbing"])

    def test_store_survives_reopen(self):
        self.s.add_lead({"business": "Acme"})
        self.assertEqual(len(store.Store(Path(self._tmp.name)).leads()), 1)

    def test_rejects_blank_business(self):
        with self.assertRaises(ValueError):
            self.s.add_lead({"business": "  "})

    def test_rejects_overlong_fields(self):
        with self.assertRaises(ValueError):
            self.s.add_lead({"business": "x" * 500})

    def test_update_status_changes_only_that_lead(self):
        a = self.s.add_lead({"business": "A"})
        b = self.s.add_lead({"business": "B"})
        self.s.update_lead(a["id"], {"status": "contacted"})
        by_id = {l["id"]: l for l in self.s.leads()}
        self.assertEqual((by_id[a["id"]]["status"], by_id[b["id"]]["status"]), ("contacted", "new"))

    def test_rejects_unknown_status(self):
        a = self.s.add_lead({"business": "A"})
        with self.assertRaises(ValueError):
            self.s.update_lead(a["id"], {"status": "bogus"})

    def test_update_unknown_lead_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.s.update_lead("nope", {"status": "won"})

    def test_delete_lead(self):
        a = self.s.add_lead({"business": "A"})
        self.s.delete_lead(a["id"])
        self.assertEqual(self.s.leads(), [])

    def test_scoreboard_counts_pipeline_and_includes_money_settings(self):
        for biz, status in (("A", "contacted"), ("B", "replied"), ("C", "call"), ("D", "won")):
            lead = self.s.add_lead({"business": biz})
            self.s.update_lead(lead["id"], {"status": status})
        self.s.set_money(mrr=1000, cash=250)
        board = self.s.scoreboard()
        self.assertEqual(board["conversations"], 3)  # contacted excluded; replied+call+won
        self.assertEqual((board["calls"], board["sales"], board["mrr"], board["cash"]), (2, 1, 1000, 250))

    def test_money_must_be_non_negative_numbers(self):
        with self.assertRaises(ValueError):
            self.s.set_money(mrr=-1, cash=0)
        with self.assertRaises(ValueError):
            self.s.set_money(mrr="lots", cash=0)

    def test_approval_roundtrip(self):
        self.s.set_approval("email-1", True)
        self.assertTrue(self.s.approvals()["email-1"]["approved"])
        self.s.set_approval("email-1", False)
        self.assertFalse(self.s.approvals()["email-1"]["approved"])

    def test_corrupt_file_falls_back_to_empty(self):
        (Path(self._tmp.name) / "leads.json").write_text("{not json", encoding="utf-8")
        self.assertEqual(self.s.leads(), [])

    def test_posts_log_and_mark_deleted(self):
        rec = self.s.add_post({"platform": "facebook", "text": "hi", "post_id": "1_2"})
        self.assertEqual(self.s.posts()[0]["id"], rec["id"])
        self.s.mark_post_deleted(rec["id"])
        self.assertTrue(self.s.posts()[0]["deleted"])

    def test_recent_duplicate_detects_same_text_within_window(self):
        self.s.add_post({"platform": "facebook", "text": "Same text", "post_id": "1"})
        self.assertTrue(self.s.recent_duplicate("facebook", "same text ", seconds=60))
        self.assertFalse(self.s.recent_duplicate("facebook", "different", seconds=60))

    def test_deleted_posts_do_not_block_reposting(self):
        rec = self.s.add_post({"platform": "facebook", "text": "Oops", "post_id": "1"})
        self.s.mark_post_deleted(rec["id"])
        self.assertFalse(self.s.recent_duplicate("facebook", "Oops", seconds=60))

    def test_council_question_lifecycle(self):
        q = self.s.add_question({"question": "Should we price at $499?", "asked_by": "Alan", "topic": "strategy"})
        self.assertEqual((q["status"], q["asked_by"], q["topic"]), ("open", "Alan", "strategy"))
        done = self.s.answer_question(q["id"], "Yes, keep $499.", "ECC")
        self.assertEqual((done["status"], done["answer"], done["answer_source"]), ("answered", "Yes, keep $499.", "ECC"))
        self.assertEqual(len(self.s.questions()), 1)

    def test_council_rejects_blank_unknown_asker_and_unknown_topic(self):
        with self.assertRaises(ValueError):
            self.s.add_question({"question": " ", "asked_by": "Alan", "topic": "general"})
        with self.assertRaises(ValueError):
            self.s.add_question({"question": "q", "asked_by": "Bob", "topic": "general"})
        with self.assertRaises(ValueError):
            self.s.add_question({"question": "q", "asked_by": "Alan", "topic": "weather"})

    def test_answer_unknown_question_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.s.answer_question("nope", "x", "Alan")

    def test_asked_today_detects_todays_question(self):
        self.assertFalse(self.s.asked_today())
        self.s.add_question({"question": "q", "asked_by": "Axiom", "topic": "general"})
        self.assertTrue(self.s.asked_today())

    def test_dismiss_today_hides_prompt(self):
        self.assertFalse(self.s.dismissed_today())
        self.s.dismiss_today()
        self.assertTrue(self.s.dismissed_today())

    def test_delete_question(self):
        q = self.s.add_question({"question": "q", "asked_by": "Alan", "topic": "general"})
        self.s.delete_question(q["id"])
        self.assertEqual(self.s.questions(), [])


if __name__ == "__main__":
    unittest.main()
