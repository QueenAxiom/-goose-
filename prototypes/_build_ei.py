import json,urllib.request,re
ho=open('../site-handoffs/everythinginternet.ca.md',encoding='utf-8').read()
rules=ho.split('## PASTE FROM HERE')[1].split('### Current code')[0] if '### Current code' in ho else ho.split('## PASTE FROM HERE')[1][:5000]
cov=open('../docs/competitor-research/coverage-map-EverythingInternet.md',encoding='utf-8').read()
cur=open('everythinginternet-home-draft.html',encoding='utf-8').read()
p=("Rewrite this homepage as ONE self-contained HTML file (inline CSS, no external scripts except a GA4 gtag placeholder G-XXXXXXXXXX). Follow the rules and facts below exactly. "
"Add SEO: <title>, meta description, canonical https://everythinginternet.ca/, Open Graph, a google-site-verification meta placeholder, JSON-LD Organization + WebSite + FAQPage (FAQ answers stay [FLAG]), one H1, semantic H2/H3, internal anchors. "
"Cover every competitor section/keyword in the coverage map as a page section (directory search UI, browse by province and category, add your business, latest listings, guides and tools, events, newsletter, advertise, about). Where Axiom doesn't confirm the feature exists, keep the section but mark it [FLAG: Alan to confirm]. No invented numbers, testimonials, listings counts or prices other than the $499 launch listing. Return only HTML.\n\n"
"RULES AND FACTS:\n"+rules+"\n\nCOVERAGE MAP:\n"+cov+"\n\nCURRENT CODE:\n"+cur)
req=urllib.request.Request('http://127.0.0.1:8000/v1/chat/completions',json.dumps({"model":"olmoe-colibri","messages":[{"role":"user","content":p}],"max_tokens":6000}).encode(),{'Content-Type':'application/json'})
r=json.load(urllib.request.urlopen(req,timeout=3000))
t=r['choices'][0]['message']['content']
m=re.search(r'<!DOCTYPE.*</html>',t,re.S|re.I)
open('everythinginternet-home-v2.html','w',encoding='utf-8').write(m.group(0) if m else t)
print('ok',len(t))
