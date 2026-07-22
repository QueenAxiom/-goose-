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

Alan posts 8x/day, alternating English and Spanish — each individual post is written in **one language only** (never mixed in one post). Track which language is next in `automation/content-log.md`.

> **Open discrepancy — needs Alan's call, not resolved here:** `guardian.md`'s checklist literally says to check that "both English and Spanish versions provided" per post, which reads as one post = two language versions — but `content-agent.md`'s actual instruction is single-language posts alternating across the 8/day cadence. These two source files disagree. The automated routine defaults to the more detailed, mechanism-bearing rule (alternating single-language posts, per `content-agent.md`) since it's the one with an actual tracking mechanism. Flagging rather than silently picking — update whichever agent file is stale once you confirm which behavior you actually want.

## Guardian review scope

Guardian reviews every draft from: Automation Engineer, Website Manager, Research Analyst, Content Agent, Marketing Director, Media Studio, Sales Manager, Recorder, Operations Manager — before it reaches Sophia or Alan. Nothing ships without passing this first.

## TODO(Alan)
- Confirm the language-rotation discrepancy above.
- List any platform-specific specs (image dimensions, caption character limits) per destination — not yet captured anywhere.
