#!/usr/bin/env python3
"""Stage 3b: automatic claim-vs-source check on fetched pages."""
import json,re
recs=json.load(open('data/pass2_frozen.json'))
def rd(n,k):
    try: return open(f'data/pages/{n}_{k}.txt').read().lower()
    except: return ''
M={'oauth':r'oauth','api key':r'api[ -_]?key|apikey|secret key|app key|api id|api token|app token','token':r'token|bearer|\bpat\b|jwt','basic':r'basic','jwt':r'jwt|json web token','hmac':r'hmac|signature','proxy':r'proxy','login':r'login|password'}
SELF=r'free|trial|sandbox|developer account|developer edition|sign up|signup|create an? (account|app)|self-serve|no credit card|test mode|generate'
GATE=r'approval|approve|apply|contact (us|sales)|enterprise|partner|request|review|paid|subscription|admin'
out=[]
for r in recs:
    n=r['n']; auth=rd(n,'auth')+' '+rd(n,'gate'); flags=[]
    a=r['auth'].lower()
    if a.startswith('none') or a.startswith('unclear'): pass
    else:
        for key,rx in [('oauth','oauth'),('api key','api key|api-key|apikey|api token|app key|secret key'),('token','token|bearer|pat'),('basic','basic'),('jwt','jwt')]:
            if re.search(r'\b'+key.split()[0],a) or (key=='api key' and re.search(r'api key|key \+|secret|app key|api id|consumer key|api token',a)):
                if not re.search(M[key],auth): flags.append(f'claimed {key} not found in cited pages')
    acc=r['access']
    gt=rd(n,'gate')+' '+rd(n,'auth')
    if acc=='Self-serve' and not re.search(SELF,gt): flags.append('self-serve not supported by cited pages')
    if acc=='Gated' and not re.search(GATE,gt): flags.append('gated not supported by cited pages')
    if r['mcp'] in('Official','Community only') and 'mcp' not in rd(n,'mcp') and 'model context' not in rd(n,'mcp'): flags.append('mcp page lacks mcp mention')
    if len(rd(n,'auth'))<400: flags.append('auth page empty/short')
    out.append({'n':n,'app':r['app'],'flags':flags})
json.dump(out,open('autocheck.json','w'),indent=1)
fl=[o for o in out if o['flags']]
print(len(fl),'flagged of 100')
for o in fl: print(o['n'],o['app'],o['flags'])
