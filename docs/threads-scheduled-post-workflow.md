# Threads — Scheduled Auto-Post to the Axiom Enterprises Threads Profile

Design for automatically publishing drafted posts to the **Axiom Enterprises Threads profile** on a schedule, following the same "full zero-touch auto-publish" pattern as `automation/youtube-scheduled-upload.json` and the Facebook build — no Guardian review, no Alan-manually-posts step, per Alan's explicit request (2026-07-27). See `docs/decisions-log.md` and the **Open question** section below, same one flagged on both the LinkedIn and Facebook builds — still unresolved.

## Build status (2026-07-27): BLOCKED — importable JSON + doc only, nothing imported or connected in the live N8N instance

Verified live on `developers.facebook.com/apps/1818439532478073` (Threads is managed through the same Meta developer app as Facebook, under a separate "Threads API" use case) and inside `goldengoose.app.n8n.cloud`:

### What's confirmed

1. The **Threads API** use case is already added to Alan's Meta app ("Axiom Content Automation", App ID `1818439532478073`) — a product exists, same as Pages API.
2. On the app Dashboard's own "App customization and requirements" checklist, **"Customize the Manage everything on your Page use case" has a green checkmark; "Customize the Access the Threads API use case" does not** — Meta's own UI is flagging the Threads side as not fully configured, distinct from and behind the Pages API side.
3. `threads_basic` shows **"Ready for testing"**, but **`threads_content_publish` — the actual permission required to post — is NOT added/tested**. This is the permission that matters; without it, nothing can be published regardless of anything else being in place.
4. **Threads uses its own, separate App ID** (`1047046641402198`, visible in the Meta console) **and its own App Secret** — distinct from the main Facebook App ID/Secret (`1818439532478073`) Alan already supplied for the Pages/Graph API work. That Threads-specific secret was not retrieved or copied during this build; Alan hasn't been asked for it either, since there was no point collecting it while the permission itself is unavailable.
5. **n8n Cloud has no dedicated Threads node at all.** Confirmed live in the node picker: searching "Threads" returns n8n's own "we didn't make that... yet" message, suggesting the generic **HTTP Request** node as the only option. This is a real step down from Facebook (dedicated node, including native binary upload) and LinkedIn (dedicated node, blocked only on permissions) — Threads would need hand-built HTTP calls against `graph.threads.net`, a completely different host from `graph.facebook.com`.
6. Threads' Content Publishing API also requires **a publicly-reachable image URL** for image posts — it does not accept binary/multipart upload the way Facebook's `/photos` edge does. That forces a real structural deviation from every other Sheet-driven workflow in this repo (see below).

### Why this is BLOCKED, not just "needs one click" like Facebook

