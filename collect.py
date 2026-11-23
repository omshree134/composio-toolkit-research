#!/usr/bin/env python3
"""Stage 1: evidence collection (search).

Default mode is OFFLINE REPLAY: it copies the saved results of the original run
(data/search/) into --out. Nothing is searched and nothing is regenerated.
The output folder gets a PROVENANCE.json that says mode=replay.

Live mode (--live) calls a search API. Configure it only through environment variables:
  SEARCH_PROVIDER   'brave' (default). Uses https://api.search.brave.com/res/v1/web/search
  SEARCH_API_KEY    your key (never put keys in files or the repo)
  SEARCH_BASE_URL   optional override of the endpoint (for a proxy or a test server)
Output shape per app: data/search-style JSON {n, app, hint, cat, ev:{auth|gate|mcp:[{url,title,domain,published_date,highlights}]}}
Live-mode tested scope: protocol only, against a local stand-in server (see tests/). It has not been run against the real Brave API in this archive.
"""
import argparse,json,os,shutil,sys,urllib.parse,urllib.request,datetime
Q={'auth':'{app} API authentication OAuth2 API key developer documentation',
   'gate':'{app} API access developer account free sandbox trial pricing approval partner program',
   'mcp':'{app} MCP server model context protocol'}
def search(query,limit=6):
    key=os.environ.get('SEARCH_API_KEY')
    if not key: sys.exit('SEARCH_API_KEY is not set (live mode needs it)')
    prov=os.environ.get('SEARCH_PROVIDER','brave')
    if prov!='brave': sys.exit('only SEARCH_PROVIDER=brave is implemented')
    base=os.environ.get('SEARCH_BASE_URL','https://api.search.brave.com/res/v1/web/search')
    req=urllib.request.Request(base+'?'+urllib.parse.urlencode({'q':query,'count':limit}),headers={'Accept':'application/json','X-Subscription-Token':key})
    d=json.load(urllib.request.urlopen(req,timeout=30))
    out=[]
    for r in d.get('web',{}).get('results',[])[:limit]:
        u=r.get('url','')
        out.append({'url':u,'title':r.get('title'),'domain':urllib.parse.urlparse(u).netloc,'published_date':r.get('page_age'),
                    'highlights':[x for x in [r.get('description')]+list(r.get('extra_snippets') or []) if x]})
    return out
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--apps',default='data/apps.json');ap.add_argument('--out',default='runs/replay/search')
    ap.add_argument('--live',action='store_true')
    a=ap.parse_args()
    apps=json.load(open(a.apps));os.makedirs(a.out,exist_ok=True)
    for x in apps:
        dst=f"{a.out}/{x['n']}.json"
        if a.live:
            json.dump({**x,'ev':{k:search(q.format(app=x['app'])) for k,q in Q.items()}},open(dst,'w'))
        else:
            shutil.copy(f"data/search/{x['n']}.json",dst)
    json.dump({'mode':'live' if a.live else 'replay','apps':len(apps),'at':datetime.datetime.now().isoformat(timespec='seconds'),
      'note':None if a.live else 'saved results from the original run were copied; no search happened'},open(os.path.dirname(a.out.rstrip('/'))+'/PROVENANCE_search.json' if os.path.dirname(a.out.rstrip('/')) else 'PROVENANCE_search.json','w'),indent=1)
    print(('live search' if a.live else 'replayed saved search results'),len(apps),'apps ->',a.out)
if __name__=='__main__': main()
