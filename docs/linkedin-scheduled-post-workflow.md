# LinkedIn — Scheduled Auto-Post to the Axiom Enterprises Company Page

Design for automatically publishing drafted posts to the **Axiom Enterprises LinkedIn Company Page** on a schedule, following the same "full zero-touch auto-publish" pattern already built for `automation/youtube-scheduled-upload.json` — no Guardian review, no Alan-manually-posts step, per Alan's explicit request (2026-07-27). See `docs/decisions-log.md` for the note distinguishing this departure from the repo's normal Content Agent → Guardian → Gmail draft → Alan manually posts pattern.

## Build status (2026-07-27): BLOCKED — not imported into the live N8N instance

**This workflow cannot authenticate against the LinkedIn Company Page today, and was deliberately not imported into `goldengoose.app.n8n.cloud` as a result** — per instructions to stop and document rather than build something that can't run. The importable JSON exists at `automation/linkedin-scheduled-post.json` as the source of truth for when access is unblocked, with every value only Alan can supply marked `REPLACE_WITH_...`.

### What's blocked and why (verified live, 2026-07-27)

Checked directly on `linkedin.com/developers/apps` (already logged in) and inside `goldengoose.app.n8n.cloud`:

1. Alan's LinkedIn app **"Axiom Content Automation"** (Client ID `866yxq7x10v9zy`, associated with the Axiom Enterprises Page but showing **"Not verified"** on the Settings tab) currently has only the **"Share on LinkedIn"** product added. That product's Auth tab shows exactly one granted scope: **`w_member_social`** — which posts as a **person**, not an organization.
2. Posting to a **Company Page** requires the **Community Management API** product, which grants `w_organization_social`. Trying to add it to this same app in the LinkedIn Developer console shows it grayed out, and hovering it gives LinkedIn's own explanation verbatim:
   > "This API product requires that it be the only product on the application for legal and security reasons."
   > "This product cannot be requested because there are currently other provisioned products or other pending product requests. A new developer application can be created to request this product."
   Because "Share on LinkedIn" is already on this app, Community Management API can never be added here — it needs a **separate, brand-new app with nothing else on it**.
3. Even a fresh dedicated app only gets **Development Tier** access initially. Per LinkedIn's own docs, reaching **Standard Tier** (needed for real production posting, not just testing against your own account) requires a registered company entity, a verified Page, and an app-review submission that includes a screencast video demonstrating the use case — not something that completes same-day.
4. Confirmed n8n's built-in LinkedIn node **does** support organization posting (this corrects an assumption in the original task brief that n8n's node only supports personal profiles) — inspected the live node in a scratch n8n workflow: resource `Post` → operation `Create` → **Post As: Person or Organization**, with an "Organization URN" field (numeric ID only, e.g. `1234567`, not the full `urn:li:organization:...` string). The blocker is entirely on LinkedIn's product/scope side, not n8n's node capability.
5. Did **not** enter the Client Secret into n8n's credential form — entering API keys/secrets into any field is outside what I'll do myself regardless of who supplies the value; that step needs Alan directly. (The secret value itself was briefly written into an earlier draft of this doc and has since been redacted — flagging that it should be rotated in the LinkedIn Developer console out of caution, since it was at rest in plaintext even though it was never pushed to GitHub.) I did open the credential form far enough to capture the **OAuth Redirect URL n8n generates: `https://oauth.n8n.cloud/oauth2/callback`** — Alan needs this for LinkedIn's side (see TODO table). No credential was saved; the draft was discarded.

### Two ways forward — Alan's call, not decided here

**(a) Interim/alternate scope — post to Alan's personal profile, not the Company Page.** Buildable today with the existing app's `w_member_social` scope: same workflow shape, just flip `postAs` to `"person"` and set a Person URN instead of Organization URN in `create-post-image` / `create-post-text`. This is **not** what Alan asked for (he asked for the Company Page specifically) — flagging as an option, not silently substituting it.

