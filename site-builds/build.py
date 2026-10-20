"""Build five single-file SEO sites locally. Section copy comes from Colibri (local model); this script only does structure.
Nothing is published. Output: site-builds/<domain>/{index.html,sitemap.xml,robots.txt}
Run: python build.py [domain ...]
"""
import json, os, re, sys, urllib.request

COLIBRI = "http://127.0.0.1:8000/v1/chat/completions"
ROOT = os.path.dirname(os.path.abspath(__file__))
ANCHOR = "Proud Sponsor of The Golden Goose Project - Building Stronger Communities."
FLAG = "[FLAG: Alan to confirm]"

SITES = {
    "everythinginternet.ca": {
        "name": "EverythingInternet.ca", "accent": "#c8102e",
        "title": "Canadian Business Directory | EverythingInternet.ca",
        "desc": "Canada's directory for finding and supporting Canadian businesses. One-time lifetime listings for Canadian tech companies. Browse by province and category.",
        "h1": "Canada's directory for Canadian businesses",
        "facts": "Canada's directory for finding and supporting Canadian businesses, with one-time lifetime listings for Canadian tech companies. Launch offer: Lifetime Directory Listing, $499 one-time. No member counts, listing counts, testimonials or refund terms.",
        "sections": ["Search the directory", "Browse by province", "Browse by category", "Add your business", "Lifetime Directory Listing", "Latest additions", "Guides and tools for Canadian business", "Events", "Advertise and sponsor", "Newsletter", "Questions"],
        "keywords": "Canadian business directory, Canadian tech companies, free business listing Canada, lifetime listing, small business Canada, local search, Alberta, Ontario, British Columbia, Quebec",
    },
    "empoweredathome.com": {
        "name": "EmpoweredAtHome.com", "accent": "#0b6e4f",
        "title": "AI, Robotics and Smart Home Confidence | EmpoweredAtHome.com",
        "desc": "Practical AI, robotics and smart-home guides and a beginner AI course for real life. Always choose the exciting thing.",
        "h1": "AI, robotics and smart-home confidence for real life",
        "facts": "AI, robotics, and smart-home confidence for real life. Always choose the exciting thing.(TM) Course: 'Making AI Part of Your Life: A Practical Introduction to Artificial Intelligence', $50 (marked down from $99.99); format and contents unconfirmed. Do not claim Axiom makes or resells any device. No invented course contents.",
        "sections": ["Making AI Part of Your Life (course)", "AI for beginners", "Prompting and AI productivity", "Responsible AI", "Smart home setup guides", "Automations and voice control", "Energy saving and privacy", "Home security and cameras", "Robotics for beginners", "AI voice recorders explained", "Glossary", "Newsletter", "Questions"],
        "keywords": "AI for beginners, AI course, generative AI, prompting, smart home, home automation, voice assistant, privacy, robotics, responsible AI, AI voice recorder",
    },
    "everythingclaude.ca": {
        "name": "EverythingClaude.ca", "accent": "#b4532a",
        "title": "Claude and Super-Intelligence Guides | EverythingClaude.ca",
        "desc": "Independent guides on Claude and super-intelligence. Not affiliated with Anthropic or Claude.",
        "h1": "Independent guides on Claude and super-intelligence",
        "facts": "Independent content on Claude and super-intelligence: the Claude-current hub. Must state: EverythingClaude.ca is independent and not affiliated with Anthropic or Claude. No Anthropic/Claude logos, no implied endorsement. No product yet.",
        "sections": ["What is Claude", "Claude vs ChatGPT", "Claude guides", "Prompting Claude", "Claude Code explained", "Super-intelligence explained", "News and updates", "Glossary", "Newsletter", "Questions"],
        "keywords": "Claude, what is Claude, Claude vs ChatGPT, Claude Code, Anthropic, super-intelligence, prompting, guide, EverythingClaude",
    },
    "schmucksdebate.com": {
        "name": "SchmucksDebate.com", "accent": "#7a1f1f",
        "title": "Debate and Negotiation Coaching | SchmucksDebate.com",
        "desc": "Debate, negotiation and critical-thinking coaching built on Sun Tzu's Art of War. Fight = Debate = Negotiate.",
        "h1": "Fight = Debate = Negotiate",
        "facts": "Debate, negotiation and critical-thinking coaching built on Sun Tzu's Art of War. Coaching, certifications, video consultations, blog; names, prices and inclusions unconfirmed. Separate product: a business-learning game, the Rocksmith of learning to play business. No outcome claims, no testimonials.",
        "sections": ["Debate coaching", "Negotiation coaching", "Critical thinking", "Art of War for business", "Certifications", "Video consultations", "Workshops and groups", "The business game", "Blog", "Resources", "Questions"],
        "keywords": "debate coaching, negotiation coaching, critical thinking, Art of War, Sun Tzu, business strategy, argument, persuasion, video consultation",
    },
    "alangooding.ca": {
        "name": "Alan Gooding", "accent": "#1f3a5f",
        "title": "Technology Consulting in Alberta | Alan Gooding",
        "desc": "Alan Gooding's personal site. Technology solutions that make business and life better. Consulting for small business in Alberta and across Canada.",
        "h1": "Technology solutions that make business and life better",
        "facts": "Alan Gooding's personal site, sibling to the other Axiom Enterprises sites. Consulting is where we start. Offer names, audiences and prices unconfirmed. No fake credentials, client lists or testimonials.",
        "sections": ["Consulting", "Small business technology", "Artificial intelligence for business", "Websites and SEO", "Automation", "How it works", "About Alan", "Axiom Enterprises sites", "Contact", "Questions"],
        "keywords": "technology consultant Alberta, small business technology consulting, artificial intelligence consultant Canada, automation, website consulting, Axiom Enterprises",
    },
    "supergrok.ca": {
        "name": "SuperGrok.ca", "accent": "#222222",
        "title": "Grok and Super-Intelligence Guides | SuperGrok.ca",
        "desc": "Independent guides on Grok and super-intelligence. Not affiliated with xAI or Grok.",
        "h1": "Independent guides on Grok and super-intelligence",
        "facts": "Independent content on Grok and super-intelligence. Must state: SuperGrok.ca is independent and not affiliated with xAI or Grok. No xAI/Grok logos, no implied endorsement. No product yet.",
        "sections": ["What is Grok", "Grok vs ChatGPT", "Grok guides", "Prompting Grok", "Super-intelligence explained", "News and updates", "Glossary", "Newsletter", "Questions"],
        "keywords": "Grok, what is Grok, Grok vs ChatGPT, xAI, super-intelligence, AI guide, SuperGrok",
    },
}


