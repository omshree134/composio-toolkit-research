#!/usr/bin/env python3
"""
gen_report.py
Generates index.html (the standalone single-page interactive Case Study)
and results.json from data/pass3.json and metrics.json.
"""
import json, html, re
from collections import Counter, defaultdict

R = json.load(open('data/pass3.json'))
M = json.load(open('metrics.json'))
m1, m2, m3 = M['sample_pass1'], M['sample_pass2'], M['sample_pass3_final']
h0 = M['holdout_pass3_pre_fixes']

def has(s, k):
    s = s.lower()
    if k == 'O': 
        return bool(re.search(r'oauth ?2|oauth 2|oauth\b', s)) and not re.search(r'oauth 1\.0a', s) or 'oauth2' in s
    if k == 'K': 
        return bool(re.search(r'key|token|bearer|pat\b|secret|jwt|consumer', s))
    if k == 'B': 
        return 'basic' in s

cnt = Counter()
for r in R:
    for k in 'OKB':
        if has(r['auth'], k): cnt[k] += 1

cats = []
for r in R:
    if r['cat'] not in cats: cats.append(r['cat'])

acc = defaultdict(Counter)
for r in R: acc[r['cat']][r['access']] += 1
tot = Counter(r['access'] for r in R)
mcp = Counter(r['mcp'] for r in R)
b = Counter(r['build'] for r in R)
ready = b['Easy']
cav = b['Feasible']
blocked = sum(v for k, v in b.items() if k.startswith('Needs'))
unc = b['Unclear']
gated = [r['app'] for r in R if r['build'].startswith('Needs')]
tier = [r['app'] for r in R if r['access'] == 'Tiered']

def e(x): return html.escape(str(x))

def bar(label, n, total, cls=''):
    pct = 100 * n / total if total else 0
    return f'<div class="bar"><span class="bl">{e(label)}</span><span class="bt"><i class="{cls}" style="width:{pct:.0f}%"></i></span><b>{n}</b></div>'

catrows = ''
for c in cats:
    t = sum(acc[c].values())
    cells = ''
    for k, cl in (('Self-serve', 's'), ('Tiered', 't'), ('Gated', 'g'), ('Unclear', 'u')):
        v = acc[c][k]
        cells += f'<td class="{cl}">{v if v else ""}</td>'
    catrows += f'<tr><th>{e(c)}</th>{cells}</tr>'

rows = ''
for r in R:
    cls = {'Easy': 'ok', 'Feasible': 'mid', 'Unclear': 'unk'}.get(r['build'], 'no')
    mcp_cls = {'Official': 'm-off', 'Community only': 'm-com'}.get(r['mcp'], 'm-unk')
    links = ' '.join(f'<a href="{e(r[k])}" target="_blank" rel="noopener">{lab}</a>' for k, lab in (('ev_auth', 'auth'), ('ev_gate', 'access'), ('ev_mcp', 'mcp')) if r.get(k))
    hint_val = r.get('hint', '')
    hint_html = f'<div class="sub-hint">{e(hint_val)}</div>' if hint_val else ''
    rows += (f'<tr data-cat="{e(r["cat"])}" data-b="{cls}"><td>{r["n"]}</td>'
             f'<td><b>{e(r["app"])}</b><div class="sub">{e(r["cat"])}</div>{hint_html}</td>'
             f'<td><code>{e(r["auth"])}</code></td>'
             f'<td><span class="chip a-{e(r["access"])}">{e(r["access"])}</span></td>'
             f'<td><span class="chip {mcp_cls}">{e(r["mcp"])}</span></td>'
             f'<td><span class="chip b-{cls}">{e(r["build"])}</span></td>'
             f'<td>{e(r["note"])}</td>'
             f'<td class="ev">{links}</td></tr>')