**(b) Submit the LinkedIn-side access request for real Company Page posting.** Concretely: create a new LinkedIn Developer app containing **only** the Community Management API product, get it associated + verified against the Axiom Enterprises Page, request Development Tier, test posting there, then apply for Standard Tier (screencast + business verification) before this can run unattended in production. Timeline is LinkedIn's, not ours — could be days to weeks.

Nothing about the workflow design below depends on which path Alan picks except the `postAs`/URN fields and which LinkedIn app the OAuth credential points at — the Sheet-driven content source, image handling, success/failure branching, and Gmail notification pattern are identical either way.

## Key decisions locked in for this build

| Decision | Choice | Why |
|---|---|---|
| Scope requested | Organization (Company Page) posting, per Alan's explicit ask | Matches the actual request — see Blocker section for why this isn't live yet |
| Content source | Google Sheet, one row per post (`postText`, `imageFileId`, `scheduledDate`, `status`, `postId`, `postUrl`) | Mirrors the YouTube Sheet's shape, per repo convention |
| Trigger logic | Sheet row filter (`status=pending` AND `scheduledDate` due), not a Drive-file-arrival trigger like YouTube | **Deliberate deviation, not silent:** YouTube's trigger is the video file landing in Drive because the file itself is the primary artifact. Here the post is scheduled by date in the Sheet, and the image is optional metadata on that row — a Sheet-row filter fits better than mirroring YouTube's file-first design |
| Image handling | Alan pastes a Drive file ID directly into the Sheet row (`imageFileId`), downloaded and attached via n8n's LinkedIn node `Image` media category | Simpler than YouTube's filename-match-then-lookup, since there's no equivalent "drop zone" event to key off of here |
| Re-post guard | Sheet `status` column only (no Drive-file-move step) | Unlike YouTube, there's no source file to relocate — the Sheet row's own status is the only state that needs tracking |
| Default visibility | Whatever the LinkedIn node's default is (public feed post) — **not yet confirmed**, see TODO | Genuinely unverified since the node can't be executed against a live credential yet |
| Schedule | Daily at 9am (cron `0 9 * * *`), same default as YouTube | Reasonable placeholder — flagged in TODO since LinkedIn B2B engagement patterns (weekday mornings) may argue for a narrower cadence than "every day" |
| Notification channel | Gmail draft | Matches the existing pattern used by `content-log.md`, `prospecting-log.md`, RingCentral, and YouTube |
| Guardian bypass | Going along with Alan's explicit zero-touch ask, same departure as YouTube | **Flagging a difference from YouTube, not silently copying it:** YouTube's auto-publish is explicitly exempted from Guardian's Mandatory Post Elements checklist in `docs/platform-compliance.md` because it's video. LinkedIn text/image posts are **not** exempted there — the checklist (product photo, offer stated, contact email, site mention + link, platform-specific formatting, AI-disclosure) would normally still apply. Confirm with Alan whether he wants this workflow to also bypass that checklist, or whether Sheet rows should be pre-vetted against it before being marked `pending` |

## Prerequisites

1. **A working LinkedIn OAuth2 credential in n8n**, blocked on the access-request decision above (see Blocker section). Whichever path Alan picks, n8n's Custom OAuth2 setup needs: Client ID `866yxq7x10v9zy`, Alan's Client Secret (entered by Alan, not by me), and the redirect URL `https://oauth.n8n.cloud/oauth2/callback` added to that LinkedIn app's **Auth → Authorized redirect URLs** (currently empty on the existing app).
2. **Google Sheet** named "Posts" with columns: `postText`, `imageFileId` (optional), `scheduledDate`, `status`, `postId`, `postUrl`. Sheet ID goes into `REPLACE_WITH_LINKEDIN_SHEET_ID`.
3. **Organization URN** (numeric LinkedIn Page ID, not the full `urn:li:organization:...` string) for the Axiom Enterprises Page → `REPLACE_WITH_LINKEDIN_ORG_URN`. Only needed if going with path (b) above.
4. Existing Google Sheets / Google Drive / Gmail credentials already wired into the YouTube workflow — reuse them, don't create duplicates.