Facebook Pages posting only needed a couple of console clicks and Alan finishing an OAuth consent screen — the underlying pieces (app, product, node, credential shape) were all already there. Threads is missing three separate things at once: the permission (`threads_content_publish`), the credentials (separate Threads App ID/Secret, not yet supplied), and the tooling (no native n8n node, so it's hand-rolled HTTP calls against undocumented-in-n8n behavior). Any one of those alone would just be a TODO; together, building and testing this live wasn't a responsible use of time until at least the permission and credential pieces are resolved.

## Key decisions locked in for this build (and one forced deviation)

| Decision | Choice | Why |
|---|---|---|
| Node choice | Generic `HTTP Request` node against `graph.threads.net`, not a dedicated node | No dedicated Threads node exists in n8n as of 2026-07-27 (confirmed live) |
| Publish mechanism | Two-step: create a "media container" (`POST /{threads-user-id}/threads`), then publish it (`POST /{threads-user-id}/threads_publish` with the returned `creation_id`) | This is how Meta's Threads Content Publishing API is documented to work — not optional, not a preference |
| **Image handling (DEVIATION, flagged not silent)** | Sheet column is `imageUrl` (a public image URL), **not** `imageFileId` like every other workflow in this repo | Threads' container-creation call only accepts a public `image_url` param — no binary upload support, unlike Facebook/LinkedIn/YouTube. A Google Drive file ID doesn't work here without an extra step to make it publicly fetchable, so the Sheet shape itself has to change for this platform |
| Content source | Google Sheet, one row per post (`postText`, `imageUrl`, `scheduledDate`, `status`, `postId`, `postUrl`) | Same overall shape as the other workflows, adjusted only where Threads' API forces it |
| Credential type | Generic n8n **OAuth2 API** credential (`oAuth2Api`), manually pointed at Threads' own authorize/token URLs, since there's no dedicated Threads credential type | Best available option without a custom node; untested |
| Schedule | Daily at 9am (cron `0 9 * * *`), same default as the other workflows | Placeholder, adjust once this is actually being worked on |
| Notification channel | Gmail draft | Matches every other automation in this repo |

## Prerequisites (none of these exist yet)

1. **`threads_content_publish` added/tested** on the Threads API use case in Alan's Meta app (developers.facebook.com/apps/1818439532478073/use_cases — "Access the Threads API" section, Permissions tab).
2. **Threads' own App ID and App Secret.** The App ID (`1047046641402198`) is visible in the console; the secret needs to be retrieved by Alan (Meta hides secrets behind a re-auth/reveal step) and supplied the same way the Facebook App ID/Secret were.
3. **A Threads OAuth2 credential built in n8n** using the generic OAuth2 API credential type, pointed at Threads' authorize URL (`https://threads.net/oauth/authorize`) and token URL (`https://graph.threads.net/oauth/access_token`) — not yet created.
4. **The Threads user/profile ID** (`REPLACE_WITH_THREADS_USER_ID` in the JSON) — obtainable via `GET /me` on `graph.threads.net` once a credential exists, but not yet known.
5. **A Google Sheet** named "Posts" with columns `postText`, `imageUrl`, `scheduledDate`, `status`, `postId`, `postUrl` — not yet created. Sheet ID goes into `REPLACE_WITH_THREADS_SHEET_ID`.
6. **A way to host images at a public URL** — Drive's own "anyone with the link" share URLs are unverified against Threads' image fetcher and may not work reliably; a dedicated image host may be more reliable. Not resolved.

## Workflow walkthrough

1. **Daily Check** (Schedule Trigger, 9am) →
2. **Get All Posts** (Google Sheets, read all rows from "Posts") →
3. **Filter Ready To Post** (Filter: `status == pending` AND `scheduledDate` is today or earlier) →
4. **Has Image?** (IF, checks `imageUrl` is non-empty)
   - True → **Create Media Container (Image)** (HTTP Request, `POST /{threads-user-id}/threads`, `media_type=IMAGE`, `image_url`, `text`)
   - False → **Create Media Container (Text)** (HTTP Request, `POST /{threads-user-id}/threads`, `media_type=TEXT`, `text`)
5. **Publish Media Container** (HTTP Request, `POST /{threads-user-id}/threads_publish`, `creation_id` from the previous step's response)
6. **Posted OK?** (IF, checks response has an `id`) — unverified assumption, flagged in the JSON.
   - True → **Update Row Status** (Sheet: status=posted, postId, postUrl — matched by `row_number`) → **Notify Success (Gmail Draft)**
   - False → **Format Error** → **Notify Failure (Gmail Draft)**. Row stays `pending` and retries next run.

## Open question — same one flagged on the LinkedIn and Facebook builds, still unresolved

**Should Threads posts bypass Guardian's Mandatory Post Elements checklist (`docs/platform-compliance.md`) for full zero-touch like YouTube, or still route through Guardian review before being marked `pending` in the Sheet?** Not answered on any of the three social builds yet — answering it once likely settles it for all of them.

## TODO(Alan) — decisions/actions needed before this can even be tested

| Dependency | Action/decision needed |
|---|---|
| Add posting permission | Click "Add" on `threads_content_publish` in the Meta app's "Access the Threads API" use case |
| Threads App Secret | Retrieve Threads' own App Secret (App ID `1047046641402198` already visible) from the Meta console and supply it |
| Build the OAuth2 credential | Create a generic OAuth2 API credential in n8n pointed at Threads' authorize/token URLs, using the Threads App ID/Secret above |
| Threads user ID | Once connected, `GET /me` on `graph.threads.net` to get the numeric profile ID |
| Sheet | Create the "Posts" Sheet described above |
| Image hosting | Decide how images get a public URL — Drive public-share link (unverified) vs. a dedicated image host |
| Guardian bypass | Same open question as LinkedIn/Facebook — confirm whether Threads posts skip the Mandatory Post Elements checklist or not |
| postId/postUrl format | Best-guess based on Threads' documented response/URL shape — verify and correct once a real post succeeds |
| Repeated-failure handling | Same open question as every other workflow in this repo |
| Cadence | Confirm daily @ 9am vs. a different schedule |

## What was actually done (2026-07-27)

- Confirmed live in Meta's developer console that the Threads API use case is added to Alan's app but not fully customized (no green checkmark on the Dashboard checklist, unlike Pages API), that `threads_basic` is "Ready for testing" while `threads_content_publish` is not, and that Threads runs on a separate App ID/Secret from the main Facebook app.
- Confirmed live in n8n's node picker that no dedicated Threads node exists.
- **Did not** create any n8n credential, did not import `automation/threads-scheduled-post.json` into the live n8n instance, and did not attempt to connect anything — there was no working permission or credential to connect yet, and live browser automation against n8n's UI stalled repeatedly during this session (see `docs/facebook-scheduled-post-workflow.md` for the same tooling limitation encountered there). `automation/threads-scheduled-post.json` and this doc are the source of truth for whenever the prerequisites above are resolved. **Alan needs to import `automation/threads-scheduled-post.json` into n8n himself** (Workflows → "..." → Import from File) once he's ready to wire it up, the same way he'll need to finish the Facebook credential connection himself.

No changes were made to Stripe, RingCentral, YouTube, LinkedIn, or Facebook workflows or credentials.