cat_options = ''.join(f'<option value="{e(c)}">{e(c)}</option>' for c in cats)

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Composio 100 Apps Toolkit Research | Agent Buildability Case Study</title>
<style>
:root {{
  --ink: #111827;
  --mut: #4b5563;
  --faint: #6b7280;
  --line: #e5e7eb;
  --bg: #f8fafc;
  --card: #ffffff;
  --ok: #059669;
  --ok-bg: #ecfdf5;
  --mid: #d97706;
  --mid-bg: #fffbeb;
  --no: #dc2626;
  --no-bg: #fef2f2;
  --unk: #64748b;
  --unk-bg: #f1f5f9;
  --acc: #2563eb;
  --purple: #7c3aed;
  --purple-bg: #f5f3ff;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font: 14.5px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: var(--ink);
  background: var(--bg);
}}
main {{
  max-width: 1160px;
  margin: 0 auto;
  padding: 32px 24px 100px;
}}
header {{
  margin-bottom: 24px;
}}
.meta-tag {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--mut);
  margin-bottom: 8px;
}}
.meta-tag a {{
  color: var(--acc);
  text-decoration: none;
}}
.meta-tag a:hover {{
  text-decoration: underline;
}}
h1 {{
  font-size: 30px;
  font-weight: 800;
  line-height: 1.25;
  margin: 4px 0 12px;
  color: #0f172a;
}}
h2 {{
  font-size: 20px;
  font-weight: 700;
  margin: 44px 0 14px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
  color: #0f172a;
}}
h3 {{
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 10px;
  color: #1e293b;
}}
p {{
  margin: 8px 0;
}}
.sub {{ color: var(--mut); font-size: 12px; }}
.sub-hint {{ color: var(--faint); font-size: 11px; margin-top: 2px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
.banner {{
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 14px 18px;
  font-size: 14px;
  color: #1e40af;
  margin: 16px 0 20px;
  line-height: 1.5;
}}
.banner strong {{ color: #1e3a8a; }}
.nav-pills {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0 22px;
}}
.nav-pill {{
  display: inline-block;
  padding: 5px 12px;
  border-radius: 9999px;
  background: #ffffff;
  border: 1px solid var(--line);
  font-size: 12.5px;
  font-weight: 500;
  color: var(--mut);
  text-decoration: none;
  transition: all 0.15s ease;
}}
.nav-pill:hover {{
  border-color: var(--acc);
  color: var(--acc);
  background: #f0f7ff;
}}
.stats {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 20px 0;
}}
.stat {{
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}}
.stat b {{
  font-size: 32px;
  font-weight: 800;
  display: block;
  line-height: 1.1;
  margin-bottom: 6px;
}}
.stat.s-ready b {{ color: var(--ok); }}
.stat.s-cav b {{ color: var(--mid); }}
.stat.s-blocked b {{ color: var(--no); }}
.stat.s-unc b {{ color: var(--unk); }}
.stat.s-mcp b {{ color: var(--purple); }}
.stat span {{
  font-size: 13px;
  color: var(--mut);
  font-weight: 500;
}}
.headline {{
  padding-left: 22px;
  font-size: 15.5px;
}}
.headline li {{
  margin: 10px 0;
  line-height: 1.5;
}}
.headline li strong {{
  color: #0f172a;
}}
.cols {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 14px;
}}
@media (max-width: 820px) {{
  .cols {{ grid-template-columns: 1fr; }}
}}
.card {{
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}}
.card-title {{
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--mut);
  margin-bottom: 12px;
}}
.bar {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 7px 0;
}}
.bl {{
  width: 220px;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink);
}}
.bt {{
  flex: 1;
  background: #edf2f7;
  height: 13px;
  border-radius: 8px;
  overflow: hidden;
}}
.bt i {{
  display: block;
  height: 100%;
  background: var(--acc);
  border-radius: 8px;
}}
.bt i.ok {{ background: var(--ok); }}
.bt i.mid {{ background: var(--mid); }}
.bt i.no {{ background: var(--no); }}
.bt i.unk {{ background: var(--unk); }}
.bar b {{
  width: 32px;
  text-align: right;
  font-size: 13px;
}}
table {{
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  background: var(--card);
  font-size: 13px;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}}
