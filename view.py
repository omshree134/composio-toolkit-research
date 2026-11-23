import json,re,sys
a,b=int(sys.argv[1]),int(sys.argv[2])
KW=re.compile(r'oauth|api key|api-key|token|basic auth|free|trial|sandbox|approval|approve|partner|contact sales|paid|plan|enterprise|admin|review|rate limit|rest|graphql|mcp|waitlist|apply|developer account|self-serve|request access',re.I)
for n in range(a,b+1):
    d=json.load(open(f'data/search/{n}.json'))
    print(f"\n=== {n} {d['app']} [{d['cat']}] hint={d['hint']}")
    for k in ('auth','gate','mcp'):
        seen=0
        for r in d['ev'][k][:3]:
            sents=[]
            for h in r.get('highlights',[]):
                for s in re.split(r'(?<=[.!?])\s+|\n+',h):
                    s=s.strip()
                    if 30<len(s)<260 and KW.search(s): sents.append(s)
            print(f" [{k}] {r['url'][:70]} | "+' / '.join(sents[:1])[:220])
