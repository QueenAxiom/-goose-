import tempfile
import unittest
from pathlib import Path
from unittest import mock

import deploy

GOOD = "<html><body>" + "Real content about this brand. " * 80 + "<footer>(c) Axiom Enterprises</footer></body></html>"


def make_env(tmp: Path, pages: dict) -> deploy.Deployer:
    sites = {}
    for domain, html in pages.items():
        d = tmp / "sites" / domain
        d.mkdir(parents=True)
        (d / "index.html").write_text(html, encoding="utf-8")
        sites[domain] = {"live": f"https://{domain}", "staging": f"https://stg-{domain}"}
    return deploy.Deployer(sites, tmp / "sites", tmp / "data", env={})


class CheckTests(unittest.TestCase):
    def test_good_page_passes(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": GOOD, "b.com": GOOD + "x"})
            self.assertEqual(dep.problems("a.com"), [])

    def test_flags_localhost_ai_and_missing_footer(self):
        bad = "<html>" + "word " * 400 + "http://localhost:8800 AI </html>"
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": bad})
            text = " ".join(dep.problems("a.com"))
            self.assertIn("localhost", text)
            self.assertIn('"AI"', text)
            self.assertIn("footer", text)

    def test_flags_identical_copies(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": GOOD, "b.com": GOOD})
            self.assertTrue(any("identical" in p for p in dep.problems("a.com")))

    def test_flags_thin_page(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": "<html>hi (c) Axiom Enterprises</html>"})
            self.assertTrue(any("thin" in p for p in dep.problems("a.com")))


class GateTests(unittest.TestCase):
    def test_autopilot_refused_until_all_ready_and_staged(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": GOOD, "b.com": GOOD + "x"})
            with self.assertRaises(ValueError) as ctx:
                dep.autopilot(confirm=True)
            self.assertIn("staged", str(ctx.exception))

    def test_autopilot_requires_confirm(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": GOOD})
            with self.assertRaises(ValueError):
                dep.autopilot(confirm=False)

    def test_push_without_credentials_explains(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": GOOD})
            with self.assertRaises(ValueError) as ctx:
                dep.push("a.com", "staging")
            self.assertIn("MC_WP_A_COM_USER", str(ctx.exception))

    def test_staged_then_all_ready_runs_live_pushes(self):
        with tempfile.TemporaryDirectory() as t:
            dep = make_env(Path(t), {"a.com": GOOD, "b.com": GOOD + "x"})
            with mock.patch.object(dep, "_publish", return_value={"page_id": 1}) as pub:
                for d in dep.sites:
                    dep.push(d, "staging")
                dep.autopilot(confirm=True)
            targets = [c.args[1] for c in pub.call_args_list]
            self.assertEqual(targets.count("live"), 2)


if __name__ == "__main__":
    unittest.main()
