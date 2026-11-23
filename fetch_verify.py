#!/usr/bin/env python3
"""Stage 3: fetch each cited evidence page (plain HTTP, standard library only) and store its text.
Output: data/pages/<n>_<auth|gate|mcp>.txt. Pages that need JavaScript or block bots come back near-empty."""
import json,os,re,urllib.request,html
from concurrent.futures import ThreadPoolExecutor
recs=json.load(open('data/pass2_frozen.json'))
os.makedirs('data/pages',exist_ok=True)
def text(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (research script)'})
    raw=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore')
    raw=re.sub(r'(?is)<(script|style).*?</\1>',' ',raw)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',raw)))[:30000]
def fetch(a):
    n,k,u=a
    f=f'data/pages/{n}_{k}.txt'
    if os.path.exists(f) or not u: return
    try: open(f,'w').write(u+'\n\n'+text(u))
    except Exception as e: open(f,'w').write('')
jobs=[(r['n'],k,r['ev_'+k]) for r in recs for k in ('auth','gate','mcp')]
if __name__=='__main__':
    with ThreadPoolExecutor(10) as ex: list(ex.map(fetch,jobs))
