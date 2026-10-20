# Change log

One section per day. Site pushes are appended automatically by Mission Control; other changes are added by hand.

## 2026-10-16
- Mission Control now starts automatically when Chrome is running (mission-control/chrome-watcher.ps1 + a Startup-folder launcher).
- Added Autopilot tab: per-site readiness checks, push to staging, and a gated "push all five live" button (mission-control/deploy.py). Replaced pages are backed up first.
- Saved WordPress Application Password for alangooding.ca staging to the git-ignored mission-control/.env. The staging REST API returns 401 to every request, so the push can't use it; switching to SFTP.
- Daily host backups are on; to be confirmed that staging and production restores are separate before the all-five push.
