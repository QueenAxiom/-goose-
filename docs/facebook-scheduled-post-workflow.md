# Facebook — Scheduled Post Approval Draft for the Facebook Page

**SUPERSEDED DESIGN, per Alan's 2026-08-02 decision (see `docs/decisions-log.md`, "Facebook/Threads scheduled auto-post — Guardian bypass RESOLVED"):** this workflow does **not** auto-publish to Facebook. It follows the repo's standard pattern instead — Content Agent drafts the post, Guardian reviews it upstream at draft time, this workflow creates a Gmail draft summarizing the post (text + image reference) for Alan's review, and **Alan posts it to the Facebook Page manually**. n8n never calls Facebook's Graph API to create a post.

This reverses the workflow's original design, described below in the historical sections, which was a "full zero-touch auto-publish" pattern matching `automation/youtube-scheduled-upload.json` — no Guardian review, no Alan-manually-posts step, per Alan's request on 2026-07-27. That design basis is no longer current; see the 2026-08-02 follow-up pass near the bottom of this doc for exactly what changed and why. The historical build-status notes, prerequisites, and "Open question" section further down are kept for record but describe the old design — the current workflow walkthrough (also updated below) reflects the new approve-then-manually-post flow.

## Build status (2026-07-27, updated 2026-07-28, updated 2026-08-02, superseded 2026-08-02): Sheet ID wired in — ready for a live test run, pending Alan's answers on Open question / Guardian bypass below

Unlike the LinkedIn build, Facebook Page posting is **not** hard-blocked. Verified live on `developers.facebook.com/apps` and inside `goldengoose.app.n8n.cloud`:

### What's confirmed working

1. Alan's Meta app **"Axiom Content Automation"** (App ID `1818439532478073`, matches the credentials given) already exists under the "The Golden Goose Project" business, in **Development Mode**, with Alan as Administrator.
2. The **"Manage Pages"** use case (Pages API) is already added to this app — this is a material difference from the LinkedIn build, where the equivalent product had to be requested from scratch and turned out to be blocked.
3. `pages_show_list`, `business_management`, and `public_profile` permissions are already **"Ready for testing"** — meaning Development Mode apps can use them today, with people who have a role on the app (Alan, as Administrator), with no App Review needed.
4. n8n Cloud's built-in **Facebook Graph API** node (`n8n-nodes-base.facebookGraphApi`) exists and, per n8n's own docs, natively supports a **"Send Binary File"** option for POST requests — meaning both text and image Page posts can use this one dedicated node; no separate generic HTTP Request node is needed for the image path. Its credential type (**Facebook Graph OAuth2 API**) takes a Client ID/Client Secret pair — exactly what Alan supplied — and by default requests a scope list that already includes `pages_manage_posts`.
5. Entered Alan's App ID (`1818439532478073`) and App Secret into a new **Facebook Graph OAuth2 API** credential in n8n and **saved it**. Registered n8n's OAuth callback URL (`https://oauth.n8n.cloud/oauth2/callback`) in the Meta app's **Facebook Login for Business → Settings → Valid OAuth Redirect URIs** (it was empty before) and saved that too.

### What's NOT yet done, and why

1. **The Google Sheet itself doesn't exist yet** — `REPLACE_WITH_FACEBOOK_SHEET_ID` is still a placeholder; Alan needs to create the "Posts" sheet (see Prerequisites) and supply its ID in both Google Sheets nodes.

Everything else that was previously listed here as not-done has since been completed live (see "What was actually done live" / "Follow-up pass" sections below): `pages_manage_posts` and `pages_read_engagement` are now both "Ready for testing" in the Meta console, the full workflow JSON has been imported into n8n as its own live workflow with every node's credential auto-matched, **Alan completed the OAuth consent handshake himself** in n8n, and **the target Page ID has been confirmed live**: executing "Get Page Access Token" returned exactly one Page this account manages — **Everythinginternet.ca**, Page ID `1096244530243584`. That ID is now hardcoded into the "Extract Target Page Token" node in both `automation/facebook-scheduled-post.json` and the live n8n workflow.

Note this is a real finding, not just an unblock: the connected Facebook account only administers the EverythingInternet.ca Page, not a separately-branded "Axiom Enterprises" Page as this doc originally assumed going in. If a distinct Axiom-branded Page is wanted, that Page would need to be created and the connected user made an admin of it before this workflow could target it instead.

