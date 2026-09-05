# Products & Services — Axiom Enterprises

Referenced by `sales-manager.md` and `content-agent.md`. Previously a pure skeleton with no sourced data. Partially filled in on 2026-08-02 by pulling live pricing directly off the three sites (via web search + fetch, since direct automated access to EmpoweredAtHome.com and SchmucksDebate.com is currently blocked by their bot/WAF protection — see note at bottom). Everything below is sourced; anything still unconfirmed is marked TODO(Alan) rather than guessed. Content-agent and sales-manager should still say "I don't have enough information" for anything not listed here.

## EmpoweredAtHome.com

**"Making AI Part of Your Life: A Practical Introduction to Artificial Intelligence"**
- Price: $50.00 (marked down from $99.99)
- Live in the site's Shop as of 2026-08-02
- TODO(Alan): confirm format (ebook/course/video) and what it actually covers — search snippet only confirms name and price

**Pocket AI Voice Recorder** — active content-marketing subject (see `automation/content-log.md`, 2026-07-24 EN/ES drafts, real product photos referenced), but NOT confirmed as an Axiom-manufactured product:
- This appears to be a third-party device made by Open Vision Engineering, sold on Amazon (ASINs `B0GV1JFT89`, `B0GV214XQ9`) at $79, with an optional $19.99/mo "Pocket Pro" subscription
- **Update (2026-08-07):** Alan confirmed Axiom Enterprises owns/has access to a **Plaud Note Pro** device — a different manufacturer than the Open Vision Engineering attribution above. Not yet confirmed whether this is the same device being marketed here (i.e. the Open Vision Engineering research was wrong) or a separate asset unrelated to this content. See `docs/tool-inventory.md` for the Plaud asset entry, including its new MCP server support.
- TODO(Alan): clarify the actual relationship — is EmpoweredAtHome.com an affiliate for this device, a reseller, or is this a private-label/rebrand? Is the marketed device the Plaud Note Pro or the Open Vision Engineering device? Content-agent needs this to know what claims it's allowed to make (e.g. can it link to a purchase page, or only describe the product editorially?)

## EverythingInternet.ca

**Lifetime Directory Listing**
- Price: $499.00 (marked down from $2,999.00), one-time fee
- Confirmed live at everythinginternet.ca/shop — "SHOWING THE SINGLE RESULT," category tagged "REVENUE ENGINES"
- This is a B2B product: Canadian tech companies pay once for a permanent listing in the directory. It is the site's actual monetization mechanism — not a consumer product.

## SchmucksDebate.com
- Confirmed via search (direct site access currently blocked, see note below): a debate/negotiation/critical-thinking coaching platform, tagline "Fight = Debate = Negotiate," framed around Sun Tzu's Art of War principles applied to negotiation and career/life "battles." Site includes business services, certifications, video consultations, a blog, and a shop section.
- TODO(Alan): actual course/certification/consultation names and prices — not recoverable via search, site itself needs to be checked directly.

## Axiom the Novel
- TODO(Alan): could not find any trace of this anywhere online (search for title + Axiom Enterprises returned nothing). Format, price, where it's sold, one-line description safe to use in copy — all still needed.

## Golden Goose Project merchandise
- TODO(Alan): item list, pricing, where sold, and connection to the "Proud Sponsor of The Golden Goose Project — Building Stronger Communities" anchor phrase (is Axiom Enterprises the sponsor, or does merch revenue fund it?). Nothing found on SchmucksDebate.com or elsewhere to confirm this exists as an active product line yet.

## Access note (2026-08-02)
Automated fetch (WebFetch) and browser automation (Chrome extension) both hard-failed against EmpoweredAtHome.com and SchmucksDebate.com — TLS cert error / network error page / `curl` 403, while EverythingInternet.ca loaded fine through the same tools. Confirmed by Alan: this is local network filtering on this session's side, not a WAF on the sites themselves — real visitors are unaffected. No website-health concern here; it just means the remaining pricing gaps (SchmucksDebate.com courses/certifications, Pocket AI Voice Recorder relationship) need Alan to pull directly rather than another automated attempt from this environment.

## TODO(Alan)
- Anything else sold across the three sites that content-agent/sales-manager will need to reference accurately.
