# Website Ecosystem Rebuild — Council Recommendation

Status: **Stack, domain architecture, and sequencing LOCKED — see `docs/decisions-log.md` 2026-08-06 entries.** Build horizon: roughly one year, not the tight weekly schedule below (kept as a proposed internal cadence, not a hard deadline). Current catalog/positioning on EmpoweredAtHome and SchmucksDebate is expected to change as this rebuild proceeds — the "tension" flagged below is being resolved through the rebuild itself, not treated as a precondition. Produced 2026-08-06 by convening architect, marketing-director, and media-studio agents in parallel against Alan's brief: rebuild alangooding.ca, schmucksdebate.com, everythinginternet.ca, and empoweredathome.com to "multimillion dollar sales grossing companies" credibility standards, targeting professional companies and the people who work at them, each site fit to its own market, built in "the current industry standard programming language."

---

## The tension to resolve first

Two of the four properties, as currently built, don't match the stated audience:

- **empoweredathome.com** — confirmed catalog is a $50 ebook and a possibly-affiliate ~$79 gadget. That's a prosumer/individual buyer, not corporate procurement. Nothing wrong with that market — but it's not "professional companies."
- **everythinginternet.ca** — the one property that DOES match the brief (companies pay $499–$2,999 for a directory listing) is currently showing "single result" in its own shop — i.e., the directory looks empty to the exact buyer it needs to convince.
- **schmucksdebate.com** — currently framed as consumer career/life-coaching ("your life is a battle"). Marketing's read: the underlying skill (negotiation, critical thinking) is a legitimate B2B corporate-training category that would match the brief far better than the current self-help framing — but that's a repositioning call, not a copy tweak.

None of this blocks starting the work, but it means "hit the credibility bar" isn't just a design problem on 2 of the 4 sites — it's a positioning/catalog problem first. Flagging so it's a conscious choice.

---

## 1. Stack recommendation (architect)

**Next.js 15 (App Router) + TypeScript + Tailwind, one monorepo, Sanity CMS, Stripe, Vercel hosting.**

- One shared codebase (`apps/empoweredathome`, `apps/everythinginternet`, `apps/schmucksdebate`, `apps/alangooding` + shared `packages/ui, i18n, cms, commerce`) — this is what actually delivers "one consistent, professional brand system" without merging domains.
- `next-intl` for EN/FR, locale as a real route segment (`/en/`, `/fr/`) — required for Bill 96, and built locale-agnostic from day one so adding Spanish later (still open per 2026-08-03 decisions-log) is config, not a rewrite.
- Sanity over Payload/headless WordPress specifically because this team has already proven it can't keep self-hosted infrastructure alive (see SchmucksDebate's outage) — managed services minimize that failure mode.
- Stripe, not a full WooCommerce-equivalent platform — the real catalog across all three brand sites is ~3-5 products/services, mostly digital. Building commerce machinery for inventory/shipping that doesn't exist yet is the single biggest avoidable cost in this project. Shopify headless is the documented upgrade path *if* EmpoweredAtHome becomes real physical retail — decide that at the start of that site's phase, not now.

## 2. Domain architecture — the 2 scenarios, compared

This directly answers the "put everything on one site with subdomains" advice Alan was given previously.

| | **A — Four separate domains** | **B — alangooding.ca as parent, brands as subdomains** |
|---|---|---|
| SEO | Each domain keeps its own authority; everythinginternet.ca's descriptive `.ca` name carries real signal for its exact audience | Subdomains are treated by Google as largely separate sites anyway — B pays the fragmentation cost of separate domains AND the dilution cost of consolidation, without cleanly getting either benefit |
| Brand separation | Three genuinely different buyers (consumer smart-home, B2B directory, negotiation training) can each present cleanly | Forces one nav/IA/voice across three unrelated buyer types; couples reputations |
| Credibility bar | Matches how real multi-brand companies operate | **Fails the actual goal**: a company buying a $499 B2B listing expects to transact on everythinginternet.ca, not a founder's personal-name domain — that reads *smaller*, not bigger |
| Engineering cost | Slightly higher (4 domains, 4 DNS/analytics setups) — but with the shared monorepo, the 4th site's marginal cost is config, not code | Slightly lower ops overhead — the only category where B wins |