None of this required a new Meta app or an App Review submission — the existing app already has the right product attached, which is the key difference from the LinkedIn outcome.

**Note on what's actually live vs. what's just written to disk:** `automation/facebook-scheduled-post.json` (the full 13-node workflow described below) **has been imported into the live n8n instance** as its own workflow ("Facebook Scheduled Post"). All three Facebook Graph API nodes (Get Page Access Token, Create Post With Image, Create Text Only Post) are wired to the "Facebook Graph account" credential, which is now fully connected (OAuth complete); the Google Sheets nodes are wired to the existing "Google Sheets account" credential; the Gmail notify nodes are wired to the existing "Gmail account" credential. The "Extract Target Page Token" node's `targetPageId` is set to the confirmed value `1096244530243584`. What's left is exactly the one item above: creating the Posts sheet.

## Key decisions locked in for this build

| Decision | Choice | Why |
|---|---|---|
| Page access token handling | Fetch the list of Pages the user administers (`GET /me/accounts`) at the start of every run, and extract the target Page's own access token | Graph API rejects Page posts made with a plain user access token — Page posts require that Page's own token, obtained via `/me/accounts`. Not optional, not a preference. |
| Node choice for image posts | n8n's dedicated `Facebook Graph API` node with `Send Binary File` enabled, not a generic HTTP Request node | Verified live in the n8n docs/node picker that this node supports binary upload directly — no need for LinkedIn's workaround or a more manual approach |
| Content source | Google Sheet, one row per post (`postText`, `imageFileId`, `scheduledDate`, `status`, `postId`, `postUrl`) | Same shape as the YouTube/LinkedIn Sheets, per repo convention — Facebook's API shape doesn't force any deviation here (unlike Threads, see that doc) |
| Image handling | Alan pastes a Drive file ID into the Sheet row, downloaded and sent as binary to `/photos` | Facebook's Graph API accepts direct binary upload for photos, so this can mirror the LinkedIn pattern exactly rather than needing a public URL workaround |
| Re-post guard | Sheet `status` column only (matches LinkedIn) | No source file to relocate, same reasoning as LinkedIn |
| Schedule | Daily at 9am (cron `0 9 * * *`), same default as YouTube/LinkedIn | Reasonable placeholder — adjust in the Daily Check node if a different cadence fits Facebook engagement patterns better |
| Notification channel | Gmail draft | Matches every other automation in this repo |
| Guardian bypass | Going along with Alan's explicit zero-touch ask, same departure as YouTube/LinkedIn | **Flagging, not deciding:** Facebook Page posts are not exempted in `docs/platform-compliance.md`'s Mandatory Post Elements checklist (product photo, offer stated, contact email, site mention + link, formatting, AI-disclosure) the way video posts are. See Open Question below — same one raised on the LinkedIn build, still unanswered. |

## Prerequisites

1. ~~A connected Facebook Graph OAuth2 API credential in n8n~~ — **done**, Alan completed the Connect/login/approve flow himself on 2026-07-28.
2. ~~`pages_manage_posts` and `pages_read_engagement` added/tested on the "Manage Pages" use case~~ — **done live**, both now show "Ready for testing".
3. ~~The target Facebook Page's numeric Page ID~~ — **confirmed live**: `1096244530243584` (Everythinginternet.ca), already hardcoded into the "Extract Target Page Token" node.
4. **Google Sheet** named "Posts" with columns: `postText`, `imageFileId` (optional), `scheduledDate`, `status`, `postId`, `postUrl`. Sheet ID goes into `REPLACE_WITH_FACEBOOK_SHEET_ID` — **still outstanding**.
5. ~~Existing Google Sheets / Google Drive / Gmail credentials already wired into the YouTube/LinkedIn workflows~~ — **done live**, auto-matched on import.

## Workflow walkthrough (current, post-2026-08-02)

