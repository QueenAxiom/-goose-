# alangooding.ca handoff package

Copy everything from "PASTE FROM HERE" to the end into another AI. Attach the image files listed under Images.

---
## PASTE FROM HERE

### Your job
You are improving a starter web page for a small Canadian business (Axiom Enterprises, Alberta). Take the attached HTML and turn it into a polished, professional, production-ready page.

Rules:
1. Keep it a single self-contained HTML file (inline CSS, no external scripts). It must work pasted into a WordPress Custom HTML block.
2. Keep the colour palette and tone of the file. Improve layout, spacing, typography, hierarchy, mobile behaviour and polish.
3. Do NOT invent facts. Anything marked `[FLAG: ...]` stays marked. No fake testimonials, statistics, reviews, awards, customer counts, prices or credentials.
4. Keep the footer exactly: copyright, Alberta Registration placeholder, rise@empoweredathome.com, Privacy, Terms, Contact.
5. Target WCAG 2.2 AA: visible focus states, skip link, sufficient contrast, semantic headings, 44px touch targets.
6. Fast: no heavy images or libraries. Where an image would help, add a labelled placeholder with a one-line production brief instead of stock filler.
7. Tone: direct, warm, confident, proudly Canadian. Never corporate, hype-driven or fear-based. Avoid "synergy", "leverage", "disrupt".
8. Return only the finished HTML, then a short list of the FLAGs I still need to fill.

### About this site
- **Site:** alangooding.ca (Axiom Enterprises, Alberta, Canada)
- **One-liner:** Alan Gooding's personal site. Consulting is where we start: technology solutions that make business and life better. (DRAFT line.)
- **Tone:** Direct, warm, confident, proudly Canadian.
- **Offer:** Consulting. Offer names, who each is for, and pricing or 'contact for pricing' are FLAGs for Alan.
- **Hard guardrail:** This is a sibling site under Axiom Enterprises, NOT a hub the other sites route through. No fake credentials, client lists or testimonials.
- **Anchor phrase:** "Proud Sponsor of The Golden Goose Project - Building Stronger Communities." (use where appropriate)
- **Footer copyright:** "Axiom Enterprises". Keep existing wording of names, taglines and disclaimers unless told otherwise.

### Images
- No existing images for this site.

Still needed (use a labelled placeholder with a one-line production brief, no stock filler):
- Headshot placeholder with a one-line production brief (real photo to be supplied by Alan).

All photos and videos must be compressed before posting.

### FLAGs still to fill (leave marked)
- [FLAG: Offer 1 name]
- [FLAG: Offer 2 name]
- [FLAG: Offer 3 name]
- [FLAG: what the client gets, who it is for, price or "contact for pricing"]
- [FLAG: what the client gets, who it is for]

### Current code
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Alan Gooding | Consulting</title>
<meta name="description" content="Alan Gooding — consulting. Technology solutions that make business and life better.">
<style>
:root{--bg:#f7f4ee;--ink:#23252a;--mute:#5b5e66;--accent:#9a6b2f;--card:#fff;--line:#e3ded3}
*{box-sizing:border-box}body{margin:0;font:18px/1.65 Georgia,"Times New Roman",serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}h1,h2,h3{line-height:1.2;font-weight:600}
.wrap{max-width:1040px;margin:0 auto;padding:0 24px}
header{border-bottom:1px solid var(--line)}header .wrap{display:flex;justify-content:space-between;align-items:center;padding:18px 24px}
.brand{font-size:20px;letter-spacing:.04em;font-weight:700}nav a{margin-left:22px;text-decoration:none;color:var(--ink);font:15px system-ui,sans-serif}
.hero{background:#23252a;color:#f7f4ee;padding:96px 0}.hero h1{font-size:clamp(34px,6vw,58px);margin:0 0 18px;max-width:760px}
.hero p{max-width:620px;color:#d9d4c8;margin:0 0 30px}
.btn{display:inline-block;background:var(--accent);color:#fff;padding:14px 26px;text-decoration:none;font:600 16px system-ui,sans-serif;border-radius:3px}
.btn:focus,a:focus{outline:3px solid #e1b878;outline-offset:2px}
section{padding:72px 0}.grid{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);padding:28px;border-radius:4px}.card h3{margin-top:0}
.flag{background:#fff3cd;border:1px dashed #c9a227;padding:10px 14px;font:14px system-ui,sans-serif;color:#5c4a00}
footer{border-top:1px solid var(--line);padding:32px 0;font:14px system-ui,sans-serif;color:var(--mute)}
</style>
</head>
<body>
<a href="#main" style="position:absolute;left:-999px">Skip to main content</a>
<header><div class="wrap"><div class="brand">ALAN GOODING</div>
<nav aria-label="Main"><a href="#consulting">Consulting</a><a href="#about">About</a><a href="#contact">Contact</a></nav></div></header>
<main id="main">
<div class="hero"><div class="wrap">
<h1>Technology solutions that make business and life better.</h1>
<p>Consulting from Alan Gooding, founder of Axiom Enterprises, Alberta, Canada.</p>
<a class="btn" href="mailto:rise@empoweredathome.com?subject=Consulting%20enquiry">Book a consulting conversation</a>
<a class="btn" href="[FLAG: Stripe payment link URL]" target="_blank" rel="noopener">Buy</a>
</div></div>
<section id="consulting"><div class="wrap"><h2>Consulting</h2>
<div class="grid">
<div class="card"><h3>[FLAG: Offer 1 name]</h3><p>[FLAG: what the client gets, who it is for, price or "contact for pricing"]</p></div>
<div class="card"><h3>[FLAG: Offer 2 name]</h3><p>[FLAG: what the client gets, who it is for]</p></div>
<div class="card"><h3>[FLAG: Offer 3 name]</h3><p>[FLAG: what the client gets, who it is for]</p></div>
</div></div></section>
<section id="about" style="background:#fff"><div class="wrap"><h2>About Alan</h2>
<p>Alan Gooding created Axiom Enterprises with Queen Axiom. Axiom builds practical technology for businesses and households through EverythingInternet.ca, EmpoweredAtHome.com and SchmucksDebate.com.</p>
<div class="flag">FLAG: add Alan's verified bio, credentials and a real photo. Do not invent any.</div></div></section>
<section id="contact"><div class="wrap"><h2>Contact</h2>
<p>Tell me what you are trying to fix or build. Email <a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a>.</p>
<a class="btn" href="mailto:rise@empoweredathome.com?subject=Consulting%20enquiry">Email Alan</a></div></section>
</main>
<footer><div class="wrap">© 2026 Alan Gooding / Axiom Enterprises. All rights reserved. | Alberta Registration: 769776022 | <a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a> | <a href="/privacy">Privacy</a> | <a href="/terms">Terms</a> | <a href="#contact">Contact</a></div></footer>
</body>
</html>

```
## END PASTE
