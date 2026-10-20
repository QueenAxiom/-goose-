import json,urllib.request,re
raw=open('raw-findings-2026-10-19.md',encoding='utf-8').read()
parts={'EverythingInternet.ca':re.search(r'## EverythingInternet.ca.*?(?=\n## EmpoweredAtHome)',raw,re.S).group(0),
       'EmpoweredAtHome.com':re.search(r'## EmpoweredAtHome.com.*?(?=\n## SchmucksDebate)',raw,re.S).group(0)}
for site,txt in parts.items():
    p=f"From these competitor findings for {site}, write: (1) a deduplicated list of every service/feature/page/section competitors offer (no products or prices), (2) a keyword and buzzword list for on-page SEO, (3) a proposed site map covering all of it. Mark anything Axiom may not actually offer with [FLAG: Alan to confirm]. Do not invent facts, testimonials or counts. Markdown.\n\n"+txt
    req=urllib.request.Request('http://127.0.0.1:8000/v1/chat/completions',json.dumps({"model":"olmoe-colibri","messages":[{"role":"user","content":p}],"max_tokens":2500}).encode(),{'Content-Type':'application/json'})
    r=json.load(urllib.request.urlopen(req,timeout=1800))
    open('coverage-map-'+site.split('.')[0]+'.md','w',encoding='utf-8').write(r['choices'][0]['message']['content'])