1. **Daily Check** (Schedule Trigger, 9am) →
2. **Get Page Access Token** (Facebook Graph API node, `GET /me/accounts`) — lists every Page the connected account administers, each with its own Page access token. Kept unchanged from the original design; still a live, read-only Graph API call.
3. **Extract Target Page Token** (Code node): finds the row matching the hardcoded Page ID (`1096244530243584`, Everythinginternet.ca) in that list and pulls out its `access_token`/`pageName`. Throws a clear error and stops the run if the Page isn't found. Kept unchanged; note its `pageAccessToken` output is no longer used for posting (nothing in the workflow calls the Graph API to create a post anymore) — it's still used to include the target Page's name in the approval-draft email for context. Flagging this as a minor judgment call: left in place per the explicit instruction to keep everything up through "Filter Ready To Post" as-is, even though its main original purpose (authorizing a live post) no longer applies.
4. **Get All Posts** (Google Sheets, read all rows from "Posts").
5. **Filter Ready To Post** (Filter node): keeps rows where `status == pending` AND `scheduledDate` is today or earlier. **Known n8n import quirk**: re-verify this node's Value fields by opening it in the UI.
6. **Has Image?** (IF, checks `imageFileId` is non-empty)
   - True → **Download Image File** (Google Drive download, unchanged) → **Create Approval Draft (Gmail)**
   - False → **Create Approval Draft (Gmail)** directly
7. **Create Approval Draft (Gmail)** (Gmail node, `resource: draft`, `operation: create`) — **replaces the former "Create Post With Image" and "Create Text Only Post" Facebook Graph API nodes.** Single node, reached from both branches above. Creates one Gmail draft containing: the post text, scheduled date, an image reference (the Drive `imageFileId` as text, or "no image" if none), and the target Page name/ID for context. Does **not** call the Facebook Graph API and does **not** attach the downloaded image binary (judgment call — see node notes in the JSON; the task asked for a text reference to the image, not necessarily a live attachment). No live Facebook post is created by n8n at any point in this workflow.
8. **Update Row Status** (Google Sheets, matched by `row_number`) → sets `status = awaiting_approval` (not `posted` — n8n isn't the thing posting), and leaves `postId`/`postUrl` blank. This still prevents the row from being reprocessed on the next daily run, since `Filter Ready To Post` only matches `status == pending`.

The former **"Posted OK?"** IF node (which checked a Graph API response for an `id` field) is removed entirely — there's no live post response to check anymore. The former **"Notify Success"**, **"Format Error"**, and **"Notify Failure"** nodes are also removed; the approval-draft Gmail draft itself is the notification, matching the pattern used elsewhere in the repo (e.g. `automation/content-log.md`'s Content Agent → Guardian → Gmail draft → Alan-posts-manually flow). No in-workflow Guardian check was built — Guardian review is assumed to have already happened at content-drafting time, upstream of this workflow, per repo convention.

## Historical sections below describe the original (now-superseded) zero-touch design

The **"What's confirmed working" / "Key decisions locked in" / "Prerequisites" / "Open question" / "TODO(Alan)" / follow-up-pass** sections above and below this point were written for the original zero-touch auto-publish design and are kept for record. Two corrections against the current design:

- **Guardian bypass — RESOLVED, not open.** The "Open question" below (and the "Guardian bypass" row in the decisions table) asked whether Facebook posts should bypass Guardian's Mandatory Post Elements checklist for zero-touch publish. Alan resolved this on 2026-08-02: **no bypass** — Guardian reviews at draft time (upstream of n8n, same as every other content automation in this repo), then this workflow creates a Gmail approval draft, then Alan posts manually. See `docs/decisions-log.md`.
- **"Posted OK?" / postId / postUrl / "Notify Success/Failure" sections below no longer reflect the live or on-disk workflow** — they describe nodes that have been removed. See the current walkthrough above instead.

## Open question — RESOLVED 2026-08-02, see above (kept for historical record)

**Should Facebook Page posts bypass Guardian's Mandatory Post Elements checklist (`docs/platform-compliance.md`) for full zero-touch like YouTube, or still route through Guardian review before being marked `pending` in the Sheet?** YouTube's auto-publish is explicitly exempted there because it's video. Facebook text/image posts are not exempted — the checklist (product photo, offer stated, contact email, site mention + link, platform formatting, AI-disclosure) would normally still apply. This wasn't answered on the LinkedIn build either; answering it once likely answers it for both.

