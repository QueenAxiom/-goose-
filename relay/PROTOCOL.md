# Relay: edit locally, publish once

Everything lives here until the final round. Nothing is written to any site during relay.

## Files
- `current.html` - the working draft. `sites/<domain>/index.html` - per-site copies for preview.
- `preview.cmd` - serves them at http://127.0.0.1:8800/sites/<domain>/ (127.0.0.1 only).
- `outbox/round-NN-to-<model>.md` - what ECC hands to a model (draft code + brief + checklist).
- `inbox/round-NN-from-<model>.md` - that model's reply (paste it here).
- `STATUS.md` - verdict per model per round.

## Order (one round = a full lap)
ECC edit -> GPT -> ECC -> Claude -> ECC -> Claude Code -> ECC -> GPT -> ECC -> DeepSeek -> ECC -> Kimi -> ECC
After each reply ECC applies the edits to `current.html` (and the site copies), logs it, and writes the next outbox file.

## Checklist sent with every handoff
- "SI", never "AI". "sir", never "puppy". Footer: (c) Axiom Enterprises.
- No localhost links, no private ops detail, picture kept, big picture only.
- Reply with: VERDICT: AGREE or CHANGES, then the full revised code.

## Done
A lap where all models answer AGREE on unchanged code. Then, and only then: staging, Sofia's yes, Alan's yes, production.
