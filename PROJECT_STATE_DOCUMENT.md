# AI Supply Chain Equity Research — Project State Document
## Last Updated: May 27, 2026
## Current Version: v12 (card-layout report, per-layer charts, AI-rev% column, live on GitHub Pages)

---

## 0a. v12 — Card Layout, Charts Everywhere, AI-Rev% Column (May 27, 2026)

Content/presentation pass on the v11 pipeline (same DB + scripts). Edits in `data/narrative.py`, `data/layers_seed.json`, `data/companies_seed.json`, all four `scripts/`, and the builder. Report grew ~188 KB → ~230 KB. Verified via gstack `browse` (no console errors; 11 layer-heads, 21 charts, margin highlights all render).

**Layout redesign (every layer):**
- Two-column **layer header** (`render_layer_head`): left = three info cards (*What this layer does* / *Who pays whom* / *Key Metrics to Track*), right = *Analyst's Take* + stance. CSS `.layerhead`/`.infocard`/`.lhleft`/`.lhright`.
- "How to analyze this layer" → **Key Metrics to Track** (now a card, reuses the `how_to_analyze` text).
- **Margin that matters**: new `MARGIN_FOCUS` dict in narrative — per layer a `(margin_key, one-liner)`; the line shows in the Key Metrics card and the matching margin column is highlighted in the comp table (`.mfocus`). Framework: gross = pricing-power/software (L10/L9/L5/L4/L2/L1), operating = franchise profitability (L8/L6/L0), EBITDA = capital-intensive (L7/L3).
- Sub-segments rendered as a **card grid** (`render_subsegments` splits on " — ").
- GPU/CPU/ASIC box rebuilt on a **light theme** (was dark navy `#0f1b3d`); per-chip accent colors.

**Comp tables (every layer):**
- New **AI rev % of total** column (`ai_rev_share`, curated estimate per company-layer row, "~X% (est.)" / "100%" pure-play; for L8 it doubles as the cloud-revenue share). Added DB column `company_layer.ai_rev_share`.
- New **Δ % YoY** column (computed FY25→2026E where both exist).
- Sub-$1B revenue now shown in **millions** ($510M) via the updated `b()` formatter.

