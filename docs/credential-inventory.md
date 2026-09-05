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
| EmpoweredAtHome.com admin | WordPress/WooCommerce | Front-end confirmed live and healthy, 2026-08-06 | Storefront loads normally (nav, product categories, cart, checkout UI all present, no errors). Admin-credential gap still open: no owner, MFA status, or last-verified admin-login date tracked anywhere in this repo. |
| EverythingInternet.ca admin | WordPress/WooCommerce, hosted via GoDaddy | Confirmed live, 2026-08-06 | n8n integration uses a scoped **WordPress Application Password** (not the account password) — correct pattern, revocable independently. MFA status on the main admin account still unconfirmed. **Flag (2026-08-06):** front end currently presents as a directory/listing site (categories of companies/services) with no visible cart or checkout UI on the homepage, despite footer links referencing "Shop." Repo describes this as WooCommerce — worth confirming with Alan whether this is an intentional pivot or a regression. |
| SchmucksDebate.com admin | WordPress/WooCommerce | **DOWN — 404, 2026-08-06** | Confirmed HTTP 404 across `schmucksdebate.com`, `www.schmucksdebate.com`, and `http://schmucksdebate.com`. Diagnosed further: DNS resolves fine (`76.223.105.230`, `13.248.243.5` — domain not expired/lapsed), and `http://` correctly 308-redirects to `https://`, but the 404 itself comes from `Server: DPS/2.0.0-beta` — a live hosting-platform response, not a DNS or connectivity failure. So the domain and hosting account are both alive; the WordPress site itself appears missing, unpublished, or taken down at the hosting level. This supersedes the prior "Undocumented" status; the outage is now the priority issue, ahead of the admin-credential documentation gap. |

## Open items

- [ ] **SchmucksDebate.com is down — hosting account/domain are alive (DNS resolves, redirects work) but no site is published, 404 served directly by the host (2026-08-06). Escalate to Alan: was the site intentionally taken down, or did the WordPress install get removed/broken?**
- [x] Confirm with Alan whether EverythingInternet.ca's current directory-site presentation (no visible WooCommerce checkout) is intentional — resolved 2026-08-08: it's a marketplace, WooCommerce Stripe Gateway checkout is now live, see `docs/decisions-log.md`.
- [ ] **Split Pay Stripe Connect platform secret key** — EverythingInternet.ca's Split Pay install reports the on-file Stripe key (auto-populated by the WooCommerce Stripe Gateway OAuth connection) cannot list connected accounts, blocking automatic vendor onboarding. Needs a full-permission Stripe platform secret key (from Stripe Dashboard → Developers → API keys) pasted into Split Pay's own settings, separate from the WooCommerce gateway key. Alan to do this directly in-browser — not a value to paste into chat or this repo.
- [ ] Confirm Split Pay license tier (Pro required for self-service vendor onboarding) is active on everythinginternet.ca, and whether the same license extends to empoweredathome.com and schmucksdebate.com as Alan indicated.
- [ ] Verify RingCentral OAuth2 credential has refresh actually configured in n8n (not just connected) — see `docs/daily-procedures-readiness.md` #2
- [ ] Confirm actual RingCentral subscription TTL for Axiom's account tier once refresh is verified
- [ ] Retrieve Threads app secret from developers.facebook.com/apps
- [ ] Request `threads_content_publish` permission on the Threads app
- [ ] Create a new single-product LinkedIn Developer app for Company Page posting

## TODO(Alan)
- Supply WordPress admin login details (or confirm they're managed elsewhere, e.g. a password manager) so this table can actually be filled in
- Confirm whether any of these logins have MFA enabled — not tracked anywhere currently
