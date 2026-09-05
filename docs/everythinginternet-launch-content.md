# EverythingInternet.ca — Launch Content Package

Ready-to-paste copy for the live WordPress site, which is currently a barely-touched default "Twenty Twenty-Five" install (bare $499 product, one blog post with a typo, stock theme footer links). Pulled from the already-approved `prototypes/everythinginternet-directory.html` (2026-08-12 decisions — real companies, tone, pricing) and the product description drafted earlier this session. Each section below is a self-contained block — copy directly into the matching WordPress page/product editor.

**Verified 2026-08-17 against live site:** the real WooCommerce product ID is **13**, not 246 — 246 was wrong and has been corrected everywhere it appeared (this file and both CTA buttons in `prototypes/everythinginternet-directory.html`). Confirmed directly from the live product page's add-to-cart button (`value="13"`). `/shop/`, `/cart/`, `/checkout/`, `/my-account/` all confirmed live and working.

---

## Funnel update (2026-08-17, later same day)

Alan's pushback: "websites have a sales funnel - you wanted me to sell a pile of shit" — correct, the board-first reorder above was a layout fix, not a funnel. Got a real funnel structure from marketing-director and **implemented it directly in `prototypes/everythinginternet-directory.html`** (not just planned — the file now has this structure):

1. **Hero (hook)** — rewritten: "The permanent home for Canadian tech companies online."
2. **Board (proof)** — reframed as "Already Listed: 1Password. Shopify. Wealthsimple..." instead of a neutral "browse the board" framing.
3. **The Gap (new section + 1st CTA)** — "Your competitors aren't on this board yet" + "Claim Your Listing — $499" button.
4. **For Companies / For Browsers** — unchanged, the "who this is for" pitch.
5. **Objections (new FAQ section)** — 3 direct answers: why not free, how is this different from Google/LinkedIn, what if the directory doesn't grow.
6. **Founding Members (new, 2nd proof point)** — reframes the board as a founding-rate story, no fake urgency claim beyond what's real (price literally is a founding rate right now).
7. **Pricing + final CTA** — the $1,499 tier card is REMOVED from this page (matches the single-product scope decision above), single $499 card with its own "Get Listed" button.

**Not yet done, worth doing before this goes live:** the email-anchor-jump idea — outbound emails to warm/researched prospects should link mid-funnel (e.g. `/#board` or `/#pricing`) instead of the cold-hero hook, since those recipients already have context. Currently the 3 drafted Gmail outreach emails aren't confirmed to use anchor links — check before sending.

**Resolved 2026-08-17:** Alan confirmed directly — $2,999 was a real price. Not an open item, don't re-raise it.

---

## Scope note (2026-08-17, Alan's direction)

**Launch with ONE product only — the $499 Lifetime Directory Listing.** The $1,499 Featured Placement tier (Section 4 below) is drafted but explicitly OUT of scope for now — don't build or publish it yet.

**The directory board IS the front page.** Alan's words: "they have to see the shiny car before they buy right now u don't even show them a car" — then, clarifying further, "no - they directory should be the front page." This is not just "reachable without a click" — the board comes immediately after a minimal hero strip, before anything else, including the "For Companies / For Browsers" pitch copy and pricing. Corrected 2026-08-17 in `prototypes/everythinginternet-directory.html` directly: section order is now Hero → Board → For Companies/For Browsers → Pricing (previously Hero → For Companies/For Browsers → Board → Pricing). The content package below reflects this corrected order.

---

## 1. Homepage (single page — hero and board together, board visible without clicking anywhere)

**Hero eyebrow:** Now Live — Canada's Tech Directory

**Headline:** Canada's tech companies. Found.

**Subhead:** One directory, built the way Canadian businesses actually find each other — no pay-to-play rankings, no noise. Just real companies doing real work.

**CTAs:** "Browse the Directory" (scrolls down to the board on this same page) · "Get Listed — $499" (links to Shop)

**Immediately below the hero — the board itself, not a link to it:**

**Eyebrow:** The Directory
**Title:** 29 companies. Tuned in.
**Lede:** The real board — real Canadian companies, real categories, the kind of listing your company joins from day one.
**Disclaimer (small text, directly under the lede):** Shown for illustration: real, notable Canadian tech companies in each category. Inclusion here isn't an endorsement or paid partnership — it's a picture of the caliber of company this board is built for.

**The board** (Name — Category — Location — Description — Link):

