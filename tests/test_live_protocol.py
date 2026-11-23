#!/usr/bin/env python3
"""Run from the repo folder: python3 tests/test_live_protocol.py. Exercises collect.py --live and review.py --live against local stand-ins."""
import os,subprocess,sys,json
sys.path.insert(0,'tests');import mock_servers
mock_servers.start()
env={**os.environ,'SEARCH_API_KEY':'test-key','SEARCH_BASE_URL':'http://127.0.0.1:8801/s','LLM_API_KEY':'test-key','LLM_MODEL':'test-model','LLM_BASE_URL':'http://127.0.0.1:8802/v1'}
apps=json.load(open('data/apps.json'))[:2];os.makedirs('runs/test',exist_ok=True);json.dump(apps,open('runs/test/apps.json','w'))
def run(*a): return subprocess.run([sys.executable,*a],env=env,capture_output=True,text=True)
r=run('collect.py','--live','--apps','runs/test/apps.json','--out','runs/test/search');print(r.stdout.strip(),r.stderr.strip()[:200])
r=run('review.py','--live','--apps','runs/test/apps.json','--search','runs/test/search','--pages','runs/test/nopages','--out','runs/test/records.json');print(r.stdout.strip(),r.stderr.strip()[:200])
recs=json.load(open('runs/test/records.json'));assert all(x['mode']=='live' and 'review_failed' not in x for x in recs),recs
mock_servers.L.bad=True
r=run('review.py','--live','--apps','runs/test/apps.json','--search','runs/test/search','--pages','runs/test/nopages','--out','runs/test/records_bad.json');print(r.stdout.strip())
recs=json.load(open('runs/test/records_bad.json'));assert all('review_failed' in x for x in recs),recs
r=subprocess.run([sys.executable,'collect.py','--live','--apps','runs/test/apps.json','--out','runs/test/s2'],env={k:v for k,v in os.environ.items() if k!='SEARCH_API_KEY'},capture_output=True,text=True);assert 'SEARCH_API_KEY' in (r.stderr+r.stdout)
print('OK: live protocol, URL guard and missing-key handling behave')