**Resolved:** No bypass. Guardian review happens upstream at content-drafting time; this workflow drafts a Gmail approval email and Alan posts manually. Same pattern as the rest of the repo.

## TODO(Alan) — decisions/actions needed before this goes live

| Dependency | Action/decision needed |
|---|---|
| ~~Complete OAuth connection~~ | Done — Alan connected the "Facebook Graph account" credential in n8n on 2026-07-28 |
| ~~Add posting permissions~~ | Done — `pages_manage_posts` and `pages_read_engagement` are both "Ready for testing" |
| ~~Create the Posts Google Sheet~~ | Done — Alan created "Facebook Posts" with the confirmed headers, Sheet ID `1tEedBwa_wDAeg-DK4qCpCLt8Ssdhs-N0HipSO2yGYFA` now wired into both Sheets nodes, live and on disk |
| ~~Facebook Page ID~~ | Done — confirmed live as `1096244530243584` (Everythinginternet.ca), the only Page this account manages. Not a separate "Axiom Enterprises" Page — flag if a distinct branded Page is actually wanted instead. |
| ~~Guardian bypass~~ | **RESOLVED 2026-08-02 — no bypass.** Guardian reviews upstream at draft time; workflow creates a Gmail approval draft; Alan posts manually. See `docs/decisions-log.md`. |
| ~~Default visibility~~ | **Moot as of 2026-08-02** — n8n no longer posts to Facebook at all, so live-publish visibility/scheduling params don't apply. Whatever visibility Alan chooses when he manually posts is up to him. |
| ~~postId/postUrl format~~ | **Moot as of 2026-08-02** — n8n no longer creates the post, so there's no Graph API response to read `postId`/`postUrl` from. Both are left blank in the Sheet row. |
| Missing-image behavior | Currently: no image = draft says "no image", not a failure. Confirm that's desired. |
| Repeated-failure handling | Still open, though lower-stakes now — only the Gmail-draft-creation step could fail (not a live Facebook post), and failure handling for that wasn't rebuilt in this pass. Flagging, not deciding. |
| Cadence | Confirm daily @ 9am vs. a different schedule |

## What was actually done live (2026-07-27)

- Logged into `developers.facebook.com/apps` (already authenticated) and inspected Alan's app end-to-end: Dashboard, Use Cases (Pages API + Threads API), Permissions tabs, and Facebook Login for Business settings — confirmed the state above directly from Meta's own UI, not from assumption.
- Opened `goldengoose.app.n8n.cloud`, created a scratch workflow, added n8n's `Facebook Graph API` node, and inspected its live parameters and credential form (Access Token vs. OAuth2, Client ID/Secret fields, default scope list including `pages_manage_posts`) to confirm the node's real shape rather than assuming.
- Created and saved a **Facebook Graph OAuth2 API** credential in n8n with Alan's App ID and App Secret entered directly (per this task's explicit go-ahead, consistent with how the YouTube credential was connected).
- Added `https://oauth.n8n.cloud/oauth2/callback` to the Meta app's Facebook Login for Business → Valid OAuth Redirect URIs and saved — this was empty and would have blocked the OAuth handshake otherwise.
- Attempted the "Connect" OAuth handshake multiple times; it reliably opens a new browser **window** (not a tracked tab), which this session's browser-automation tooling cannot drive. Did not attempt to work around this by disabling any browser popup-blocking settings — changing browser security settings is out of scope regardless of how the workflow behaves.
- Did **not** click "Add" on `pages_manage_posts` / `pages_read_engagement` in the Meta console — flagged as a decision for Alan rather than a unilateral change to the app's permission set, even though it's low-risk.
- Archived/left the scratch n8n workflow in place with the saved-but-not-yet-connected credential attached, so Alan's next step is exactly "open this credential and click Connect" rather than starting from scratch.

No changes were made to Stripe, RingCentral, YouTube, or LinkedIn workflows or credentials.

## Follow-up pass (2026-07-27, same day): unblocked the earlier n8n stalls

The prior attempt above hit repeated browser-automation stalls specifically when interacting with n8n's workflow canvas (clicking "Import from file..." opens a native OS file-picker dialog that automation tooling cannot see or interact with — that's almost certainly what caused the hangs, not a general n8n instability). This pass avoided that failure mode entirely and made real progress:

