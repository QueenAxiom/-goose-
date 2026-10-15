import unittest
from router import extract_command, route, Route

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

    def test_matches_wake_word_mid_sentence(self):
        self.assertEqual(extract_command("ok so hey axiom status please", ("hey axiom",)), "status please")


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


if __name__ == "__main__":
    unittest.main()