def colibri(site):
    prompt = (
        f"Write website copy for {site['name']}. Facts and guardrails: {site['facts']}\n"
        f"Tone: direct, warm, confident, proudly Canadian, never hype or fear. Never invent numbers, testimonials, credentials, clients, prices or features. Avoid superlatives and unprovable claims (no best, perfect, unparalleled, meticulously, curated, trusted). Keep each paragraph under 40 words so the JSON finishes. "
        f"If a section describes something not confirmed in the facts, write one honest sentence about what the section will cover and end it with {FLAG}.\n"
        f"Weave in these keywords naturally: {site['keywords']}.\n"
        f"Return ONLY JSON: {{\"sub\": \"one-sentence hero subtitle\", \"sections\": [{{\"h\": \"<heading>\", \"p\": \"<2 sentences>\"}}], \"faq\": [{{\"q\": \"...\", \"a\": \"{FLAG}\"}}]}} "
        f"with one sections entry per heading in this order: {json.dumps(site['sections'])}. Give 3 faq questions."
    )
    body = json.dumps({"model": "olmoe-colibri", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4500}).encode()
    req = urllib.request.Request(COLIBRI, body, {"Content-Type": "application/json"})
    text = json.load(urllib.request.urlopen(req, timeout=1500))["choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0))


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def render(domain, s, copy):
    paras = {c.get("h"): c.get("p") for c in copy.get("sections", []) if isinstance(c, dict)}
    secs = [(h, paras.get(h) or f"This section is being written. {FLAG}") for h in s["sections"] if h != "Questions"]
    faq = [f for f in copy.get("faq", []) if isinstance(f, dict) and f.get("q")][:3] or [{"q": "Who is behind this site?", "a": f"Axiom Enterprises, Alberta, Canada. {FLAG}"}]
    nav = "".join(f'<a href="#{slug(h)}">{esc(h)}</a>' for h, _ in secs[:6])
    body = "".join(f'<section id="{slug(h)}"><h2>{esc(h)}</h2><p>{esc(p)}</p></section>' for h, p in secs)
    faq_html = "".join(f"<details><summary>{esc(f['q'])}</summary><p>{esc(f.get('a') or FLAG)}</p></details>" for f in faq)
    notes = {
        "supergrok.ca": "SuperGrok.ca is independent and not affiliated with xAI or Grok.",
        "everythingclaude.ca": "EverythingClaude.ca is independent and not affiliated with Anthropic or Claude.",
    }
    disclaimer = f'<p class="note">{notes[domain]}</p>' if domain in notes else ""
    ld = [
        {"@context": "https://schema.org", "@type": "Organization", "name": s["name"], "url": f"https://{domain}/", "parentOrganization": {"@type": "Organization", "name": "Axiom Enterprises"}, "address": {"@type": "PostalAddress", "addressRegion": "AB", "addressCountry": "CA"}},
        {"@context": "https://schema.org", "@type": "WebSite", "name": s["name"], "url": f"https://{domain}/"},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f.get("a") or FLAG}} for f in faq]},
    ]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(s['title'])}</title>
