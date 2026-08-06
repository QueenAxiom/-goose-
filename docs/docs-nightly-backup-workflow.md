# Docs — Nightly Backup Workflow

Design for a daily automated backup of the repo's working docs to redundant off-machine locations. Built at Alan's request (2026-08-05): "saved in as many areas as possible by automation so we have backups." Consulted the council (automation-engineer, website-manager, operations-manager) on approach and sequencing before building — see `docs/decisions-log.md`.

**Build status (2026-08-05):** importable N8N workflow JSON exists — see `automation/docs-nightly-backup.json`. Built outside the N8N UI, so sanity-check node parameters on import, especially the GitHub node's binary-output shape and the Gmail node's attachment field — both have changed across n8n versions. Every value only Alan can supply is marked `REPLACE_WITH_...` in the JSON. **No changes have been made to any live N8N instance yet.**

## Key decisions locked in for this build

| Decision | Choice | Why |
|---|---|---|
| Automation platform | N8N cloud (existing instance) | Matches the canonical-tool decision already locked in `docs/decisions-log.md`; GitHub, Google Drive, and Gmail credentials are already connected — no new integration surface |
| Source of truth for backup | GitHub (`QueenAxiom/-goose-`, `main` branch), not local disk | N8N cloud cannot read files on Alan's local machine directly. This means the backup only covers whatever has actually been **pushed** to GitHub — uncommitted or unpushed local changes are not backed up until pushed. Flagging this as a real dependency, not a detail. |
| Destinations | Google Drive folder + Gmail attachment (in addition to GitHub itself, which is already one off-machine copy) | Three total locations: GitHub (source), Drive, and Alan's inbox — matches "as many areas as possible" without adding a fourth automation system to maintain |
| Backup style | Dated snapshots in Drive (`docname_YYYY-MM-DD.md`), not overwrite-in-place | A straight overwrite means one bad night (e.g. a corrupted push) silently destroys the only backup. Dated snapshots keep history at the cost of Drive storage, which is negligible for markdown files |
| Docs covered | `docs/content-automation-pipeline.md`, `docs/decisions-log.md`, `docs/daily-procedures-readiness.md`, `automation/content-log.md`, `automation/prospecting-log.md` | The working docs actively referenced during daily operation, per Alan's council consult. Add more GitHub-get + Drive-upload branches later if other docs need covering. |
| Schedule | Daily at 1am (cron `0 1 * * *`) | Off-peak, deliberately offset from RingCentral's ~3am renewal and YouTube's 9am check |
| Notification style | Direct Gmail send, not a draft | This is a passive backup copy, not content awaiting approval — doesn't need the Guardian/draft pattern used for social posts |
| Per-file failure handling | `continueOnFail` on every GitHub fetch node | One renamed/moved/missing file shouldn't block backing up the other four; the summary email reports `attachedCount` out of 5 so a partial night is visible, not silent |

## Prerequisites

1. **GitHub credential** — already connected in this n8n instance per `docs/content-automation-pipeline.md`; reused here, not a new credential. → `REPLACE_WITH_GITHUB_CREDENTIAL_ID`.
2. **Google Drive folder** — create one (suggest "Axiom Backups") for nightly snapshots to land in. → `REPLACE_WITH_BACKUP_FOLDER_ID`.
3. **Existing Google Drive credential** — reuse whatever's already connected. → `REPLACE_WITH_GOOGLE_DRIVE_CREDENTIAL_ID`.
4. **Existing Gmail credential** — reuse whatever's wired into `content-log.md`'s automation, don't create a second one. → `REPLACE_WITH_GMAIL_CREDENTIAL_ID`.
5. **Docs must actually be pushed to GitHub** for this to back up current state — a local commit that never gets pushed is invisible to this workflow.

## Workflow walkthrough

1. **Nightly Check** (Schedule Trigger, 1am) →
2. **Compute Date Stamp** (Set): one `dateStamp` value reused by all five Drive uploads so tonight's snapshots share a filename date.
3. Five parallel branches, one per doc — each: **Get `<Doc>`** (GitHub, get file, binary output) → fans out to:
   - **Upload `<Doc>` to Drive** (dated snapshot in the Axiom Backups folder)
   - **Merge Attachments** (fan-in point for all five branches)
4. **Merge Attachments** (Code, runs once after all five branches land): combines whichever binaries actually arrived into one item (`file1`..`fileN`), tolerating any branch that failed.
5. **Send Backup Email** (Gmail, direct send, not draft): one nightly email to rise@empoweredathome.com with up to 5 attachments and a body reporting `attachedCount` out of 5.

## TODO(Alan) — decisions needed before this goes live

| Dependency | Decision needed |
|---|---|
| Drive folder | Create "Axiom Backups" (or preferred name) and supply its ID |
| Schedule | Confirm 1am daily vs. a different time |
| Doc list | Confirm these 5 docs are the right set, or add more branches |
| Live import | This JSON has not been imported into the live N8N instance yet — say the word and it gets imported next, same as the Facebook/YouTube workflows were |

No changes have been made to any live N8N instance — this is a plan/importable JSON for Alan to review and import directly.
