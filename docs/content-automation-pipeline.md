# Content Automation Pipeline — Master Workflow

## Pipeline Architecture
- Five-agent content pipeline built in Claude Code: content-generator, es-translator, compliance-formatter, peak-scheduler, approval-packager
- Three-agent prospecting pipeline built alongside it
- All governed by content-rules.md at `/mnt/user-data/outputs/content-rules.md`
- All agent specs live at `/home/claude/agents/`, mirrored to `/mnt/user-data/outputs/agents/`

## Content Rules
- 8 posts/day per platform (X, Instagram, Pinterest, LinkedIn) plus 8 YouTube videos daily
- Bilingual English/Spanish on a 4-day rotation
- 6:15am approval email to rise@empoweredathome.com
- Axiom Enterprises copyright on all content
- Peak-time scheduling per platform
- Two-market daily split: each day targets one of two markets (teens-25 for AXIOM novel/comics, or 40-65 for EmpoweredAtHome/smart-home), alternating daily
- Within each day's posts: 3 of 4 in English, 1 of 4 in Spanish

## ECC Plugin Status
- ECC plugin installed (94 skills, 140 agents, 29 hooks, 1 MCP server), then disabled via `/plugin disable ecc` due to a confirmed UI bug with individual skill toggles
- Selective control requires editing `~/.claude/settings.json` directly
- Token audit and skill pruning on ECC is a current technical priority

## N8N Automation Stack
- N8N cloud (goldengoose.app.n8n.cloud) locked as the canonical automation tool per decisions-log.md
- Connected credentials: HubSpot, Gmail, GitHub, OpenAI, Twilio (number +17197828045); Stripe connection in progress
- Facebook Graph, YouTube, Google Sheets, Google Drive, and WordPress credentials also connected (Facebook connected July 27, 2026)
- Live SMS workflow: Twilio receives texts → GPT-4o-mini AI Agent generates reply → Twilio sends response
- SMS To field needs to be dynamic using `{{ $('Webhook').item.json.body.From }}`
- Twilio A2P 10DLC registration needed for US SMS compliance before production volume

## Council / Orchestration
- RETIRED (2026-08-06): the council-of-five concept (Strategist, Builder, Analyst, Guardian, Voice agents with mandates in a `council-of-five-briefs.md` that was never actually created) is deleted. See `decisions-log.md`.
- Council function now runs on gstack's plan-review skill suite, already routed in this repo's `CLAUDE.md`: `/plan-ceo-review` (strategy/scope), `/plan-eng-review` (architecture), `/plan-design-review` (design system), `/plan-devex-review` (API/CLI/SDK experience), `/autoplan` (runs the full pipeline), `/codex` (cross-model second opinion)
- Phase Three (autonomous agents reading from Airtable and Pinecone/Supabase) — its old gate (all five council-of-five briefs confirmed) no longer applies; new gating criteria not yet defined, open item for Alan
- Guardian as a quality gate is unaffected — it's a standing agent in the roster (`guardian.md`), not part of the deleted five-role structure
- The Relevance AI Guardian-brief reconciliation item is dropped along with council-of-five-briefs.md; if Relevance AI deployment resumes, scope its Guardian brief against the current `guardian` agent instead
- Sophia ("Queen Axiom") First-in-Command orchestrator concept still open, now decoupled from council-of-five. Platform destination (Claude Code CLAUDE.md vs N8N orchestrator node vs Relevance AI) still undecided

## Reference & Documentation
- integrations-inventory.md built from scratch; reference library consolidated into a single canonical to-do document, resolving version contradictions
- CLAUDE.md created with hallucination-prevention rules, session startup protocols, and explicit failure-behavior definitions
- Reference doc stack that must load at session start: ecosystem-reference.md, may-24-2026-to-do.md, hallucination-prevention.md, build-sequence.md — never start cold
- A prior-session application password should be rotated

## Media Tools
- Runway API integration planned but not yet executed: sign up at dev.runwayml.com, generate API key, add minimum credits, wire into N8N/Claude Code; test video is a current priority
- Creatify (app.creatify.ai) already set up and in use — has Video Ads, Image Ads, Avatar Video (1500+ AI actors), Create Your Own Avatar, Asset Generator, AI Media Buyer tools

## Custom Claude Skills (10 built and installed)
website-migration-audit, redirect-mapper, seo-continuity-check, integration-reconnect, analytics-continuity, url-health-checker, launch-readiness-checklist, content-to-system, ai-workshop-designer, golden-goose-strategist

## Daily Procedure
- Starts 10am, weekdays only — weekends are for research and recreation
- First thing each day: ask the council what the next day's product or service to promote should be for each social platform
- End of day, last task: load next day's content for posting

## Plaud Capture Integration (new)
- Plaud AI recorder auto-generates daily transcript/summary
- Summary sent as email attachment into a dedicated Gmail folder: "Plaud Summaries"
- Claude pulls the file from that Gmail folder and feeds it into the pipeline as raw source material for content

## Open Decision
- Evaluating a move to GPT over Claude/ECC, citing capability — significantly more automation and a better record-keeping system
