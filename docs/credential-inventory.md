# Credential Inventory — Axiom Enterprises

Central log of every login/auth surface behind the automations and sites in this repo — what it is, where it lives, who set it up, and its verification status. Created 2026-08-06 from the first credential/access review (no prior version existed). Keep this updated whenever a credential is added, rotated, or its status changes — treat it the same way as `docs/decisions-log.md`: append/update, don't silently let it go stale.

## n8n workflow credentials (stored in n8n's own vault, not in this repo)

| Credential | Used by | Status | Verified refresh/expiry? | Notes |
|---|---|---|---|---|
| Google (Gmail account) | Facebook, docs-backup, YouTube, RingCentral alert workflows | Connected, live | Not explicitly checked | Shared across most workflows for Gmail-draft notifications |
| Google Sheets account | Facebook, YouTube | Connected, live | Not explicitly checked | |
| Google Drive account | docs-backup (reference design, not active), YouTube | Connected, live | Not explicitly checked | |
| YouTube OAuth2 (`youTubeOAuth2Api`) | YouTube scheduled upload | **Not connected yet** | N/A | Workflow not imported into n8n; credential ID still a placeholder |
| Facebook Graph API OAuth2 | Facebook scheduled post | Connected, live | Yes — `pages_manage_posts` / `pages_read_engagement` confirmed "Ready for testing"; manages exactly one Page (Everythinginternet.ca, ID `1096244530243584`) | Alan completed the OAuth "Connect" himself in n8n, 2026-07-28 |
| RingCentral OAuth2 | RingCentral subscription register/renew | Connected, but **refresh status unverified** | **No — open question** | `docs/daily-procedures-readiness.md` #2 flags: "Confirm the existing shared OAuth2 credential actually has refresh configured — don't assume." Subscription silently expires (~7 days, unconfirmed exact TTL) with no alert if refresh isn't actually wired. |
| LinkedIn (Community Management API) | LinkedIn scheduled post | **Not created** | N/A | Blocked — existing Developer app only supports personal posting (`w_member_social`); Company Page posting needs a brand-new single-product app + Page verification |
| Threads (Meta app) | Threads scheduled post | **Not created** | N/A | Separate App ID `1047046641402198` from the Facebook app; App Secret never retrieved from developers.facebook.com/apps; `threads_content_publish` permission not granted (only `threads_basic`) |

## Site logins (not n8n-managed)

| Login | Platform | Status | Notes |
|---|---|---|---|
| EmpoweredAtHome.com admin | WordPress/WooCommerce | **Undocumented here** | No credential owner, MFA status, or last-verified date tracked anywhere in this repo |
| EverythingInternet.ca admin | WordPress/WooCommerce, hosted via GoDaddy | Confirmed live, 2026-08-06 | n8n integration uses a scoped **WordPress Application Password** (not the account password) — correct pattern, revocable independently. MFA status on the main admin account still unconfirmed. |
| SchmucksDebate.com admin | WordPress/WooCommerce | **Undocumented here** | Same gap as EmpoweredAtHome |

## Open items

- [ ] Verify RingCentral OAuth2 credential has refresh actually configured in n8n (not just connected) — see `docs/daily-procedures-readiness.md` #2
- [ ] Confirm actual RingCentral subscription TTL for Axiom's account tier once refresh is verified
- [ ] Retrieve Threads app secret from developers.facebook.com/apps
- [ ] Request `threads_content_publish` permission on the Threads app
- [ ] Create a new single-product LinkedIn Developer app for Company Page posting

## TODO(Alan)
- Supply WordPress admin login details (or confirm they're managed elsewhere, e.g. a password manager) so this table can actually be filled in
- Confirm whether any of these logins have MFA enabled — not tracked anywhere currently