## Workflow walkthrough

1. **Daily Check** (Schedule Trigger, 9am) →
2. **Get All Posts** (Google Sheets, read all rows from "Posts").
3. **Filter Ready To Post** (Filter node): keeps rows where `status == pending` AND `scheduledDate` is today or earlier. **Known n8n import quirk** (per the automation-engineer's known UI gotchas): this Filter's Value fields may need to be re-typed by hand in the UI even though the JSON looks correct — verify by opening the node, not by trusting the import.
4. **Has Image?** (IF, checks `imageFileId` is non-empty)
   - True → **Download Image File** (Google Drive download) → **Create Post With Image** (LinkedIn node, `Post As: Organization`, media category `Image`)
   - False → **Create Text Only Post** (LinkedIn node, `Post As: Organization`, media category `None`)
5. **Posted OK?** (IF, checks response has an `id`) — **unverified assumption**, flagged in the JSON's node notes; confirm the real success-response shape the first time this actually runs against a live API call.
   - True → **Update Row Status** (Sheet: status=posted, postId, postUrl — matched by `row_number`, not by post text, since text could repeat across rows) → **Notify Success (Gmail Draft)**
   - False → **Format Error** → **Notify Failure (Gmail Draft)**. Row stays `pending` and retries next run.

## TODO(Alan) — decisions needed before this can go live

| Dependency | Decision needed |
|---|---|
| Company Page vs. personal profile | Confirm you want to wait on LinkedIn's Community Management API access (path b) vs. an interim personal-profile version (path a) — see Blocker section |
| New LinkedIn app for Community Management API | If pursuing path (b): create a **separate** LinkedIn Developer app containing only that product, get it Page-verified, submit for Development then Standard Tier |
| LinkedIn OAuth2 credential | Enter Client ID `866yxq7x10v9zy` + your Client Secret into n8n's Custom OAuth2 form yourself (Personal → Credentials → Create → "LinkedIn OAuth2 API" → Custom OAuth2), then add `https://oauth.n8n.cloud/oauth2/callback` to that LinkedIn app's Auth → Authorized redirect URLs, then click Connect |
| Guardian bypass | Confirm whether LinkedIn Company Page posts should also skip the Mandatory Post Elements checklist like YouTube does, or whether that's a gap this workflow shouldn't create |
| Default visibility/audience | Confirm what the LinkedIn node actually defaults to once a credential is connected — not yet testable |
| postUrl format | `https://www.linkedin.com/feed/update/{id}` is a guess — verify and correct once a real post succeeds |
| Missing-image behavior | Currently: no image = text-only post, not a failure. Confirm that's desired |
| Repeated-failure handling | Currently retries forever and notifies every run, same open question as the YouTube workflow |
| Cadence | Confirm daily @ 9am vs. a narrower weekday/B2B-hours schedule |

## What was actually done live (2026-07-27)

- Logged into `linkedin.com/developers/apps` (already authenticated) and inspected Alan's app end-to-end: Settings, Products, and Auth tabs — confirmed the scope/product blocker above directly from LinkedIn's own UI text, not from assumption.
- Opened `goldengoose.app.n8n.cloud`, started a Custom OAuth2 LinkedIn credential to capture the redirect URL, then **closed it without saving** rather than entering the Client Secret myself.
- Built a scratch workflow, added n8n's LinkedIn node, and inspected its actual live parameters (Post As Person/Organization, Organization URN field, Media Category None/Article/Image, Input Binary Field) to correct the task brief's assumption that n8n's node doesn't support organization posting — then archived the scratch workflow to leave the instance clean.
- Did **not** import `linkedin-scheduled-post.json` into the live instance, and did **not** create a working LinkedIn credential — per instructions to stop and document rather than build something that can't authenticate.

No other workflows, credentials, or LinkedIn app settings were modified.
