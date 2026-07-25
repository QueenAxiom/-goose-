# Decisions Log — Axiom Enterprises

Referenced by `operations-manager.md` and `recorder.md` (global agent configs) as the locked source of truth for past decisions. Entries here are **locked**: once a row is added, it is not silently reprioritized around, reversed, or re-debated — only Alan can supersede a decision, and doing so should add a new row noting what changed and why, rather than editing the old one.

| Decision | Choice | Date |
|---|---|---|
| Runway API integration timing | Deferred — not until 2026-07-29 at the earliest (video automation not a priority yet) | 2026-07-24 |
| Messaging/telephony provider | RingCentral (existing paid account) instead of Twilio — no need to pay for/provision a second phone number when RingCentral's API covers SMS/voice | 2026-07-24 |
| RingCentral subscription workflow alert channel | Gmail draft (matches existing `content-log.md`/`prospecting-log.md` automation-notification pattern) over Slack or self-SMS | 2026-07-24 |

## TODO(Alan)
- This log was empty when created — no decisions had been recorded anywhere in the repo. Add entries here as decisions get made, or ask Recorder to log them after calls/meetings.