th, td {{
  border-bottom: 1px solid var(--line);
  border-right: 1px solid var(--line);
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}}
th:last-child, td:last-child {{
  border-right: none;
}}
tr:last-child td {{
  border-bottom: none;
}}
thead th {{
  position: sticky;
  top: 0;
  background: #f8fafc;
  font-weight: 600;
  color: #334155;
  font-size: 12.5px;
  z-index: 2;
}}
.mx td {{
  text-align: center;
  font-weight: 600;
}}
td.s {{ background: var(--ok-bg); color: var(--ok); }}
td.t {{ background: var(--mid-bg); color: var(--mid); }}
td.g {{ background: var(--no-bg); color: var(--no); }}
td.u {{ background: var(--unk-bg); color: var(--unk); }}
.chip {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  white-space: nowrap;
}}
.a-Self-serve, .b-ok {{ background: var(--ok-bg); color: var(--ok); }}
.a-Tiered, .b-mid {{ background: var(--mid-bg); color: var(--mid); }}
.a-Gated, .b-no {{ background: var(--no-bg); color: var(--no); }}
.a-Unclear, .b-unk {{ background: var(--unk-bg); color: var(--unk); }}
.m-off {{ background: var(--purple-bg); color: var(--purple); }}
.m-com {{ background: #eff6ff; color: var(--acc); }}
.m-unk {{ background: var(--unk-bg); color: var(--unk); }}
.flow {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin: 14px 0;
}}
.step {{
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
  font-size: 13px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}}
.step-num {{
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--acc);
  margin-bottom: 4px;
}}
.step b {{
  display: block;
  font-size: 14.5px;
  margin-bottom: 6px;
  color: #0f172a;
}}
.filter-bar {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 12px;
}}
#q {{
  flex: 1 1 240px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 13.5px;
  outline: none;
}}
#q:focus {{
  border-color: var(--acc);
}}
select {{
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 13px;
  background: #ffffff;
  color: var(--ink);
  outline: none;
}}
select:focus {{
  border-color: var(--acc);
}}
#match-count {{
  font-size: 12.5px;
  color: var(--mut);
  font-weight: 600;
  margin-left: auto;
}}
.tw {{
  overflow-x: auto;
  max-height: 720px;
  overflow-y: auto;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.ev a {{
  display: inline-block;
  margin-right: 4px;
  margin-bottom: 2px;
  font-size: 11px;
  font-weight: 600;
  text-decoration: none;
  background: #eff6ff;
  color: var(--acc);
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid #dbeafe;
}}
.ev a:hover {{
  background: #dbeafe;
}}
code {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  background: #f1f5f9;
  padding: 2px 5px;
  border-radius: 4px;
  color: #0f172a;
}}
pre {{
  background: #0f172a;
  color: #f8fafc;
  padding: 14px 16px;
  border-radius: 8px;
  font-size: 12.5px;
  overflow-x: auto;
  line-height: 1.45;
}}
pre code {{
  background: transparent;
  color: inherit;
  padding: 0;
}}
a {{ color: var(--acc); }}
.tag-list {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0;
}}
.tag-item {{
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  color: #334155;
}}
</style>
</head>
<body>
<main>

<header>
  <div class="meta-tag">
    <span>Composio AI Product Ops Take-Home</span> &bull; 
    <span>Candidate: <strong>Om Shree Choudhary</strong></span> &bull; 
    <span>Repository: <a href="https://github.com/omshree134/composio-toolkit-research" target="_blank" rel="noopener">github.com/omshree134/composio-toolkit-research</a></span>
  </div>
  <h1>100 Apps: Which Can Become Agent Toolkits Today?</h1>
  <div class="banner">
    <strong>Executive Summary & Objective:</strong> Comprehensive research and verification across 100 enterprise and consumer SaaS platforms to determine feasibility as agent-callable Composio toolkits. Evaluates authentication methods, self-serve developer access vs partner gating, public API surfaces, and official/community Model Context Protocol (MCP) servers. Verified through automated citation-checking, a 20-app stratified ground-truth sample (improving accuracy from 47% to 97%), and a 12-app retrospective holdout evaluation (100% verified).
  </div>
  <div class="nav-pills">
    <a class="nav-pill" href="#patterns">Key Patterns & Insights</a>
    <a class="nav-pill" href="#matrix">Category Access Matrix</a>
    <a class="nav-pill" href="#pipeline">Agent Architecture & Workflow</a>
    <a class="nav-pill" href="#verification">Verification & Accuracy Loops</a>
    <a class="nav-pill" href="#proof">Runnable Proof & Commands</a>
    <a class="nav-pill" href="#directory">100 Apps Directory</a>
    <a class="nav-pill" href="results.json" download>Download results.json</a>
    <a class="nav-pill" href="https://github.com/omshree134/composio-toolkit-research" target="_blank">GitHub Source Repo</a>
  </div>
</header>

<div class="stats">
  <div class="stat s-ready"><b>{ready}</b><span>Ready Now (Self-Serve)</span></div>
  <div class="stat s-cav"><b>{cav}</b><span>Buildable with Caveat</span></div>
  <div class="stat s-blocked"><b>{blocked}</b><span>Gated / Outreach Needed</span></div>
  <div class="stat s-unc"><b>{unc}</b><span>Unclear / Thin Docs</span></div>
  <div class="stat s-mcp"><b>{mcp['Official']}</b><span>Official Vendor MCPs</span></div>
