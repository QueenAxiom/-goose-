# YouTube — Scheduled Auto-Upload Workflow

Design for automatically publishing videos Alan creates, on a timed schedule, without manual posting each time. Built at Alan's request (2026-07-26) after setting up a YouTube Data API v3 key and OAuth2 credentials in the "Golden Goose Project" GCP project.

**Build status (2026-07-26):** importable N8N workflow JSON exists — see `automation/youtube-scheduled-upload.json`. Built outside the N8N UI, so sanity-check node parameters on import, especially the Google Sheets node's column-mapping fields and the YouTube node's `options` shape — both have changed across n8n versions. Every value only Alan can supply is marked `REPLACE_WITH_...` in the JSON.

## Key decisions locked in for this build

| Decision | Choice | Why |
|---|---|---|
| Video source | One Google Drive folder ("Pending") as the single drop zone | iCloud Drive has no public API n8n can watch; installing the Google Drive desktop app makes the Drive folder appear as a normal folder on Alan's PC, collapsing PC + iCloud + Drive into one habit: finished video → drop zone |
| Metadata source | Google Sheet, one row per video (filename, title, description, tags, optional privacyStatus override) | Most flexible without editing the workflow per video |
| Default privacy status | `public` (true zero-touch publish) | Matches Alan's explicit ask for full automation; video posts are already exempted from Guardian's mandatory-post-elements checklist per `platform-compliance.md`, so there's no existing compliance gate this bypasses |
| Re-upload guard | Move the source file from Pending → an "Uploaded" archive folder after a successful upload | Simplest guard that's also visible by just looking at the folders, vs. hidden static-data state |
| Schedule | Daily at 9am (cron `0 9 * * *`) | Reasonable default — adjust in the Daily Check node if cadence should differ |
| Notification channel | Gmail draft | Matches the existing pattern used by `content-log.md`, `prospecting-log.md`, and the RingCentral subscription workflows |

This is a departure from the repo's other content automations (Content Agent → Guardian → Gmail draft → **Alan manually posts**) — this workflow actually publishes live to YouTube with no human step in between, per Alan's explicit request. See `docs/decisions-log.md` for the note distinguishing this from the existing Runway-deferral decision.

## Prerequisites

1. **GCP project** "Golden Goose Project" — YouTube Data API v3 enabled (done 2026-07-26).
2. **OAuth2 credential** (not an API key — uploading requires OAuth):
   - OAuth consent screen configured, External, with `.../auth/youtube.upload` scope, Alan's account added as a **test user** (keeps the token valid long-term without Google app-verification review)
   - OAuth Client ID (Web application type), redirect URI copied from n8n's YouTube OAuth2 credential setup screen
   - Connected inside n8n as a `youTubeOAuth2Api` credential
3. **Two Google Drive folders**: `YouTube Uploads/Pending` and `YouTube Uploads/Uploaded` — folder IDs go into the JSON's `REPLACE_WITH_PENDING_FOLDER_ID` / `REPLACE_WITH_UPLOADED_FOLDER_ID`.
4. **Google Sheet** named "Videos" with columns: `filename`, `title`, `description`, `tags`, `privacyStatus` (optional), `status`, `videoId`, `videoUrl`. Sheet ID goes into `REPLACE_WITH_SHEET_ID`.
5. Existing Gmail credential (reuse whatever's already wired into `content-log.md`'s automation, don't create a second one) → `REPLACE_WITH_GMAIL_CREDENTIAL_ID`.

## Workflow walkthrough

1. **Daily Check** (Schedule Trigger, 9am) →
2. **List Pending Videos** (Google Drive search, Pending folder, video mimeType). Zero results = nothing downstream runs, no error, no notification — that's expected on days with nothing new.
3. **Lookup Metadata** (Google Sheets lookup by filename). No matching row = item silently drops today — **flagging, not deciding:** consider whether a missing metadata row should trigger a failure notification instead of silent skip.
4. **Combine Video Data** (Set): merges file ID/name from step 2 with title/description/tags/privacyStatus from step 3. Defaults `privacyStatus` to `public` if the Sheet row leaves it blank.
5. **Download Video File** (Google Drive download, binary).
6. **Upload Video** (YouTube node, resource: video, operation: upload). `categoryId: 22` ("People & Blogs") is a placeholder — confirm against YouTube's category list if something else fits better.
7. **Uploaded OK?** (IF, checks response has an `id`)
   - True → **Move To Uploaded Folder** (re-upload guard) → **Update Row Status** (Sheet: status=uploaded, videoId, videoUrl) → **Notify Success (Gmail Draft)**
   - False → **Format Error** → **Notify Failure (Gmail Draft)**. File stays in Pending and will retry next run.

## TODO(Alan) — decisions needed before this goes live

| Dependency | Decision needed |
|---|---|
| Missing-metadata behavior | Silent skip (current) vs. failure notification when a video has no matching Sheet row |
| Repeated-failure handling | Currently retries forever and notifies every run — decide if files should auto-move to a "Failed" folder after N attempts instead |
| Default privacy status | Confirm `public` is really wanted vs. `unlisted`/`private` with a manual review step |
| categoryId | Confirm `22` ("People & Blogs") is correct for the channel's content |
| Cadence | Confirm daily @ 9am vs. a different schedule |

No changes have been made to any live N8N instance — this is a plan/importable JSON for Alan to review and import directly.