**Charts (`EXTRA_CHARTS` dict, merged after each layer's own charts):**
- L9: annual **LLM revenue trend** (2023→2030E bars). L8: **per-hyperscaler 2026E capex** + **big-5 capex history/forecast** bars; cloud-share donut legend now carries capex. L6: **optical transceiver / RAN / fiber** donuts (added to ethernet). L4: **GPU + ASIC + CPU** donuts (was GPU only). L3: **DRAM / NAND / HDD** donuts + sizes in titles (added to HBM). L1: **WFE + EDA** donuts.
- L2: **TSMC capacity & AI-mix trajectory** fact table via new `EXTRA_TABLES` dict + `render_extra_table`.

**Membership / data:**
- Added **EMCOR (EME)** to L7 (companies_seed + layers_seed + fetched its market data via a targeted yfinance call). Quanta/Comfort Systems were already there.
- Added **Meta** (L8, flagged captive — no external cloud, ~0% cloud-rev share, top-5 capex) and **Tencent (0700.HK)** (L8 Tencent Cloud) to the cloud table.
- Added **Alibaba (9988.HK)** to L9 (Qwen).
- L9 segment notes enriched with **lab-ownership stakes** (MSFT 27% OpenAI, AMZN largest Anthropic holder ~high-teens %, GOOGL/META own their models 100%, etc.).

**Schema note:** `company_layer` gained `ai_rev_share TEXT`. Because the table pre-existed, the migration drops + recreates `company_layer` (it is fully rebuilt from seed; market_data/financials are keyed by ticker and untouched), then re-runs `1_init_db.py` + `2_seed_companies.py`. 83 companies, 96 layer appearances.

---

## 0. v11 — Analyst Voice, Citations, Charts + Live Hosting (May 27, 2026)

v11 is a content/presentation overhaul of the v10 pipeline (same DB + scripts) plus public hosting. No schema or refresh-logic changes; all edits are in `data/narrative.py` and `scripts/4_build_report.py`.

**What changed:**
- **First-person head-of-research voice.** Every layer now opens with an **Analyst's Take** (the thesis) and a one-line **My Stance** (the investment call), stored as `analyst_take` / `stance` keys per layer in `LAYER_CONTENT`. Section intros (§2, §3) rewritten in first person.
- **Clickable citations.** Prose embeds `[[cite:ID]]` tokens; `process_citations()` in the builder numbers them in document order and renders **§8 Sources & References** from the `SOURCES` registry in `narrative.py`. ~62 footnotes → 14 sources. External links where a public URL exists. "Sources" added to the top nav.
- **Inline SVG charts.** `render_charts()` + `svg_donut()` / `svg_bars()` (pure SVG, no JS/libs). 6 donuts (LLM share, cloud, GPU, HBM, foundry, switching) + 2 bar charts (app ARR, enterprise API share). Chart data lives in a `charts` key per layer.
- **Per-layer $725B capex slice.** Each Market-Size cell shows that layer's slice of the $725B funnel vs the independently-researched TAM (`capex_slice` key). Rendered as a dashed callout inside `render_block_three()`.
- **§2 restructured.** Allocation table 2.1 now leads (with `allocation_intro` + sourced `allocation_source` line); the "is the $725B the top-level flow?" analysis is distilled into a `takeaway` callout *below* the table (was a callout above it, keyed `is_it_the_top_flow` in v10).
- **§3 numbering fixed.** Was 3.1 → 3.3 (no 3.2). Now **3.1** money flow, **3.2** value capture, **3.3** takeaways.
- **L9 share data restored as charts** (was collapsed to run-on bullets in v10): Global LLM revenue share (Counterpoint) donut + Enterprise API spend share (Menlo/Ramp) bars, both with ARR/valuation notes.
- **Comp-table columns relabelled** (`LAYER_TABLE_COLS`): Revenue FY25, Revenue 2026E, Gross Margin, Operating Margin, EBITDA Margin, Market Cap, P/E (TTM), Fwd P/E, P/S, EPS Growth.
- Report grew ~142 KB → ~184 KB. Verified via gstack `browse` (no console errors; donuts/bars/refs render).

**Live hosting (new):**
- Repo: **https://github.com/jefferror404/aisc-research** (public). GitHub account `jefferror404`.
- Live site: **https://jefferror404.github.io/aisc-research/** (GitHub Pages, `main` branch, root). `index.html` is a meta-refresh redirect to `report/ai_supply_chain_report.html`. The interactive graph is also live at `/ai_deal_network_layered.html` and is linked from §7 via a "Launch Interactive Deal Network Map" button.
- `.gitignore` excludes `data/aisc.db`, `.venv/`, `.gstack/`, `__pycache__`. The DB stays local; the committed HTML is the published artifact.
- **Publish workflow:** edit → `python scripts/4_build_report.py` → `git add report/ai_supply_chain_report.html && git commit && git push`. Pages redeploys in ~30s. Quarterly data refresh adds `3_refresh_market.py` before the build.
- GitHub Pages on a **private** repo needs a paid plan (422 error), which is why the repo is public.

---

## 1. Project Overview

User is conducting equity research on the AI supply chain for investment purposes. The goal is a comprehensive deep-dive mapping the entire AI value chain — from end-user apps to raw materials — with market share data, revenue figures, stock tickers, deal analysis, and actionable investment framing.

Coverage date: May 2026. User prefers focused leader-only coverage over breadth.

---

## 1a. v10 — Major Architecture Change (May 2026)

v10 replaces the static `.docx` workflow with a **refreshable data pipeline + scrollable HTML report**. The `.docx` (v9) is retained for reference but is no longer the primary deliverable. The interactive network graph HTML was intentionally NOT touched this round.

**New files:**
- `data/aisc.db` — SQLite database (the "simple database"). Tables: `companies` (curated entity data), `company_layer` (each appearance of a company in a layer, with contextual segment/contract notes), `market_data` (auto-fetched valuation + TTM margins, one snapshot row per refresh date), `financials` (auto-fetched per-fiscal-year revenue/margins/net income), `estimates` (FY+1 consensus revenue), `fx_rates`.
- `data/companies_seed.json` — curated master list (82 public tickers + private names). Entity-level: ticker, name, country, primary_layer, is_pure_play, fiscal_note.
- `data/layers_seed.json` — layer definitions + 92 `company_layer` appearances with curated `segment_rev_note` (segment $ + % of total), `key_contracts` (with durations), `backlog_rpo`, `note`.
- `data/narrative.py` — ALL prose (kept separate from data so writing and numbers refresh independently): META/what's-new, CAPEX (incl. the "$725B" answer), CONNECT (§3.3 value capture), RISKS, DEAL_WEB, GPU_CPU_ASIC deep-dive, and per-layer LAYER_CONTENT (what-it-does, who-pays-whom, expanded Bottleneck/Market-Size/Value-Added, sub-segments, glossary, deals_detail). Also CURATED_FY_NEXT_EST_USD_B overrides.
- `scripts/1_init_db.py` — create schema (idempotent).
- `scripts/2_seed_companies.py` — load seed JSONs into DB (re-run after editing seeds; never touches fetched data).
- `scripts/3_refresh_market.py` — **the refresh**: pulls yfinance → market_data/financials/estimates. Run with sandbox network access (on macOS the venv works directly).
- `scripts/4_build_report.py` — joins DB + narrative → `report/ai_supply_chain_report.html`.
- `report/ai_supply_chain_report.html` — the deliverable (~135 KB, self-contained, scrollable wide comp tables).
- `.venv/` — Python venv with `python-docx`, `yfinance`, `requests`.

**Refresh workflow (quarterly):** `python scripts/3_refresh_market.py` (update numbers) → `python scripts/4_build_report.py` (regenerate HTML). Edit `data/*_seed.json` for curated facts and `data/narrative.py` for prose, then re-run `2_seed_companies.py` + `4_build_report.py`.

**Data sourcing & accuracy notes:**
- Valuation (market cap, P/E TTM, fwd P/E, earnings/revenue growth, 3 margins, TTM + per-FY revenue/net income) is auto-fetched from yfinance. Verified accurate (cross-checked vs stockanalysis.com).
- yfinance's `.info` (valuation) is reliable; statement/estimate endpoints throw intermittent curl_cffi TLS errors → wrapped in retry(). In THIS sandbox, yfinance needs `dangerouslyDisableSandbox: true` (the sandbox SSL-intercepts curl_cffi); on the user's normal machine it works directly.
- **P/S is recomputed as market cap ÷ TTM revenue** (both USD) because Yahoo's reported P/S is broken for ADRs/foreign listings (divides USD price by local-currency sales). E.g. TSM: Yahoo 0.5× → correct 16.4×.
- International market caps converted to USD at refresh-date FX. Korean memory names (SK Hynix ~$0.97T, Samsung ~$1.3T) are correct for the May 2026 dataset — cross-checked vs stockanalysis.com; it is a memory-supercycle re-rating, not a data glitch.
- **FY+1 (FY26E) estimates from yfinance are unreliable** for foreign/ADR tickers (currency scaling) and some US names (MU showed $172B, SNDK $42B). Builder logic: curated override wins (TSM $160B, ORCL $67B guide, Alibaba); else trust yfinance only for US-reporting domiciles within a size-aware sanity band (≤2.6× for >$10B, ≤5× for $1–10B); else show "—".
- Segment splits, AI/cloud quarterly revenue, contract terms+durations, and backlog/RPO are hand-curated from earnings releases / filings (sourced via web research May 2026).

---

## 2. Legacy Deliverables (v9 — retained for reference)

### 2a. AI_Supply_Chain_Equity_Research_v9.docx (~62KB)
The main equity research report. 11-layer supply chain analysis, ~63 core names, ~1,700 paragraphs. Structure:
- §1 Executive Summary (11-layer overview table)
- §2 Hyperscaler Capex ($725B 2026; allocation breakdown)
- §3 How Layers Connect (money flow table + value capture map)
  - NEW in v9: §3.3 Value Capture Map — quantifies margins/pricing power per layer (NVDA 73% GM = 10/10 pricing power; Foxconn 5-7% GM = 2/10)
- §4 Supply Chain Layer by Layer (L10 → L0, top-down)
  - Each layer has: Bottleneck/Market Size/Value-Added block (3-column colored cells), inline glossary (yellow boxes), who pays whom, sub-segments, how to analyze, data tables with tickers
- §5 Key Risks & Debates (8 risk items)
- §6 Core Coverage Matrix (~63 names, all with tickers)
- §7 The AI Deal Web (OpenAI stack, Anthropic stack, NVIDIA portfolio, circular financing debate)
- §8 Key Data Points to Track
- §9 Companion Files (HTML + CSV description)

### 2b. ai_deal_network_layered.html (~40KB)
Interactive D3.js force-directed graph showing all major deals. v9 version is LAYERED — nodes are vertically anchored to their supply-chain layer (LLMs at top, foundry at bottom), X-axis free for force simulation. Features:
- 29 entities, 40 deals
- 6 horizontal layer bands (Apps → LLMs → Hyperscalers+Neoclouds → Networking/Fiber → Chips+Servers → Foundry+Equipment)
- Color-coded edges: green = equity, red = compute, orange = chip supply
- Click node → entity detail + all deals; click edge → deal detail
- Filter by deal type + entity category; search box
- Edge width proportional to deal size; node size proportional to total value
- Drag horizontally to reposition; vertical locked to layer; scroll to zoom

### 2c. ai_supply_chain_tickers.csv (~7KB)
~70 tickers categorized by layer (L0-L10), with Yahoo Finance-compatible symbols (.TW, .KS, .T, .HK, .PA, .L, .AS, .SS suffixes). Columns: Layer, Ticker_yfinance, Ticker_Native, Company, Country, Category, Notes. Ready for `yf.download()`.

---

## 3. Version History (v1 → v9)

| Version | Key Changes |
|---------|------------|
| v1 | Initial 11-layer report. Hyperscaler capex ($725B 2026), LLM revenue, full supply chain. |
| v2 | Added market share + revenue data to every layer. Restructured top-down L10→L0. Separated Layers 5 (servers) and 7 (DC REITs). Added LLM market share (Counterpoint Q1 26: Anthropic 31%, OpenAI 29%, Google 12%). |
| v3 | Added storage layer (SNDK +492% YTD, WDC +850% LTM, STX +600% LTM). Added Nokia (NVIDIA $1B stake). Added Bloom Energy as core. Added EDA layer (Synopsys, Cadence, Arm). Added ex-bitcoin miners (CORZ, WULF, HUT, CIFR, APLD). |
| v4 | Trimmed to ~55 core names. Added Hoya (75% EUV mask blanks), Daikin (cooling), BWXT (SMRs), Lumentum elevated to core. Added adjacent commodities sidebar. |
| v5 | Added ticker columns everywhere. Expanded Layer 10 apps table (Cursor $2B ARR, GH Copilot 4.7M paid). Added Corning (Meta $6B deal). Silicon photonics sub-segment. Fuel cell competitors (Ceres, Doosan, FuelCell Energy). Added Cerebras (CBRS — May 2026 IPO). |
| v6 | Added Section 8 "AI Deal Web" with all major deals + embedded SVG network diagram. |
| v7 | AI-RAN table added (Nokia/Ericsson/Huawei/Samsung/ZTE). Deleted Adjacent section. Moved L9 into 4.2. NEW Section 3 explainer + standalone technical glossary. Network chart moved OUT of doc to standalone HTML. Ticker CSV created. |
| v8 | Deleted standalone glossary → embedded terms inline within each layer using yellow callout boxes. Each layer now opens with "What this layer does / Who pays whom / Sub-segments / How to analyze this layer" deep analytical framing. §3 trimmed to concise money-flow overview only. |
| v9 | Added per-layer Bottleneck (severity + resolution), Market Size, Value-Added/Margins analysis blocks (3-column colored cells). NEW §3.3 Value Capture Map quantifying margins by layer. HTML chart upgraded to LAYERED top-to-bottom layout. |
| v10 | **Architecture pivot: SQLite DB + yfinance refresh pipeline + scrollable HTML report** (replaces static docx). Every public name now carries a full live comp set (FY rev, FY+1E, GM/OM/EBITDA, mkt cap, P/E TTM, fwd P/E, P/S, earnings growth) + segment-% of total. GPU vs CPU vs ASIC deep-dive added to L4. $725B "top flow vs total market" answered in §2. Bottleneck/Market/Value blocks expanded from bullets to full analysis. Contract durations added to every major deal. Deal elaboration paragraphs after each layer table. Network graph untouched (per user). |
| v11 | **Analyst-voice overhaul + live hosting.** First-person Analyst's Take + investment stance per layer. Clickable numbered footnotes → §8 Sources & References (SOURCES registry). Inline SVG donuts/bars for share data. Per-layer slice of the $725B funnel in Market Size. §2 restructured (table 2.1 leads, takeaway below + sourced). §3 numbering fixed (3.1/3.2/3.3). L9 share tables restored as charts. Comp columns relabelled. Published to GitHub Pages (public repo `jefferror404/aisc-research`). |
| v12 | **Card layout + charts everywhere + AI-rev% column.** Two-column layer header (3 info cards incl. Key Metrics to Track + Analyst's Take). New AI-rev-%-of-total and Δ%-YoY comp columns; per-layer "margin that matters" with highlighted column. Charts added across L9 (LLM trend), L8 (per-co + historical capex), L6 (optical/fiber/AI-RAN), L4 (GPU/ASIC/CPU), L3 (DRAM/NAND/HDD), L1 (WFE/EDA); TSMC capacity table re-added. Meta+Tencent added to L8, Alibaba to L9, EMCOR to L7; L9 ownership stakes shown. Sub-segments as cards; GPU/CPU/ASIC box light-themed. Sub-$1B revenue shown in millions. |

---

## 4. Key Corrections Made During Development

These are cases where the user caught errors or I self-corrected after deeper research:

| Item | Original Position | Corrected To | Version Fixed |
|------|-------------------|--------------|---------------|
| Storage (SNDK, WDC, STX) | Excluded as "not AI-relevant" | Core AI play — SNDK +492%, data lakes thesis | v3 |
| Nokia (NOK) | Excluded as "telecom" | Core — NVIDIA $1B equity, AI-RAN, +73% YTD | v3 |
| Bloom Energy (BE) | "Optional" | Core — Oracle 2.8 GW, +400% LTM | v3 |
| Hoya (7741.T) | Under-emphasized | Core — 75%+ EUV mask blanks, only validated High-NA | v4 |
| Daikin (6367.T) | Wrongly cut as "too diffuse" | Core — $2B FY30 DC cooling target, DDC+Chilldyne | v4 |
| BWXT | Marginal | Core — $7.3B backlog +50%, BANR SMR for DC | v4 |
| Lumentum (LITE) | "Optional optics" | Core — +1,474% LTM, NVDA $2B, 50-60% EML share | v4 |
| Corning (GLW) | Missing entirely | Core — Meta $6B fiber deal, +50% YTD | v5 |
| Cerebras (CBRS) | Missing (pre-IPO) | Core — May 2026 IPO, $10B OpenAI, $510M rev | v5 |
| Ceres Power (CWR.L) | Missing | Added — SOFC licensor, +237% YTD | v5 |
| Doosan Fuel Cell (336260.KS) | Missing | Added — Ceres licensee | v5 |
| FuelCell Energy (FCEL) | Missing | Added — 1.5 GW DC pipeline | v5 |
| Terumo/Lasertec ticker confusion | User's source list had wrong ticker (4543.T = Terumo medical) | Corrected to 6920.T = Lasertec | v3 |

---

## 5. The 11-Layer Structure

| Layer | Function | 2026E Market | Key Names |
|-------|----------|-------------|-----------|
| L10 Apps | End-user AI products | ~$30-40B | MSFT, GOOGL; Cursor/Claude Code/Glean (private) |
| L9 LLMs | Foundation models | ~$100B ARR | Anthropic 31%, OpenAI 29%, Google 12% |
| L8 Cloud | Hyperscalers + neoclouds | ~$520B | AWS 30%, Azure 25%, GCP 13%; CRWV, NBIS, IREN + ex-miners |
| L7 DC Real Estate | REITs + contractors | $200B+ | EQIX, DLR; PWR, FIX |
| L6 Networking | Switches + optics + fiber + AI-RAN | ~$60B | AVGO, ANET, NOK, MRVL, COHR, LITE, GLW |
| L5 Servers | AI servers + ODMs + PSUs | $444B FY25 | Foxconn 2317.TW, DELL, SMCI, Delta 2308.TW |
| L4 Accelerators | GPUs/ASICs | ~$300B | NVDA 86-90%, AVGO, AMD, MRVL, CBRS, MPWR |
| L3 Memory+Storage | HBM/DRAM/NAND/HDD | ~$300B+ | SK Hynix, Samsung, MU; SNDK, WDC, STX |
| L2 Foundry | Chip manufacturing + CoWoS | $200B | TSM 70%; AMKR, ASX |
| L1 EDA/Equipment | Design tools + WFE + materials | $140B+ | SNPS, CDNS, ARM; ASML, AMAT, LRCX, KLAC; Hoya, Hanmi, BESI |
| L0 Power+Cooling | Electricity + thermal + electrical | ~$80B AI-relevant | VRT, SU.PA, ETN; CEG, VST, BE, BWXT, GEV; Daikin |

---

## 6. Key Data Points Researched (verified via web search)

### Hyperscaler 2026 Capex
- AMZN ~$200B, MSFT $190B, GOOGL $185-190B, META $135-145B, ORCL $50B = ~$770B total
- Goldman cumulative 2025-2027: $1.15-1.4T
- BofA: 2026 capex consumes 94% of OCF after dividends

### LLM Layer
- OpenAI $25B ARR, Anthropic $30B ARR (passed OpenAI Apr 2026), $852B / $350B valuations respectively
- Counterpoint Q1 2026 revenue share: Anthropic 31.4%, OpenAI 29%, Google 12.1%, MSFT 7.2%, Tencent 4.8%, Baidu 3.6%, Alibaba 2.9%
- Enterprise API share (Menlo/Ramp Jan 2026): Anthropic 40%, OpenAI 25%, Google 20%

### The Deal Web (major entries)
- MSFT-OpenAI: 27% stake worth $135B post-PBC restructure (Oct 28, 2025); $250B Azure commitment
- NVIDIA-OpenAI: $100B LOI for 10 GW (Sep 22, 2025) — still LOI per Kress at UBS Dec 2025
- AMD-OpenAI: 160M share warrant (~10% AMD) for 6 GW deployment (Oct 6, 2025)
- Oracle-OpenAI Stargate: $300B / 5 years from 2027
- AMZN-OpenAI: $38B / 7 yr (Nov 3, 2025) — first AWS-OpenAI deal
- AMZN-Anthropic: $46B+ equity ($8B + $13B + $25B Apr 2026); $100B / 10 yr AWS
- GOOGL-Anthropic: $3B equity (14%); tens of $B for 1M TPUs
- MSFT+NVDA-Anthropic (Nov 18, 2025): MSFT $5B + NVDA $10B + Anthropic $30B Azure
- NVIDIA investments: non-marketable securities $3.4B→$22.25B; 2025: 67 rounds; 2026 YTD $40B+

### Memory/Storage
- SK Hynix 57% HBM, Samsung 22%, Micron 21%. SK Hynix 34% DRAM (took #1 2025)
- HBM TAM: $35B (2025) → $58B (2026) → $100B (2028)
- SNDK FQ3 26 $5.95B (+97% YoY), 78.4% GAAP GM. Storage: all sold out through 2026

### TSMC
- 69.9% pure-play foundry share; $122.5B FY25 → ~$160B 2026E
- CoWoS 35K→130K wafers/mo 2024→2026E; still over-subscribed
- Q1 2026 gross margin 66.2% (record)

### Key Margins Quantified (v9 addition)
- NVDA: 73% GM, 75% op margin → captures ~30% of all AI capex as profit
- TSMC: 66% GM, 49% net margin
- ASML: 51% GM, 35% op margin
- SK Hynix: 58% op margin Q4 25
- SNPS: 35% op margin (EDA software)
- EQIX: 49% GM, 51% adj EBITDA margin
- ANET: 41% op margin
- LITE: 32% op margin
- DELL: 20-22% GM, 8-12% op margin
- SMCI: 9.7-11.8% GM
- Foxconn AI servers: 5-7% GM

### Other Key Data
- Nokia: NVIDIA $1B equity Oct 2025; Q1 26 AI & Cloud +49% YoY; stock +73% YTD
- Bloom Energy: 2026 guide $3.4-3.8B (+80%); Oracle Project Jupiter 2.8 GW
- Cerebras: May 2026 IPO; $5.55B raised; opened +89%, closed +68%; $510M FY25 rev (+76%); 47% net margin
- Lumentum: Q3 FY26 $808M (+90% YoY); NVIDIA $2B; +1,474% LTM; 50-60% EML share
- Corning: Meta $6B deal Jan 2026; Q1 26 optical comm $1.8B (+36%)

---

## 6a. v10 Research Highlights (May 2026, sourced from earnings/filings)

**Hyperscaler AI/cloud (full detail in layers_seed.json):**
- AWS: FY25 $128.7B (+19%), op income $45.6B (35.4% margin); Q4'25 $35.6B → Q1'26 $37.6B (+5.6% QoQ, +28% YoY); $150B run-rate. AWS = 18% of Amazon's $716.9B rev but ~57% of operating income. Amazon RPO ~$200B.
- Azure: MS Cloud $54.5B FQ3'26 (+29%); Intelligent Cloud $34.7B (+30%); Azure +40% (Azure $ not disclosed). AI run-rate >$37B (+123%). Commercial RPO $627B (+99%; +26% ex-OpenAI).
- Google Cloud: FY25 ~$59B; Q4'25 $17.7B (+48%) → Q1'26 $20.0B (+63%, +13% QoQ); op income $6.6B (33%, vs $2.2B yr-ago). Backlog $462B. Cloud = 15% of Alphabet's $402.8B.
- Oracle: cloud $8.9B FQ3'26 (+44%), OCI $4.9B (+84%). RPO $553B (+325% YoY). FY26 guide $67B, FY27 $90B, FY30 OCI $144B.
- Alibaba Cloud: ~$5B/qtr, ~10% of $150.9B FY (Mar'26); AI rev +triple-digit 11 straight qtrs.

**Neocloud contracts (durations):** CoreWeave $22.4B OpenAI through May 2031 (Mar'25 $11.9B/5yr + May'25 $4B + Sep'25 $6.5B), RPO $66.8B, FY25 $5.13B. Nebius–Microsoft $17.4B through 2031 (→$19.4B) + Meta $3B/5yr; ARR exit '25 $0.9-1.1B. IREN–Microsoft $9.7B/5yr (20% prepay, GB300, ~$1.94B run-rate). Cipher–AWS $5.5B/15yr (300MW). Hut 8–Fluidstack(Google) $7.0B + $9.8B, both 15yr, 3% escalators. TeraWulf–Fluidstack(Google) 10yr ~$12.8B; HPC>BTC first time Q1'26.

**Segment splits:** NVDA DC $193.7B = 89.7% of $215.9B. AMD DC $16.6B (+32%) = 48% of $34.6B. AVGO AI semi $20B FY25 (+65%) = 31% of $64B; AI switch backlog >$10B. MRVL DC ~75% of $8.2B. TSM HPC 61% of Q1'26 rev (was 51% yr-ago). SK Hynix FY25 ₩97.1T (~$64.5B, +~50%), HBM rev >2x.

**Deal nature corrections:** NVDA–Lumentum/Coherent = $2B equity EACH (Mar 2026, not Oct'25), funding US fabs + multibillion purchase commitment + capacity-access rights (not a simple supply deal). AMD–OpenAI = 160M-share warrant (~10%, $0.01/sh, vests to $600) alongside 6 GW MI450.

**Valuation snapshot (2026-05-26):** NVDA $5.2T/PE33/fwd17; TSM $2.14T (P/S 16.4× recomputed); AVGO $2.0T; GOOGL $4.7T; MSFT $3.1T; AMZN $2.9T; SK Hynix ~$0.97T (fwd P/E ~5×); MU fwd P/E ~8×; CRWV $59B (op margin -7%); CBRS $53B (PE 583×, PS 103×).

---

## 7. User Preferences & Directives

- Prefers leaders-only coverage, drop noise (small, marginal, or diffuse-exposure names)
- Wants ticker columns on every table
- Wants tickers marked as "Private" or "Acquired by X" where applicable
- Wants technical terms explained INLINE in each layer (not standalone glossary)
- Wants deeper analytical openings per layer (who pays whom, sub-segments, how to analyze)
- Wants bottleneck severity, market size, and value-added/margins quantified per layer
- Wants the network chart to show BOTH network connections AND supply-chain layering (top-to-bottom)
- Deleted the "Adjacent / Second-Order" section (FCX, MP no longer covered)
- LLM section merged into §4.2 (not a separate section)
- Companion files (HTML + CSV) are separate from the .docx
- **(v10) Prefers an HTML report over docx** for wide, scrollable comp tables
- **(v10) Wants a simple, refreshable database** so data can be updated later (esp. yfinance-sourced valuation)
- **(v10) Wants accurate data from official earnings/financial statements + reliable sources**; tables hold the data, short paragraphs after tables carry elaboration
- **(v10) Wants for every public name: FY25 rev, FY26E rev, gross/operating/EBITDA margin, mkt cap, P/E TTM, fwd P/E, P/S, earnings growth, and segment revenue as % of total (or "pure play")**
- **(v10) Do NOT modify the network-graph HTML** unless asked
- **(v11) Wants a first-person, professional head-of-research voice** — unique insights/views per layer, not just tables and numbers; elaborate, don't write terse one-liners
- **(v11) Wants sources to be clickable** (footnotes → references) wherever a figure is cited
- **(v11) Wants share/ranking data as small tables or charts**, not run-on sentences
- **(v11) Wants each layer's Market Size to show its slice of the $725B capex** alongside the researched TAM
- **(v11) Wants the report public/shareable** — hosted live on GitHub Pages; will keep updating it

---

## 8. Names Explicitly Dropped (and why)

| Names | Why |
|-------|-----|
| ALB, LAC (lithium) | EV-only; no AI link |
| UUUU (Energy Fuels) | Sub-scale vs CCJ |
| RIO, BHP, GLEN, FCX, MP | Indirect commodity; removed from Adjacent in v7 |
| QCOM, MediaTek (2454.TW) | Mobile chips; edge AI secondary |
| NXP, STM, Sony (as chip play) | Auto/consumer; diffuse |
| TDK, Murata, Rohm | Passive components; too small |
| Ericsson (ERIC) | Lost AI-RAN race to Nokia; no NVIDIA partnership |
| IBM | Cloud share <2% |
| PLTR, NOW, CRM, SAP | Consume AI, don't build it |
| JD.com (9618.HK) | E-commerce |
| SoftBank (9984.T) | Holdco — better via ARM; appears in deal web only |
| Acer, Lite-On, Jabil, Flex | Consumer/contract manufacturing; diffuse |
| Hitachi, Sumitomo Heavy, Yaskawa, TEPCO, GS Yuasa | Japanese conglomerates; too diffuse |
| First Solar, Plug Power | Solar/hydrogen; marginal AI |
| SSE, Iberdrola, E.ON | European regulated utilities |
| AES, Brookfield Renewable | AI is small % of revenue |
| Modine, nVent | Real DC exposure but overlap with VRT/Schneider |
| NuScale | No commercial revenue; speculative SMR |

---

## 9. Potential Future Work

The user mentioned wanting to continue in a Claude project long-term. Potential next steps:
- **Portfolio construction view**: weight allocation by layer, risk-adjusted sizing
- **China AI stack deep-dive**: DeepSeek, Moonshot, Zhipu, Baidu, Alibaba, SMIC, CXMT, Huawei
- **Sovereign AI**: UAE (MGX, G42), Saudi (Aramco AI), Japan (Sakana), France (Mistral)
- **yfinance stock analysis**: use the CSV to pull performance data, correlations, factor analysis
- **Earnings tracker**: quarterly update template keyed to the "Key Data Points" in §8
- **AMD warrant tranche modeling**: what each GW deployment is worth to AMD shareholders
- **OpenAI IPO analysis**: expected timing, valuation scenarios, MSFT stake implications
- **Stargate execution tracker**: site-by-site progress vs $500B headline
- **TSMC CoWoS capacity modeling**: allocation between NVIDIA/AMD/Broadcom/Marvell
- **HBM4 qualification tracking**: SK Hynix vs Samsung vs Micron second-source dynamics
- **Power layer deep-dive**: grid queue modeling by market (PJM, ERCOT, NYISO)
- **Interactive dashboard**: React/HTML artifact showing real-time layer-by-layer metrics

---

## 10. Technical Notes

**v10 (current) — Python pipeline, all local to the project dir:**
- Python venv at `.venv/` (`python-docx`, `yfinance`, `requests`). Activate: `source .venv/bin/activate`.
- Pipeline order: `1_init_db.py` → `2_seed_companies.py` → `3_refresh_market.py` → `4_build_report.py`.
- `3_refresh_market.py` needs network egress: in the Claude Code sandbox run Bash with `dangerouslyDisableSandbox: true` (the sandbox SSL-intercepts curl_cffi); on the user's normal macOS shell it runs directly.
- yfinance `.info` is reliable; `income_stmt`/`revenue_estimate` are flaky (curl_cffi TLS) → retry() wrapper, ~6 tries.
- Report is a single self-contained HTML file (inline CSS, no external deps, no JS framework). Verified via the gstack `browse` binary (no console errors).
- CSV (`ai_supply_chain_tickers.csv`) and the v9 docx are retained but secondary; ticker conventions still Yahoo-Finance-compatible.

**v9 and earlier (legacy):** reports built with Node.js + `docx` npm package; build scripts `build_report_vN.js`; HTML charts use D3.js v7. No longer the active workflow.

**v11 builder additions (`scripts/4_build_report.py`):**
- `process_citations(body)` — regex-replaces `[[cite:ID]]` with numbered superscript links (document order); returns `(html, ordered_ids)`. Run once over the full assembled body in `build()` before appending references.
- `render_references(order)` — builds §8 from `N.SOURCES`.
- `svg_donut(rows, unit)` / `svg_bars(rows, unit)` / `render_charts(charts)` — pure inline SVG, palette `CHART_PALETTE`. Chart `source` adds a `[[cite:ID]]` token in the caption (processed in the global pass).
- `render_block_three()` injects the `capex_slice` dashed callout into the Market-Size cell.
- `render_layer_section()` renders Analyst's Take + stance after `what_it_does`, and charts after the three-up block.
- Self-contained: still no JS, no external deps. Charts are SVG; citations are in-page anchors.

**Hosting / git:** public repo `jefferror404/aisc-research`; `gh` CLI authenticated as `jefferror404`. Pages enabled via `gh api repos/.../pages` (source `main` / root). Update = rebuild HTML, commit `report/ai_supply_chain_report.html`, push.

---

*This state document should be uploaded as project knowledge alongside the deliverable files when creating the project. The live report is at https://jefferror404.github.io/aisc-research/.*
