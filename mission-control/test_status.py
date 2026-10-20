import unittest
from unittest import mock

import status


class StripeModeTests(unittest.TestCase):
    def test_detects_test_key(self):
        self.assertEqual(status.detect_stripe_mode('{"key":"pk_test_AbC123xyz"}'), "test")

    def test_detects_live_key(self):
        self.assertEqual(status.detect_stripe_mode("pk_live_ABCdef456"), "live")

    def test_detects_mixed_keys(self):
        self.assertEqual(status.detect_stripe_mode("pk_test_AAAA1111 pk_live_BBBB2222"), "mixed")

    def test_unknown_without_keys(self):
        self.assertEqual(status.detect_stripe_mode("<html>no keys</html>"), "unknown")


class FrameTests(unittest.TestCase):
    def test_blocked_by_x_frame_options(self):
        self.assertFalse(status.frame_allowed({"X-Frame-Options": "SAMEORIGIN"}))

    def test_blocked_by_csp_frame_ancestors(self):
        self.assertFalse(status.frame_allowed({"Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'"}))

    def test_allowed_without_headers(self):
        self.assertTrue(status.frame_allowed({}))

    def test_header_names_are_case_insensitive(self):
        self.assertFalse(status.frame_allowed({"x-frame-options": "deny"}))


class CheckSiteTests(unittest.TestCase):
    def test_up_site(self):
        fetch = mock.Mock(return_value=(200, {"Server": "x"}, ""))
        r = status.check_site("https://a.example", fetch=fetch)
        self.assertEqual((r["up"], r["status"], r["frame_ok"]), (True, 200, True))

    def test_server_error_is_down(self):
        r = status.check_site("https://a.example", fetch=mock.Mock(return_value=(503, {}, "")))
        self.assertFalse(r["up"])

    def test_exception_is_down_without_leaking_details(self):
        r = status.check_site("https://a.example", fetch=mock.Mock(side_effect=OSError("secret detail")))
        self.assertFalse(r["up"])
        self.assertNotIn("secret", str(r))

    def test_one_transient_failure_is_retried(self):
        fetch = mock.Mock(side_effect=[TimeoutError("slow"), (200, {}, "")])
        r = status.check_site("https://a.example", fetch=fetch)
        self.assertTrue(r["up"])
        self.assertEqual(fetch.call_count, 2)

    def test_untrusted_cert_is_labelled(self):
        import ssl, urllib.error
        err = urllib.error.URLError(ssl.SSLCertVerificationError("unable to get local issuer certificate"))
        r = status.check_site("https://a.example", fetch=mock.Mock(side_effect=err))
        self.assertFalse(r["up"])
        self.assertIn("cert not trusted", r["reason"])


class StripeModesTests(unittest.TestCase):
    def test_slow_probe_falls_back_to_unknown_without_blocking(self):
        import threading
        gate = threading.Event()
        def slow(url):
            gate.wait(5)
            return 200, {}, "pk_live_ABCdef456"
        status._stripe_cache.clear()
        out = status.stripe_modes({"live": "https://slow.example"}, fetch=slow, wait_seconds=0.1)
        gate.set()
        self.assertEqual(out, {"live": "unknown"})

    def test_fast_probes_return_mode(self):
        status._stripe_cache.clear()
        out = status.stripe_modes({"live": "https://fast.example"}, fetch=lambda u: (200, {}, "pk_test_AbC123xyz"), wait_seconds=2)
        self.assertEqual(out, {"live": "test"})


class ParseTemplatesTests(unittest.TestCase):
    def test_splits_email_sections(self):
        md = "# T\n\n## Email 1 — cold\nSubject: A\n\nBody1\n\n## Email 2 — follow\nSubject: B\n\nBody2\n\n## Rules\n- x\n"
        out = status.parse_templates(md)
        self.assertEqual([t["id"] for t in out], ["email-1", "email-2"])
        self.assertIn("Body1", out[0]["body"])
        self.assertNotIn("Rules", out[1]["body"])


if __name__ == "__main__":
    unittest.main()