1. **1Password** — Password & Security — Toronto, ON — Password, passkey, and security vault for individuals and enterprises. — https://1password.com/
2. **Ada** — AI & Customer Service — Toronto, ON — AI-native customer service platform and voice AI agents for automated support at scale. — https://www.ada.cx/
3. **Benevity** — Corporate Giving & Grants — Calgary, AB — Employee giving, volunteering, grants management, and impact reporting platform. — https://www.benevity.com/
4. **Blackberry** — Secure Communications — Waterloo, ON — Critical event management, crisis communications, and sovereign-grade secure communications. — https://www.blackberry.com/
5. **Blackberry QNX** — Embedded Systems — Ottawa, ON — Embedded OS and middleware for safety-critical vehicles, medical devices, and industrial systems. — https://qnx.com/
6. **Clio** — Legal Practice Management — Vancouver, BC — Legal practice management, CRM, accounting, payments, and AI tools built for law firms. — https://www.clio.com/
7. **Coveo** — AI Search & Recommendations — Québec City, QC — AI relevance platform delivering search, recommendations, and generative experiences for enterprises. — https://www.coveo.com/
8. **D2L** — Learning Management — Kitchener, ON — Learning management (Brightspace), content authoring, and ecommerce for corporate training and education. — https://www.d2l.com/
9. **Dayforce** — HR & Payroll — Toronto, ON — Unified payroll, HR, talent, workforce management, and AI-powered people platform. — https://www.dayforce.com/
10. **Ecobee** — Smart Home — Toronto, ON — Smart thermostats, doorbell cameras, and connected home security systems. — https://www.ecobee.com/
11. **Fongo** — VoIP & Business Phone — Mississauga, ON — VoIP calling, texting, and cloud business phone services for Canadian consumers and businesses. — https://www.fongo.com/
12. **Freshbooks** — Accounting & Invoicing — Toronto, ON — Cloud accounting, invoicing, payments, and time tracking built for small and medium businesses. — https://www.freshbooks.com/
13. **Geotab** — Fleet & Vehicle Telematics — Oakville, ON — Fleet telematics hardware, analytics, driver management, and marketplace for connected vehicles. — https://www.geotab.com/
14. **Hootsuite** — Social Media Management — Vancouver, BC — Social media management and social listening suite for brands and agencies. — https://www.hootsuite.com/
15. **Jane Software** — Healthcare Practice Management — Vancouver, BC — Clinic and practitioner management platform with telehealth and online booking. — https://jane.app/
16. **Jobber** — Field Service Management — Edmonton, AB — Field service management for home-service businesses — scheduling, invoicing, and client management. — https://www.getjobber.com/
17. **Kinaxis** — Supply Chain Planning — Ottawa, ON — AI-enabled supply chain planning and orchestration for global enterprises. — https://www.kinaxis.com/
18. **Later** — Social Media Scheduling — Vancouver, BC — Social media scheduling, publishing, and influencer marketing platform. — https://later.com/
19. **Lightspeed** — Retail & Restaurant POS — Montréal, QC — Retail POS, restaurant POS, ecommerce, and integrated payments for merchants. — https://www.lightspeedhq.com/
20. **Miovision** — Smart City Traffic Management — Kitchener, ON — Traffic operations cloud, video traffic data collection, and AI signal optimization for smart cities. — https://miovision.com/
21. **Nanoleaf** — Smart Lighting — Toronto, ON — Modular smart lighting panels, bulbs, and connected lighting systems for homes and offices. — https://nanoleaf.me/
22. **Opentext** — Enterprise Content Management — Waterloo, ON — Enterprise content management, B2B integration, cybersecurity, DevOps, IT operations, analytics, and AI. — https://www.opentext.com/
23. **Pointclickcare** — Senior Care EHR — Mississauga, ON — Senior care EHR and operational platform with AI-powered advisory tools for long-term care. — https://www.pointclickcare.com/
24. **Rakuten Kobo** — eBooks & eReaders — Toronto, ON — eBook and audiobook app plus e-reader hardware (Clara, Libra, Sage, Elipsa). — https://www.kobo.com/
25. **Safe Software** — Data Integration & Automation — Surrey, BC — Enterprise data integration (FME), automation, and spatial data authoring tools. — https://safe.com/
26. **Shopify** — Ecommerce Platform — Ottawa, ON — All-in-one commerce platform — checkout, payments, POS, creator tools, and affiliate marketplace. — https://www.shopify.com/
27. **Soti** — Enterprise Mobility Management — Mississauga, ON — Enterprise mobility management, device diagnostics, IoT management, and low-code business apps. — https://soti.net/
28. **Thinkific** — Course & Community Platform — Vancouver, BC — Course, community, membership, and creator monetization platform for knowledge entrepreneurs. — https://www.thinkific.com/
29. **Wealthsimple** — Trading & Investing — Toronto, ON — Trading, managed investing, cash accounts, tax filing, and crypto platform for Canadians. — https://www.wealthsimple.com/