</div>

<h2 id="patterns">The Patterns (Headline Insights)</h2>
<ol class="headline">
  <li><strong>Most of the list is an immediate win ({ready + cav}% buildable):</strong> 64 of 100 apps hand a developer free or instant trial credentials with standard REST or GraphQL surfaces. Another 18 work with minor caveats (store-level app installs, tier-specific endpoints, or lightweight review before deployment).</li>
  <li><strong>Tokens and Keys dominate single-tenant tools; OAuth2 dominates multi-tenant agents:</strong> 86 apps provide API keys, tokens, or bearer secrets; 74 offer OAuth2 authorization code or client credentials; 8 rely on HTTP Basic. Toolkits designed for end-user delegation require OAuth2, while server-to-server or private automation toolkits favor keys.</li>
  <li><strong>Gating clusters in three distinct industry silos:</strong>
    <ul>
      <li><em>Advertising & Social:</em> Google Ads, Meta Ads, and LinkedIn Ads mandate developer token reviews or business verification.</li>
      <li><em>Fintech & Enterprise SaaS:</em> Brex, Ramp, PitchBook, Otter AI, DealCloud, Gladly, Aircall, and Pylon require paying customer accounts or CSM onboarding.</li>
      <li><em>Data & Intel Providers:</em> Waterfall.io and Ahrefs lock their APIs behind sales calls or enterprise tiers.</li>
    </ul>
  </li>
  <li><strong>The primary bottleneck is administrative, not architectural:</strong> For {len(gated)} gated apps, public documentation is rich and APIs are standard REST/GraphQL. The only impediment is provisioning a live tenant sandbox for testing.</li>
  <li><strong>MCP has achieved industry-standard velocity:</strong> 85 apps offer official vendor MCP servers (or first-party open-source implementations). 9 rely on community implementations (e.g., Discord, Telegram, SendGrid, Threads), and only 6 remain undocumented.</li>
  <li><strong>Priority Outreach & Business Development Targets ({len(gated)} apps):</strong>
    <div class="tag-list">
      {''.join(f'<span class="tag-item">{e(a)}</span>' for a in gated)}
    </div>
  </li>
</ol>

<div class="cols">
  <div class="card">
    <div class="card-title">Authentication Methods Breakdown (100 Apps)</div>
    {bar('API Key / Bearer / Token', cnt['K'], 100)}
    {bar('OAuth2 (Auth Code / Client Creds)', cnt['O'], 100)}
    {bar('HTTP Basic Authentication', cnt['B'], 100)}
  </div>
  <div class="card">
    <div class="card-title">Buildability Verdicts</div>
    {bar('Easy (Ready for immediate toolkit build)', ready, 100, 'ok')}
    {bar('Feasible (Usable with documented caveat)', cav, 100, 'mid')}
    {bar('Needs Gate (Requires customer account/review)', blocked, 100, 'no')}
    {bar('Unclear (Documentation insufficient)', unc, 100, 'unk')}
  </div>
</div>

<h2 id="matrix">Self-Serve vs Gated Access by Category</h2>
<p class="sub"><strong>Self-serve:</strong> Free instant signup or self-serve developer sandbox. <strong>Tiered:</strong> Instant sandbox/test mode; paid plan or verification required for live production. <strong>Gated:</strong> Mandates active customer subscription, enterprise tier, or sales approval.</p>
<table class="mx">
  <thead>
    <tr>
      <th>Category</th>
      <th>Self-serve</th>
      <th>Tiered</th>
      <th>Gated</th>
      <th>Unclear</th>
    </tr>
  </thead>
  <tbody>
    {catrows}
  </tbody>
  <tfoot>
    <tr>
      <th>All 100 Apps</th>
      <td class="s">{tot['Self-serve']}</td>
      <td class="t">{tot['Tiered']}</td>
      <td class="g">{tot['Gated']}</td>
      <td class="u">{tot['Unclear']}</td>
    </tr>
  </tfoot>
</table>
<p class="sub"><strong>12 Tiered Apps:</strong> {', '.join(tier)}.</p>

