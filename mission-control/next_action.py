"""Pick the single next thing Alan should do, from live state. Pure functions; no I/O."""
from datetime import datetime, timedelta

FOLLOW_UP_AFTER = timedelta(days=4)
UPCOMING_COUNT = 3
ACTION_IDS = ("council-checkin", "site-down", "pay-link", "test-purchase", "add-leads", "approve-drafts",
              "book-call", "follow-up", "contact-lead", "setup-posting", "post-today", "council-open", "backup", "idle")
STRIPE_TEST_PAYMENT_LINK_URL = "https://dashboard.stripe.com/test/payment-links/create"


def _pane(pane: str) -> dict:
    return {"type": "pane", "target": pane}


def _url(url: str) -> dict:
    return {"type": "url", "target": url}


def _action(action_id: str, title: str, why: str, go: dict, manual: bool = False) -> dict:
    return {"id": action_id, "key": f"{action_id}:{title}", "title": title, "why": why, "go": go, "manual": manual}


def _age(lead: dict, now: datetime) -> timedelta:
    stamp = lead.get("updated") or lead.get("created")
    return now - datetime.fromisoformat(stamp)


def _by_status(leads: list, status: str) -> list:
    return [lead for lead in leads if lead["status"] == status]


def candidates(f: dict) -> list:
    """Every applicable action, highest priority first. Always ends with an idle fallback."""
    leads, now, done = f["leads"], f["now"], f["manual_done"]
    out = []

    if not f["asked_today"] and not f["dismissed_today"]:
        out.append(_action("council-checkin", "Daily council check-in",
                           "Your standing first step each day: do you or Axiom have a question for the council?",
                           _pane("council")))
    if f["sites_down"]:
        out.append(_action("site-down", "Look at the down site: " + ", ".join(f["sites_down"]),
                           "A site that is down loses customers and trust faster than anything else.", _pane("system")))
    if "pay-link" not in done:
        out.append(_action("pay-link", "Create the $499 Stripe Payment Link (test mode)",
                           "Nobody can pay you for the SMB offer until this exists. Test mode costs nothing.",
                           _url(STRIPE_TEST_PAYMENT_LINK_URL), manual=True))
    if "test-purchase" not in done:
        out.append(_action("test-purchase", "Make a test purchase on EverythingInternet staging",
                           "Proves checkout works end to end using the fake card 4242 4242 4242 4242, with no real money.",
                           _url(f["staging_checkout"]), manual=True))
    if not leads:
        out.append(_action("add-leads", "Add your first leads",
                           "Sales need names. Aim for 10 Canadian trades, clinics or accountants.", _pane("sales")))
    if _by_status(leads, "new") and f["approved_templates"] == 0:
        out.append(_action("approve-drafts", "Approve the outreach drafts",
                           "Nothing can be sent until you approve at least one draft.", _pane("sales")))
    for lead in _by_status(leads, "replied"):
        out.append(_action("book-call", f"Book a call with {lead['business']}",
                           "They replied. A warm lead cools fast.", _pane("sales")))
    for lead in _by_status(leads, "contacted"):
        if _age(lead, now) >= FOLLOW_UP_AFTER:
            out.append(_action("follow-up", f"Send the follow-up to {lead['business']}",
                               "It has been 4+ days since the first message. Draft 2 is written.", _pane("sales")))
    for lead in _by_status(leads, "new"):
        out.append(_action("contact-lead", f"Send outreach to {lead['business']}",
                           "Conversations are the bottleneck: 30 a week is the plan.", _pane("sales")))
    if not f["fb_configured"]:
        out.append(_action("setup-posting", "Connect Facebook posting",
                           "Add MC_FB_PAGE_ID and MC_FB_PAGE_TOKEN to mission-control/.env so the post box works.",
                           _pane("posts")))
    elif f["posts_today"] == 0:
        out.append(_action("post-today", "Post today's update",
                           "Nothing has gone out today. The plan is a steady posting cadence.", _pane("posts")))
    if f["open_questions"]:
        out.append(_action("council-open", f"Get an answer on {f['open_questions']} open council question(s)",
                           "Unanswered questions are decisions you are carrying in your head.", _pane("council")))
    if f["unpushed"] or f["uncommitted"]:
        out.append(_action("backup", "Back up your work",
                           f"{f['uncommitted']} uncommitted and {f['unpushed']} unpushed changes exist only on this PC.",
                           _pane("system")))
    out.append(_action("idle", "Nothing urgent. Check the sales scoreboard.",
                       "Everything due is done. Reviewing the numbers is the best use of a quiet minute.", _pane("sales")))
    return out


def pick(f: dict) -> dict:
    return next(a for a in candidates(f) if a["id"] not in f["snoozed"])


def plan(f: dict) -> dict:
    """The dispatcher's view: the whole remaining route, plus the stop to do right now."""
    live = [a for a in candidates(f) if a["id"] not in f["snoozed"]]
    route = [a for a in live if a["id"] != "idle"]
    return {"now": live[0], "route": route, "upcoming": [a for a in route if a is not live[0]][:UPCOMING_COUNT]}