**Recommendation: A.** Keep four separate domains. The real fix for what the "put it all on subdomains" advice was reaching for — consistency, one design system, one maintenance burden — comes from the shared monorepo/codebase, not from merging domains. alangooding.ca's role: founder/authority hub that **links to** the three brands (portfolio-of-companies credibility), not a parent that absorbs them. This stays reversible — because everything shares one codebase, a future move to subdirectories (the technically-correct version of "consolidate," if ever wanted) is a routing change, not a rebuild.

## 3. WordPress Pro — reconciling with what Alan said

Alan indicated wanting to move onto a new WordPress.com Pro plan in one conversation, then asked for a full modern-stack rebuild in the next. Architect's read: **these only conflict if Pro is treated as the destination.** They reconcile if Pro is just a stopgap.

**Question for Alan: has WordPress.com Pro already been purchased/committed?**
- If yes — use it only to host a bilingual holding page for schmucksdebate.com for the next few weeks, migrate nothing onto it, let it lapse.
- If no — don't buy it. Put that budget toward French translation instead (see below — it's the actual critical-path risk).

Either way: migrating the two *healthy, revenue-carrying* sites (EmpoweredAtHome, EverythingInternet) onto WordPress Pro now, only to rebuild them again in a few months, is pure downside with no upside. Recommend the WordPress Pro migration be marked superseded in the decisions log once Alan confirms.

## 4. Sequencing

1. **This week** — resolve whether SchmucksDebate's content still exists (backup/export check); ship a bilingual holding page so it stops 404ing; verify EverythingInternet's $499 checkout actually completes (flagged as a possible live revenue outage, not just a cosmetic gap); start French translation procurement now (longest lead-time item in the whole plan).
2. **Weeks 1-4 — SchmucksDebate.com first.** It's already down, so there's no migration risk and nothing to break. This phase builds the real deliverable: the shared platform (monorepo, design system, i18n pipeline, CMS model, Stripe, deploy process). The site is small; the platform is the point.
3. **Weeks 5-9 — EverythingInternet.ca.** The B2B revenue product and the audience closest to Alan's brief — attack its harder content model (directory/listings/search) once the platform is proven.
4. **Weeks 10-14 — EmpoweredAtHome.com.** Last of the three brand sites, precisely because it's the one already healthy and taking money — highest cost of a mistake.
5. **Weeks 15-17 (or parallel, low-priority) — alangooding.ca.** Zero existing traffic/revenue, can wait, benefits from a matured design system.

## 5. Per-site positioning (marketing-director)

- **empoweredathome.com** — practical, no-hype AI/smart-home guidance for professionals buying for their own home, not a B2B facilities sale. *"Smart home and AI, explained by people who use it — not people selling it to you."* Open question: is "professional companies" here meant literally (pivot to B2B proptech) or "professionals as individual buyers" (matches current catalog)? Also: the Pocket AI Recorder's affiliate/reseller/private-label status is still unresolved and blocks any claims-heavy copy.
- **everythinginternet.ca** — the one site that already matches the brief: paying customer is a company buying visibility. Two-track messaging (companies: "get discovered"; browsing consumers: "the honest way to compare"). Biggest open question, genuinely blocking: is this a lead-gen directory or an e-commerce storefront? The WooCommerce backend and the directory-only front end currently disagree.
- **schmucksdebate.com** — recommend repositioning from consumer "life is a battle" self-help toward **B2B corporate negotiation/critical-thinking training** — same sharp, no-fluff voice, sharper buyer (sales teams, procurement, executives). *"Negotiation training for people whose job depends on winning the room."* Blocked entirely until the site is back up.
- **alangooding.ca** — the "meta-trust" layer: people check this before trusting the other three. Needs a real answer to what actually connects the three brands as one operator's thesis — currently a documented TODO nobody's written (`ecosystem-reference.md`). Provisional line: *"One operator, three doors into better decisions — at home, online, and at the table."* Not to be treated as locked.

