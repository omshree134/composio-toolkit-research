# Composio 100-App Agent Toolkit Research & Verification Pipeline

> **AI Product Ops Take-Home Case Study**  
> Candidate: **Om Shree Choudhary**  
> 🔗 **Live Interactive Case Study:** [omshree134.github.io/composio-toolkit-research](https://omshree134.github.io/composio-toolkit-research/)  
> 📁 **GitHub Source Repository:** [github.com/omshree134/composio-toolkit-research](https://github.com/omshree134/composio-toolkit-research)  
> 📊 **Machine-Readable Dataset:** [`results.json`](./results.json)

---

## Executive Summary

Composio turns SaaS applications into agent-callable tools. Before building an agent toolkit for any platform, Product Operations must evaluate:
1. **Authentication:** OAuth2 (code/client creds), API keys, Personal Access Tokens, or Basic auth.
2. **Access Model:** Self-serve developer signup vs. Tiered sandbox vs. Gated behind paid subscriptions, admin approval, or partner outreach.
3. **API & MCP Surface:** Documented REST/GraphQL APIs and existence of official or community Model Context Protocol (MCP) servers.
4. **Buildability Verdict:** Can an agent toolkit be built today, and what is the primary blocker if not?

This project implements an **automated research and multi-loop verification pipeline** across the requested **100 SaaS applications** spanning 10 industry categories. It features zero-dependency Python 3 scripts, full offline replay capability, deterministic source-citation auditing, and quantitative accuracy progression tracking.

---

## Headline Findings & Strategic Patterns

| Metric | Count | Strategic Insight |
|---|---|---|
| **Easy (Ready Now)** | **64** | Instant self-serve credentials, documented REST/GraphQL surfaces, and official/community MCP readiness. |
| **Feasible with Caveats** | **18** | Functional for toolkits, but requires store-level app installations, plan-specific endpoints, or lightweight verification. |
| **Gated / Outreach Needed** | **16** | Blocked administratively (requires paying enterprise subscription, partner review, or sales outreach). |
| **Unclear / Thin Docs** | **2** | Documentation insufficient or partner portal private. |
| **Official MCP Servers** | **85** | 85 of 100 apps have official vendor (or vendor GitHub org) MCP servers published. |

### Core Patterns
1. **Tokens Dominate Private Tools; OAuth2 Dominates Delegated Agents:**
   - **86 apps** offer API keys or Bearer tokens (ideal for single-tenant or headless automation).
   - **74 apps** offer OAuth2 flows (essential for user-delegated agents). Most mature apps support both.
2. **Gating Clusters in Three Silos:**
   - *Ad Networks (Google Ads, Meta Ads, LinkedIn Ads):* Free sandboxes, but live deployment requires developer token audits and business verification.
   - *Fintech & Enterprise SaaS (Brex, Ramp, PitchBook, DealCloud, Gladly, Aircall, Pylon):* Requires an active customer billing relationship.
   - *Data Intel (Waterfall.io, Ahrefs):* Locked behind sales calls or enterprise tiers.
3. **The Bottleneck is Administrative, Not Technical:**
   - For all 16 gated apps, public documentation is comprehensive and standard REST APIs exist. The only barrier is provisioning a live tenant for end-to-end integration testing.
4. **High MCP Velocity:**
   - MCP has transitioned from experimental to mainstream: 85% of evaluated apps have official MCP implementations. Only 9 rely on community packages, and 6 remain undocumented.

---

## Pipeline Architecture & Verification Loops

```
┌─────────────────┐     ┌──────────────────────┐     ┌────────────────────────┐
│  1. Collect     │ ──> │  2. Keyword Baseline │ ──> │  3. AI Reviewer        │
│  (300 Searches) │     │  (Naive: 47% acc.)   │     │  (Schema: 87% acc.)    │
└─────────────────┘     └──────────────────────┘     └────────────────────────┘
                                                                  │
┌─────────────────┐     ┌──────────────────────┐                  ▼
│  5. Final Score │ <── │  4. Citation Audit   │ <── ┌────────────────────────┐
│  (97% - 100%)   │     │  (autocheck.py)      │     │  Fetched 300 Docs      │
└─────────────────┘     └──────────────────────┘     └────────────────────────┘
```

1. **Stage 1 &mdash; Collection (`collect.py`):**
   - Dispatches 3 targeted search queries per app (`auth`, `gating/access`, `mcp`).
   - 300 search result bundles cached in `data/search/`.
2. **Stage 2 &mdash; Baseline Classifier (`pass1.py`):**
   - Fast, deliberately naive regex matcher over search snippets.
   - **Accuracy: 28/60 (47%)**. Demonstrates why keyword scraping fails: words like *"partner"*, *"approval"*, and *"pricing"* occur on almost every SaaS site, falsely classifying 91% of apps as gated.
3. **Stage 3 &mdash; Structured AI Reviewer (`review.py`):**
   - Synthesizes evidence per app into strict JSON enums (`Self-serve`, `Tiered`, `Gated`; `Official`, `Community only`).
   - Validates that every citation URL was present in the provided evidence snippets.
   - **Accuracy: 52/60 (87%)**.
4. **Stage 4 &mdash; Deterministic Source Verification (`fetch_verify.py` & `autocheck.py`):**
   - Fetched raw HTML/text for 300 cited documentation pages (saved in `data/pages/`).
   - `autocheck.py` scans fetched pages to confirm claimed auth mechanisms and access tiers are supported by page text. Flagged 25 anomalies for human/agent review.
5. **Stage 5 &mdash; Ground-Truth Stratified & Holdout Audit (`score_repro.py`):**
   - Stratified 20-app sample across 3 fields each (60 checks): **improved to 58/60 (97%)**.
   - 12-app retrospective holdout evaluation (33 checkable fields): **scored 33/33 (100%)**.

### Where a Human Was Essential
- **Homonym & Entity Disambiguation:** Differentiating tools with generic or overlapping names (e.g., *Sherlock* OSINT CLI vs. commercial analytics, *Paygent Connect* payment gateways, *YouTube Transcript* third-party APIs vs. official Google APIs).
- **Defining the "Tiered" Taxonomy:** Recognizing hybrid access models where test credentials are free/self-serve, but production requires formal business approval (e.g., Meta Ads, Pinterest, Binance).
- **Paywall Triage:** Confirming when developer portals are gated behind login screens (e.g., PitchBook, DealCloud).

---

## Accuracy Progression Summary

| Evaluation Phase | Sample Set | Fields Checked | Correct | Accuracy |
|---|---|---|---|---|
| **Pass 1: Keyword Baseline** | 20-app stratified | 60 | 28 | **46.7%** |
| **Pass 2: AI Review of Evidence** | 20-app stratified | 60 | 52 | **86.7%** |
| **Pass 3: Post-Verification Audit** | 20-app stratified | 60 | 58 | **96.7%** |
| **Holdout Evaluation** | 12-app holdout | 33 | 33 | **100.0%** |

*Note on Pass 3 misses:* Salesforce (JWT Bearer flow counted under Key/Token) and Jira (API token passed via HTTP Basic header) remain noted as subtle discrepancies under strict automated scoring (58/60) to maintain scoring integrity.

---

## How to Run the Research Pipeline

The pipeline uses **Python 3 standard library only** (no external pip dependencies).

### 1. Reproduce Accuracy Metrics (Deterministic Replay)
```bash
# Recompute all sample and holdout scores from frozen data
python score_repro.py
```

### 2. Run Automated Documentation Checks
```bash
# Verify claims against the 300 fetched vendor documentation pages
python autocheck.py
```

### 3. Run Protocol & Mock Server Tests
```bash
# Exercises live collection and LLM validation against local mock servers
python tests/test_live_protocol.py
```

### 4. Regenerate the Case Study & Results
```bash
# Builds index.html and results.json from data/
python gen_report.py
```

### 5. Inspect Live Modes (Optional)
Both `collect.py` and `review.py` support `--live` execution using standard environment variables:
```bash
# Live Search Collection (Brave Search API)
export SEARCH_API_KEY="your_brave_api_key"
python collect.py --live --out runs/live_search

# Live LLM Evidence Review (OpenAI-compatible endpoint)
export LLM_API_KEY="your_llm_api_key"
export LLM_MODEL="gpt-4o"
python review.py --live --search runs/live_search --out runs/live_records.json
```

---

## Repository Structure

```
.
├── index.html                      # Standalone interactive Case Study report (for GitHub Pages)
├── results.json                    # Machine-readable output for all 100 apps
├── metrics.json                    # Accuracy metrics across evaluation passes
├── autocheck.json                  # Automated claim-vs-source verification flags
├── gen_report.py                   # Script generating index.html & results.json
├── score_repro.py                  # Script verifying accuracy scores
├── autocheck.py                    # Script auditing fetched pages against claimed capabilities
├── collect.py                      # Stage 1 evidence collector (replay & live Brave API)
├── pass1.py                        # Stage 2 naive keyword classifier baseline
├── review.py                       # Stage 3 LLM evidence reviewer (replay & live OpenAI API)
├── fetch_verify.py                 # HTTP downloader for cited vendor documentation
├── view.py                         # CLI evidence inspector for triage
├── data/
│   ├── apps.json                   # List of 100 target apps & hints
│   ├── pass1.json                  # First-pass keyword baseline output
│   ├── pass2_frozen.json           # Frozen second-pass AI review output
│   ├── pass3_pre_holdout.json      # Pre-holdout snapshot
│   ├── pass3.json                  # Final audited records (100 apps)
│   ├── truth.json                  # Ground-truth labels for sample & holdout sets
│   ├── search/                     # 100 JSON search bundles (300 queries)
│   └── pages/                      # 300 raw text excerpts from cited vendor docs
├── logs/
│   └── manifest.json               # Timestamped audit log of all original fetches
└── tests/
    ├── mock_servers.py             # Local HTTP mock servers for Brave & OpenAI APIs
    └── test_live_protocol.py       # Integration tests for live protocol & guardrails
```

---

## Honest Scope & Production Boundaries

1. **No Paid Accounts Purchased:** In strict accordance with the assignment instructions, gated apps were identified via vendor documentation, pricing terms, and developer policies without purchasing enterprise licenses.
2. **Deterministic Replay Guarantee:** All search bundles and vendor documentation pages from the run are committed to `data/` to guarantee 100% reproducibility without third-party network flakiness.
3. **Official vs. Community MCP Audit:** MCP servers were strictly audited against vendor GitHub organizations and official documentation to prevent misattributing third-party community adapters as official releases.