**Trust line:** No pay-to-play rankings, no pay-to-fake reviews.

**Immediately below the board — For Companies / For Browsers (two columns):**

*For Companies — Get Discovered*
- Get discovered by buyers who are already searching — not scrolling past another ad.
- One flat $499, once. No subscription, no algorithm to keep feeding.
- Submit your details, set your listing, and it's yours — no pay-to-play rankings, ever.

*For Browsers — Compare Honestly*
- Every listing is a real, verified company — not a sponsored slot dressed up as a result.
- Compare by category, not by who paid the most this month.
- Built by Canadians who got tired of guessing too.

**Closing line (bottom of homepage):** List your company. Or find the one you've been looking for. Either way, welcome to the directory Canada actually needed.

---

## 3. Shop — $499 Lifetime Directory Listing (only product for launch — replace bare listing)

**Title:** Lifetime Directory Listing

**Short description:**
Get your company in front of the Canadian tech buyers already searching for it. One flat fee, listed for good — no renewals, no algorithm to feed, no pay-to-play rankings.

**Full description:**
EverythingInternet.ca is Canada's honest tech company directory — a place buyers go to compare real Canadian vendors, not scroll past another ad. The Lifetime Directory Listing puts your company permanently on that board, alongside established Canadian names buyers already trust.

This is a one-time fee, not a subscription. Set your profile up once and you're listed for good — no renewal invoices, no "boost your ranking" upsells, no fake reviews inflating anyone's position.

**What you get:**
- Permanent listing — no renewal fees, ever
- Full profile setup handled for you: send your company details, we get you live
- A dedicated profile page: company description, category tag, logo, contact info, and outbound link to your site
- Equal footing in your category — no pay-to-play ranking games
- Placement in the same directory Canadian buyers browse when comparing vendors

**See the Directory:** Browse the current board before you list: [link back to the homepage board, e.g. `/#board`]. Every company shown there is real — we don't publish fictional listings to pad the count.

**Trust line:** No pay-to-play rankings, no pay-to-fake reviews.

---

## 4. Shop — $1,499 Featured Placement — **DEFERRED, not part of this launch**

Alan's direction 2026-08-17: ship with the $499 listing only for now. Keep this copy drafted and ready, but do not build or publish this product until told otherwise.

**Title:** Featured Placement — Directory Listing

**Short description:**
Everything in the standard listing, plus top billing. For companies who want to be the first name a buyer sees in their category — not just on the board, but at the front of it.

**Full description:**
Featured Placement includes everything in the Lifetime Directory Listing, with one difference: priority position. Your listing appears at the top of your category and gets homepage placement, so buyers browsing the directory see your company first — not after scrolling past everyone else in your space.

This is a one-time fee, same as Standard — no recurring cost, no bidding war for position. You pay once for the top spot and keep it.

**What you get:**
- Everything in the Standard Listing (permanent listing, full profile, no renewal fees)
- Priority position within your category's directory board
- Homepage placement
- Best fit for companies launching a new product or service and wanting maximum visibility from day one

**Trust line:** No pay-to-play rankings, no pay-to-fake reviews — Featured Placement is a paid position upgrade, not a ranking manipulation; it's disclosed as what it is.

---

## 5. Footer (site-wide — replaces stock WordPress "Patterns" / "Themes" theme-demo links)

Logo: EVERYTHINGINTERNET

Links: Browse Directory · Pricing · Shop · Cart · Checkout · My Account · Contact (mailto:rise@empoweredathome.com) · Privacy Policy · Terms and Conditions

Anchor line: Proud Sponsor of The Golden Goose Project — Building Stronger Communities

Copyright line: © 2026 Axiom Enterprises. All rights reserved. · rise@empoweredathome.com

**Note:** the current live footer shows "Patterns" and "Themes" — these are unmodified WordPress theme-demo defaults, not site content. Remove them and replace with the links above.

---

## 6. One-line fix

Blog post typo: "believe3s" → "believes" — in the "Largest AI Contribution" post (dated 2026-08-13). Exact location within the post body wasn't confirmed from outside WordPress; search the post content for "believe3s" to find it.

---

## Open items not covered by this package

- **Refund policy** (`prototypes/everythinginternet-terms.html` §4.3) is still an unresolved placeholder — needs Alan's decision before Terms goes live.
- **Governing province** (§11 of the same file) also needs Alan's confirmation.
- Both Terms and Privacy Policy pages exist as drafts (`prototypes/everythinginternet-terms.html`, `everythinginternet-privacy.html`) but are marked pending legal review — not rewritten here, just flagged.