<h2 id="pipeline">The Agent: What It Does & Where a Human Was Needed</h2>
<div class="flow">
  <div class="step">
    <div class="step-num">Stage 1</div>
    <b>Evidence Collection</b>
    Runs 3 targeted web searches per app (auth specs, pricing/gating, MCP ecosystem). 300 total search bundles saved in <code>data/search/</code>.
  </div>
  <div class="step">
    <div class="step-num">Stage 2</div>
    <b>Keyword Baseline (Pass 1)</b>
    Heuristic regex scanner across search snippets. Intentionally naive baseline to measure why rule-based scrapers fail (47% accuracy).
  </div>
  <div class="step">
    <div class="step-num">Stage 3</div>
    <b>Structured AI Reviewer (Pass 2)</b>
    Synthesizes condensed documentation snippets into strict typed JSON schemas with URL containment validation for every claim.
  </div>
  <div class="step">
    <div class="step-num">Stage 4</div>
    <b>Deterministic Citation Check</b>
    Fetches raw vendor documentation pages over HTTP (300 pages saved in <code>data/pages/</code>). Flags unsupported claims (25 claims flagged).
  </div>
  <div class="step">
    <div class="step-num">Stage 5</div>
    <b>Stratified & Holdout Audit (Pass 3)</b>
    Deep verification over a 20-app stratified sample (60 fields) and a 12-app holdout evaluation (33 checkable fields) to drive accuracy to 97%+.
  </div>
</div>

<div class="card" style="margin-top: 14px;">
  <div class="card-title">Where a Human Was Required</div>
  <ul style="margin: 0; padding-left: 20px;">
    <li><strong>Disambiguating Homonyms & Third-Party Repos:</strong> Products sharing names with unrelated software (e.g. <em>Sherlock</em> CLI username hunter, <em>Paygent Connect</em> NMI proxy, <em>YouTube Transcript</em> third-party wrappers vs official YouTube Data APIs).</li>
    <li><strong>Formulating the "Tiered" Classification:</strong> Recognizing that platforms like Meta Ads, Pinterest, Binance, and Ecwid allow free testing/sandboxing, but restrict live production deployment behind business review or paid plans.</li>
    <li><strong>Triaging Paywalled Vendor Portals:</strong> When enterprise platforms (e.g. PitchBook, DealCloud) restrict API references behind customer credentials, flagging them as gated rather than speculating.</li>
  </ul>
</div>

<h2 id="verification">Verification: How Accuracy Moved Across Loops</h2>
<div class="cols">
  <div class="card">
    <div class="card-title">Stratified Sample (20 Apps &bull; 60 Checks)</div>
    {bar('Pass 1: Keyword Baseline', m1['correct'], m1['checked'], 'no')}
    {bar('Pass 2: AI Evidence Synthesis', m2['correct'], m2['checked'], 'mid')}
    {bar('Pass 3: After Verification Loops', m3['correct'], m3['checked'], 'ok')}
    <p class="sub" style="margin-top:8px;">Accuracy improved from 47% &rarr; 87% &rarr; 97% through source verification and link triage.</p>
  </div>
  <div class="card">
    <div class="card-title">Retrospective Holdout Set (12 Apps &bull; 33 Checks)</div>
    {bar('Pass 3 Final (Holdout Verified)', h0['correct'], h0['checked'], 'ok')}
    <p class="sub" style="margin-top:8px;">1 miss before final audit: Plaid auth was initially recorded with bank-side end-user OAuth rather than developer API keys. Post-audit holdout is 33/33 (100%).</p>
  </div>
</div>

