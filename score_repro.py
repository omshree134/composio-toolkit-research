#!/usr/bin/env python3
"""Recompute every accuracy number on the page from the frozen data files. Prints and writes metrics.json."""
import json,re
L=lambda f:{(r['n']):r for r in (json.load(open(f)) if not isinstance(json.load(open(f)),dict) else json.load(open(f))['rows'])}
p1,p2,p3pre,p3=[L('data/'+f) for f in ('pass1.json','pass2_frozen.json','pass3_pre_holdout.json','pass3.json')]
T=json.load(open('data/truth.json'))['rows']
def n2(s):
    s=s.lower();o=set()
    if re.search(r'oauth ?2|oauth2',s) or ('oauth' in s and not re.search(r'oauth 1',s)): o.add('O')
    if re.search(r'key|token|bearer|pat\b|secret|jwt|consumer',s): o.add('K')
    if 'basic' in s: o.add('B')
    return o
def n1(a): return {'O' if x=='OAuth2' else 'K' if x in('API key','Token') else 'B' for x in a if x in('OAuth2','API key','Token','Basic')}
def rec2(r): return n2(r['auth']),{'Self-serve':'S','Tiered':'T','Gated':'G'}.get(r['access'],'U'),1 if r['mcp']=='Official' else 0
def rec1(r): return n1(r['auth']),('S' if r['access']=='Self-serve' else 'G'),1 if r['mcp'] else 0
def score(rows,src,f):
    ok=tot=0;miss=[]
    for t in rows:
        a,c,m=f(src[t['n']])
        for name,got,want in (('auth',a,set(t['auth'])),('access',c,t['access']),('mcp',m,t['mcp_official'])):
            if want is None: continue
            tot+=1
            if got==want: ok+=1
            else: miss.append([t['n'],src[t['n']]['app'],name,sorted(got) if isinstance(got,set) else got,sorted(want) if isinstance(want,set) else want])
    return ok,tot,miss
S=[t for t in T if t['group']=='sample'];H=[t for t in T if t['group']=='holdout']
out={'sample_pass1':score(S,p1,rec1),'sample_pass2':score(S,p2,rec2),'sample_pass3_final':score(S,p3,rec2),'holdout_pass3_pre_fixes':score(H,p3pre,rec2),'holdout_pass3_final':score(H,p3,rec2)}
res={k:{'correct':v[0],'checked':v[1],'misses':v[2]} for k,v in out.items()}
json.dump(res,open('metrics.json','w'),indent=1)
for k,v in res.items(): print(k,f"{v['correct']}/{v['checked']}",v['misses'])