<meta name="description" content="{esc(s['desc'])}">
<link rel="canonical" href="https://{domain}/">
<meta name="google-site-verification" content="GSC-VERIFICATION-TOKEN">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(s['title'])}"><meta property="og:description" content="{esc(s['desc'])}"><meta property="og:url" content="https://{domain}/">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{json.dumps(ld)}</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-XXXXXXXXXX');</script>
<style>
:root{{--a:{s['accent']};--bg:#fff;--fg:#1a1a1a;--mut:#555;--line:#e3e3e3}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#eee;--mut:#aaa;--line:#2a2a2a}}}}
*{{box-sizing:border-box}}body{{margin:0;font:17px/1.6 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}}
a{{color:var(--a)}}.skip{{position:absolute;left:-999px}}.skip:focus{{left:8px;top:8px;background:#fff;color:#000;padding:8px;z-index:9}}
header{{border-bottom:1px solid var(--line);padding:12px 16px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}}
header strong{{font-size:1.1rem}}nav{{display:flex;flex-wrap:wrap;gap:4px 14px}}nav a{{padding:10px 4px;min-height:44px;text-decoration:none;font-size:.95rem}}
:focus-visible{{outline:3px solid var(--a);outline-offset:2px}}
.hero{{padding:56px 16px;background:var(--a);color:#fff}}.hero>div,main,footer>div{{max-width:860px;margin:0 auto}}.hero h1{{font-size:clamp(1.9rem,5vw,3rem);line-height:1.15;margin:0 0 12px}}.hero p{{font-size:1.15rem;margin:0}}
main{{padding:8px 16px 40px}}section{{padding:24px 0;border-bottom:1px solid var(--line)}}h2{{margin:0 0 8px;font-size:1.4rem}}p{{margin:0;color:var(--mut)}}
details{{border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:10px 0}}summary{{cursor:pointer;font-weight:600;min-height:44px;display:flex;align-items:center}}
footer{{border-top:1px solid var(--line);padding:24px 16px;font-size:.9rem;color:var(--mut)}}.note{{margin-top:12px;font-weight:600;color:var(--fg)}}
</style></head><body>
<a class="skip" href="#main">Skip to content</a>
<header><strong>{esc(s['name'])}</strong><nav aria-label="Main">{nav}<a href="#questions">Questions</a></nav></header>
<div class="hero"><div><h1>{esc(s['h1'])}</h1><p>{esc(copy.get('sub') or s['desc'])}</p></div></div>
<main id="main">{body}<section id="questions"><h2>Questions</h2>{faq_html}</section>{disclaimer}</main>
<footer><div><p>{ANCHOR}</p><p>(c) Axiom Enterprises &middot; Alberta Registration: {FLAG} &middot; <a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a> &middot; <a href="/contact">Contact</a></p></div></footer>
</body></html>"""


AI_RE = re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])")
MISSION_CONTROL_SITES = ["everythinginternet.ca", "schmucksdebate.com", "alangooding.ca", "supergrok.ca", "everythingclaude.ca"]


def no_bare_ai(html):
    """Mission Control's readiness check rejects the standalone word AI in page text."""
    return re.sub(r">([^<]+)<", lambda m: ">" + AI_RE.sub("artificial intelligence", m.group(1)) + "<", html)


def main():
    targets = sys.argv[1:] or MISSION_CONTROL_SITES
    for d in targets:
        s = SITES[d]
        try:
            copy = colibri(s)
            src = "colibri"
        except Exception as e:  # Colibri slow/unavailable: ship structure with FLAGs, never invented copy
            copy, src = {}, f"fallback ({type(e).__name__})"
        out = os.path.join(ROOT, d)  # staged here first; copy to relay/sites/<domain>/ after review
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
            f.write(no_bare_ai(render(d, s, copy)))
        with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://{d}/</loc></url></urlset>')
        with open(os.path.join(out, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(f"User-agent: *\nAllow: /\nSitemap: https://{d}/sitemap.xml\n")
        print(d, src, flush=True)


if __name__ == "__main__":
    main()
