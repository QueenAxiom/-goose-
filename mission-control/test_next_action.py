import unittest
from datetime import datetime, timedelta, timezone

import next_action as na


def facts(**over):
    base = {
        "asked_today": True, "dismissed_today": False, "open_questions": 0,
        "fb_configured": True, "leads": [], "approved_templates": 1, "posts_today": 1,
        "sites_down": [], "uncommitted": 0, "unpushed": 0, "manual_done": {"pay-link", "test-purchase"},
        "snoozed": set(), "staging_checkout": "https://staging.example/checkout/",
        "now": datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc),
    }
    return {**base, **over}


def lead(status="new", business="Acme", days_ago=0, email="a@b.ca"):
    ts = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc) - timedelta(days=days_ago)
    return {"id": business, "business": business, "status": status, "email": email,
            "created": ts.isoformat(), "updated": ts.isoformat()}


class PickTests(unittest.TestCase):
    def pick(self, **over):
        return na.pick(facts(**over))

    def test_council_checkin_comes_first_each_day(self):
        a = self.pick(asked_today=False)
        self.assertEqual((a["id"], a["go"]["target"]), ("council-checkin", "council"))

    def test_dismissed_checkin_is_not_repeated(self):
        self.assertNotEqual(self.pick(asked_today=False, dismissed_today=True)["id"], "council-checkin")

    def test_site_down_is_urgent_even_before_sales(self):
        a = self.pick(sites_down=["EverythingInternet.ca (live)"], leads=[lead()])
        self.assertEqual(a["id"], "site-down")
        self.assertEqual(a["go"], {"type": "pane", "target": "system"})

    def test_payment_link_before_outreach(self):
        a = self.pick(manual_done=set())
        self.assertEqual(a["id"], "pay-link")
        self.assertEqual(a["go"]["type"], "url")

    def test_test_purchase_goes_to_staging_checkout(self):
        a = self.pick(manual_done={"pay-link"})
        self.assertEqual((a["id"], a["go"]["target"]), ("test-purchase", "https://staging.example/checkout/"))

    def test_no_leads_sends_to_sales(self):
        self.assertEqual(self.pick(leads=[])["id"], "add-leads")

    def test_unapproved_drafts_before_contacting_leads(self):
        a = self.pick(leads=[lead()], approved_templates=0)
        self.assertEqual(a["id"], "approve-drafts")

    def test_new_lead_gets_outreach_task_naming_the_business(self):
        a = self.pick(leads=[lead(business="Acme Plumbing")] * 1 + [lead(business="B", status="lost")])
        self.assertEqual(a["id"], "contact-lead")
        self.assertIn("Acme Plumbing", a["title"])

    def test_follow_up_due_after_four_days(self):
        a = self.pick(leads=[lead(status="contacted", days_ago=5, business="Slowpoke")])
        self.assertEqual(a["id"], "follow-up")
        self.assertIn("Slowpoke", a["title"])

    def test_recent_contact_is_not_due_yet(self):
        a = self.pick(leads=[lead(status="contacted", days_ago=1)])
        self.assertNotEqual(a["id"], "follow-up")

    def test_replied_lead_means_book_a_call(self):
        a = self.pick(leads=[lead(status="replied", business="Warm Co")])
        self.assertEqual(a["id"], "book-call")

    def test_posting_not_configured_is_prompted(self):
        a = self.pick(fb_configured=False, leads=[lead(status="lost")])
        self.assertEqual(a["id"], "setup-posting")

    def test_no_post_today_sends_to_posts_tab(self):
        a = self.pick(posts_today=0, leads=[lead(status="lost")])
        self.assertEqual((a["id"], a["go"]["target"]), ("post-today", "posts"))

    def test_open_council_questions_surface(self):
        a = self.pick(open_questions=2, leads=[lead(status="lost")])
        self.assertEqual(a["id"], "council-open")

    def test_unpushed_work_is_a_backup_nudge(self):
        a = self.pick(unpushed=2, leads=[lead(status="lost")])
        self.assertEqual(a["id"], "backup")

    def test_snoozed_actions_are_skipped(self):
        a = self.pick(asked_today=False, snoozed={"council-checkin"})
        self.assertNotEqual(a["id"], "council-checkin")

    def test_idle_fallback_when_nothing_is_due(self):
        a = self.pick(leads=[lead(status="won")])
        self.assertEqual(a["id"], "idle")

    def test_every_action_explains_why_and_has_a_destination(self):
        for over in ({"asked_today": False}, {"sites_down": ["x"]}, {"manual_done": set()}, {"leads": []}):
            a = self.pick(**over)
            self.assertTrue(a["why"])
            self.assertIn(a["go"]["type"], ("pane", "url"))


class UpcomingTests(unittest.TestCase):
    def test_upcoming_lists_next_actions_after_the_current_one(self):
        out = na.plan(facts(asked_today=False, leads=[]))
        self.assertEqual(out["now"]["id"], "council-checkin")
        self.assertIn("add-leads", [a["id"] for a in out["upcoming"]])
        self.assertLessEqual(len(out["upcoming"]), 3)

class RouteTests(unittest.TestCase):
    def test_every_stop_has_a_unique_key_even_for_same_kind_of_stop(self):
        leads = [lead(business="A"), lead(business="B")]
        keys = [a["key"] for a in na.candidates(facts(leads=leads))]
        self.assertEqual(len(keys), len(set(keys)))

    def test_plan_route_lists_every_remaining_stop_without_idle(self):
        out = na.plan(facts(asked_today=False, leads=[lead(business="A"), lead(business="B")]))
        ids = [a["id"] for a in out["route"]]
        self.assertEqual(ids[0], "council-checkin")
        self.assertEqual(ids.count("contact-lead"), 2)
        self.assertNotIn("idle", ids)

    def test_snoozed_stops_leave_the_route(self):
        out = na.plan(facts(asked_today=False, snoozed={"council-checkin"}))
        self.assertNotIn("council-checkin", [a["id"] for a in out["route"]])


if __name__ == "__main__":
    unittest.main()
