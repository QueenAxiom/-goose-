import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import check_links as cl

# A tiny fake site: one broken page, one long redirect chain, one temporary redirect.
PAGES = {
    "/": '<a href="/about">About</a> <a href="/gone">Old</a> <a href="/old">Moved</a>'
         ' <img src="/logo.png"> <a href="mailto:hi@example.com">Mail</a> <a href="#top">Top</a>'
         ' <a href="/temp">Temp</a>',
    "/about": '<a href="/">Home</a> <a href="/about#team">Team</a>',
    "/new": "<p>New page</p>",
}
REDIRECTS = {"/old": (301, "/older"), "/older": (301, "/new"), "/temp": (302, "/new")}


class Handler(BaseHTTPRequestHandler):
    def _send(self, with_body):
        if self.path in REDIRECTS:
            code, loc = REDIRECTS[self.path]
            self.send_response(code)
            self.send_header("Location", loc)
            self.end_headers()
        elif self.path in PAGES:
            data = PAGES[self.path].encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if with_body:
                self.wfile.write(data)
        elif self.path == "/logo.png":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        self._send(True)

    def do_HEAD(self):
        self._send(False)

    def log_message(self, *args):
        pass


class CrawlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.root = f"http://127.0.0.1:{cls.server.server_address[1]}/"
        cls.site = cl.check_site(cls.root, max_pages=50)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_finds_broken_link_and_where_it_lives(self):
        gone = self.root + "gone"
        self.assertTrue(cl.is_broken(self.site["results"][gone]))
        self.assertEqual(self.site["found_on"][gone], {self.root})

    def test_skips_mailto_and_fragments(self):
        urls = self.site["results"].keys()
        self.assertFalse(any(u.startswith("mailto:") for u in urls))
        self.assertNotIn(self.root + "about#team", urls)

    def test_records_redirect_chain(self):
        r = self.site["results"][self.root + "old"]
        self.assertEqual(r["status"], 200)
        self.assertEqual(r["final_url"], self.root + "new")
        self.assertEqual(len(r["hops"]), 2)
        self.assertIn("2 hops", cl.redirect_problems(self.root + "old", r)[0])

    def test_flags_temporary_redirect(self):
        r = self.site["results"][self.root + "temp"]
        self.assertTrue(any("302" in p for p in cl.redirect_problems(self.root + "temp", r)))

    def test_image_checked(self):
        self.assertEqual(self.site["results"][self.root + "logo.png"]["status"], 200)

    def test_report_counts_broken(self):
        report, broken = cl.build_report([self.site])
        self.assertEqual(broken, 1)
        self.assertIn("### Broken", report)
        self.assertIn("### Redirects to fix", report)

    def test_unreachable_host_is_broken(self):
        r = cl.fetch("http://127.0.0.1:1/", want_body=False)
        self.assertTrue(cl.is_broken(r))
        self.assertIsNotNone(r["error"])


class HelperTests(unittest.TestCase):
    def test_same_site_ignores_www(self):
        self.assertTrue(cl.same_site("https://www.schmucksdebate.com/x", "https://schmucksdebate.com/"))
        self.assertFalse(cl.same_site("https://example.com/", "https://schmucksdebate.com/"))

    def test_https_to_http_downgrade_flagged(self):
        r = {"hops": [(301, "https://a.com/")], "final_url": "http://a.com/"}
        self.assertIn("redirects from https to http", cl.redirect_problems("https://a.com/", r))

    def test_clean_site_report(self):
        site = {"root": "https://a.com/", "results": {"https://a.com/": {"status": 200, "final_url": "https://a.com/",
                "hops": [], "body": b"", "error": None}}, "found_on": {}, "pages_crawled": 1}
        report, broken = cl.build_report([site])
        self.assertEqual(broken, 0)
        self.assertIn("No problems found.", report)


if __name__ == "__main__":
    unittest.main()