## 6. Design direction (media-studio)

Four visually distinct directions, each independently hitting the credibility bar — not one template reused four times:

| Site | Register | Palette direction |
|---|---|---|
| alangooding.ca | Executive personal-brand, editorial-minimal | Charcoal/graphite + warm off-white, restrained bronze/gold accent |
| everythinginternet.ca | Editorial-trustworthy, proud-Canadian (not kitsch) | Deep ink navy + paper off-white, considered red accent |
| empoweredathome.com | Clean D2C-premium, product-forward | Warm neutral/sand, teal or emerald accent |
| schmucksdebate.com | Bold, high-contrast, confrontational-but-credible | Near-black + stark white, amber/red accent |

EN/FR selector on all three brand sites: an equal-weight "EN | FR" segmented control in the primary header row — same size/weight as top-level nav, never a small flag icon or footer dropdown, persists through checkout on EmpoweredAtHome. This is a compliance requirement (Bill 96: French not subordinate), not a style preference.

---

## Locked (2026-08-06, see decisions-log.md)

- Stack: Next.js 15 + TypeScript + Tailwind monorepo, Sanity CMS, Stripe, Vercel, `next-intl`.
- Domain architecture: four separate domains, not subdomains — codebase/design system is shared, domains are not.
- Sequencing: SchmucksDebate.com first (pilot — already down, nothing to break), then EverythingInternet.ca, then EmpoweredAtHome.com, then alangooding.ca, over a roughly one-year horizon rather than the tight week-by-week schedule above.
- Current catalog/positioning gaps (EmpoweredAtHome's consumer-only catalog, SchmucksDebate's self-help framing) are not blockers — expected to evolve through the rebuild itself.

## Rolled into Phase 0 investigation (not pre-build blockers)

1. **WordPress.com Pro** — was it already purchased/committed? If yes, use only as a temporary bilingual holding page for schmucksdebate.com; migrate nothing onto it.
2. **SchmucksDebate.com** — was the outage deliberate, and does a content backup exist? Biggest schedule unknown in the plan — resolve early in Phase 1.
3. **EverythingInternet.ca** — does the $499 listing checkout currently complete? Check before positioning/design work lands, since a broken checkout is a live revenue issue, not a cosmetic one.

## Still open — needs Alan's input before the relevant phase, not before starting

4. ~~**EverythingInternet.ca** — lead-gen directory or e-commerce storefront?~~ **ANSWERED 2026-08-08** (see `docs/decisions-log.md`): it's a multi-vendor marketplace — vendors self-onboard and connect their own Stripe account via Split Pay's Stripe Connect flow, platform takes a cut. Changes the homepage's entire job accordingly; carry into Phase 2 (weeks 5-9) design.
5. **EmpoweredAtHome.com** — real physical inventory coming, or staying digital/affiliate? Also: Pocket AI Recorder's actual relationship to Axiom (affiliate/reseller/private-label). Needed before Phase 3 (weeks 10-14).
6. **SchmucksDebate.com repositioning** — consumer career-coaching vs. B2B corporate-training? Marketing recommends B2B; needed before Phase 1 content work.
7. **alangooding.ca** — the "three doors" thesis connecting the three brands still isn't written down anywhere (`ecosystem-reference.md` TODO). Needed before Phase 4, and before any positioning copy is drafted for that site. Does it need EN/FR too?
8. Spanish on the sites — still open since 2026-08-03; cheap to absorb now (stack is built locale-agnostic), expensive to retrofit later.
9. Is a corporate `axiomenterprises.*` domain wanted for a parent-brand role, separate from Alan's personal domain?
