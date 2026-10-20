"""Turn each original draft's EN home page into one self-contained relay/sites/<domain>/index.html."""
import re
import sys
from pathlib import Path

SRC = Path(r"C:/Axiom Enterprises/all websites/axiom-six-websites/sites")
OUT = Path(__file__).resolve().parent.parent / "relay" / "sites"
DOMAINS = ["everythinginternet.ca", "schmucksdebate.com", "alangooding.ca", "supergrok.ca", "everythingclaude.ca"]
FOOTER = "(c) Axiom Enterprises"
AI_RE = re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])")


def no_bare_ai(html: str) -> str:
    return re.sub(r">([^<]+)<", lambda m: ">" + AI_RE.sub("artificial intelligence", m.group(1)) + "<", html)


def assemble(domain: str) -> str:
    base = SRC / domain
    html = (base / "en" / "index.html").read_text(encoding="utf-8")
    css = (base / "style.css").read_text(encoding="utf-8")
    js = (base / "tools.js").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="../style.css">', "<style>%s</style>" % css)
    html = re.sub(r'<script[^>]+src="[^"]*tools\.js"[^>]*></script>', lambda m: "<script>%s</script>" % js, html)
    html = re.sub(r'<link rel="(icon|alternate)"[^>]+href="\.\./[^"]*"[^>]*>', "", html)
    html = no_bare_ai(html)
    if FOOTER not in html:
        html = html.replace("</body>", '<footer style="padding:24px;text-align:center">%s. Alberta Registration: [FLAG: Alan to confirm]</footer></body>' % FOOTER)
    return html


for d in DOMAINS:
    out = OUT / d
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(assemble(d), encoding="utf-8")
    print(d, (out / "index.html").stat().st_size)
