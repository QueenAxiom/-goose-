import unittest
from unittest import mock

import requests

import posting


class ValidateTests(unittest.TestCase):
    def test_accepts_normal_text(self):
        self.assertIsNone(posting.validate_post("facebook", "Hello world"))

    def test_rejects_blank(self):
        self.assertIn("empty", posting.validate_post("facebook", "   "))

    def test_rejects_too_long(self):
        self.assertIn("long", posting.validate_post("facebook", "x" * (posting.MAX_POST_CHARS + 1)))

    def test_rejects_unknown_platform(self):
        self.assertIn("platform", posting.validate_post("myspace", "hi"))

    def test_rejects_unavailable_platform(self):
        self.assertIn("not available", posting.validate_post("linkedin", "hi"))


class PreflightTests(unittest.TestCase):
    def test_flags_missing_contact_and_site(self):
        flags = posting.preflight("facebook", "Big sale today")
        self.assertTrue(any("email" in f for f in flags))
        self.assertTrue(any("site" in f for f in flags))

    def test_clean_post_has_no_flags(self):
        text = "Lifetime listing $499 at EverythingInternet.ca. Email rise@empoweredathome.com"
        self.assertEqual(posting.preflight("facebook", text), [])

    def test_flags_long_for_facebook_recommendation(self):
        text = "EverythingInternet.ca rise@empoweredathome.com " + "x" * posting.RECOMMENDED_CHARS["facebook"]
        self.assertTrue(any("longer" in f.lower() for f in posting.preflight("facebook", text)))


class FacebookPosterTests(unittest.TestCase):
    ENV = {"MC_FB_PAGE_ID": "123", "MC_FB_PAGE_TOKEN": "secret-token"}

    def test_unconfigured_reports_status(self):
        self.assertFalse(posting.Poster(env={}).configured("facebook"))
        self.assertTrue(posting.Poster(env=self.ENV).configured("facebook"))

    def test_publish_posts_to_page_feed_with_token_in_body_not_url(self):
        resp = mock.Mock(status_code=200, json=lambda: {"id": "123_456"})
        with mock.patch("posting.requests.post", return_value=resp) as post:
            result = posting.Poster(env=self.ENV).publish("facebook", "hello")
        self.assertEqual(result, {"post_id": "123_456"})
        url = post.call_args.args[0]
        self.assertIn("/123/feed", url)
        self.assertNotIn("secret-token", url)
        self.assertEqual(post.call_args.kwargs["data"]["message"], "hello")

    def test_publish_when_unconfigured_raises_posting_error(self):
        with self.assertRaises(posting.PostingError):
            posting.Poster(env={}).publish("facebook", "hello")

    def test_publish_api_error_surfaces_message_without_token(self):
        resp = mock.Mock(status_code=400, json=lambda: {"error": {"message": "Invalid OAuth token"}})
        with mock.patch("posting.requests.post", return_value=resp):
            with self.assertRaises(posting.PostingError) as ctx:
                posting.Poster(env=self.ENV).publish("facebook", "hello")
        self.assertIn("Invalid OAuth", str(ctx.exception))
        self.assertNotIn("secret-token", str(ctx.exception))

    def test_network_error_is_wrapped_without_leaking(self):
        with mock.patch("posting.requests.post", side_effect=requests.ConnectionError("secret-token boom")):
            with self.assertRaises(posting.PostingError) as ctx:
                posting.Poster(env=self.ENV).publish("facebook", "hello")
        self.assertNotIn("secret-token", str(ctx.exception))

    def test_delete_calls_graph_delete(self):
        resp = mock.Mock(status_code=200, json=lambda: {"success": True})
        with mock.patch("posting.requests.delete", return_value=resp) as delete:
            posting.Poster(env=self.ENV).delete("facebook", "123_456")
        self.assertIn("123_456", delete.call_args.args[0])

    def test_delete_rejects_odd_post_ids(self):
        with self.assertRaises(posting.PostingError):
            posting.Poster(env=self.ENV).delete("facebook", "../me/accounts")


class EnvFileTests(unittest.TestCase):
    def test_parses_key_values_and_ignores_comments(self):
        text = "# c\nMC_FB_PAGE_ID=1\n\nMC_FB_PAGE_TOKEN = abc def \nbad line\n"
        self.assertEqual(posting.parse_env(text), {"MC_FB_PAGE_ID": "1", "MC_FB_PAGE_TOKEN": "abc def"})


if __name__ == "__main__":
    unittest.main()
