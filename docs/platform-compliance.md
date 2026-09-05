# Platform Compliance — Axiom Enterprises

Seeded from `content-agent.md` (Mandatory Post Elements) and `guardian.md` (Guardian Compliance Checklist). Guardian rejects anything missing these rather than letting it through with a note.

## Mandatory Post Elements (every social/blog/email/product-listing post)

Unless it's a video post, or Alan explicitly waives a rule for that specific post:

- Product photo — must be a **real photo of the actual product**, never an abstract, stock, or lifestyle-only shot as the hero image (coordinate with media-studio for the spec; the actual photo is supplied by Alan or a production tool — media-studio only produces briefs, not final assets)
- The offer stated clearly in the text/caption
- Contact email: `rise@empoweredathome.com`
- A mention of the relevant site (EmpoweredAtHome.com, EverythingInternet.ca, or SchmucksDebate.com — all three if the offer spans more than one)
- A link to the relevant site where the platform supports inline links; where it doesn't (e.g. Instagram captions), say "link in bio" and the bio link must point there
- Formatting matched to the destination platform's specs (image dimensions, caption length, etc.)
- AI-generated content disclosure where the destination platform requires it

If the destination platform requires video rather than a photo + caption: don't force a photo-based post — flag that it needs video and stop. Alan creates the video himself.

## Language rotation

RESOLVED 2026-09-04, supersedes the discrepancy note below. Alan posts 8x/day, cycling one language per post through this fixed 8-language order (each individual post is written in **one language only** — never mixed):

1. English (en)
2. Spanish (es)
3. French (fr)
4. Arabic (ar)
5. Ukrainian (uk)
6. Chinese (zh)
7. Japanese (ja)
8. Filipino/Tagalog (fil)

Track which language is next in `automation/content-log.md` (cycles through the 8 in order, wrapping back to English after Filipino). This applies to social/ad post rotation — separate from the LOCKED EN/FR bilingual requirement for the *website rebuild* itself (`docs/decisions-log.md`, 2026-08-03 entry, Quebec Bill 96), which is a full-site parity requirement, not a rotation.

> Former discrepancy (now resolved): `guardian.md` previously said to check for "both English and Spanish versions" per post, while `content-agent.md`'s actual mechanism was single-language posts alternating across the 8/day cadence. The single-language-per-post model (with the 8-language cycle above) is now the confirmed behavior — `guardian.md` has been updated to match.

## Platform specs (defaults — override per Alan's actual guidance if given later)

| Platform | Image size | Caption/copy limit |
|---|---|---|
| Instagram feed | 1080x1080 (square) or 1080x1350 (portrait) | ~2,200 char max, front-load first 125 chars |
| Facebook Page | 1200x630 (link/share image) | ~500 char recommended |
| X / Twitter | 1600x900 | 280 char max |
| Blog/website featured image | 1200x630 (also serves as OG image) | N/A |

## Post Inspection Checklist (Guardian checks every post against this, in addition to Mandatory Post Elements above)

- [ ] Language of this post clearly labeled (one of the 8 above) and correctly next-in-rotation per `automation/content-log.md`
- [ ] Destination platform clearly labeled (e.g. "Instagram — square 1080x1080")
- [ ] Image/media sized to the platform spec table above (or explicitly flagged as needing a custom size with reason)
- [ ] All Mandatory Post Elements above still satisfied

If a post fails any item, Guardian rejects it with the specific failing item(s) — it does not pass anything through "with a note."

## Content Approval Pipeline (full flow, updated 2026-09-04 — variable-round council)

Every post goes through a Guardian interim check, then **Alan-controlled** external council rounds (as many as he wants — one, two, six, whatever), then a Guardian final check before Alan publishes. Nothing skips a step, no round count is assumed, and nothing publishes without Alan's own final action.

1. **Draft** — Content Agent drafts the post per Mandatory Post Elements above.
2. **Guardian interim check** — Guardian runs the Post Inspection Checklist. If it fails, it's rejected back to Content Agent with the specific failing item(s). If it passes, Guardian creates a Gmail **draft** to `rise@empoweredathome.com` (never a live send) asking Alan to confirm it's ready to go to external council review. Logged in `automation/content-log.md` as `status: drafted (interim)`.
3. **External council round** — the agent prepares a copy-paste-ready package: the current post text/caption plus a review prompt (e.g. "Review this post for [site]'s brand voice and tone, suggest edits: <post>" for a first opinion, or "check this and suggest improvements or additions" for later ones). Alan pastes this into whichever external AI platform he chooses, then pastes the response back into the session. No API integration — this is a manual relay, Alan is the courier.
4. **Incorporate the round** — the agent merges that platform's suggested edits into the post.
5. **Mandatory check-in — the agent MUST ask before doing anything else**: "Do you want to stop here, or get another opinion?" This is not optional and not inferred — the agent asks explicitly after every single round, including the first. It never assumes one round is enough and never assumes Alan wants more.
   - If Alan says get another opinion → repeat steps 3–5 (a new external round, which can be the same platform or a different one each time — Alan's choice, no fixed count).
   - If Alan says stop → proceed to step 6.
6. **Guardian final check** — once Alan says stop, Guardian re-runs the full Post Inspection Checklist on the fully revised post (external edits can break compliance — e.g. drop the contact email, change length past a platform's caption limit — so this is a full re-check, not a rubber stamp). If it fails, it's rejected back for correction (and re-enters the council loop if Alan wants further opinions on the fix). If it passes, Guardian creates a **final** Gmail draft to `rise@empoweredathome.com` summarizing the final version — site/campaign, language, platform, size, offer, and how many council rounds it went through — asking for final confirmation. Logged in `automation/content-log.md` as `status: drafted (final)`.
7. **Alan's final approval & publish** — Alan confirms via that final email and publishes the post himself. No agent auto-publishes at any stage — matches the locked no-zero-touch-bypass decision (`docs/decisions-log.md`, 2026-08-02 entry).

## Guardian review scope

Guardian reviews every draft from: Automation Engineer, Website Manager, Research Analyst, Content Agent, Marketing Director, Media Studio, Sales Manager, Recorder, Operations Manager — before it reaches Sophia or Alan. Nothing ships without passing this first.
