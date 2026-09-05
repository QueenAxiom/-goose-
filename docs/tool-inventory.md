# Axiom Tool Box — Third-Party Providers

Catalog of third-party providers (TPPs) — external services/platforms Axiom Enterprises has an account or vendor relationship with. Distinct from `docs/credential-inventory.md`, which tracks login/auth status for existing connections; this doc tracks *what each tool is, what it's for, and its cost/commitment*. Open-source frameworks/languages (e.g. Next.js, TypeScript, Tailwind) are excluded — they're code libraries, not vendor relationships with an account, billing, or ToS to track.

Started 2026-08-07 from the website-rebuild stack decision (`docs/decisions-log.md`, `docs/website-ecosystem-rebuild-plan.md`). Add entries here whenever a new TPP account gets created or evaluated — same append/update discipline as `docs/decisions-log.md`.

## Website rebuild stack (planned, per 2026-08-06 decision)

| Tool | What it does | Cost tier | Status |
|---|---|---|---|
| Sanity | Headless CMS — where content (text, prices, images) gets edited after the rebuild, across all four sites | Free tier available; paid tiers scale with usage | Planned, not yet set up |
| Stripe | Payment processing for the rebuilt sites | Free to integrate; per-transaction fee | Planned, not yet set up |
| Vercel | Hosting/deployment for the rebuilt sites | Free tier (Hobby) available; paid tiers for production/team use | Planned, not yet set up |

## Owned hardware assets

| Asset | What it is | Status |
|---|---|---|
| Plaud Note Pro | AI voice recorder hardware, owned by Axiom Enterprises | Owned. Plaud shipped MCP server support (2026-07-23) — transcripts/summaries can connect directly to Claude Desktop/Claude Code without manual export. Not yet connected in this environment. |

**Open question:** `docs/products-services.md` flags an unresolved relationship between EmpoweredAtHome.com's marketed "Pocket AI Voice Recorder" content and a third-party device made by Open Vision Engineering (sold on Amazon, ASINs `B0GV1JFT89`/`B0GV214XQ9`). Confirm with Alan whether the owned Plaud Note Pro is that same device (i.e. the Open Vision Engineering attribution was wrong) or a separate internal asset unrelated to the marketed product — this changes what claims EmpoweredAtHome.com content is allowed to make.

## Already in use (cross-referenced from `docs/credential-inventory.md`)

| Tool | What it does | Status |
|---|---|---|
| n8n (cloud) | Automation platform — runs the content/social/backup workflows in `automation/` | Connected, live |
| Google Workspace (Gmail, Drive, Sheets, Calendar) | Notifications, backups, scheduling data for automations | Connected, live |
| GoDaddy | Hosting for EverythingInternet.ca (WordPress) | Connected, live |
| Facebook Graph API | Facebook Page scheduled posting | Connected, live |
| RingCentral | SMS/voice | Connected, refresh status unverified — see `docs/credential-inventory.md` |
| WordPress/WooCommerce | Current CMS/storefront for the three brand sites, being phased out per the rebuild plan | Live now, superseded by the rebuild |
| Stripe (via WooCommerce Stripe Gateway) | Card payment processing for EverythingInternet.ca's $499 listing checkout | Connected, live — "Stripe Optimized Checkout" confirmed active 2026-08-08, resolving the bank-transfer-only checkout blocker |
| Split Pay (Stripe Connect plugin) | Multi-vendor payment splitting + automatic vendor Stripe onboarding for WooCommerce. Alan holds licensing usable across all three brand sites (EmpoweredAtHome, EverythingInternet, SchmucksDebate) | Installed on EverythingInternet.ca; vendor-onboarding not yet functional — needs a Stripe platform secret key with Connect permissions, see `docs/credential-inventory.md` open items. Not yet installed/configured on the other two sites. |

## TODO(Alan)
- Confirm who owns each new TPP account (billing contact, admin access) once Sanity/Stripe/Vercel accounts actually get created.
