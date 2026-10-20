# EverythingInternet.ca handoff package

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
- **Site:** EverythingInternet.ca (Axiom Enterprises, Alberta, Canada)
- **One-liner:** Canada's directory for finding and supporting Canadian businesses, with one-time lifetime listings for Canadian tech companies. (DRAFT line, not yet approved by Alan; state no price in this line.)
- **Tone:** Proud, Canadian, community-focused.
- **Offer:** Lifetime Directory Listing: one-time fee, $499 launch price (regular $2,999). B2B: Canadian tech companies pay once for a permanent listing. Show the $499 offer only; do not show other tiers.
- **Hard guardrail:** Do not invent member counts, listings counts, testimonials or refund terms. Refund and FAQ answers are FLAGs for Alan.
- **Anchor phrase:** "Proud Sponsor of The Golden Goose Project - Building Stronger Communities." (use where appropriate)
- **Footer copyright:** "Axiom Enterprises". Keep existing wording of names, taglines and disclaimers unless told otherwise.

### Images
- `images/everythinginternet.ca/logo.png`: Site logo, 800px wide. Use in header.
- `images/everythinginternet.ca/site-icon.png`: Square site icon, 512px. Use as favicon/social icon.
- `images/everythinginternet.ca/lifetime-listing-600x600.jpg`: Product image for the Lifetime Directory Listing.
- `images/everythinginternet.ca/25-monthlylisting-600x632.png`: Monthly-listing graphic. Confirm with Alan before using; the launch offer is the $499 lifetime listing only.

Still needed (use a labelled placeholder with a one-line production brief, no stock filler):
- Hero image: placeholder with a one-line production brief (maple/Canadian business theme, no stock-photo faces).

All photos and videos must be compressed before posting.

### FLAGs still to fill (leave marked)
- [FLAG: 3-5 real FAQs: who qualifies, how fast it goes live, how to edit the listing, refund terms.]

### Current code
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EverythingInternet.ca | Canada's Directory of Canadian Business</title>
<meta name="description" content="Canada's directory for discovering and supporting Canadian businesses.">
<style>
:root{--bg:#f8f6f1;--ink:#14213d;--mute:#4b5563;--accent:#c1121f;--card:#fff;--line:#e2ddd0}
*{box-sizing:border-box}body{margin:0;font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}h1,h2,h3{line-height:1.2}.wrap{max-width:1100px;margin:0 auto;padding:0 24px}
header{background:var(--ink);color:#fff}header .wrap{display:flex;justify-content:space-between;align-items:center;padding:16px 24px}
.brand{font-weight:800;font-size:20px}nav a{color:#fff;text-decoration:none;margin-left:22px;font-size:15px}
.hero{background:linear-gradient(180deg,var(--ink),#1d2f57);color:#fff;padding:88px 0}
.hero h1{font-size:clamp(34px,6vw,56px);margin:0 0 16px;max-width:780px}.hero p{max-width:640px;color:#d6dcea}
.btn{display:inline-block;background:var(--accent);color:#fff;padding:14px 26px;border-radius:6px;text-decoration:none;font-weight:700;margin:8px 12px 0 0}
.btn.alt{background:transparent;border:2px solid #fff}.btn:focus,a:focus{outline:3px solid #ffd166;outline-offset:2px}
section{padding:68px 0}.grid{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:28px}.card h3{margin-top:0}
.price{font-size:40px;font-weight:800}.price s{font-size:20px;color:var(--mute);font-weight:400}
.flag{background:#fff3cd;border:1px dashed #c9a227;padding:10px 14px;font-size:14px;color:#5c4a00;border-radius:6px}
footer{background:var(--ink);color:#c9d1e3;padding:32px 0;font-size:14px}footer a{color:#fff}
</style>
</head>
<body>
<a href="#main" style="position:absolute;left:-999px">Skip to main content</a>
<header><div class="wrap"><div class="brand">EverythingInternet<span style="color:#ff6b6b">.ca</span></div>
<nav aria-label="Main"><a href="#directory">Directory</a><a href="#listing">Get listed</a><a href="#about">About</a><a href="#contact">Contact</a></nav></div></header>
<main id="main">
<div class="hero"><div class="wrap">
<h1>Discover and support Canadian businesses.</h1>
<p>Canada's directory of Canadian technology companies, built so buyers can find them and companies can be found.</p>
<a class="btn" href="#directory">Browse the directory</a><a class="btn alt" href="#listing">List your company</a>
</div></div>
<section id="directory"><div class="wrap"><h2>The directory</h2>
<p>Search and browse Canadian tech companies.</p>
<div class="flag">FLAG: keep the existing live directory content/search here. Do not replace real listings with placeholders.</div></div></section>
<section id="listing" style="background:#fff"><div class="wrap"><h2>Lifetime Directory Listing</h2>
<div class="grid"><div class="card">
<div class="price">$499 <s>$2,999</s></div><p>One-time fee. CAD. No recurring charge.</p>
<p><strong>What you get:</strong> a permanent listing for your company in the directory.</p>
<div class="flag">FLAG: confirm exact deliverables (profile fields, links, categories, logo). Checkout has no payment method live, so the button below goes to email until payment works.</div>
<p><a class="btn" href="mailto:rise@empoweredathome.com?subject=Lifetime%20Directory%20Listing">Ask about a listing</a> <a class="btn" href="[FLAG: Stripe payment link URL]" target="_blank" rel="noopener">Buy</a></p></div>
<div class="card"><h3>Questions before you buy</h3><p>[FLAG: 3-5 real FAQs: who qualifies, how fast it goes live, how to edit the listing, refund terms.]</p></div></div></div></section>
<section id="about"><div class="wrap"><h2>About</h2>
<p>EverythingInternet.ca is operated by Axiom Enterprises, Alberta, Canada. Proud Sponsor of The Golden Goose Project: Building Stronger Communities.</p></div></section>
<section id="contact" style="background:#fff"><div class="wrap"><h2>Contact</h2>
<p><a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a></p></div></section>
</main>
<footer><div class="wrap">© 2026 EverythingInternet.ca / Axiom Enterprises. All rights reserved. | Alberta Registration: 769776022 | <a href="mailto:rise@empoweredathome.com">rise@empoweredathome.com</a> | <a href="/privacy">Privacy</a> | <a href="/terms">Terms</a> | <a href="#contact">Contact</a></div></footer>
</body>
</html>

```
## END PASTE
