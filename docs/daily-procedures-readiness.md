# Daily Procedures — Readiness Punch List

Status snapshot as of 2026-08-02. Tracks what's blocking each scheduled/recurring n8n automation from actually running unattended. See `docs/decisions-log.md` for the decisions behind these builds, and each workflow's own doc (`docs/*-workflow.md`) for full build history.

## Summary

| Workflow | Ready to test? | Blocking item |
|---|---|---|
| Facebook scheduled post | No | Live n8n workflow is in a broken 23-node dual state (old + new design side by side, disconnected) from a failed cleanup attempt — needs manual fix before any test run |
| RingCentral subscription register/renew | No | Webhook validation handshake not yet added to the existing receive workflow; JSON never imported into n8n |
| YouTube scheduled auto-upload | No | Never imported into n8n; `REPLACE_WITH_...` placeholders (folder IDs, Sheet ID, Gmail credential) still unfilled |
| LinkedIn Company Page post | Blocked externally | LinkedIn won't add the Company Page product to the existing app — needs a new single-product app + Page verification |
| Threads post | Blocked externally | `threads_content_publish` permission not granted, app secret not retrieved, no dedicated n8n node |

Zero of the five are currently live and verified. Priority order below reflects urgency, not doc order — RingCentral is time-sensitive (silent subscription expiry, ~7 days) even though Facebook is closer to done.

## 1. Facebook — fix the live n8n workflow (closest to done)

Workflow: `https://goldengoose.app.n8n.cloud/workflow/ZHavctjH5ZG4un8X`

- [ ] Delete the 14 old auto-post nodes (`Daily Check`, `Get Page Access Token`, `Extract Target Page Token`, `Get All Posts`, `Filter Ready To Post`, `Has Image?`, `Download Image File`, `Create Post With Image`, `Create Text Only Post`, `Posted OK?`, `Update Row Status`, `Notify Success (Gmail Draft)`, `Format Error`, `Notify Failure (Gmail Draft)`)
- [ ] Rename the 9 remaining `...1`-suffixed nodes back to their clean names
- [ ] Re-confirm the renamed `Daily Check` is set as the active trigger
- [ ] Re-verify credentials picked up correctly on the renamed nodes
- [ ] Retry the "No columns found" warning on `Update Row Status` (Mapping Column Mode)
- [ ] Confirm the Sheet tab is actually named `Posts` (not just the spreadsheet title "Facebook Posts")
- [ ] Save, run one live test → confirm a Gmail draft appears with post text/date/image reference, and the Sheet row flips to `awaiting_approval`

Fallback if manual edits keep failing in the n8n UI: delete all 23 nodes and re-import `automation/facebook-scheduled-post.json` clean onto an empty canvas — that file on disk is already the correct, current source of truth (approve-then-Alan-posts-manually design, no direct Facebook API posting).

## 2. RingCentral — do this before it silently breaks

