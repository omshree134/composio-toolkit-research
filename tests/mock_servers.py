#!/usr/bin/env python3
"""Local stand-in for a search API and a chat-completions API. Used ONLY to test the request/response handling
and the validation guards of collect.py and review.py. Its answers are canned, so a run against it proves nothing about research quality.
Usage: python3 tests/mock_servers.py   (search on :8801, model on :8802)"""
import json,threading,http.server,urllib.parse
class S(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        assert self.headers.get('X-Subscription-Token')=='test-key'
        q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)['q'][0]
        body={'web':{'results':[{'url':'https://example.com/docs/'+str(i),'title':'Example docs '+str(i),'description':'Example excerpt for: '+q,'extra_snippets':['OAuth 2.0 and API keys are supported.']} for i in range(3)]}}
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(body).encode())
class L(http.server.BaseHTTPRequestHandler):
    bad=False
    def log_message(self,*a): pass
    def do_POST(self):
        assert self.headers.get('Authorization')=='Bearer test-key'
        n=int(self.headers['Content-Length']);req=json.loads(self.rfile.read(n))
        assert req['model']=='test-model'
        rec={'auth':'OAuth2; API key','access':'Self-serve','mcp':'Unclear','build':'Easy','note':'None material',
             'ev_auth':'https://example.com/docs/0','ev_gate':'','ev_mcp':'https://not-supplied.example/x' if L.bad else ''}
        out={'choices':[{'message':{'content':json.dumps(rec)}}]}
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(out).encode())
def start(bad=False):
    L.bad=bad
    a=http.server.HTTPServer(('127.0.0.1',8801),S);b=http.server.HTTPServer(('127.0.0.1',8802),L)
    for s in (a,b): threading.Thread(target=s.serve_forever,daemon=True).start()
    return a,b
if __name__=='__main__':
    start();import time;time.sleep(10**6)
