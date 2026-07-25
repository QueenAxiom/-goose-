# RingCentral SMS — Webhook Subscription Registration & Renewal

Design for the two missing pieces of the N8N RingCentral SMS system. The **send** and **receive** handlers are already built and working in N8N (not documented in this repo — no `automation/*.json` exists for them). This doc covers what makes the receive handler actually receive anything in production: RingCentral doesn't push SMS events to a webhook URL until a **subscription** is registered for it, and that subscription **expires** (~7 days for webhook delivery mode, unconfirmed for Axiom's account tier) and silently stops delivering if not renewed.

Provider is RingCentral, not Twilio — see `docs/decisions-log.md` (2026-07-24). This plan touches production messaging and needs Alan's review before implementation, per `automation-engineer.md`'s standing instruction.

**Build status (2026-07-24):** importable N8N workflow JSON now exists for both workflows below — see:
- `automation/ringcentral-subscription-register.json` (Workflow 1)
- `automation/ringcentral-subscription-renew.json` (Workflow 2)
- `automation/ringcentral-webhook-handshake-snippet.js` — paste into the **existing** receive handler (see the handshake section below); not a standalone workflow.

These were built outside the N8N UI, so sanity-check node parameters on import (especially the IF-node condition syntax and the Execute Workflow node's workflow-reference field, which n8n may re-serialize slightly differently across versions). Every value only Alan can supply is marked `REPLACE_WITH_...` in the JSON — fill those in before running: the receive handler's public URL, the existing RingCentral OAuth2 credential ID, a Gmail credential ID, and (in Workflow 2) the Registration workflow's ID once both are imported.

## Prerequisite — shared OAuth2 credential

- Both new workflows reuse the **same** N8N OAuth2 credential already wired into the send/receive handlers. Do not create a second credential against the same RingCentral app.
- **Verify before building:** open the existing credential in N8N and confirm it's actually configured with a refresh mechanism (N8N auto-refreshes on 401, but only if set up that way — common silent-failure point).
- **TODO(Alan):** confirm the RingCentral app has the subscription-webhook permission scope enabled, not just SMS send/receive. Subscription create/renew/delete calls 403 without it.

## Change required to the existing receive workflow (before either new workflow runs)

RingCentral's subscription-creation call makes an immediate validation request to the webhook URL, expecting a `Validation-Token` header echoed back. This must be handled inside the **existing** receive workflow, not the new ones:

- Add a Code/Function node right after the Webhook node, before any SMS-processing logic.
- If the incoming request has a `Validation-Token` header, it's RingCentral's handshake, not a real message — respond immediately via Respond to Webhook with that same token echoed back in the response headers, empty body, and stop. Otherwise fall through to existing processing.
- Test the handshake in isolation (RC sandbox or a manual curl with a fake header) before pointing the registration workflow at production.

## Workflow 1 — Subscription Registration

Manual Trigger (run once on deploy; also exposed as an Execute Workflow Trigger so Workflow 2 can call it as a fallback).

1. **Manual/Execute Workflow Trigger**
2. **Set — Config**: `webhookUrl` (existing receive handler's public URL), `eventFilter` (SMS message-store event filter — confirm exact path against RC docs or whatever the existing receive handler already assumes), `expiresIn` (max allowed, ~604800s), `deliveryMode.transportType: WebHook`
3. **HTTP Request — Create Subscription**: `POST /restapi/v1.0/subscription`, shared OAuth2 credential, body from Config. Requires the receive-handler handshake (above) to already be live or this call fails.
4. **IF — Created OK?** (status 200/201 + `id` present)
   - True → 5
   - False → 6
5. **Set/Code — Persist Subscription ID**: extract `id`, `expirationTime`, `creationTime`. **New state this system doesn't have yet — needs Alan's call:**
   - N8N workflow static data — simplest, fine for single-subscription/single-number scope
   - A DB row — better if planning multiple numbers/accounts later
   - Env var/credential — not recommended, awkward to write programmatically
   - Recommendation: static data now, revisit if scaling.
6. **Set/Code — Format Error** (False branch): capture status + body. Common causes: handshake not implemented yet, missing scope (403), malformed filter (400).
7. **Notification node** (both branches): success with ID + expiry, or failure with error. Don't skip — a failed registration with no alert is the same blind spot as an expired subscription.

## Workflow 2 — Subscription Renewal

Schedule Trigger, daily, off-peak (e.g. 3am) — comfortably inside the ~7-day TTL with room for retries.

1. **Schedule Trigger** — daily
2. **Code/Set — Read Persisted Subscription ID** (from wherever step 5 above wrote it). No ID found → skip straight to step 5 (fallback).
3. **HTTP Request — Renew Subscription**: `POST /restapi/v1.0/subscription/{id}/renew`, shared credential.
4. **IF — Renewed OK?** (status 200 + updated `expirationTime`)
   - True → 6
   - False → 5. Causes to distinguish: 404 (already expired/deleted server-side — the exact failure mode this workflow exists to catch), 401 after refresh already attempted (credential misconfigured — alert loudly, don't retry-loop), 403 (scope revoked).
5. **Execute Workflow — Fallback: Re-register** (False branch): calls Workflow 1 as a sub-workflow rather than duplicating creation logic. Pass a `reason: renewal-fallback` flag so Workflow 1's notification distinguishes "fresh deploy" from "had to recover" — the latter means something's wrong upstream and Alan should know even though it self-healed.
6. **Set — Update Persisted Expiry** (True branch): overwrite stored `expirationTime` (and ID, if RC ever rotates it on renew — verify against actual response; RC typically doesn't).
7. Notification fires from Workflow 1's node when the fallback path is taken, not duplicated here, to avoid double-alerting on one incident.

## TODO(Alan) — decisions needed before build

| Dependency | Decision needed |
|---|---|
| Subscription ID persistence | Static data vs. DB row vs. env var (see Workflow 1 step 5) |
| Webhook validation handshake | Add to existing receive workflow, test standalone, before running registration against production |
| OAuth2 credential refresh | Confirm the existing shared credential is actually configured with refresh, don't assume |
| Event filter string | Confirm exact filter path against what the existing send/receive handlers assume, or current RC API docs |
| Renewal cadence | Daily recommended against ~7-day TTL — confirm actual TTL for Axiom's RC account tier |
| ~~Alert channel~~ | **Resolved 2026-07-24:** Gmail draft, matching the pattern already used by `automation/content-log.md` and `automation/prospecting-log.md`. Built into both workflows' Notify nodes. |

No files in the actual N8N instance have been changed — this is a plan for Alan or a reviewer to build directly in N8N.
