#!/usr/bin/env python3
"""Stage 2 (first pass): keyword classifier over collected evidence. Deliberately naive baseline."""
import json,re
apps=json.load(open('data/apps.json'))
def txt(ev,k): return ' '.join(' '.join(r.get('highlights',[])) for r in ev[k]).lower()
out=[]
for a in apps:
    ev=json.load(open(f"data/search/{a['n']}.json"))['ev']
    t=txt(ev,'auth')+' '+txt(ev,'gate')
    auth=[]
    if re.search(r'oauth ?2|oauth 2|authorization code',t): auth.append('OAuth2')
    if re.search(r'api[ -]?key',t): auth.append('API key')
    if re.search(r'bearer|access token|personal access token|api token',t): auth.append('Token')
    if re.search(r'basic auth',t): auth.append('Basic')
    g=txt(ev,'gate')
    gated='Gated' if re.search(r'contact sales|partner program|approval|apply for access|enterprise plan|paid plan|review process|waitlist',g) else 'Self-serve'
    mcp=ev['mcp']
    has_mcp=any(re.search(r'mcp',(r['title']+' '.join(r.get('highlights',[]))).lower()) and a['app'].split()[0].lower() in (r['title']+r['url']).lower() for r in mcp)
    build='Yes' if auth and gated=='Self-serve' else ('Needs outreach' if gated=='Gated' else 'Unclear')
    out.append({**{k:a[k] for k in ('n','app','cat')},'auth':auth or ['Unknown'],'access':gated,'mcp':has_mcp,'build':build})
json.dump(out,open('pass1_rerun.json','w'),indent=1)
from collections import Counter
print(Counter(o['access'] for o in out),Counter(o['build'] for o in out))
