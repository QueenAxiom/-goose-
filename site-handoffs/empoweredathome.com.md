# EmpoweredAtHome.com handoff package

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
- **Site:** EmpoweredAtHome.com (Axiom Enterprises, Alberta, Canada)
- **One-liner:** AI, robotics, and smart-home confidence for real life. Always choose the exciting thing.(TM)
- **Tone:** Practical, forward-thinking, quietly exciting.
- **Offer:** Course: 'Making AI Part of Your Life: A Practical Introduction to Artificial Intelligence', $50 (marked down from $99.99). Format and contents are unconfirmed (FLAG). Content marketing around AI voice recorders; relationship to any device is unconfirmed, so no purchase claims.
- **Hard guardrail:** Do not claim Axiom makes or resells any device. No invented course contents.
- **Anchor phrase:** "Proud Sponsor of The Golden Goose Project - Building Stronger Communities." (use where appropriate)
- **Footer copyright:** "Axiom Enterprises". Keep existing wording of names, taglines and disclaimers unless told otherwise.

### Images
- No existing images for this site.

Still needed (use a labelled placeholder with a one-line production brief, no stock filler):
- Hero image placeholder with a one-line brief; real product photos exist in the content log but are not in this package.

All photos and videos must be compressed before posting.

### FLAGs still to fill (leave marked)
- None in the code; see the 'Unconfirmed' notes above.

### Current code
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Empowered At Home | AI, Robotics and Smart-Home Confidence</title>
<meta name="description" content="AI, robotics, and smart-home confidence for real life.">
<style>
:root{--bg:#f6f1e7;--ink:#1f2a28;--mute:#55605d;--accent:#0f766e;--card:#fff;--line:#e4dccb}
*{box-sizing:border-box}body{margin:0;font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}h1,h2,h3{line-height:1.2}.wrap{max-width:1100px;margin:0 auto;padding:0 24px}
header .wrap{display:flex;justify-content:space-between;align-items:center;padding:18px 24px}
.brand{font-weight:800;font-size:20px}nav a{color:var(--ink);text-decoration:none;margin-left:22px;font-size:15px}
.hero{padding:84px 0}.hero h1{font-size:clamp(34px,6vw,56px);margin:0 0 16px;max-width:760px}.hero p{max-width:620px;color:var(--mute);font-size:19px}
.btn{display:inline-block;background:var(--accent);color:#fff;padding:14px 28px;border-radius:999px;text-decoration:none;font-weight:700}
.btn:focus,a:focus{outline:3px solid #f59e0b;outline-offset:2px}
section{padding:64px 0}.grid{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:28px}.card h3{margin-top:0}
.price{font-size:38px;font-weight:800}.price s{font-size:20px;color:var(--mute);font-weight:400}
.flag{background:#fff3cd;border:1px dashed #c9a227;padding:10px 14px;font-size:14px;color:#5c4a00;border-radius:8px}
footer{border-top:1px solid var(--line);padding:32px 0;font-size:14px;color:var(--mute)}
</style>
</head>
<body>
<a href="#main" style="position:absolute;left:-999px">Skip to main content</a>
<header><div class="wrap"><div class="brand">Empowered<span style="color:var(--accent)">AtHome</span></div>
<nav aria-label="Main"><a href="#shop">Shop</a><a href="#learn">Learn</a><a href="#contact">Contact</a></nav></div></header>
<main id="main">
<div class="hero"><div class="wrap">
<h1>AI, robotics and smart-home confidence for real life.</h1>
<p>Plain-language help for using AI and smart technology at home. Always choose the exciting thing.™</p>
<a class="btn" href="#shop">See what's available</a></div></div>
<section id="shop"><div class="wrap"><h2>Shop</h2>
<div class="grid"><div class="card">
<h3>Making AI Part of Your Life: A Practical Introduction to Artificial Intelligence</h3>
<div class="price">$50 <s>$99.99</s></div>
<div class="flag">FLAG: confirm format (ebook, course or video), what it covers and currency before publishing a description.</div>
<p><a class="btn" href="/shop">View in shop</a></p></div></div></div></section>
<section id="learn" style="background:#fff"><div class="wrap"><h2>Why Empowered At Home</h2>
<div class="grid">
<div class="card"><h3>Practical</h3><p>Tools you can use this week, explained without jargon.</p></div>
<div class="card"><h3>Honest</h3><p>Clear about what things cost and what they do.</p></div>
<div class="card"><h3>Canadian</h3><p>Built by Axiom Enterprises in Alberta.</p></div></div></div></section>
<section id="contact"><div class="wrap"><h2>Contact</h2>
<p><a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a></p></div></section>
</main>
<footer><div class="wrap">© 2026 EmpoweredAtHome.com / Axiom Enterprises. All rights reserved. | Alberta Registration: 769776022 | <a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a> | <a href="/privacy">Privacy</a> | <a href="/terms">Terms</a> | <a href="#contact">Contact</a></div></footer>
</body>
</html>

```
## END PASTE
