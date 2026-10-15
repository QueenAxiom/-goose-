# Promotion Channels — limits and communities (researched 2026-10-15)

Confidence: **official** = from the platform's own docs; **third-party** = blogs/vendor pages, verify before relying. "Limit" below is the technical ceiling. The real ceiling on every platform is spam enforcement, which judges patterns (volume + repetition), not a number.

## Posting limits by platform

| Platform | Limit found | Confidence | Source |
|---|---|---|---|
| Facebook Page | No published daily cap. Spam policy: "very high frequencies"; API throttle error 80001 | official | https://transparency.meta.com/policies/community-standards/spam/ , https://developers.facebook.com/docs/graph-api/overview/rate-limiting/ |
| Instagram | 100 API-published posts per rolling 24h (carousel = 1). Meta's docs also say 50 in places; query the `content_publishing_limit` endpoint for the live value | official, conflicting | https://developers.facebook.com/documentation/instagram-platform/content-publishing |
| Threads | 250 API-published posts per rolling 24h; check `threads_publishing_limit` | official | https://developers.facebook.com/documentation/threads/overview |
| LinkedIn | No published number. Per-author daily share limit (HTTP 429), app + per-member daily quotas visible in Developer Portal; duplicate text rejected (422, wait 10 min) | official | https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits |
| X (Twitter) | No post-count cap found; pay-per-use pricing (~$0.01-0.015 per post, posts with links reported at ~$0.20). Fixed tiers closed to new signups | third-party, sources disagree | check developer.x.com |
| Bluesky | 5,000 points/hour and 35,000/day; a post costs 3 points = ~1,666/hour, ~11,666/day | official | https://docs.bsky.app/docs/advanced-guides/rate-limits |
| TikTok | "Typically around 15 posts per day" per creator account; error `spam_risk_too_many_posts`; unaudited apps post private only | official | https://developers.tiktok.com/doc/content-sharing-guidelines |
| YouTube | 10,000 quota units/day default. Upload cost is 100 units (newer) or 1,600 (older page) = about 6 to 100 uploads/day; check the Cloud Console quota calculator | official, conflicting | https://developers.google.com/youtube/v3/determine_quota_cost |
| Pinterest | No pins/day number. Trial apps: 1,000 requests/day total; Standard: per-minute limits by category (pin creation reported ~300/day on Trial) | official + third-party | https://developers.pinterest.com/docs/reference/ratelimits/ |
| Reddit | ~60 requests/minute (third-party). Norm: ~9:1 non-promo to promo; identical link across many subreddits is a spam signal | third-party | https://postiz.com/blog/reddit-api-limits-rules-and-posting-restrictions-explained |

Not researched yet: Mastodon, Telegram, Discord, Medium, Dev.to, Hashnode, WordPress, Google Business Profile.

## Where to promote (only places found in research; rules change, read each sidebar first)

**Facebook "pages that let you post on their page":** most Pages don't let outsiders post on them. Groups are the realistic route. Search Facebook for Canadian small-business groups and read each group's rules; I could not view or join groups from here.

**Reddit (read the sidebar; use designated threads)**
- r/BuyCanadian: self-promotion without mod approval is removed; has a monthly Self-Promotion Megathread.
- r/canadasmallbusiness (~22k members): self-promotion is a common theme; rules not verified.
- r/EntrepreneurCanada (~1k members): small; rules not verified.
- r/Entrepreneur: rules say it is not for self-promotion; needs 10 comment karma to post.
- r/smallbusiness: no official rules found; reported as tolerant if you lead with value.

**Canadian business communities and directories**
- Small Business Hub (smehub.ca): free Canadian community.
- Shop Local CANADA: directory plus private members group.
- CFIB ShopSmallBiz.ca: national directory (older source, confirm it is still active).
- Startup Canada local communities (older source).
- LinkedIn groups named in one list: Go Small Business Canada, eCommerce Canada, Startup Canada (undated list, confirm they exist).

**Launch and directory sites**
- Product Hunt: free to submit.
- Indie Hackers: forum, share progress and story.
- BetaList: pre-launch products only; unpaid wait can be ~2 months, $130 fast track (third-party).
- StartupBase: free to list.
- Hacker News "Show HN": light-touch rules, maker only, no asking for votes, primary use of HN should not be promotion: https://news.ycombinator.com/newsguidelines.html

**Cheapest rule across all of them:** unique copy per channel. Duplicate text is both a spam signal and the most common reason directory listings get rejected.
