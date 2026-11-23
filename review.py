#!/usr/bin/env python3
"""Stage 3: review. Turns the evidence for each app into a structured record.

Default mode is OFFLINE REPLAY: it writes the saved records (data/pass3.json, the
final reviewed records of the original run, which an AI reviewer wrote by hand) to --out and
marks them mode=replay. No model is called and nothing is regenerated.

Live mode (--live) asks a language model for each record. Configure only through environment variables:
  LLM_API_KEY    your key (never put keys in files or the repo)
  LLM_MODEL      model name (required)
  LLM_BASE_URL   OpenAI-compatible base URL, default https://api.openai.com/v1 (calls POST {base}/chat/completions)
Guards: the model must return JSON with allowed values, and every ev_* link must be one of the URLs supplied as evidence;
otherwise the record is retried once and then marked review_failed. Nothing is auto-trusted: records are drafts for a human reader.
Live-mode tested scope: protocol and validation only, against a local stand-in server (see tests/). It has not been run against a real model in this archive.
"""
import argparse,json,os,sys,urllib.request,datetime
ACCESS={'Self-serve','Tiered','Gated','Unclear'};MCP={'Official','Community only','Unclear'}
BUILD={'Easy','Feasible','Needs customer account','Needs outreach','Needs approval','Needs paid plan','Needs enterprise plan','Unclear'}
SYS=("You assess whether a SaaS app can become an agent toolkit. Use ONLY the evidence provided. Reply with one JSON object with keys: "
"auth (string, e.g. 'OAuth2; API key'), access (Self-serve|Tiered|Gated|Unclear), mcp (Official|Community only|Unclear; Official means the vendor or its own GitHub org publishes the MCP server), "
"build (Easy|Feasible|Needs customer account|Needs outreach|Needs approval|Needs paid plan|Needs enterprise plan|Unclear), note (short blocker or 'None material'), "
"ev_auth, ev_gate, ev_mcp (each must be one of the evidence URLs, or empty string). Say Unclear when the evidence does not support a call.")
def evidence(app,sd,pd):
    d=json.load(open(f"{sd}/{app['n']}.json"));urls=[];txt=[]
    for k in ('auth','gate','mcp'):
        for r in d['ev'][k][:4]:
            urls.append(r['url']);txt.append(f"[{k}] {r['url']}\n{r['title']}\n"+' '.join(r.get('highlights',[]))[:700])
    for k in ('auth','gate','mcp'):
        f=f"{pd}/{app['n']}_{k}.txt"
        if os.path.exists(f):
            t=open(f).read()
            if t.strip(): u=t.split('\n')[0]; urls.append(u); txt.append(f"[page {k}] {t[:1800]}")
    return urls,'\n\n'.join(txt)
def ask(prompt):
    key=os.environ.get('LLM_API_KEY');model=os.environ.get('LLM_MODEL')
    if not key or not model: sys.exit('LLM_API_KEY and LLM_MODEL must be set (live mode)')
    base=os.environ.get('LLM_BASE_URL','https://api.openai.com/v1').rstrip('/')
    body=json.dumps({'model':model,'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':SYS},{'role':'user','content':prompt}]}).encode()
    req=urllib.request.Request(base+'/chat/completions',data=body,headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    return json.loads(json.load(urllib.request.urlopen(req,timeout=120))['choices'][0]['message']['content'])
def valid(r,urls):
    if r.get('access') not in ACCESS or r.get('mcp') not in MCP or r.get('build') not in BUILD: return 'bad enum'
    if not isinstance(r.get('auth'),str) or not isinstance(r.get('note'),str): return 'bad text field'
    for k in ('ev_auth','ev_gate','ev_mcp'):
        if r.get(k,'') and r[k] not in urls: return k+' is not a supplied URL'
    return None
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--apps',default='data/apps.json');ap.add_argument('--search',default='runs/replay/search')
    ap.add_argument('--pages',default='data/pages');ap.add_argument('--out',default='runs/replay/records.json')
    ap.add_argument('--live',action='store_true')
    a=ap.parse_args()
    apps=json.load(open(a.apps));os.makedirs(os.path.dirname(a.out) or '.',exist_ok=True)
    if not a.live:
        saved={r['n']:r for r in json.load(open('data/pass3.json'))}
        recs=[{**{k:v for k,v in saved[x['n']].items() if k!='fixes'},'mode':'replay'} for x in apps]
        print('replayed saved records for',len(recs),'apps (no model called)')
    else:
        recs=[]
        for x in apps:
            urls,ev=evidence(x,a.search,a.pages);r=None;err=None
            for _ in range(2):
                try:
                    r=ask(f"App: {x['app']} ({x['cat']}, {x['hint']})\n\nEVIDENCE\n{ev}");err=valid(r,urls)
                    if not err: break
                except Exception as e: err=str(e)[:120]
            rec={**x,'mode':'live','at':datetime.datetime.now().isoformat(timespec='seconds')}
            rec.update(r if r and not err else {'review_failed':err or 'no answer'})
            recs.append(rec)
        print('live review done:',sum('review_failed' in r for r in recs),'failed of',len(recs))
    json.dump(recs,open(a.out,'w'),indent=1)
if __name__=='__main__': main()
