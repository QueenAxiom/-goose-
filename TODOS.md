# TODOs — Axiom Enterprises

Deferred work items surfaced during planning/review sessions. Each item includes context so it's actionable months later, not just a bullet point.

## v2: Real gadget integration for the Jarvis voice AI demo

**What:** Wire the EmpoweredAtHome "Jarvis" demo (`~/.gstack/projects/QueenAxiom--goose-/DELL-main-design-20260811-053653.md`) up to actually control the real smart-home gadget via its API/webhook, replacing the v1 scripted/simulated gadget response.

**Why:** v1 deliberately ships with a simulated gadget response to test the funnel fast (Premise 1). If v1 content actually drives traffic/conversion, real device control becomes the credible next differentiator — but only then, not before.

**Pros:** Makes the demo mechanism a genuine capability instead of a one-off video prop; closer to Alan's longer-term "sellable product" ambition stated in the original problem statement.

**Cons:** Real device integration means firmware/API work, auth, latency handling, and failure modes with a physical product — a multi-week project, not a weekend build. Not worth it if v1 doesn't prove the funnel works.

**Context:** During eng review, it was confirmed (Assignment #1) whether the gadget has any voice-control capability at all — check that record before scoping this. If the gadget can't be controlled this way in principle, this TODO may need to become "evaluate a different gadget" instead.

**Depends on / blocked by:** v1 shipping and clearing its success bar (both CTR and conversion targets met, per the design doc's Success Criteria).

---

## Sharpen the target persona using v1 engagement data

**What:** Replace "curious early-adopter professional" (still a category, never resolved to a specific person across the office-hours and eng-review sessions) with an actual persona, informed by who engages with the v1 content.

**Why:** The design doc proceeded without a resolved persona because resolving it further didn't block v1 (the demo format is generic enough to work across platform/persona variants). But post-v1, real engagement data (who watches, who clicks, who buys) is the cheapest way to actually answer the question instead of guessing again.

**Pros:** Turns a genuinely unresolved unknown into a data-backed answer instead of another round of speculation; sharpens targeting for any v2 content or paid promotion.

**Cons:** None significant — this is low-cost to do once data exists; the only cost is doing it too early (before there's data to look at).

**Context:** See `DELL-main-design-20260811-053653.md`, "Target User & Narrowest Wedge" section — pushed twice during office-hours, stayed at "curious early-adopter professional" both times.

**Depends on / blocked by:** v1 shipping and accumulating enough engagement data to actually read a pattern from (not just a handful of views).