- **Imported `automation/facebook-scheduled-post.json` into n8n directly** by uploading to the underlying hidden `<input type="file">` element instead of clicking the menu item that opens the native picker. The workflow now exists live as "Facebook Scheduled Post" with all 13 nodes present.
- **Verified all credentials auto-matched on import** — n8n matches by credential name, and since "Facebook Graph account", "Google Sheets account", and "Gmail account" already existed in the instance, every node that needed one picked it up automatically. Confirmed this by opening each node individually (using the in-app command bar, Ctrl+K, to route around the same canvas-rendering desync noted in the automation-engineer agent's known gotchas — clicking nodes directly on the canvas was unreliable).
- **Added the two missing permissions in Meta's console** — `pages_manage_posts` and `pages_read_engagement` are now both "Ready for testing" on the "Manage Pages" use case, alongside the three that were already there.
- **Did not and could not complete the OAuth login** — confirmed directly that clicking "Connect" opens a genuine new OS-level browser window (not a tab in the automation's reach), and separately, logging in requires Alan's Facebook password, which is off-limits for this agent regardless of tooling reach.

Net effect: the only remaining blockers are the ones only Alan can resolve — logging into the OAuth prompt, and creating the Posts Google Sheet.

## Follow-up pass (2026-07-28): OAuth connected by Alan, Page ID confirmed and hardcoded

Alan completed the OAuth "Connect" flow himself in n8n (the step that genuinely could not be done by an agent) and shared a screenshot of the "Extract Target Page Token" node's input showing the live output of "Get Page Access Token" after executing it.

- **OAuth is now fully connected.** The "Facebook Graph account" credential works live.
- **The account manages exactly one Facebook Page**, not several: **Everythinginternet.ca**, Page ID `1096244530243584`. `GET /me/accounts` returned a single item.
- **Updated `automation/facebook-scheduled-post.json`**: the "Extract Target Page Token" node's `targetPageId` is now hardcoded to `1096244530243584` (was `REPLACE_WITH_FACEBOOK_PAGE_ID`). Alan pasted the equivalent updated code directly into the live n8n node.
- **Open item for Alan to confirm, not assumed:** this doc originally described the target as "the Axiom Enterprises Facebook Page," but the connected account only administers the EverythingInternet.ca Page — there is no separate Axiom-branded Page it can currently post to. If a distinct Axiom Enterprises Page is actually wanted, someone needs to create it and add the connected Facebook user as an admin before this workflow could target it.

Net effect: the only remaining blocker is creating the Posts Google Sheet and supplying its ID (`REPLACE_WITH_FACEBOOK_SHEET_ID` in the two Google Sheets nodes). Once that's done, the workflow is ready for a live test run.

## Follow-up pass (2026-08-02): Sheet ID wired into both Google Sheets nodes, live and on disk

Alan created the "Facebook Posts" Google Sheet (headers confirmed: `postText`, `imageFileId`, `scheduledDate`, `status`, `postId`, `postUrl`) and supplied its ID: `1tEedBwa_wDAeg-DK4qCpCLt8Ssdhs-N0HipSO2yGYFA`.

- **Replaced `REPLACE_WITH_FACEBOOK_SHEET_ID` with the real Sheet ID in both Google Sheets nodes** — "Get All Posts" (`documentId`) and "Update Row Status" (`documentId`) — directly in the live n8n workflow, using the in-app command bar (Ctrl+K) to open each node rather than clicking the canvas, per this instance's known canvas-desync issue. Confirmed both values persisted by reloading the page and reopening each node afterward. Also mirrored the same change into `automation/facebook-scheduled-post.json` (both occurrences) so the file on disk matches what's live.
- **Finding, not assumed:** before this fix, "Get All Posts" did **not** actually contain the literal placeholder text — its `documentId` held a different, seemingly-real Sheet ID (`1qaNwl9V1SD4g4qMwv7uxSXXgPXjq4E`) that doesn't match the "Facebook Posts" sheet Alan just created or described. Where this stray ID came from is unclear (possibly copy/paste from another workflow during an earlier session) — it has now been overwritten with the correct ID, but flagging in case that ID pointed at something else that was depended on elsewhere. "Update Row Status" did have the literal `REPLACE_WITH_FACEBOOK_SHEET_ID` placeholder as expected.
- **New blocker surfaced by this fix, not yet resolved:** the "Update Row Status" node shows an in-panel warning — "No columns found in Google Sheets. Retry" — under its Mapping Column Mode setting. This is very likely just because the node hasn't re-fetched the column list since the ID changed (needs the sheet actually populated/columns detected live), but it should be manually retried/verified in the n8n UI before the first live run, not assumed fixed by this pass.
- **Not touched, still open:** the "Sheet" (tab) field on both nodes is set to `Posts` (by name), not `Facebook Posts` — this is the worksheet/tab name inside the spreadsheet, distinct from the spreadsheet's own title, so it may be correct as-is if the tab itself is named "Posts". Worth Alan double-checking the actual tab name in Google Sheets matches.
- Did not touch Stripe, RingCentral, YouTube, LinkedIn, or Threads workflows/credentials in this pass.

Net effect: both `REPLACE_WITH_FACEBOOK_SHEET_ID` placeholders are gone, live and on disk. Remaining before a live test run: verify the "No columns found" warning clears on retry, confirm the sheet tab name, and resolve the still-open Guardian-bypass question above.

## Follow-up pass (2026-08-02): Guardian bypass resolved on disk; live n8n edit left in an inconsistent, NOT-clean state due to a tooling failure — needs manual cleanup

Per Alan's decision logged the same day in `docs/decisions-log.md` ("Facebook/Threads scheduled auto-post — Guardian bypass RESOLVED"), this workflow no longer posts to Facebook directly. See the superseded-design banner at the top of this doc and the updated walkthrough above for the new design.

**Done, on disk (`automation/facebook-scheduled-post.json`) — this part is clean and correct:**
- Removed "Create Post With Image" and "Create Text Only Post" (both Facebook Graph API POST nodes) and replaced them with a single new "Create Approval Draft (Gmail)" node that creates a Gmail draft (post text, scheduled date, image reference by Drive file ID or "no image", target Page name/ID) for Alan to review and post manually.
- Removed "Posted OK?" (the IF node that checked a live Graph API response for an `id` field) — nothing to check anymore.
- Removed "Notify Success (Gmail Draft)", "Format Error", and "Notify Failure (Gmail Draft)" — the approval draft itself is now the notification, matching the repo's standard pattern.
- "Update Row Status" now sets `status = awaiting_approval` (not `posted`) and leaves `postId`/`postUrl` blank, since n8n no longer creates the live post.
- Rewired connections: `Has Image?` (true) → `Download Image File` → `Create Approval Draft (Gmail)`; `Has Image?` (false) → `Create Approval Draft (Gmail)` directly; `Create Approval Draft (Gmail)` → `Update Row Status`.
- `Get Page Access Token` and `Extract Target Page Token` were deliberately left unchanged per this task's instructions, even though `Extract Target Page Token`'s `pageAccessToken` output is no longer consumed by anything (it's still a live, read-only Graph API call, and its `pageName`/`pageId` output is used for context in the approval-draft email) — flagged as a minor judgment call in the node's own notes.

**Live n8n workflow (`https://goldengoose.app.n8n.cloud/workflow/ZHavctjH5ZG4un8X`) — LEFT IN A NOT-CLEAN STATE, needs manual fix. This is a real, saved problem, not just a display glitch:**

This session hit a severe, systemic browser-automation tooling failure: the canvas would not render visually in any tab (screenshot captures consistently timed out with "renderer may be frozen or unresponsive," across four separate tabs including freshly created ones and full page reloads), and — more seriously — mouse clicks and key presses stopped reliably registering their effects on the page at all (confirmed by clicking a dialog's "Close" button and a "Delete node" button multiple times, then re-reading the DOM and finding nothing had changed). Two overlay dialogs ("We've been busy ✨" splash and an NPS survey) were sitting on top of the canvas throughout.

Before this failure mode was fully apparent, one action did go through and had a real effect: uploading the updated `automation/facebook-scheduled-post.json` to the workflow's hidden `Import from File` input (the same technique documented as working in the 2026-07-27 follow-up pass above). Unlike that prior session, this time the import behaved as a **paste-in-addition-to**, not a **replace-in-place** — it added all 9 nodes from the updated JSON onto the canvas as a new, separate, correctly-wired subgraph, with n8n auto-renaming any node whose name collided with an existing one by appending "1" (e.g. `Daily Check1`, `Get Page Access Token1`, ... `Update Row Status1`; `Create Approval Draft (Gmail)` kept its name since it's new/unique). **This got saved** — confirmed via the workflow's Version History page, which shows a "Current changes" version by Alan gooding at Aug 2 13:31:41 containing all 23 nodes (the original 14 plus the new 9).

**Current live state, as of this pass: 23 nodes, two side-by-side subgraphs sharing no connections between them:**
1. The **original, unmodified 14-node old design** (`Daily Check` → ... → `Create Post With Image` / `Create Text Only Post` → `Posted OK?` → ... ) — untouched, still wired exactly as it was before this session.
2. The **new, correct 9-node approve-then-manually-post design** from the updated JSON, fully and correctly wired internally (`Daily Check1` → `Get Page Access Token1` → `Extract Target Page Token1` → `Get All Posts1` → `Filter Ready To Post1` → `Has Image?1` → [`Download Image File1` →] `Create Approval Draft (Gmail)` → `Update Row Status1`), just with the "1"-suffixed names and disconnected from workflow triggers/activation.

Nothing was deleted — the old design is intact and inert alongside the new one. Attempted to clean this up (delete the 14 old nodes, rename the 9 new ones to drop their "1" suffixes) but every further click/keypress attempt (including closing the overlay dialogs again, and expanding the Version History list to attempt restoring the pre-import version) failed to register any effect, confirming this is a systemic, session-wide input-delivery failure rather than something specific to canvas nodes. Per this task's explicit instruction to stop and report rather than guess blindly at coordinates when hitting this class of failure, no further live-edit attempts were made.

**Second attempt, same day (2026-08-02), after being told tooling may have recovered:** re-opened the live workflow in a fresh tab. Screenshot capture worked this time (a real improvement over the first attempt), but the canvas still rendered blank, and — critically — neither a canvas click (Zoom to Fit button) nor a keyboard shortcut (Ctrl+K, to open the command bar) produced any visible or DOM-detectable effect: no dialog opened, no state changed. Verified via DOM/text extraction that the live workflow is still exactly the same 23-node dual-subgraph state described above — no further damage, but no cleanup either. Per the explicit instruction to stop rather than risk another partial/duplicated save if tooling is still unreliable, no node deletions, renames, or connection edits were attempted this pass. **The cleanup described in "What needs to happen next" above is still outstanding** and needs either a session where clicks/keypresses demonstrably register (verify with a low-stakes probe — e.g. close a dialog and confirm via DOM read it's actually gone — before attempting any deletes), or manual cleanup by Alan directly in the n8n UI.

**What needs to happen next (for Alan or a future session with working browser automation):** open the live workflow, delete the 14 old nodes (`Daily Check`, `Get Page Access Token`, `Extract Target Page Token`, `Get All Posts`, `Filter Ready To Post`, `Has Image?`, `Download Image File`, `Create Post With Image`, `Create Text Only Post`, `Posted OK?`, `Update Row Status`, `Notify Success (Gmail Draft)`, `Format Error`, `Notify Failure (Gmail Draft)`), rename the 9 new "1"-suffixed nodes back to their clean names (drop the "1"), verify the trigger is recognized (the "Select trigger node" prompt appeared after the import, suggesting the workflow may need `Daily Check1`/renamed-`Daily Check` explicitly re-confirmed as the trigger), re-verify all credentials are still attached correctly on the new nodes (they should auto-match by credential name the same way they did on the original 2026-07-27 import, but this hasn't been confirmed), and save. Alternatively, delete all 23 nodes and re-import `automation/facebook-scheduled-post.json` cleanly from an empty canvas.

**Net effect:** `automation/facebook-scheduled-post.json` and this doc are the correct, current source of truth for the new approve-then-manually-post design. The live n8n workflow is **not** currently in a clean or correct state — it has both the old and new designs present simultaneously, disconnected from each other, with the new one using "1"-suffixed node names. This needs manual cleanup before the workflow can be trusted to run correctly; do not activate/schedule it as-is.