SMS send/receive already works in n8n, but the webhook subscription that feeds the receive handler **expires in ~7 days** (unconfirmed exact TTL for Axiom's account tier) and stops delivering with no alert if not renewed.

- [ ] Add the webhook validation handshake to the **existing** receive workflow — a Code node right after the Webhook node that echoes back RingCentral's `Validation-Token` header. Nothing else works until this is live.
- [ ] Test the handshake standalone (RC sandbox or curl) before pointing anything at production
- [ ] Confirm the existing shared OAuth2 credential actually has refresh configured — don't assume
- [ ] Confirm the RingCentral app has the subscription-webhook scope enabled (subscription calls 403 without it)
- [ ] Decide subscription-ID persistence: n8n static data (recommended for single-number scope) vs. DB row vs. env var
- [ ] Fill in `REPLACE_WITH_...` values in both `automation/ringcentral-subscription-register.json` and `automation/ringcentral-subscription-renew.json` (receive handler's public URL, OAuth2 credential ID, Gmail credential ID, and Workflow 1's ID once both are imported)
- [ ] Import Workflow 1 (Register), run once manually — confirm it returns a real subscription `id` + `expirationTime`
- [ ] Import Workflow 2 (Renew) on a daily off-peak schedule (~3am), comfortably inside the TTL
- [ ] Confirm actual TTL for Axiom's RC account tier once renewal is live

## 3. YouTube — lowest urgency, but needs the most care before activating

This is the only workflow in the repo that publishes live with **zero human review** (`public` privacy, no Guardian/approval step) — treat the pre-go-live decisions as mandatory, not optional.

- [ ] Fill in `REPLACE_WITH_...` placeholders in `automation/youtube-scheduled-upload.json` (Drive `Pending`/`Uploaded` folder IDs, "Videos" Sheet ID, Gmail credential ID)
- [ ] Create the two Drive folders and the "Videos" Sheet if they don't already exist
- [ ] Import into n8n, sanity-check the Google Sheets column-mapping and the YouTube node's `options` shape (both drift across n8n versions; this JSON was built outside the UI)
- [ ] Connect the `youTubeOAuth2Api` credential
- [ ] Decide: missing-metadata row → silent skip or failure alert?
- [ ] Decide: repeated upload failures → retry forever, or move to a "Failed" folder after N attempts?
- [ ] Confirm `public` privacy default is really wanted
- [ ] Confirm `categoryId: 22` ("People & Blogs") is right for the channel
- [ ] Test with one throwaway video end-to-end before trusting the daily schedule

## Not actionable yet — blocked externally

**LinkedIn** and **Threads** are gated by LinkedIn's/Meta's own app-permission processes, not anything in this repo:
- LinkedIn needs a brand-new single-product app plus Page verification/app-review before Company Page posting can be requested at all.
- Threads needs `threads_content_publish` granted (currently only `threads_basic` is ready) and its separate app secret retrieved; n8n also has no dedicated Threads node, so any build would go through a generic HTTP Request node against `graph.threads.net`.

Importable JSON + design docs already exist for both (`automation/linkedin-scheduled-post.json` / `docs/linkedin-scheduled-post-workflow.md`, `automation/threads-scheduled-post.json` / `docs/threads-scheduled-post-workflow.md`) for whenever access is unblocked.

## Blocked — needs Alan

### LinkedIn Company Page posting

**What's blocking it:** The existing LinkedIn Developer app already has "Share on LinkedIn" (personal posting) attached, and LinkedIn only allows one product-type per app in this category — it won't let Company Page posting (`w_organization_social`, via the Community Management API) be added to the same app.

**What Alan needs to do to unblock:**
1. Create a **new, separate** LinkedIn Developer app (single-purpose: Company Page posting only)
2. Verify the app against the EverythingInternet.ca / Axiom Company Page
3. Apply for the Community Management API product on that new app — this is LinkedIn's own review process, turnaround isn't in our control
4. Once approved, the existing `automation/linkedin-scheduled-post.json` is ready to import as-is

**Effort/cost signal:** this is a LinkedIn app-review queue, not a build task — could be days to weeks on their side once submitted.

### Threads posting

**What's blocking it:** Two separate gaps —
1. `threads_content_publish` (the actual posting permission) isn't added yet — only `threads_basic` ("Ready for testing") is
2. Threads runs on its own separate App ID/Secret from the Facebook app, and the secret was never retrieved

**What Alan needs to do to unblock:**
1. Retrieve the Threads app's App Secret from `developers.facebook.com/apps` (separate from the Facebook App ID/Secret already in n8n)
2. Add/request `threads_content_publish` on that app's Threads Use Case
3. Note: n8n has no dedicated Threads node, so this build goes through a generic HTTP Request node against `graph.threads.net` — more moving parts than Facebook's build, worth knowing before prioritizing it

**Recommendation:** LinkedIn is the more strategic channel (B2B, matches the directory-listing product) — if only one can be chased right now, LinkedIn's app-review process is likely worth starting first since it has a fixed queue time, whereas Threads is just permission-request paperwork within Alan's own pace.