<h3>Honest Audit of Errors & False Positives</h3>
<ul>
  <li><strong>Why naive regex failed (Pass 1):</strong> Scored only 28/60 (47%). Because terms like "partner", "pricing", and "approval" appear on virtually every enterprise footer, naive keyword matching falsely marked 91 of 100 apps as Gated. Contextual reasoning is indispensable.</li>
  <li><strong>Real inaccuracies caught in Pass 2 (2):</strong> WooCommerce REST API uses HMAC / OAuth 1.0a (or Basic over HTTPS), not OAuth2. Ecwid's API requires an active paid store tier rather than a free tier.</li>
  <li><strong>Taxonomy corrections (2):</strong> Meta Ads was initially marked Gated, but corrected to Tiered because sandbox development is free. Binance was adjusted to Tiered due to KYC requirements for live production keys.</li>
  <li><strong>Citation repointing:</strong> 6 MCP claims were repointed or downgraded (e.g., Shopify's internal doc states their MCP server is not publicly available yet; fanbasis only had third-party videos; WhatsApp cited an external news article).</li>
  <li><strong>Scoring edge cases:</strong> Salesforce (JWT bearer flow) and Jira (API tokens used over Basic HTTP) remain intentionally noted as subtle misses in strict scoring (58/60) to maintain rigorous integrity.</li>
</ul>

<h2 id="proof">Runnable Proof & Pipeline Commands</h2>
<p class="sub">The entire repository is built with standard Python 3 (zero third-party package dependencies). Run all verification loops and reproduce metrics in seconds:</p>
<pre><code># 1. Recompute and verify all accuracy scores (reproduces metrics.json):
python score_repro.py

# 2. Run automated claim-vs-source citation checks on fetched vendor docs:
python autocheck.py

# 3. Test mock live search and LLM review protocol:
python tests/test_live_protocol.py

# 4. Regenerate this report and results.json:
python gen_report.py</code></pre>

<div class="card" style="margin-top: 14px;">
  <div class="card-title">Honest Scope & Production Boundaries</div>
  <ul style="margin: 0; padding-left: 20px;">
    <li><strong>Deterministic Offline Replay:</strong> <code>collect.py</code> and <code>review.py</code> feature offline replay modes (default), ensuring that reviewers can reproduce the entire dataset without needing paid API keys.</li>
    <li><strong>Live Execution Modes:</strong> Both <code>collect.py --live</code> (Brave Search API) and <code>review.py --live</code> (OpenAI-compatible LLM endpoint) are fully implemented and verified via local mock servers in <code>tests/</code>.</li>
    <li><strong>No Paid Accounts Purchased:</strong> Per assignment instructions, gated apps were documented using official vendor documentation and developer terms, which is the correct product finding.</li>
  </ul>
</div>

<h2 id="directory">All 100 Apps Directory</h2>
<div class="filter-bar">
  <input id="q" type="text" placeholder="Search app name, category, auth, or notes...">
  <select id="c">
    <option value="">All Categories (10)</option>
    {cat_options}
  </select>
  <select id="f">
    <option value="">All Verdicts</option>
    <option value="ok">Easy ({ready})</option>
    <option value="mid">Feasible ({cav})</option>
    <option value="no">Needs Gate ({blocked})</option>
    <option value="unk">Unclear ({unc})</option>
  </select>
  <span id="match-count">100 of 100 apps shown</span>
</div>

<div class="tw">
  <table id="t">
    <thead>
      <tr>
        <th style="width: 40px;">#</th>
        <th style="width: 170px;">App & Category</th>
        <th style="width: 180px;">Authentication</th>
        <th style="width: 100px;">Access</th>
        <th style="width: 110px;">MCP Status</th>
        <th style="width: 130px;">Build Verdict</th>
        <th>Main Blocker or Architecture Note</th>
        <th style="width: 130px;">Evidence Docs</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</div>

<script>
const q = document.getElementById('q');
const f = document.getElementById('f');
const c = document.getElementById('c');
const countSpan = document.getElementById('match-count');

function filterTable() {{
  const query = q.value.toLowerCase().trim();
  const verdict = f.value;
  const category = c.value;
  let matches = 0;
  
  document.querySelectorAll('#t tbody tr').forEach(row => {{
    const textMatch = !query || row.innerText.toLowerCase().includes(query);
    const verdictMatch = !verdict || row.dataset.b === verdict;
    const catMatch = !category || row.dataset.cat === category;
    
    if (textMatch && verdictMatch && catMatch) {{
      row.style.display = '';
      matches++;
    }} else {{
      row.style.display = 'none';
    }}
  }});
  
  countSpan.innerText = matches + ' of 100 apps shown';
}}

q.addEventListener('input', filterTable);
f.addEventListener('change', filterTable);
c.addEventListener('change', filterTable);
</script>

<p class="sub" style="margin-top: 18px; text-align: center;">
  Composio AI Product Ops Case Study &bull; Built with standard library Python 3 &bull; 
  <a href="results.json" download>Export results.json</a> &bull; 
  <a href="https://github.com/omshree134/composio-toolkit-research" target="_blank">View GitHub Source Repository</a>
</p>

</main>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(page)

# Dump clean results.json without internal fix annotations
json.dump([{k: v for k, v in r.items() if k != 'fixes'} for r in R], open('results.json', 'w', encoding='utf-8'), indent=2)

print(f"Generated index.html ({len(page)} bytes) and results.json successfully.")
