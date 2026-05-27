# -*- coding: utf-8 -*-
"""
narrative.py — All prose content for the AI Supply Chain report.

Kept separate from the database (data/aisc.db) so you can edit the writing here
without touching the numbers, and refresh the numbers without touching the writing.
The report builder (scripts/4_build_report.py) imports NARRATIVE, LAYER_CONTENT,
and the section blocks below and merges them with the live DB data.

Coverage date: May 2026. Severity scale for bottlenecks: LOW < MEDIUM < HIGH < EXTREME.
"""

META = {
    "title": "The AI Supply Chain",
    "subtitle": "An Equity Research Deep-Dive — v12",
    "tagline": "11 Layers · Bottlenecks · Market Sizes · Value Capture · Live Comps",
    "coverage_date": "May 2026",
    "whats_new": [
        "Each layer now opens with a <b>two-column header</b>: three info cards (What this layer does / Who pays whom / Key Metrics to Track) on the left, my <b>Analyst’s Take</b> and stance on the right.",
        "New <b>AI revenue % of total</b> column on every comp table (curated estimate; pure-plays = 100%), plus a <b>Δ % YoY</b> revenue-growth column.",
        "Every layer flags the <b>margin that matters</b> (gross / operating / EBITDA) and highlights that column in the table.",
        "Many more <b>charts</b>: annual LLM-revenue trend, per-hyperscaler &amp; historical capex, optical / fiber / AI-RAN, GPU / ASIC / CPU, DRAM / NAND / HDD, WFE &amp; EDA splits — plus a TSMC capacity-trajectory table.",
        "Coverage added: <b>Meta &amp; Tencent</b> (L8 capex / cloud), <b>Alibaba</b> (L9), <b>EMCOR</b> (L7 contractors); L9 now shows each backer’s LLM ownership stake.",
        "Sub-segments redesigned as cards; the GPU/CPU/ASIC explainer rebuilt on a readable light theme; first-person analyst voice and clickable source footnotes throughout.",
        "Still a single scrollable HTML file backed by a refreshable SQLite database + one-command yfinance refresh.",
    ],
    "data_note": (
        "Valuation and margin data are pulled live from Yahoo Finance via yfinance and stored in a "
        "local SQLite database (snapshot date shown on each table). Segment splits, contract terms, "
        "backlog/RPO and AI-specific revenue are hand-curated from company earnings releases and filings. "
        "P/S is computed as market cap ÷ TTM revenue (both USD) to avoid the currency mismatch that breaks "
        "Yahoo's reported P/S for ADRs and foreign listings. International market caps are converted to USD "
        "at the refresh-date FX rate."
    ),
}

# Curated next-fiscal-year revenue estimates (USD billions). These OVERRIDE the
# yfinance FY+1 figure, which is unreliable for ADRs / foreign listings (currency
# scaling) and for a few US names. Sourced from company guidance or clean consensus.
CURATED_FY_NEXT_EST_USD_B = {
    "TSM": 160.0,    # TSMC guided >30% FY26 revenue growth (≈$121B → ~$160B)
    "ORCL": 67.0,    # Oracle's own FY26 (ending May'26) total-revenue guidance
    "9988.HK": 165.0,  # Alibaba ~+10% on ~$151B FY (Mar'26)
}

# Trust yfinance FY+1 only for these USD-reporting domiciles; suppress elsewhere
# (foreign/ADR estimates come back in distorted units). Curated values always win.
US_REPORTING_COUNTRIES = {"US", "US/Ireland"}


# ---------------------------------------------------------------------------
# SOURCES REGISTRY
#   Cite anywhere in prose with the token [[cite:ID]]. The builder assigns
#   footnote numbers in order of first appearance and renders a clickable
#   "Sources & References" section. id -> (label, detail, url-or-None).
# ---------------------------------------------------------------------------
SOURCES = {
    "counterpoint": ("Counterpoint Research", "Global GenAI / LLM revenue and AI-app market tracker, Q1 2026.", "https://www.counterpointresearch.com/"),
    "menlo": ("Menlo Ventures / Ramp", "‘The State of Generative AI in the Enterprise’ (2025) and Ramp enterprise card-spend data on LLM API share.", "https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/"),
    "synergy": ("Synergy Research Group", "Cloud infrastructure services market share and quarterly spend.", "https://www.srgresearch.com/"),
    "idc": ("IDC", "Worldwide Quarterly Server Tracker and infrastructure forecasts.", "https://www.idc.com/"),
    "trendforce": ("TrendForce", "HBM / DRAM / NAND market share, supply and contract-pricing data.", "https://www.trendforce.com/"),
    "yole": ("Yole Group", "Silicon photonics and advanced-packaging market forecasts.", "https://www.yolegroup.com/"),
    "delloro": ("Dell’Oro Group", "Data-center Ethernet switching and networking market share.", "https://www.delloro.com/"),
    "omdia": ("Omdia", "AI-RAN and telecom-infrastructure TAM forecasts.", "https://omdia.tech.informa.com/"),
    "mckinsey": ("McKinsey & Company", "‘The cost of compute’ and global data-center capital outlook to 2030.", "https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights"),
    "goldman": ("Goldman Sachs Research", "AI infrastructure investment forecasts, 2025–2027.", "https://www.goldmansachs.com/insights/"),
    "bofa": ("BofA Global Research", "Hyperscaler capex vs operating-cash-flow analysis.", None),
    "bernstein": ("Bernstein Research", "Stacy Rasgon / semiconductor and AI-buildout research on the power constraint.", None),
    "bloomberg": ("Bloomberg", "Market data, deal terms and capex guidance aggregation.", "https://www.bloomberg.com/"),
    "filings": ("Company filings & earnings", "SEC 10-K/10-Q, 20-F, and quarterly earnings releases (FY2025 / Q1 2026) for the named companies.", None),
    "yahoo": ("Yahoo Finance (yfinance)", "Live valuation and margin snapshot stored in the project’s SQLite database (see snapshot date on each table).", "https://finance.yahoo.com/"),
}


# ---------------------------------------------------------------------------
# SECTION 2 — HYPERSCALER CAPEX  (+ the "$725B" conceptual answer)
# ---------------------------------------------------------------------------
CAPEX = {
    "intro": (
        "Everything in this report ultimately traces back to one number, so I start here. The five largest "
        "hyperscalers — Amazon, Microsoft, Alphabet, Meta and Oracle — are guiding to roughly <b>$725B of "
        "capital expenditure in 2026</b> (Amazon ~$200B, Microsoft ~$190B, Alphabet ~$185–190B, Meta ~$135–145B, "
        "Oracle ~$50B).[[cite:filings]] In my framework this is the single most important money flow in the AI "
        "economy: it is the ‘source water’ that fans out down every layer below, and the one figure I watch as "
        "the leading indicator for the entire chain. Table 2.1 shows where I think it lands."
    ),
    "allocation_intro": (
        "My estimate of how the 2026 capex breaks down by category. I build this bottom-up from hyperscaler "
        "guidance and the bill-of-materials of a modern AI rack, then cross-check it against the sell-side; "
        "treat the ranges, not the point figures, as the signal."
    ),
    # Where the $725B flows. (category, % of capex, $ range, primary beneficiaries)
    "allocation": [
        ("AI accelerators (GPUs + ASICs)", "~40–45%", "$290–325B", "NVDA, AVGO, MRVL, AMD"),
        ("HBM + system memory", "~10–12%", "$70–85B", "SK Hynix, MU, Samsung"),
        ("Data-center shell, land, fiber", "~10–12%", "$70–85B", "EQIX, DLR, GLW"),
        ("Power & electrical equipment", "~8–10%", "$60–75B", "SU.PA, VRT, ETN, GEV, BE, BWXT"),
        ("Servers, CPUs, NICs, PSUs", "~8–10%", "$60–70B", "DELL, SMCI, Foxconn, Delta"),
        ("Networking", "~6–8%", "$45–60B", "ANET, AVGO, NOK, COHR, LITE"),
        ("Storage (SSDs + HDDs)", "~3–4%", "$22–30B", "SNDK, WDC, STX"),
        ("Cooling", "~3–4%", "$22–30B", "VRT, SU.PA, TT, JCI, Daikin"),
        ("Software, EDA, security", "~3–5%", "$25–35B", "SNPS, CDNS; in-house"),
    ],
    "allocation_source": (
        "Source: author’s estimates built from company capex guidance and earnings disclosures,[[cite:filings]] "
        "cross-checked against IDC server data,[[cite:idc]] TrendForce memory data[[cite:trendforce]] and "
        "McKinsey’s data-center capital model.[[cite:mckinsey]] Allocation shifts each earnings cycle."
    ),
    "allocation_note": (
        "Accelerators are the largest single bucket and the tightest bottleneck, while power &amp; cooling is the "
        "fastest-growing line as rack density climbs from ~130 kW (Blackwell) toward ~1 MW (Rubin)."
    ),
    # Distilled key takeaway, rendered AFTER table 2.1 (the user's direct question, answered concisely).
    "takeaway": {
        "heading": "So is the $725B the ‘top-level flow’, and does it equal the market size?",
        "body": [
            ("My answer: <b>yes, it is the keystone flow you should track above all others — but no, it is not the "
             "total addressable market.</b> I think of $725B as the top of the <i>infrastructure funnel</i>: it is "
             "annual <i>capital spending</i> by the five biggest buyers, and it cascades into accelerators (L4), "
             "memory (L3), servers (L5), networking (L6), data centers (L7) and power (L0)."),
            ("It understates the full AI economy for three reasons I keep front of mind. <b>(1) It is capex, not "
             "revenue</b> — the market also includes the operating revenue flowing in from the top (apps ~$30–40B, "
             "models ~$100B ARR),[[cite:counterpoint]] which is the demand the capex is a bet on. <b>(2) It is only "
             "the big five</b> — add neoclouds, sovereign AI, Chinese hyperscalers and enterprise clusters and "
             "Goldman models $1.15–1.4T of cumulative spend across 2025–27.[[cite:goldman]] <b>(3) It is partly "
             "circular</b> — some of it flows to NVIDIA, which reinvests in customers that buy more compute, so the "
             "headline double-counts (see §7). The number I actually watch is the gap: ~$725B of spend against "
             "~$170B of AI revenue today. Closing or not closing that gap is the central bull/bear debate of the "
             "cycle — I return to it in §5."),
        ],
    },
}

# ---------------------------------------------------------------------------
# SECTION 3 — HOW LAYERS CONNECT + 3.3 VALUE CAPTURE
# ---------------------------------------------------------------------------
CONNECT = {
    "intro": (
        "Having sized the source water, I want to trace where it goes. A single hyperscaler capex dollar fans out "
        "across all 11 layers, and the chain is not strictly linear: hyperscalers (L8) own custom chips (L4: "
        "Trainium, TPU) and apps (L10: Copilot), and a bottleneck at any layer (HBM in 2024–25, CoWoS today, power "
        "in 2026–27) caps the throughput of everything above it. Two questions decide where the money <i>stays</i>: "
        "how the dollar physically moves (3.1), and who keeps the most of it as profit (3.2). My synthesis of both "
        "is in 3.3."
    ),
    "value_capture_intro": (
        "This is the part I care most about as an investor. Two metrics together explain who keeps the most of "
        "each capex dollar: <b>wallet share</b> (what % of capex flows into the layer) and <b>gross/operating "
        "margin</b> (how much of that the layer keeps as profit). High wallet share × high margin is what defines "
        "the great businesses in this chain. The pattern, in my view, is barbell-shaped: the biggest profit pools "
        "sit at the chip (L4) and its irreplaceable inputs (L2 foundry, L1 EUV, L3 HBM), while the "
        "hardware-integration middle (L5 servers/ODMs) does real and fast-growing work at commodity margins. The "
        "margins in the table below are pulled live from the database, not hard-coded."
    ),
    "observations": [
        ("NVIDIA captures the largest single profit pool in the entire chain — roughly $120B of net income on "
         "$216B of revenue (FY26), equivalent to capturing on the order of a third of all AI capex as profit. "
         "No other layer comes close in absolute dollars."),
        ("The highest-quality monopolies cluster at the input end (L1, L2): ASML (EUV), TSMC (leading-edge + "
         "CoWoS), Hoya (EUV mask blanks), Hanmi (HBM bonders). Their margins are durable because the barrier to "
         "replicate them is measured in decades and tens of billions of dollars, not quarters."),
        ("The lowest-value layer is hardware integration (L5 branded OEMs and ODMs): Foxconn runs 5–7% gross "
         "margins on AI servers. The work is real and volumes are exploding, but pricing power is near zero — "
         "margins compress as scale rises. Own the scarcity, not the assembly."),
    ],
    # 3.1 money flow. (step, who pays whom, example)
    "money_flow": [
        ("1. End-customers → Apps (L10)", "Consumers + enterprises pay subscriptions / per-seat licenses", "$20/mo for ChatGPT Plus → OpenAI"),
        ("2. Apps → Foundation Models (L9)", "Apps are the model, or pay per-token via API", "Cursor pays Anthropic for Claude API"),
        ("3. LLMs → Cloud (L8)", "Labs are the biggest customers of hyperscalers + neoclouds", "Anthropic $100B/10-yr AWS; OpenAI $300B/5-yr Oracle"),
        ("4. Cloud → Data Centers (L7)", "Own DCs or lease from REITs; hire builders", "MSFT leases Equinix space; pays Quanta to build"),
        ("5. Cloud/DC → Networking (L6)", "Each rack needs switches, optics, fiber", "AWS buys Arista switches + Corning fiber + Lumentum 1.6T optics"),
        ("6. Cloud → Servers (L5)", "ODMs assemble the physical racks", "MSFT pays Foxconn to assemble GB200 NVL72 racks"),
        ("7. Servers → Accelerators (L4)", "GPUs/ASICs = 40–45% of server cost", "Foxconn buys NVIDIA Blackwell GPUs"),
        ("8. Chips → Memory (L3)", "Every GPU needs HBM + DRAM + storage", "NVIDIA buys HBM3E from SK Hynix"),
        ("9. Chips → Foundry (L2)", "Fabless designers send designs to TSMC", "NVIDIA pays TSMC to fab + CoWoS-package Blackwell"),
        ("10. Foundry → Equipment (L1)", "Foundries buy WFE + materials + software", "TSMC buys ASML EUV + Hoya mask blanks"),
        ("11. Everything → Power (L0)", "Every layer needs electricity; cooling removes heat", "AWS signs Talen 960 MW nuclear PPA"),
    ],
    # 3.3 value capture. (layer label, wallet share, ticker for LIVE margin, margin type 'om'|'gm',
    #                      pricing power 1-10, takeaway)
    "value_capture": [
        ("L4 — Accelerators", "~40–45%", "NVDA", "om", "10 — monopoly", "Largest single profit pool: ~$120B net income on $216B revenue (FY26)."),
        ("L2 — Foundry", "~5–7%*", "TSM", "om", "9 — near-monopoly", "Highest-quality monopoly; sole leading-edge + CoWoS. *chip-cost component."),
        ("L3 — HBM/Memory", "~10–12%", "000660.KS", "om", "9 — sold-out oligopoly", "SK Hynix at cycle peak; HBM TAM $35B→$100B (2028). Priced for mean-reversion (fwd P/E ~5×)."),
        ("L1 — EUV", "~3–4%*", "ASML", "om", "10 — pure monopoly", "Sole EUV supplier; High-NA $380M/unit, no substitute. *litho component."),
        ("L1 — EDA", "~1%", "SNPS", "om", "9 — duopoly", "Software economics: ~95% incremental gross margins on every chip designed."),
        ("L8 — Cloud (hyperscale)", "captures L9→L8", "MSFT", "om", "8 — three-player oligopoly", "Captures the labs' compute spend at 35–50% margins; $1.8T+ combined backlog."),
        ("L6 — Networking + Optics", "~6–8%", "ANET", "om", "7–8 — capacity-constrained", "Optics (LITE/COHR) supply-bottlenecked through 2027; switching leaders 40%+ margins."),
        ("L7 — DC REITs", "~3–4%*", "EQIX", "om", "7 — interconnection moats", "High recurring revenue, capital-intensive. *real-estate component."),
        ("L0 — Power & Equip", "~8–12%", "VRT", "om", "6–7 — supply-constrained", "Multiple suppliers, but transformer/turbine lead times = pricing power."),
        ("L5 — Servers / ODMs", "~8–10%", "2317.TW", "gm", "2 — near-commodity", "Foxconn ~6% gross margin on AI servers; volume game, margins compress with scale."),
    ],
}

# ---------------------------------------------------------------------------
# SECTION 5 — RISKS
# ---------------------------------------------------------------------------
RISKS = [
    ("Revenue-to-Capex Gap",
     "$725B of 2026 capex versus ~$100B of LLM ARR + ~$70B of hyperscaler AI revenue is a ~4–5x gap. Backlog "
     "(Microsoft $627B RPO, Oracle $553B, Google $462B) is the bull case — it implies the demand is contracted, "
     "not hypothetical. The bear case is that backlog is concentrated in a handful of model labs funded partly "
     "by their own suppliers."),
    ("Circular Financing",
     "NVIDIA → OpenAI / Anthropic / CoreWeave → NVIDIA-chips loops now exceed $150B in announced flows. Vendor "
     "investing in customer, customer buying vendor's product, both booked — 'round-tripping' risk. Not illegal "
     "or hidden, but it inflates apparent demand and concentrates counterparty risk."),
    ("Hyperscaler ASIC Substitution",
     "Google TPU, AWS Trainium ($20B+ run-rate), Meta MTIA and Microsoft Maia are in production; Broadcom's "
     "custom-AI revenue alone hit $20B in FY25. Every ASIC GW is a GW NVIDIA does not sell at merchant margins. "
     "The offset: total demand is growing faster than ASICs can absorb it — so far."),
    ("Power & Buildout Delays",
     "Bernstein’s Rasgon: the binding constraint is increasingly ‘physical inability to accept delivery because "
     "the buildings and power aren’t ready.’[[cite:bernstein]] Grid interconnect queues run 7–10 years; transformer "
     "and switchgear lead times exceed 100 weeks."),
    ("Storage / Memory Cycle Risk",
     "SNDK +492% YTD, STX +600% LTM, WDC +850% LTM; NAND contract prices +246% in 2025. Memory is cyclical — "
     "today's sold-out, peak-margin conditions (SK Hynix 80%+ operating margin) have always mean-reverted. Low "
     "forward P/Es (5–8x) reflect the market pricing in an eventual down-cycle."),
    ("Optics Cycle Risk",
     "Lumentum +1,474% LTM at ~50x forward earnings; AAOI +441% YTD. The optics complement to every GPU upgrade "
     "is real, but the multiples assume the LTA-backed boom runs uninterrupted through 2027."),
    ("Taiwan / Geopolitics",
     "TSMC manufactures essentially all leading-edge AI silicon and holds the CoWoS monopoly; Hoya supplies "
     "~75% of EUV mask blanks from Japan. Single-country / single-supplier tail risks sit under the whole chain."),
    ("Funding & Free Cash Flow",
     "BofA estimates 2026 hyperscaler capex consumes ~94% of operating cash flow after dividends, versus a "
     "~40% ten-year average.[[cite:bofa]] The capex is increasingly debt- and prepayment-financed; a demand wobble "
     "would hit FCF and credit metrics fast."),
]

# ---------------------------------------------------------------------------
# SECTION 7 — DEAL WEB (kept concise; full interactive view is the companion HTML graph)
# ---------------------------------------------------------------------------
DEAL_WEB = {
    "intro": (
        "Three patterns define this cycle: (1) model labs signing decade-long compute commitments larger than "
        "their current revenue; (2) chipmakers taking equity in their own customers; and (3) ex-bitcoin miners "
        "and neoclouds raising debt against 10–15-year hyperscaler leases. The companion file "
        "<code>ai_deal_network_layered.html</code> visualizes the full network interactively."
    ),
    "openai_stack": [
        ("Microsoft", "27% economic stake (~$135B) + $250B Azure commitment; IP rights to 2032 (post-PBC restructure, Oct'25)."),
        ("NVIDIA", "Up to $100B for 10 GW — still an LOI as of late 2025; first GW H2'26 on Vera Rubin."),
        ("AMD", "6 GW MI450 + a 160M-share warrant (~10% of AMD at $0.01, vesting up to a $600 share price)."),
        ("Oracle (Stargate)", "~$300B over 5 years from 2027 — Abilene TX + 5 new sites."),
        ("Amazon", "$38B over 7 years (first AWS–OpenAI deal, Nov'25)."),
        ("CoreWeave", "$22.4B through May 2031 (three tranches: Mar/May/Sep 2025)."),
        ("Broadcom", "10 GW of custom OpenAI silicon through 2030."),
        ("Cerebras", "$10B / 750 MW via AWS Bedrock."),
    ],
    "anthropic_stack": [
        ("Amazon", "$8B + $13B + $25B (Apr'26) = $46B+ equity; ~$100B / 10-yr AWS; Project Rainier (1M+ Trainium2)."),
        ("Google", "$3B equity (~14%); tens of $B for 1M+ TPUs (Ironwood)."),
        ("Microsoft", "$5B (up to $10B) equity + $30B Azure on Grace Blackwell / Vera Rubin."),
        ("NVIDIA", "Up to $10B (joint with Microsoft, Nov'25)."),
        ("Broadcom", "Multi-gigawatt custom silicon (confirmed Apr'26)."),
    ],
    "nvidia_portfolio_note": (
        "NVIDIA's non-marketable equity grew from $3.4B (Jan'25) to $22.25B (Jan'26) across 67 venture rounds in "
        "2025, with $40B+ more in 2026 YTD. Stakes span its own customers and suppliers: OpenAI (up to $100B LOI), "
        "Anthropic (up to $10B), xAI ($2B+), Intel ($5B), CoreWeave ($2B), Nebius ($2B), Nokia ($1B/2.9%), "
        "Lumentum ($2B), Coherent ($2B), and Synopsys. The optics investments (Lumentum, Coherent) are equity "
        "stakes that fund US fabs plus multibillion purchase commitments and capacity-access rights — securing "
        "supply, not just returns."
    ),
    "circular_note": (
        "'Round-tripping' = a vendor invests cash in a customer; the customer uses that cash to buy the vendor's "
        "product; it counts as both an investment and revenue. The biggest loops: NVDA→OpenAI→NVDA (~$100B), "
        "MSFT→OpenAI→Azure/NVDA ($250B), AMZN→Anthropic→AWS ($100B), NVDA→CoreWeave→NVDA ($2B equity + ~70% of "
        "CoreWeave's opex flowing back to NVIDIA). It is disclosed and legal, but it concentrates risk and "
        "inflates the apparent independence of demand."
    ),
}

# ---------------------------------------------------------------------------
# THE GPU vs CPU vs ASIC DEEP-DIVE  (Layer 4 feature box — user request)
# ---------------------------------------------------------------------------
GPU_CPU_ASIC = {
    "heading": "GPU vs CPU vs ASIC — what each does, and can one replace another?",
    "intro": (
        "These are the three chip types that do computation in an AI data center. They are <b>complementary, "
        "not interchangeable</b>: a modern AI server uses all three. The investment thesis, the bottleneck, and "
        "the profit pool, however, sit overwhelmingly on the <b>accelerator</b> (GPU + ASIC) — which is why this "
        "layer is named for accelerators, not CPUs."
    ),
    "cards": [
        {"name": "CPU — Central Processing Unit",
         "tagline": "The generalist / orchestrator",
         "body": (
             "A few powerful cores (8–128) optimized for <b>sequential, branch-heavy, latency-sensitive</b> work: "
             "running the operating system, orchestrating the job, moving data to the accelerators, handling "
             "storage and networking. Analogy: a few experts solving hard problems one step at a time. Every AI "
             "server still needs one — in NVIDIA's GB200, the Grace CPU is the 'G' paired with the Blackwell GPU. "
             "Examples: Intel Xeon, AMD EPYC, NVIDIA Grace (Arm), AWS Graviton."),
         "value": "Necessary but lower-value: smaller share of the bill of materials, a competitive 3-way market (Intel/AMD/Arm) → thinner margins. Not the AI thesis."},
        {"name": "GPU — Graphics Processing Unit",
         "tagline": "The engine of AI",
         "body": (
             "Thousands of simpler cores optimized for <b>massively parallel math</b> (matrix multiplication). "
             "Training and running neural networks is almost entirely matrix multiply across billions of "
             "parameters — embarrassingly parallel — so GPUs are 10–100x more efficient than CPUs at it. Analogy: "
             "thousands of students each doing simple arithmetic at once. Crucially, GPUs are <b>programmable</b>: "
             "the same chip runs any model architecture. Examples: NVIDIA Blackwell/Rubin, AMD Instinct."),
         "value": "Highest value in the chain. ~40–45% of every capex dollar; NVIDIA's ~86–90% share + 73% gross margin = the single largest profit pool in AI."},
        {"name": "ASIC — Application-Specific IC",
         "tagline": "The specialist",
         "body": (
             "A chip hard-wired for <b>one workload</b> (e.g. transformer inference). For that one task it is even "
             "more power- and cost-efficient than a GPU — typically 30–50% cheaper per workload — but it cannot "
             "flexibly run new model types. Hyperscalers design ASICs for their own huge, stable workloads. "
             "Examples: Google TPU, AWS Trainium, Meta MTIA, Microsoft Maia (designed with Broadcom / Marvell, "
             "built by TSMC)."),
         "value": "The hyperscalers' lever against NVIDIA pricing. Counted as cloud revenue (L8) and as Broadcom/Marvell silicon (L4). The key substitution battle is GPU vs ASIC — not GPU vs CPU."},
    ],
    "can_they_replace": (
        "<b>CPU vs GPU: no — they are partners, not substitutes.</b> A CPU <i>can</i> technically run AI but is "
        "so much slower at the parallel math that it is economically unviable for training or large-scale "
        "inference; a GPU is poor at the serial control logic a CPU handles. They sit side-by-side in every "
        "node — the CPU orchestrates, the GPU computes. <b>The real substitution battle is GPU vs ASIC,</b> "
        "because both do the AI math. ASICs win on cost/efficiency for a fixed, high-volume workload; GPUs win "
        "on flexibility, time-to-market, and running any model. A hyperscaler with one enormous stable workload "
        "(Google's ranking on TPU) builds an ASIC; everyone else — and anyone needing to run the newest models — "
        "buys GPUs. That is why merchant GPU demand keeps rising even as ASIC volumes grow."
    ),
    "use_cases": [
        ("CPU", "Web/app servers, databases, job orchestration, the host in every AI node, light inference."),
        ("GPU", "Training frontier models; large-scale + flexible inference; the default for anyone without the scale to design a custom ASIC."),
        ("ASIC", "A hyperscaler's own massive, stable workload — Google search/ads ranking (TPU), Amazon's Anthropic training (Trainium)."),
    ],
}

# ---------------------------------------------------------------------------
# PER-LAYER CONTENT
#   each: what_it_does, who_pays_whom, bottleneck{severity,points[]},
#         market_size[], value_added[], how_to_analyze, sub_segments[],
#         glossary[(term,def)], deals_detail[] (paragraphs after the table)
# ---------------------------------------------------------------------------
LAYER_CONTENT = {

  "L10": {
    "what_it_does": "Where end-users actually pay for AI. Apps either bundle a foundation model behind a UI (ChatGPT, Claude.ai) or wrap one via API to solve a specific job (Cursor for coding, Harvey for legal).",
    "analyst_take": "My read: L10 is where cash <i>enters</i> the system, but very little of it stays here today — the model underneath captures most of the economics. I treat the app layer as an option on workflow lock-in. The winners I’d back are the ones with distribution (Microsoft pushing Copilot into 400M+ M365 seats) or proprietary data and workflow (Harvey, Glean); the undifferentiated ‘GPT wrappers’ get squeezed every time model prices fall. The frustrating part for public investors is that almost every pure-play is still private, so the only liquid exposure is Microsoft and Alphabet.",
    "stance": "Own the distribution (MSFT) and the proprietary-workflow winners; avoid thin wrappers with no data moat. Mostly a private-market layer for now.",
    "capex_slice": "Not a slice of the $725B. L10 is the <i>demand</i> the capex is built to serve — the ~$30–40B app market is end-user revenue, not capital spending.",
    "charts": [
      {"title": "Selected AI-app annualized run-rates", "source": "filings", "type": "bar", "unit": "$B ARR",
       "rows": [("M365 Copilot (run-rate)", 5.0, "~$5B+"), ("Cursor (Anysphere)", 2.0, "$2B in ~24 mo"),
                ("Perplexity", 1.0, "~$1B"), ("Claude Code", 1.0, "$1B+ in 6 mo")]},
    ],
    "who_pays_whom": "Consumers pay $20–200/month subscriptions; enterprises pay per-seat licenses (Microsoft 365 Copilot $30/user/mo; GitHub Copilot Business $19). Apps in turn pay LLM providers (L9) per token, or — if they own the model — pay the cloud (L8) directly.",
    "bottleneck": {"severity": "LOW", "points": [
      "Not a capacity bottleneck — apps depend on L9 model availability and L8 compute, both of which the $725B capex is solving.",
      "The real constraint is <b>customer acquisition and retention economics</b>: Cursor, Cognition, Windsurf and others compete fiercely, and switching costs are low because they can swap the underlying model.",
      "Margin compression risk: an app's gross margin is whatever is left after paying the model provider; if model prices don't fall as fast as competition pushes app prices down, the middle gets squeezed.",
    ]},
    "market_size": [
      "~$30–40B in 2026E[[cite:counterpoint]] — the fastest-growing software category in history.",
      "Cursor reached $2B ARR within ~24 months; Claude Code hit $1B+ ARR within 6 months of launch; GitHub Copilot has 4.7M paid subscribers.[[cite:filings]]",
      "Still tiny relative to the $100B+ model layer below it — most of the value today is captured by the model, not the app wrapper.",
    ],
    "value_added": [
      "VERY HIGH for winners, LOW for losers. Winning apps earn 70–90% SaaS-like gross margins — but only on the spread above model spend.",
      "The durable moats are distribution (Microsoft bundles Copilot into 400M+ M365 seats), proprietary workflow/data (Glean, Harvey), and habit.",
      "Most pure-plays remain private (Anysphere/Cursor, Glean, Perplexity, Cognition); public-market access is essentially limited to Microsoft and Alphabet.",
    ],
    "how_to_analyze": "Track ARR growth + net revenue retention for the private names (via funding rounds), and seat counts + attach rates for the public proxies. The key question for any app: how much of its gross margin survives the next round of model price cuts and competition?",
    "sub_segments": [
      "General-purpose chatbots — ChatGPT, Claude.ai, Gemini App (~$20B).",
      "Coding assistants/agents — Cursor ($2B ARR), GitHub Copilot (4.7M subs), Claude Code ($1B+); fastest-growing.",
      "Enterprise productivity — M365 Copilot (~$5B+ run-rate), Google Workspace AI.",
      "Vertical agents — Harvey (legal), Glean (search), Sierra (CX), Cognition/Devin (coding); mostly private.",
      "AI search — Perplexity (~$1B ARR); creative — Midjourney, Runway, ElevenLabs.",
    ],
    "glossary": [
      ("ARR (Annualized Run-Rate)", "Current monthly revenue × 12 — how private AI companies report scale. Forward-looking, not GAAP."),
      ("Net revenue retention", "Revenue this year from last year's cohort ÷ what they paid last year. >100% means existing customers expand."),
    ],
    "deals_detail": [],
  },

  "L9": {
    "what_it_does": "Foundation-model labs train the large neural networks (GPT-5, Claude Opus 4.5, Gemini 3, Llama 4, Grok 4) that every app in Layer 10 builds on. The capital-intensive heart of the AI stack.",
    "analyst_take": "This is the layer everyone argues about, and my view is deliberately unsentimental. The labs are extraordinary businesses on revenue growth and genuinely awful on GAAP profitability — they burn billions training the next model while the last one decays toward worthless. What I actually track is not the leaderboard but two things: enterprise API share (where Anthropic has quietly taken the lead) and <i>who funds the compute</i>. Each lab has effectively sold a piece of itself to one or two hyperscalers in exchange for GPUs, which means you cannot analyse L9 without analysing the balance sheets of L8. There is no clean public pure-play, so I play it through the backers.",
    "stance": "No pure-play; express the view through proxies — MSFT (OpenAI), AMZN (Anthropic), GOOGL (owns the full stack). Watch enterprise API share and compute funding, not benchmark wins.",
    "capex_slice": "Not a slice of the $725B. L9 is the largest <i>customer</i> of the capex (labs are the biggest buyers of L8 compute); the ~$100B of LLM ARR[[cite:counterpoint]] is the revenue the buildout is chasing.",
    "charts": [
      {"title": "Global LLM revenue share — Q1 2026", "source": "counterpoint", "type": "donut", "unit": "%",
       "rows": [("Anthropic", 31.4, "$30B ARR; $350B val — overtook OpenAI Apr’26"),
                ("OpenAI", 29.0, "$25B ARR; $852B PBC val"),
                ("Google (Gemini)", 12.1, "Embedded across Workspace + Cloud"),
                ("Microsoft (Phi)", 7.2, "Separate from its OpenAI stake"),
                ("Tencent (Hunyuan)", 4.8, "#1 Chinese by revenue"),
                ("Baidu (Ernie)", 3.6, "Enterprise + search"),
                ("Alibaba (Qwen)", 2.9, "Strong open-weight; cloud bundle"),
                ("Meta (Llama)", 1.4, "Open-source; indirect/ad revenue"),
                ("xAI (Grok)", 1.4, "X-tied; ~$3B ARR"),
                ("Others", 6.0, "Perplexity + long tail")]},
      {"title": "Enterprise API spend share — vs end-2023", "source": "menlo", "type": "bar", "unit": "%",
       "rows": [("Anthropic", 40.0, "rising from 12% → +28 pts; now the enterprise leader"),
                ("OpenAI", 25.0, "down from 50% → −25 pts"),
                ("Google", 20.0, "+15 pts"),
                ("Meta (Llama)", 9.0, "open-source, ~stable"),
                ("DeepSeek + others", 14.0, "fragmented long tail")]},
    ],
    "who_pays_whom": "End-users pay labs directly (subscriptions, seats) or indirectly (apps pay per token via API). Labs are in turn the <b>largest customers of the cloud (L8)</b> — Anthropic ~$100B/10-yr AWS, OpenAI $250B Microsoft + ~$300B Oracle + $38B AWS — and that compute spend is funded substantially by hyperscaler equity.",
    "bottleneck": {"severity": "MEDIUM-HIGH", "points": [
      "Frontier training runs need tens of thousands of the latest GPUs in a single coherent cluster — gated by L4 chip supply and L0 power, not by talent or data alone.",
      "Capital is the second constraint: a frontier run + serving infrastructure costs billions, which is why labs trade equity for compute (OpenAI–NVIDIA, Anthropic–Amazon).",
      "Resolution path is the hyperscaler equity-for-compute deals — but that ties each lab's fate to one or two backers and creates the circular-financing risk.",
    ]},
    "market_size": [
      "~$100B in LLM ARR (Q1’26)[[cite:counterpoint]] — from under $1B in Jan 2023.",
      "Forecast $400B+ by 2030 if scaling continues to translate into capability and demand.[[cite:counterpoint]]",
      "Concentration is extreme: the top three (Anthropic, OpenAI, Google) take ~70%+ of revenue (see charts).",
    ],
    "value_added": [
      "HIGH for the top three, brutal for everyone else. Anthropic + OpenAI together capture ~60% of LLM revenue.",
      "Gross margins on inference are ~50–60% once a model is trained, but <b>GAAP margins are deeply negative</b> while training the next model and amortizing compute — the labs are burning billions.",
      "The model itself is depreciating inventory: each generation makes the last one nearly worthless, so labs must keep spending just to stay frontier. Pricing power is real but transient.",
    ],
    "how_to_analyze": "No pure-play public exposure. Four proxies: MSFT (27% of OpenAI), AMZN (largest Anthropic holder), GOOGL (Gemini, fully owned stack), META (Llama, monetized via ads). Track each lab's ARR, enterprise API share (Menlo/Ramp), gross margin trajectory, and — critically — who is funding its compute.",
    "sub_segments": [
      "Three lenses give three rankings: <b>consumer revenue</b> (OpenAI’s ChatGPT still leads on raw users), <b>total LLM revenue</b> (Anthropic edged ahead in Q1’26), and <b>enterprise API spend</b> (Anthropic clearly leads) — see the two charts above.",
      "The Chinese stack (Tencent, Baidu, Alibaba, DeepSeek) is a separate, largely walled market served by the domestic clouds.",
    ],
    "glossary": [
      ("Foundation model", "A large neural network trained on internet-scale data that many downstream apps build on top of."),
      ("Tokens", "The unit of text models read/write (~0.75 words each). APIs charge per million in/out tokens (Claude Opus ~$15/M in, ~$75/M out)."),
      ("PBC", "Public-Benefit Corporation — OpenAI's restructured for-profit entity (Oct'25) that crystallized Microsoft's ~27% stake."),
    ],
    "deals_detail": [
      "<b>The labs are mostly private, so the table shows public proxies.</b> Microsoft is the cleanest OpenAI proxy (27% economic stake worth ~$135B); Amazon is the cleanest Anthropic proxy (~$46B+ invested, largest holder); Alphabet is the only frontier lab that owns its entire stack — model (Gemini), accelerator (TPU) and cloud — which is why its cloud margins inflected so sharply. Meta is a different animal: it open-sources Llama and monetizes indirectly through ad-targeting uplift rather than API fees.",
    ],
  },

  "L8": {
    "what_it_does": "Cloud providers own data centers and chips and rent them by the hour or via long-term contract. Two sub-types: <b>hyperscalers</b> (general-purpose, full-stack, own custom silicon) and <b>neoclouds</b> (GPU-as-a-service pure-plays, faster to spin up GPU capacity).",
    "analyst_take": "L8 is the toll booth on the whole chain, and I think it is the highest-quality way for most investors to own the buildout. The hyperscalers convert the labs’ compute spend into 35–50% operating margins, and the leading indicator I trust most is RPO/backlog — over $1.8T contracted across the big four[[cite:filings]] tells me the demand is signed, not hoped for. The neoclouds are a different animal entirely: I view them as securitized compute contracts wearing equity clothing. Their gross margins look fine (~70%) but depreciation and interest push operating margins negative, so they live or die on a handful of mega-contracts and the debt raised against them. High beta, high binary risk.",
    "stance": "Core long: the hyperscalers (MSFT, AMZN, GOOGL, ORCL) for quality + backlog. Neoclouds/ex-miners only for high-beta exposure, sized for binary contract risk.",
    "capex_slice": "L8 <i>is</i> the $725B — this layer does the spending, it does not receive a slice. The capex is L8 converting its balance sheet into the L0–L7 stack below.",
    "charts": [
      {"title": "Cloud infrastructure market share — 2026E", "source": "synergy", "type": "donut", "unit": "%",
       "rows": [("AWS (Amazon)", 30.0, "$128.7B FY25, +19%"),
                ("Microsoft Azure", 23.0, "+40% growth; $ not disclosed"),
                ("Google Cloud", 13.5, "~$59B FY25, +~50%"),
                ("Alibaba Cloud", 4.0, "largest non-Western"),
                ("Oracle (OCI)", 3.0, "fastest-growing; $553B RPO"),
                ("Others + neoclouds", 26.5, "CoreWeave, Nebius, IBM, Tencent, etc.")]},
    ],
    "who_pays_whom": "Model labs (L9) are the largest customers; enterprises buy AI services on top. Clouds in turn pay L7 (real estate), L6 (networking), L5 (servers), L4 (chips) and L0 (power). Neoclouds raise debt against their hyperscaler/lab contracts to buy GPUs from NVIDIA.",
    "bottleneck": {"severity": "MEDIUM", "points": [
      "Capacity is sold out across AWS/Azure/GCP for 2026 — the constraint is upstream (L4 GPUs, L7 buildings, L0 power), not demand.",
      "The $725B capex IS the resolution; neoclouds and ex-miners add capacity faster than hyperscalers can build, which is why they exist.",
      "For neoclouds specifically, the binding constraint is <b>capital and customer concentration</b>: they live or die on a handful of mega-contracts and the debt raised against them.",
    ]},
    "market_size": [
      "Total cloud infrastructure ~$520B in 2026E.[[cite:synergy]] AWS FY25 $128.7B (+19%); Azure +40%; Google Cloud ~$59B FY25 (+~50%); Oracle cloud ~$35B run-rate.[[cite:filings]]",
      "Backlog is the leading indicator and it is enormous: Microsoft RPO $627B, Oracle $553B, Google $462B, Amazon ~$200B — over $1.8T of contracted cloud combined.[[cite:filings]]",
      "Neocloud contracted HPC revenue exceeds $100B+ (CoreWeave $66.8B RPO alone).[[cite:filings]]",
    ],
    "value_added": [
      "HIGH for hyperscalers, THIN and volatile for neoclouds. AWS runs ~35% operating margin; Azure ~50% on the AI run-rate; Google Cloud inflected to ~33%.",
      "Neoclouds run 5–15% operating margins at best — many are GAAP-unprofitable today (CoreWeave op margin ~-7%) because GPU depreciation and interest swamp early revenue, even at ~70% gross margins.",
      "The ex-miners (IREN, TeraWulf, Hut 8, Cipher) are the highest-beta exposure: they own power and shells, sign 10–15-yr hyperscaler leases, and finance the GPUs with debt — huge upside if contracts perform, severe risk if a counterparty wobbles.",
    ],
    "how_to_analyze": "Hyperscalers: cloud revenue growth YoY, RPO/backlog (the leading indicator), AI revenue run-rate, and capex-to-OCF (the funding stress test). Neoclouds: contracted RPO vs market cap, customer concentration, contract duration, cost of debt, and the gap between gross margin (good) and operating margin (often negative).",
    "sub_segments": [
      "Hyperscalers — AWS (30% share), Azure (21–25%), Google Cloud (13–14%), Oracle (~3%, fastest-growing), Alibaba (~4%, largest non-Western).",
      "Neoclouds (pure) — CoreWeave, Nebius, Lambda.",
      "Ex-bitcoin miners (pivoted) — IREN, TeraWulf, Hut 8, Cipher Mining.",
    ],
    "glossary": [
      ("Hyperscaler", "Global-scale cloud (AWS, Azure, Google Cloud, Oracle, Alibaba) that owns its DCs, designs custom chips, and sells a broad stack."),
      ("Neocloud (GPUaaS)", "GPU-as-a-Service pure-play renting AI compute by the hour. Lower margin, less stack, faster to deploy GPUs."),
      ("RPO / Backlog", "Remaining Performance Obligation — total contracted future revenue not yet recognized. The cleanest leading indicator for cloud demand."),
      ("GW / MW", "1 GW = 1,000 MW. A typical AI DC draws 100–500 MW; 1 GW of AI DC costs ~$50–60B to build (~$35B of it chips)."),
    ],
    "deals_detail": [
      "<b>Hyperscalers — how the AI/cloud revenue compares to the whole company.</b> The point of showing both segment and total revenue is to see how much of each franchise is actually cloud: AWS is only ~18% of Amazon's $716.9B revenue but ~57% of its operating income; Google Cloud is ~15% of Alphabet; Microsoft Cloud is roughly half of Microsoft. Note that Microsoft does <i>not</i> disclose Azure revenue in dollars — only its growth rate (+40%) — so Azure dollar figures industry-wide are estimates (~$30B+/quarter). Oracle is the outlier: cloud is now the majority of the company, and its $553B RPO (up 325% YoY) is ~8x current revenue, almost entirely large-scale AI contracts (mainly OpenAI Stargate).",
      "<b>Neoclouds & ex-miners — the contracts, with durations.</b> These businesses are essentially securitized compute contracts, so the term length is the whole story. CoreWeave's $22.4B OpenAI commitment runs through <b>May 2031</b> (built up in three tranches: $11.9B in Mar'25 on an initial 5-year deal, +$4B in May'25, +$6.5B in Sep'25), and its total RPO is $66.8B. Nebius's Microsoft deal is ~$17.4B <b>through 2031</b> (expandable to ~$19.4B) plus a ~$3B / <b>5-year</b> Meta deal. Among the ex-miners: IREN–Microsoft is $9.7B over <b>5 years</b> (20% prepaid); Cipher–AWS is $5.5B over <b>15 years</b>; Hut 8 has two <b>15-year</b> Fluidstack/Google-backed leases ($7.0B + $9.8B, with 3% annual escalators); TeraWulf's Fluidstack deals run <b>10 years</b> (plus extensions, ~$12.8B total, Google-backstopped) and its HPC revenue overtook bitcoin for the first time in Q1'26. The common thread: 10–15-year terms backstopped by a hyperscaler, against which the miner raises debt to buy GPUs.",
    ],
  },

  "L7": {
    "what_it_does": "The physical buildings and the contractors who build them. Hyperscalers either own DCs (Microsoft, Google, Meta build a lot) or lease from REITs; specialty contractors handle the power/cooling/electrical build-out.",
    "analyst_take": "I find L7 underappreciated because the bottleneck has quietly moved here. You can have all the GPUs in the world and still not deploy them if there is no powered shell to put them in — Northern Virginia vacancy is under 5% and interconnect queues run 7–10 years. The REITs (Equinix, Digital Realty) are the purer exposure with interconnection moats, but they carry REIT multiples that make the headline P/E look scary. The contractors (Quanta, Comfort Systems) are my preferred angle: they trade on ordinary earnings multiples, are not seen as ‘AI stocks’, yet their backlogs are increasingly data-center-driven with high incremental margins.",
    "stance": "Prefer the contractors (PWR, FIX) for lower-multiple, high-incremental-margin exposure; own the REITs (EQIX) for the interconnection moat, judged on AFFO not P/E.",
    "capex_slice": "~$70–85B of the $725B (10–12%, the ‘shell, land &amp; fiber’ bucket), against a researched global DC-infrastructure TAM of ~$200B+[[cite:idc]] — the gap is the non-hyperscaler and maintenance spend.",
    "who_pays_whom": "Hyperscalers + enterprises pay DC REITs monthly rent for space + power. Hyperscalers + REITs pay construction/electrical contractors (Quanta, Comfort Systems, EMCOR) to build. REITs pay L0 for power and L6 for fiber.",
    "bottleneck": {"severity": "HIGH", "points": [
      "Northern Virginia vacancy is <5% and grid-interconnect queues run 7–10 years — you cannot build a DC where there is no power, regardless of capital.",
      "Resolution is geographic: build in Texas, Wisconsin, Ohio, New Mexico where power is available; Stargate is explicitly a land-and-power solution. Permitting reform is helping at the margin.",
      "Skilled-labor and long-lead-equipment shortages (electricians, transformers, switchgear) cap how fast contractors can deliver even when sites are secured.",
    ]},
    "market_size": [
      "Global DC infrastructure ~$200B+ in 2026E; US colocation market ~$72B.[[cite:idc]]",
      "McKinsey models a $5.2T global DC build by 2030, with ~$1.3T (25%) flowing to ‘energizers’ (utility + electrical).[[cite:mckinsey]]",
      "REIT capacity is pre-leased years out — Digital Realty had 769 MW under construction at end-2025.[[cite:filings]]",
    ],
    "value_added": [
      "MEDIUM-HIGH for REITs, LOWER but steady for builders. Equinix runs ~49% gross / ~51% adjusted-EBITDA margins; Digital Realty ~48% gross.",
      "REIT economics are high-recurring but capital-intensive; the durable moat for Equinix is interconnection density (network effects), not just real estate.",
      "Contractors (Quanta ~16% gross / 8% operating; Comfort Systems ~22% gross) earn modest margins but have record multi-year backlogs and very high incremental returns on capital.",
    ],
    "how_to_analyze": "REITs: leased backlog, MW under construction, vacancy (NoVa <5% = pricing power), and AFFO growth. Contractors: backlog, book-to-bill, and the data-center/advanced-tech mix within that backlog (rising fast for both PWR and FIX).",
    "sub_segments": [
      "Colocation REITs (EQIX retail, DLR wholesale) — own and lease buildings.",
      "Wholesale developers (QTS/Blackstone, Vantage/DigitalBridge — private) — single-tenant powered shells.",
      "Electrical & mechanical contractors (PWR, FIX, EME) — the physical build-out.",
    ],
    "glossary": [
      ("Retail colo", "Many customers lease individual cabinets/cages; Equinix is #1. Value is interconnection — connecting to many clouds in one place."),
      ("Wholesale colo", "One large customer leases an entire building / powered shell; Digital Realty is #1."),
      ("DC REIT", "Real-Estate Investment Trust that owns DC buildings, leases them, and distributes income as dividends."),
      ("Powered shell", "A building delivered with power and cooling infrastructure but fitted out by the tenant."),
    ],
    "deals_detail": [
      "<b>Why the contractors look 'cheap' next to the REITs.</b> Quanta and Comfort Systems trade on normal-looking earnings multiples and are not pure AI plays — data centers are a (fast-growing) slice of diversified electrical/mechanical contracting books. But their record backlogs are increasingly DC- and fab-driven, and incremental margins are high, so they offer a lower-multiple, lower-glamour way to own the build-out. The REITs (Equinix, Digital Realty) are the purer DC exposure and carry REIT-style multiples (P/AFFO, not P/E), which is why their headline P/E looks elevated.",
    ],
  },

  "L6": {
    "what_it_does": "Connects thousands of GPUs so they behave as one machine. AI training is bandwidth-bound — networking is ~10–15% of cluster cost but mission-critical. Four sub-segments: Ethernet switching, optical transceivers, optical fiber, and AI-RAN (AI compute inside telecom networks).",
    "analyst_take": "Optics is the sub-segment I’d single out from this entire report as both the best and the most dangerous trade. The physics is simple and powerful: every GPU-generation upgrade (Blackwell→Rubin) roughly doubles the optical interconnect required, so demand for EML lasers and transceivers compounds faster than the chain can add InP fab capacity — sold out through 2027. That is why Lumentum is up four-figure percentages. But the multiples now price the boom running uninterrupted, and NVIDIA’s $2B equity stakes in both Lumentum and Coherent tell you supply, not just demand, is being engineered. Switching is the calmer, higher-quality place to sit (Arista at 40%+ margins).",
    "stance": "Own switching quality (ANET) as the core; trade optics (LITE, COHR) for the supply-squeeze beta but respect the ~50× multiples and cycle risk. Fiber (GLW) is the lower-beta tag-along.",
    "capex_slice": "~$45–60B of the $725B (6–8%, the networking bucket), versus a researched ~$60B 2026E networking TAM[[cite:delloro]] — close, because networking is almost entirely an AI-buildout spend today.",
    "charts": [
      {"title": "DC Ethernet switching share", "source": "delloro", "type": "donut", "unit": "%",
       "rows": [("Arista", 19.0, "hyperscaler design wins"), ("NVIDIA (Ethernet)", 15.2, "Spectrum-X"),
                ("Cisco", 14.0, "diversified incumbent"), ("Others", 51.8, "white-box + Juniper/HPE etc.")]},
    ],
    "who_pays_whom": "Hyperscalers and neoclouds (L8) are the primary buyers — every new GPU cluster needs switches, transceivers and fiber. Switch and optics vendors buy ASICs from Broadcom/Marvell (L4) and lasers/InP from the optics makers.",
    "bottleneck": {"severity": "VERY HIGH (optics) / MEDIUM (switching)", "points": [
      "EML lasers and InP transceivers are sold out through 2027 — each GPU-generation upgrade (Blackwell→Rubin) roughly doubles the optical interconnect needed, so demand compounds faster than capacity.",
      "Switching is less constrained (multi-vendor), but the underlying Tomahawk/Jericho ASIC silicon from Broadcom is allocated.",
      "Resolution: capacity is being added through 2027 under long-term agreements (and funded partly by NVIDIA's equity investments in Lumentum and Coherent), but it ramps slowly because InP fab capacity has long lead times.",
    ]},
    "market_size": [
      "~$60B in 2026E overall.[[cite:delloro]] DC Ethernet switching ~$60–65B; optical transceivers ~$22B growing 25%+; silicon photonics $2.6B→$22B by 2034 (~26% CAGR).[[cite:yole]]",
      "Optical components have been the highest-returning sub-segment of the entire chain in 2025–26 (Lumentum +1,474% LTM).[[cite:bloomberg]]",
      "AI-RAN is a longer-dated option: cumulative TAM >$200B by 2030.[[cite:omdia]]",
    ],
    "value_added": [
      "VERY HIGH for optics specialists and switching leaders. Arista ~43% operating margin; Broadcom networking ~50%; Lumentum ~22% and rising on AI mix.",
      "The optics names carry the highest cycle risk: extraordinary returns but extreme multiples (Lumentum ~50x forward earnings), all premised on the LTA-backed boom running uninterrupted.",
      "Fiber (Corning) is lower-margin at the group level (~diversified) but the Optical Communications segment is re-rating as the AI mix climbs.",
    ],
    "how_to_analyze": "Different metric per sub-segment. Switching (ANET, CSCO): hyperscaler design wins + DC switch share. Optics (LITE, COHR, AAOI): capacity utilization, LTA coverage, and EML/InP supply. Fiber (GLW): optical-segment growth + hyperscaler fiber deals. AI-RAN (NOK): quarterly Cloud & AI revenue + carrier pilots. For all: watch the next GPU-generation interconnect spec — it sets the demand step-up.",
    "sub_segments": [
      "DC Ethernet switching — ANET (19% DC), NVIDIA networking (15.2% DC Ethernet), Cisco (14%), Broadcom (switch silicon).",
      "Optical components/transceivers — Lumentum (50–60% EML), Coherent (InP sold out '27), AAOI (800G), Marvell (DSPs).",
      "Silicon photonics — Intel (21.5%, #1), Cisco/Acacia, Broadcom, Lumentum, NVIDIA (CPO).",
      "Optical fiber — Corning (#1 global; Meta $6B deal).",
      "AI-RAN — Nokia (NVIDIA tie), Ericsson (no NVIDIA tie), Huawei (excluded from West), Samsung.",
    ],
    "glossary": [
      ("Ethernet switch", "Routes traffic between servers. Arista + Cisco lead; inside training clusters, NVIDIA InfiniBand competes with Ethernet."),
      ("Optical transceiver", "Module converting electrical signals to light for fiber. AI clusters moved 800G→1.6T. Coherent + Lumentum lead."),
      ("EML (Externally Modulated Laser)", "Laser inside high-speed transceivers; enables 200G/lane → 1.6T modules. Lumentum 50–60% share."),
      ("OCS (Optical Circuit Switch)", "Routes light without converting to electrons — big power saving. Google deployed at scale in TPU pods; Lumentum leads."),
      ("SiPho / CPO", "Silicon photonics integrates optics onto silicon; co-packaged optics puts them in the switch/GPU package, cutting power ~40%."),
      ("AI-RAN", "AI-empowered Radio Access Network — AI inference compute inside telecom base stations (NVIDIA + Nokia, Oct'25)."),
    ],
    "deals_detail": [
      "<b>The NVIDIA–Lumentum / Coherent investments ($2B each, March 2026) — what they actually are.</b> These are not simple supply contracts. NVIDIA is making an <b>equity investment of $2B in each company</b> (≈$4B total) to fund their build-out of US-based optics manufacturing (new fabs), <i>and</i> the deals carry a multibillion-dollar NVIDIA purchase commitment plus future capacity-access rights — all on a non-exclusive basis. In other words, NVIDIA is using its balance sheet to lock up future optics supply and accelerate domestic capacity, the same playbook as its Nokia ($1B/2.9%), CoreWeave ($2B) and memory-adjacent stakes. For Lumentum and Coherent, it is validation, capital, and a guaranteed anchor customer at once — which is why both stocks re-rated sharply.",
      "<b>Reading the optics financials.</b> Lumentum's and Coherent's <i>fiscal-year</i> figures (FY ends June) predate the optics inflection and understate the run-rate — Lumentum's FY25 revenue of $1.6B sits against TTM revenue growth of +90% and a recovered ~41% gross margin. Use TTM, not the stale FY, for these names. The segment context also matters: Coherent and Corning are diversified (industrial lasers; display/auto glass), so the AI lever is the datacom/optical-communications segment, not the whole company; Arista, Astera and Credo are the cleaner pure-plays.",
      "<b>How much of each company is actually this layer.</b> Broadcom's networking sits inside its $20B FY25 AI-semiconductor revenue (≈31% of its $64B total); Cisco's DC switching is a small slice of a ~$56B diversified company; Corning's Optical Communications is ~$5B+ of ~$14–15B; NVIDIA's networking is inside its $193.7B Data Center line (but grew +142%). The pure-plays — Arista, AAOI, Astera, Credo — are where a dollar of revenue is almost entirely this layer.",
    ],
  },

  "L5": {
    "what_it_does": "Server makers physically assemble GPUs, CPUs, memory, networking and power supplies into rack systems. Distinct from chip makers (L4) — servers integrate the chips someone else designed.",
    "analyst_take": "L5 is the value trap of the supply chain, and I want to be blunt about it. Revenue here looks spectacular — Foxconn’s AI-server line is exploding — but at 5–7% gross margins almost none of it reaches the bottom line. The chip (40–45% of the bill of materials) dominates the economics, ODMs undercut the branded OEMs from below, and hyperscalers dual-source to keep everyone honest. So I own this layer for revenue <i>beta</i>, never for margin. The one place I’d look for quality is the power-supply specialists (Delta): high-density racks need their efficient PSUs, and that earns better margins than box assembly.",
    "stance": "Trade for GPU-cycle revenue beta (Foxconn, SMCI), not for profit. The quieter quality pick is Delta (PSUs). Watch gross-margin trajectory, not revenue growth.",
    "capex_slice": "~$60–70B of the $725B (8–10%, the ‘servers, CPUs, NICs, PSUs’ bucket), against a $444B total server market in 2025[[cite:idc]] — most of that TAM is non-AI servers; the AI slice is what the capex funds.",
    "who_pays_whom": "Hyperscalers (L8) increasingly buy direct from ODMs (Foxconn et al.) and bypass branded OEMs. ODMs buy GPUs from L4, HBM from L3, switches from L6, PSUs from Delta, and assemble. Branded OEMs (Dell, Supermicro) serve enterprises and non-hyperscaler clouds.",
    "bottleneck": {"severity": "MEDIUM", "points": [
      "Server assembly is <b>not</b> the structural bottleneck — it is gated by what flows into it (L4 GPUs, L3 HBM, L2 CoWoS). Once those clear, racks can be built.",
      "Foxconn is already assembling GB200/GB300 at scale; multiple ODMs are qualified, so there is no single-vendor choke point here.",
      "The real risk in this layer is commercial, not physical: margin compression as volume scales and hyperscalers dual-source.",
    ]},
    "market_size": [
      "$444B server market in 2025 (+80% YoY); GPU-embedded servers are >50% of revenue.[[cite:idc]]",
      "ODM Direct (hyperscaler-direct) is 59.4% of the market and rising as hyperscalers cut out branded OEMs.[[cite:idc]]",
      "2026E ~$650–700B as Rubin-class racks (higher ASP per rack) ship.[[cite:idc]]",
    ],
    "value_added": [
      "VERY LOW — the structurally worst layer for pricing power. Foxconn earns 5–7% gross margin on AI servers; pricing power ~2/10.",
      "Branded OEMs are squeezed from both sides: ODMs undercut them below, and GPU costs (40–45% of the BOM) dominate above. Dell's group GM is ~22% but its AI-server margin is materially lower; Supermicro runs ~9.7% gross and falling; HPE's server GM dropped to ~6%.",
      "It is a volume/working-capital game: revenue scales spectacularly with the GPU cycle, but very little of it drops to the bottom line. Own this layer for revenue beta, not for margins.",
    ],
    "how_to_analyze": "The key variable is gross-margin trajectory, not revenue growth — revenue will look explosive regardless. Watch ODM share gains vs OEMs, working-capital intensity (huge GPU inventory), and customer concentration. Delta (PSUs) is the higher-quality way to play the layer because high-density racks need its efficient power supplies.",
    "sub_segments": [
      "ODMs (Foxconn, Quanta, Wistron, Inventec) — 59.4% of the market; low margin, high volume.",
      "Branded OEMs (Dell, Supermicro, HPE, Lenovo) — enterprise + non-hyperscaler cloud + government.",
      "Power-supply specialists (Delta) — PSUs inside racks; critical for 100+ kW AI racks.",
    ],
    "glossary": [
      ("ODM", "Original Design Manufacturer — designs AND builds hardware on contract (Foxconn, Quanta). Hyperscalers buy direct; ODMs = 59.4% of the server market."),
      ("OEM", "Original Equipment Manufacturer — branded makers (Dell, HPE, Supermicro) selling to enterprises, often built by ODMs underneath."),
      ("PSU", "Power Supply Unit — converts wall AC to the DC voltages servers need. Delta is #1 for AI-server PSUs."),
    ],
    "deals_detail": [
      "<b>Foxconn's revenue dwarfs everyone — but read it carefully.</b> Foxconn (Hon Hai) is a ~$220B-revenue company, far larger than Dell or Supermicro, and its cloud/networking + AI-server business is a fast-growing ~40% of that. But at ~6% gross margin, scale doesn't translate into the profit pool you'd expect — which is exactly the layer's lesson. Dell's AI server backlog is ~$14B and its AI-server run-rate is $25B+, but that sits inside a $113.5B company at group margins that mask the thin AI-server economics. Supermicro is the closest pure-play and the highest revenue beta, but also the thinnest margins and a governance overhang. Delta Electronics is the quieter, higher-quality name: PSUs and power management carry better margins than box assembly.",
    ],
  },

  "L4": {
    "what_it_does": "The chips that actually do AI math. Every other layer ultimately exists to feed these with power, cooling, memory and data. Three types do the work — GPUs (programmable, general), ASICs (hard-wired, hyperscaler-custom), and a niche of wafer-scale — plus the CPUs that host them and the power ICs that feed them.",
    "analyst_take": "If I could own one layer outright, it would be this one — and the whole report is really a study of the businesses that orbit it. NVIDIA captures roughly a third of all AI capex as <i>profit</i>: ~73% gross margin, ~$120B of net income, the single largest profit pool in technology. That is the position. The risk I weigh against it is equally specific: ASIC substitution. Every Google TPU, AWS Trainium and Meta MTIA gigawatt is demand NVIDIA does not sell at merchant margins, and Broadcom’s custom-silicon revenue alone hit $20B. My base case is that total demand keeps outrunning combined GPU+ASIC supply, so merchant GPU demand still rises even as ASICs grow — but the day that stops being true is the day this trade changes.",
    "stance": "NVIDIA is the master long of the cycle. Pair it with the ASIC arms-dealers (AVGO, MRVL) as the structural hedge — they win whether the share shift accelerates or not.",
    "capex_slice": "The big one: ~$290–325B of the $725B (40–45%, the largest single bucket), against a ~$300B 2026E accelerator TAM[[cite:idc]] — they essentially match, because the accelerator <i>is</i> the AI capex.",
    "charts": [
      {"title": "Merchant AI GPU share", "source": "filings", "type": "donut", "unit": "%",
       "rows": [("NVIDIA", 88.0, "86–90%; ~73% gross margin"), ("AMD", 6.0, "Instinct MI300/MI450"),
                ("Others", 6.0, "Intel Gaudi, startups")]},
    ],
    "who_pays_whom": "Hyperscalers (L8), neoclouds and L5 ODMs buy GPUs and ASICs from this layer. NVIDIA/AMD pay TSMC (L2) for manufacturing + CoWoS packaging and SK Hynix/Micron (L3) for HBM. Hyperscalers co-design ASICs with Broadcom/Marvell.",
    "bottleneck": {"severity": "EXTREME (the bottleneck)", "points": [
      "NVIDIA Blackwell has been sold out 12+ months ahead and Rubin is already booked — this is the binding constraint of the whole cycle.",
      "Crucially, the limit is <b>not chip design</b> — it is the supply of L3 HBM and L2 CoWoS advanced packaging. As those scale through 2026–27, the bottleneck eases.",
      "ASIC substitution is the structural relief valve: every TPU/Trainium/MTIA GW deployed is demand NVIDIA doesn't have to supply — but total demand is still outrunning combined GPU + ASIC capacity.",
    ]},
    "market_size": [
      "~$300B in 2026E;[[cite:idc]] BofA models a $1.2T accelerator TAM by 2030.[[cite:bofa]]",
      "NVIDIA FY26 Data Center revenue $193.7B (89.7% of its total); Broadcom AI semiconductors $20B FY25 (+65%); AMD data center $16.6B (+32%).[[cite:filings]]",
      "Custom ASICs are the fastest-growing share — Broadcom alone signals multiple 10-GW custom programs through 2030.[[cite:filings]]",
    ],
    "value_added": [
      "EXTREME — the highest in the chain. NVIDIA: ~73% gross margin, ~60–65% operating margin, ~$120B net income (FY26).",
      "NVIDIA single-handedly captures on the order of a third of all AI capex as profit — the single largest profit pool in AI, and the reason the whole supply chain orbits it.",
      "AMD earns lower margins and is CoWoS-gated; Broadcom's custom-AI runs ~50% operating margin; Cerebras is not yet profitable. The accelerator is where pricing power (10/10 for NVIDIA) and the bottleneck coincide.",
    ],
    "how_to_analyze": "NVIDIA is the master variable. Bull case: continued GPU dominance (Rubin late-2026, post-Rubin through 2028, $200B+/yr DC revenue). Bear case: ASIC substitution accelerates and/or a demand air-pocket hits the most over-earning name in tech. Track DC revenue + guidance, gross-margin trajectory, CoWoS/HBM supply, and ASIC ramp (Broadcom/Marvell backlog) as the share-shift tell.",
    "sub_segments": [
      "Merchant GPUs — NVIDIA 86–90%; AMD 5–7%.",
      "Custom ASICs — Broadcom (Google TPU, Meta MTIA, OpenAI), Marvell (AWS Trainium, Microsoft Maia).",
      "Wafer-scale — Cerebras (niche inference).",
      "Power ICs — Monolithic Power (GPU voltage regulation); CPUs (Grace, EPYC, Xeon) host the accelerators.",
    ],
    "glossary": [
      ("GPU", "Graphics Processing Unit — thousands of cores for parallel math; programmable, runs any model. NVIDIA, AMD."),
      ("ASIC", "Application-Specific IC — hard-wired for one workload; 30–50% cheaper per workload but inflexible. Google TPU, AWS Trainium, Meta MTIA, Microsoft Maia."),
      ("CPU", "Central Processing Unit — few powerful cores for serial/control logic; hosts and orchestrates the GPUs. Xeon, EPYC, Grace, Graviton."),
      ("Blackwell / Rubin", "NVIDIA GPU generations. Blackwell (B200/GB200) shipped 2025; Rubin late-2026, the basis of OpenAI's 10-GW deal. Each ~doubles performance."),
      ("Wafer-scale", "Using an entire silicon wafer as one chip — only Cerebras. WSE-3 has 4T transistors / 900k cores; inference-focused."),
    ],
    "deals_detail": [
      "<b>How much of each company is this layer.</b> NVIDIA is ~90% Data Center — effectively a pure AI-accelerator play at $5T+ market cap. AMD's data center segment is $16.6B, only ~48% of the company (the rest is client/gaming/embedded), and Instinct GPUs aren't broken out separately from EPYC CPUs. Broadcom's AI silicon ($20B) is ~31% of a $64B company that is also VMware software and broad-line networking. Marvell's data center is ~75% of an $8.2B company. Monolithic Power and Cerebras round out the layer — MPWR as the GPU power-delivery pick-and-shovel, Cerebras as the speculative wafer-scale pure-play (P/E ~580x, not yet group-profitable).",
      "<b>The AMD–OpenAI warrant is the structure to understand.</b> OpenAI's 6-GW MI450 commitment comes with a warrant for up to 160M AMD shares (~10% of the company) at $0.01, vesting in tranches tied to deployment milestones and AMD's share price (up to $600). It is simultaneously a customer contract and a massive equity alignment — and a template for how compute demand is being financed with equity rather than cash across this cycle.",
    ],
  },

  "L3": {
    "what_it_does": "Memory and storage hold the data AI chips work on. The closer to the GPU, the faster and more expensive: HBM sits on the GPU package; DRAM is system memory; NAND/HDD are bulk storage for the ‘data lakes’ that feed inference.",
    "analyst_take": "Memory is the most interesting valuation puzzle in the chain. The fundamentals are monopoly-like right now — SK Hynix posted 80%+ operating margins at the cycle peak and is sold out of HBM into 2027 — yet the market hands these names mid-single-digit forward P/Es. That tension <i>is</i> the thesis: the market is correctly pricing in mean reversion, because memory has always been cyclical and today’s shortage becomes tomorrow’s glut. My read is that this cycle has an unusually long runway (HBM is structurally tied to every GPU, and HBM4 is the next leg), so the down-cycle is further out than the multiples imply — but I never forget which way this industry eventually breaks.",
    "stance": "Own SK Hynix as the cleanest HBM/NVIDIA derivative and Micron as the US pure-play; size for cyclicality. The low multiples are the market pricing the eventual glut, not a free lunch.",
    "capex_slice": "~$70–85B of the $725B (10–12%, HBM + system memory), against a ~$300B+ total memory TAM[[cite:trendforce]] — AI memory is the fast-growing slice of a much larger commodity market.",
    "charts": [
      {"title": "HBM market share — Q3 2025", "source": "trendforce", "type": "donut", "unit": "%",
       "rows": [("SK Hynix", 57.0, "HBM3E leader; ~70% of NVIDIA Rubin HBM4"),
                ("Samsung", 22.0, "HBM4 qualification in progress"),
                ("Micron", 21.0, "only US-listed pure memory maker")]},
    ],
    "who_pays_whom": "Chip makers (L4) buy HBM to package next to GPUs; server makers (L5) buy DRAM and storage. Memory makers buy capital equipment from L1 (Lam etch, ASML, Hanmi/BESI bonders).",
    "bottleneck": {"severity": "EXTREME (tied with L4)", "points": [
      "SK Hynix DRAM, NAND and HBM are all sold out through 2026 — memory is co-binding with accelerators because every GPU needs HBM and the HBM supply is concentrated in three players.",
      "Resolution comes from all three makers' capex and the HBM4 ramp (2026–27); Samsung/Micron HBM4 qualifications would add second sources and ease the choke.",
      "But memory is cyclical: today's shortage is tomorrow's glut. The tightness is real through 2027 per SK Hynix, but the layer has always mean-reverted.",
    ]},
    "market_size": [
      "Memory total ~$300B+ in 2026E. HBM: $35B (2025) → $58B (2026) → $100B (2028).[[cite:trendforce]]",
      "Data centers consume >50% of industry DRAM + NAND for the first time. NAND contract prices rose +246% in 2025.[[cite:trendforce]]",
      "SK Hynix FY25 revenue hit ₩97.1T (~$64.5B, +~50%) with HBM revenue more than doubling.[[cite:filings]]",
    ],
    "value_added": [
      "HIGH and rising — but priced for a peak. SK Hynix posted ~80%+ operating margins at the cycle peak; Micron's HBM mix pushed group gross margin sharply higher.",
      "The market is paying low forward multiples (SK Hynix ~5x, Micron ~8x forward P/E) precisely because these are peak-cycle earnings the market expects to normalize.",
      "NAND/HDD margins (Sandisk hit ~56% TTM gross on a +246% price move) are almost certainly an unsustainable peak — long-cyclicals briefly priced like monopolies.",
    ],
    "how_to_analyze": "HBM: SK Hynix is the purest play and clearest NVIDIA derivative — track HBM3E shipments, HBM4 qualification (sole vs dual-source), and contract pricing. DRAM/NAND: watch the bit-supply/demand balance and contract-price direction — that, not revenue, is what turns the cycle. For SNDK/WDC/STX, use TTM not stale FY figures (Sandisk's FY straddles the WDC spin-off).",
    "sub_segments": [
      "HBM (Q3'25) — SK Hynix 57%, Samsung 22%, Micron 21%. Sold out into 2027.",
      "DRAM — SK Hynix 34% (#1), Samsung 33%, Micron 26%.",
      "NAND + storage — Sandisk (#1 pure-play NAND), Western Digital + Seagate (HDD oligopoly).",
    ],
    "glossary": [
      ("HBM", "High Bandwidth Memory — stacked DRAM placed right next to the GPU on-package; every AI accelerator needs it. SK Hynix 57%."),
      ("DRAM", "Standard system memory; only three makers globally (SK Hynix, Samsung, Micron). HBM is a specialized form of DRAM."),
      ("NAND", "Flash inside SSDs; persistent storage. Sandisk is the largest pure-play."),
      ("HDD", "Spinning-disk storage; a 3-player oligopoly (Seagate, WD, Toshiba). Cheap mass storage for AI data lakes."),
      ("HBF", "High Bandwidth Flash — Sandisk's new NAND-organized-like-HBM architecture for inference; still emerging."),
    ],
    "deals_detail": [
      "<b>Pure-play vs conglomerate matters enormously here.</b> SK Hynix is the cleanest HBM exposure — memory is essentially the whole company, HBM revenue more than doubled in 2025, and it supplies ~70% of HBM4 for NVIDIA's Rubin. Micron is the only US-listed pure memory maker. Samsung, by contrast, buries its memory upside inside a conglomerate (handsets, displays, foundry), so the HBM boom is diluted. On storage, the SanDisk spin-off from Western Digital (Feb'25) is why SanDisk's FY25 shows a net loss — the fiscal year straddles the separation; the TTM figures (+251% revenue) reflect the real NAND up-cycle. The whole layer is the textbook cyclical-priced-like-monopoly debate: spectacular current margins, low forward multiples.",
    ],
  },

  "L2": {
    "what_it_does": "Foundries physically manufacture the chips that fabless companies (NVIDIA, AMD, Broadcom) design. TSMC manufactures essentially all leading-edge AI silicon and holds the CoWoS advanced-packaging monopoly. OSATs (ASE, Amkor) handle overflow and non-AI packaging.",
    "analyst_take": "TSMC is, in my judgement, the single highest-quality business in the entire chain — higher quality than NVIDIA, even if it earns a lower margin. Here is why: NVIDIA must out-innovate AMD and the hyperscalers’ ASICs every generation, whereas TSMC simply has to keep being the only place on earth that can manufacture leading-edge silicon and CoWoS-package it. There is no substitute — Samsung and Intel cannot absorb meaningful AI volume — so TSMC rations capacity and NVIDIA, AMD and Broadcom all queue. The bear case is not competition; it is a single word, Taiwan. That geopolitical tail risk is the only reason this isn’t a 10/10 position, and it sits under the whole stack.",
    "stance": "The highest-quality pick-and-shovel long in AI (TSM), priced reasonably on ~20× earnings. The risk to underwrite is geopolitical concentration, not competitive displacement.",
    "capex_slice": "No direct line in the $725B — TSMC is paid out of the accelerator bucket (it is the manufacturing cost inside each GPU/ASIC). Its own revenue ($121.2B FY25 → ~$160B 2026E)[[cite:filings]] is the better gauge.",
    "charts": [
      {"title": "Pure-play foundry market share — 2025", "source": "trendforce", "type": "donut", "unit": "%",
       "rows": [("TSMC", 69.9, "sole leading-edge + CoWoS"), ("Samsung", 7.2, "trailing at leading edge"),
                ("SMIC", 5.3, "China; mature nodes"), ("Others", 17.6, "UMC, GlobalFoundries, etc.")]},
    ],
    "who_pays_whom": "Chip designers (L4) pay foundries to manufacture; foundries pay equipment makers (L1: ASML for EUV, AMAT/Lam for deposition/etch) and materials suppliers (Hoya mask blanks, Shin-Etsu wafers).",
    "bottleneck": {"severity": "EXTREME (advanced packaging)", "points": [
      "TSMC CoWoS is sold out through 2027 despite tripling capacity (35K→130K wafers/month); it is the single biggest physical constraint on Blackwell/Rubin output.",
      "TSMC is expanding toward ~170K wafers/month by 2027; AMD and Broadcom get rationed allocation behind NVIDIA.",
      "There is no competitive substitute at the leading edge — Samsung and Intel cannot absorb meaningful AI volume, so TSMC is a true single point of dependence (and a Taiwan tail risk).",
    ]},
    "market_size": [
      "Pure-play foundry ~$175B (2025);[[cite:trendforce]] TSMC alone $121.2B FY25 → ~$160B 2026E.[[cite:filings]]",
      "HPC (incl. AI) rose to 61% of TSMC’s revenue in Q1’26, up from 51% a year earlier — AI is now the majority of the mix.[[cite:filings]]",
      "CoWoS capacity 35K (2024) → ~130K (2026E) → ~170K (2027) wafers/month, still over-subscribed.[[cite:filings]]",
    ],
    "value_added": [
      "EXTREME. TSMC posted a record ~66% gross margin in Q1'26 and ~49–51% operating margin; FY25 net income ~$54B.",
      "This is the highest-quality monopoly in the chain (pricing power 9/10): the barrier to replicate leading-edge + CoWoS is decades and hundreds of billions.",
      "OSATs (ASE ~$18B, Amkor ~$7B) earn ordinary packaging margins but are leveraged to advanced-packaging capacity growth and CoWoS overflow.",
    ],
    "how_to_analyze": "TSMC is the highest-quality pick-and-shovels name in the chain — track monthly revenue, HPC-mix %, gross margin, capex, and CoWoS capacity commentary. The bear case is single-country (Taiwan) concentration, not competition. OSATs: advanced-packaging revenue mix and capex.",
    "sub_segments": [
      "Pure-play foundry (2025) — TSMC 69.9%, Samsung 7.2%, SMIC 5.3%, Intel (not top-10 at leading edge).",
      "OSAT / advanced packaging — ASE (#1), Amkor (#2, US/Arizona).",
    ],
    "glossary": [
      ("Foundry", "A factory that manufactures chips for fabless designers. TSMC dominates leading-edge (69.9% pure-play share)."),
      ("Node (3nm/5nm)", "Feature size; smaller = more performance/lower power. Blackwell is 4nm-class; AI leading edge is 3nm in 2026, 2nm next."),
      ("CoWoS", "Chip-on-Wafer-on-Substrate — TSMC's advanced packaging that stacks HBM next to the GPU. Effectively a TSMC monopoly and the single biggest constraint on NVIDIA output."),
      ("OSAT", "Outsourced Semiconductor Assembly & Test — packaging specialists (ASE, Amkor) that take CoWoS overflow + most non-AI packaging."),
    ],
    "deals_detail": [
      "<b>TSMC is ~70% of the world's foundry and the only place leading-edge AI silicon gets made — but note the reporting nuance:</b> its ADR (TSM) trades in USD while it reports financials in New Taiwan dollars, which is why Yahoo's headline P/S for it is broken (we recompute it at 16.4x from USD market cap ÷ USD revenue). HPC/AI is now 61% of revenue and climbing. The OSATs (ASE, Amkor) are the secondary way to play advanced packaging — Amkor's Arizona facility sits next to TSMC's US fabs and is a US-onshoring beneficiary, but neither earns TSMC-like margins.",
    ],
  },

  "L1": {
    "what_it_does": "The deepest layer — everything upstream of the foundry. Three sub-categories: (a) EDA software where chips are designed (Synopsys, Cadence) + CPU IP (Arm); (b) wafer-fab equipment (ASML, AMAT, Lam, TEL, KLA); (c) specialty materials and niche tools (Hoya mask blanks, Hanmi/BESI HBM bonders, Lasertec, Shin-Etsu wafers).",
    "analyst_take": "This is where the most durable monopolies in technology live, and I think of it as the bedrock under everything above. ASML is the purest expression: it is the sole maker of EUV lithography, a High-NA machine costs $380M, and there is no plan B anywhere on earth. EDA (Synopsys, Cadence) is almost as good — a ~65%-share duopoly with software economics (~95% incremental gross margins) embedded in every chip designed. The reason these aren’t crowded trades is that the moats are measured in decades of accumulated know-how, so they look ‘expensive’ on near-term earnings while being nearly impossible to disrupt. The one cloud is China: export controls cap ASML’s addressable market at the margin.",
    "stance": "Own the irreplaceable inputs for the long term — ASML (EUV monopoly), SNPS/CDNS (EDA duopoly). For HBM-capex beta, the niche Asian tool-makers (Hanmi, BESI, Advantest). Watch China revenue mix.",
    "capex_slice": "Mostly indirect — L1 is funded by L2/L3 capex, not the hyperscaler $725B. The one direct touch is the ‘software, EDA, security’ bucket (~$25–35B, 3–5%), of which EDA is a slice; WFE TAM is ~$120B.[[cite:trendforce]]",
    "who_pays_whom": "Chip designers pay Synopsys/Cadence/Arm to design; foundries (L2) and memory makers (L3) pay equipment makers for WFE and buy materials. This layer sells the tools and inputs that make every chip above it possible.",
    "bottleneck": {"severity": "HIGH but distributed", "points": [
      "EUV machines (ASML High-NA) carry 18-month lead times; HBM thermal-compression bonders (Hanmi, BESI) are sold out — distinct choke points rather than one binding constraint.",
      "Because the constraints are spread across many specialized suppliers, the layer eases gradually as each expands capacity (ASML targets ~$71B revenue by 2030).",
      "The deeper risk is concentration: single suppliers for irreplaceable inputs (ASML for EUV, Hoya for ~75% of EUV mask blanks, Lasertec for EUV mask inspection).",
    ]},
    "market_size": [
      "Total $140B+ (2026E): WFE ~$120B (2025), EDA ~$21B, photoresist + silicon wafers ~$15B.[[cite:trendforce]]",
      "HBM TC bonders are growing 50%+/year off a small base; every sub-segment is AI-leveraged.[[cite:yole]]",
      "Software (EDA) is tiny in dollars (~1% of the chain) but carries ~95% incremental gross margins.[[cite:filings]]",
    ],
    "value_added": [
      "EXTREME at the inputs — the most durable monopolies in the entire chain. ASML: ~51% gross / ~35% operating margin as the sole EUV maker (pricing power 10/10).",
      "Synopsys/Cadence are a ~65%-share EDA duopoly with software economics (~35% operating margins, ~95% incremental gross). KLA holds ~50% of metrology. Hoya earns 30%+ EBIT on EUV blanks.",
      "These businesses are defensible because the bar to replicate them is decades of accumulated know-how, not capital alone — and many (ASML, Lasertec, Hoya, Hanmi) are effectively sole-source.",
    ],
    "how_to_analyze": "ASML is the most defensible monopoly in the chain — the bear case is China exposure (~20–30% of revenue) under tightening export controls, not competition. EDA: recurring revenue + AI-design-tool adoption. Memory-equipment names (Lam, Hanmi, BESI, Advantest) are the cleanest HBM-capex derivatives. Watch order backlogs and China-revenue mix.",
    "sub_segments": [
      "EDA + IP — Synopsys (~35%), Cadence (~30%), Arm (CPU IP royalties).",
      "WFE Big 5 — ASML (~22%, EUV), AMAT (~18%), Tokyo Electron (~13%), Lam (~11%), KLA (~7%).",
      "Specialty / niche — Hoya (75% EUV blanks), Hanmi (71% HBM bonders), BESI (hybrid bonding), Advantest (test), Lasertec (EUV mask inspection), Disco (dicing), Shin-Etsu (wafers), Qnity (materials).",
    ],
    "glossary": [
      ("EDA", "Electronic Design Automation — software to design chips. Synopsys + Cadence duopoly (~65% combined). Every AI chip is designed in it."),
      ("WFE", "Wafer Fab Equipment — the machines inside a fab. Big 5: ASML (litho), AMAT (broadest), Lam (etch), TEL (coater/etch), KLA (metrology)."),
      ("EUV", "Extreme Ultraviolet Lithography — prints sub-7nm features. Only ASML makes it; High-NA machines cost $380M each. The most defensible position in the chain."),
      ("Metrology", "Measuring/inspecting chips at each step to catch defects. KLA ~50% share — yield-critical as nodes shrink."),
      ("TC bonder", "Thermal-Compression bonder — stacks and bonds HBM dies. Hanmi ~71% share; BESI is Micron's HBM4 sole-source and leads hybrid bonding."),
      ("Mask blank", "The quartz 'stencil' input for patterning chips. Hoya supplies 60%+ of photomask, 75%+ of EUV blanks."),
    ],
    "deals_detail": [
      "<b>This layer is where the durable monopolies live, but most names are diversified — so segment context matters.</b> Hoya, for instance, is a 75%-share EUV-mask-blank supplier, but mask blanks are only part of a company that also makes eyeglass lenses and medical endoscopes; Shin-Etsu's #1 silicon-wafer position sits inside a broad chemicals group. The cleanest pure-plays on AI/HBM capacity are the small Asian specialists — Hanmi (71% of HBM bonders), Lasertec (EUV mask-inspection monopoly), Advantest (HBM/AI-SoC test) — which is also why they are the most cyclical. ASML, Synopsys and Cadence are the high-quality, more-liquid ways to own the layer; their margins (and multiples) reflect genuine monopoly/duopoly economics. Note Synopsys closed its $35B Ansys acquisition in Jul'25, adding simulation to design.",
    ],
  },

  "L0": {
    "what_it_does": "The foundational input layer — every other layer needs electricity, and heat must be removed. As rack density climbed from ~10 kW to ~130 kW (Blackwell) toward ~1 MW (Rubin), the entire power-and-cooling chain became a hard constraint.",
    "analyst_take": "My single highest-conviction macro call in this report is that <i>power is the new GPU</i> — the binding constraint of 2026–27 is shifting from silicon to electrons. Grid interconnect queues run 7–10 years and transformer lead times exceed 100 weeks, so the scarce resource is increasingly the ability to physically power and cool a building, not to buy chips for it. Crucially, lead times have become pricing power: GE Vernova’s turbines are sold out for years, Vertiv’s orders rose 252% YoY. I’d rather own the picks-and-shovels (electrical equipment, on-site generation) than the utilities, because backlog and order growth — not current revenue — are what re-rate here.",
    "stance": "Power is the next bottleneck. Favour equipment with multi-year backlogs (VRT, GEV, ETN) and behind-the-meter optionality (BE, BWXT) over regulated utilities. Track orders/book-to-bill, not revenue.",
    "capex_slice": "~$82–105B of the $725B (power &amp; electrical ~$60–75B + cooling ~$22–30B), against a researched ~$80B AI-relevant power-and-cooling TAM[[cite:mckinsey]] — and the fastest-growing line in the funnel.",
    "who_pays_whom": "Hyperscalers + DC operators pay electricity producers via PPAs (Constellation, Vistra, Talen, NextEra), pay electrical-equipment makers (Schneider, Eaton, Vertiv, GE Vernova) for switchgear/transformers/turbines, and pay cooling vendors (Vertiv, Schneider, Daikin) for thermal management. Fuel-cell and SMR makers (Bloom, BWXT) sell behind-the-meter power.",
    "bottleneck": {"severity": "EXTREME (the next bottleneck)", "points": [
      "Grid-interconnect queues run 7–10 years in key US markets; transformer and switchgear lead times exceed 100 weeks — power, not silicon, is increasingly the binding constraint of 2026–27.",
      "Resolution is slow and multi-pronged: behind-the-meter generation (Bloom SOFC, on-site gas), nuclear restarts (Three Mile Island), SMRs (BWXT BANR), and new gas turbines (GE Vernova, sold out for years).",
      "Power demand is growing 10–100x faster than the HBM/CoWoS choke points it sits beneath — McKinsey models US DC power demand compounding 15–20%/yr through 2028.",
    ]},
    "market_size": [
      "AI-relevant power &amp; cooling ~$80B in 2026E; McKinsey’s $5.2T global DC build by 2030 routes ~$1.3T (25%) to ‘energizers’ (utility + electrical).[[cite:mckinsey]]",
      "Generation equipment (gas turbines, grid) and electrical gear (switchgear, transformers, UPS) have multi-year backlogs and the longest lead times in the chain.[[cite:filings]]",
      "Cooling is a smaller but fast-growing slice as liquid/direct-to-chip cooling becomes mandatory above ~100 kW/rack.[[cite:filings]]",
    ],
    "value_added": [
      "MEDIUM-HIGH and rising — lead times have become pricing power. Vertiv ~16–22% operating margin (Q4'25 orders +252% YoY); Schneider ~17–18%; Constellation ~30% (utility-style).",
      "Equipment makers (Vertiv, Schneider, Eaton, GE Vernova) capture the most because their order books are multi-year and backlogged; utilities earn steadier regulated/contracted returns.",
      "Behind-the-meter power (Bloom Energy — GAAP-profitable since Q1'26, 2026 guide $3.4–3.8B +80%) re-rated hardest because it bypasses the grid queue entirely.",
    ],
    "how_to_analyze": "Power has become 'the new GPU.' Equipment: orders, backlog, book-to-bill, lead-time commentary (the pricing-power tell). Utilities: contracted PPAs and behind-the-meter co-location deals. Fuel cells/SMRs: backlog and commercial milestones. The whole layer is supply-constrained, so backlog growth matters more than current revenue.",
    "sub_segments": [
      "Electricity generation — Constellation (33 GW nuclear, #1), Vistra (44 GW), Talen (10 GW), NextEra (70 GW renewables), GE Vernova (turbines + grid), plus Cameco (uranium).",
      "Fuel cells — Bloom (SOFC, integrated), Ceres (SOFC licensor), Doosan (Ceres licensee), FuelCell Energy (molten-carbonate).",
      "Electrical equipment — Schneider (#1 switchgear/UPS), Vertiv (power + cooling), Eaton (switchgear/transformers).",
      "Cooling — Vertiv + Schneider (tied #1), Johnson Controls, Trane, Daikin (liquid/DDC).",
    ],
    "glossary": [
      ("PPA", "Power Purchase Agreement — long-term contract to buy electricity from a producer (Microsoft–Constellation, AWS–Talen 960 MW)."),
      ("SOFC", "Solid-Oxide Fuel Cell — converts gas to electricity at ~60% efficiency, no combustion, deploys in ~90 days. Bloom is the leader; Ceres licenses the tech."),
      ("SMR", "Small Modular Reactor — 50–300 MW nuclear units, easier to permit. BWXT's BANR is purpose-built for data centers."),
      ("UPS / Switchgear", "UPS = backup power during outages; switchgear distributes power inside the DC. Schneider is #1 in both."),
      ("Behind-the-meter", "On-site generation that bypasses the public grid (and its 7–10-yr interconnect queue)."),
    ],
    "deals_detail": [
      "<b>Why the utilities don't show an 'AI segment.'</b> Constellation, Vistra, Talen and NextEra are power utilities — AI is a <i>demand driver</i> lifting power prices and contracting their output, not a reported business segment, so there is no clean 'AI revenue' line. The signal instead is the contracts: Microsoft's Three Mile Island restart with Constellation, AWS's 960 MW Susquehanna co-location with Talen, Meta's 1,121 MW Clinton deal. The equipment makers are the more direct plays: Vertiv is the cleanest large-cap DC power-and-cooling pure-play; Schneider and Eaton bury fast-growing DC electrical inside diversified electrification giants (DC is ~16% of Schneider); GE Vernova's gas turbines are sold out for years. Bloom Energy and BWXT are the behind-the-meter/SMR optionality — Bloom's Oracle 2.8 GW Project Jupiter and BWXT's $7.3B backlog are the proof points.",
    ],
  },
}


# ---------------------------------------------------------------------------
# v12 ADD-ONS — margin focus, extra charts, TSMC capacity table
#   Kept as separate top-level dicts (vs editing each LAYER_CONTENT entry) so the
#   builder can merge them in. margin_key in {'gm','om','ebitda'} = column to highlight.
# ---------------------------------------------------------------------------
MARGIN_FOCUS = {
    "L10": ("gm", "<b>Gross margin</b> is what matters here — an app keeps only the spread above what it pays the model provider, so gross margin <i>is</i> the business model."),
    "L9":  ("gm", "<b>Gross margin</b> (inference unit economics, ~50–60%) is the read to watch. GAAP operating margin is deeply negative mid-training and misleads."),
    "L8":  ("om", "<b>Operating margin</b> is the franchise read (AWS ~35%, Azure ~50% on AI). For neoclouds, watch the gross-to-operating <i>gap</i> — ~70% gross collapses to negative operating on GPU depreciation."),
    "L7":  ("ebitda", "<b>EBITDA margin</b> is the right lens — REITs carry heavy depreciation, so EBITDA / AFFO, not net or operating margin, reflects the economics."),
    "L6":  ("om", "<b>Operating margin</b> separates the winners — Arista ~43%, Broadcom networking ~50% — from the commodity box-shifters."),
    "L5":  ("gm", "<b>Gross margin</b> is the entire thesis: Foxconn's 5–7% gross on AI servers tells you the assembly layer has almost no pricing power."),
    "L4":  ("gm", "<b>Gross margin</b> is the pricing-power tell. NVIDIA's ~73% vs the rest of the layer is the single clearest signal of who holds the monopoly."),
    "L3":  ("ebitda", "<b>EBITDA margin</b> reads the cycle best — memory is capital-intensive and cyclical, so D&A distorts net income; watch EBITDA alongside the (huge) operating-margin swings."),
    "L2":  ("gm", "<b>Gross margin</b> is the monopoly tell — TSMC's record ~66% gross is pricing power earned by being the only option at the leading edge."),
    "L1":  ("gm", "<b>Gross margin</b> captures the software/IP economics — EDA runs ~95% incremental gross; for the equipment makers, gross margin shows pricing power on irreplaceable tools."),
    "L0":  ("om", "<b>Operating margin</b> is the read for the equipment franchises (Vertiv ~18%); for the utilities, lean on EBITDA and contracted-return visibility instead."),
}

# Extra charts merged AFTER each layer's existing `charts`. Same schema as LAYER_CONTENT charts.
EXTRA_CHARTS = {
    "L9": [
        {"title": "Global LLM industry revenue — annual trend & forecast", "source": "counterpoint",
         "type": "bar", "unit": "$B",
         "rows": [("2023", 3, "from <$1B in Jan'23"), ("2024", 12, "first scaled year"),
                  ("2025", 45, "inflection"), ("2026E", 100, "~$100B ARR by Q1'26"),
                  ("2028E", 230, "if scaling holds"), ("2030E", 400, "$400B+ base case")]},
    ],
    "L8": [
        {"title": "2026E capex by hyperscaler — the $725B", "source": "filings", "type": "bar", "unit": "$B",
         "rows": [("Amazon", 200, "largest spender"), ("Microsoft", 190, ""), ("Alphabet", 187, ""),
                  ("Meta", 140, "captive only"), ("Oracle", 50, "Stargate-driven")]},
        {"title": "Big-5 hyperscaler capex — history & forecast", "source": "filings", "type": "bar", "unit": "$B",
         "rows": [("2023", 150, ""), ("2024", 230, "+~53%"), ("2025", 420, "+~83%"),
                  ("2026E", 725, "+~73% YoY")]},
    ],
    "L6": [
        {"title": "Optical transceiver makers — 2025 (~$22B TAM)", "source": "yole", "type": "donut", "unit": "%",
         "rows": [("Coherent", 25, "InP leader"), ("Innolight (China)", 24, "#1 in modules"),
                  ("Eoptolink", 13, "China challenger"), ("Lumentum", 12, "50–60% EML share"),
                  ("Others", 26, "Fabrinet, Marvell, AAOI")]},
        {"title": "RAN / AI-RAN market share — 2025", "source": "omdia", "type": "donut", "unit": "%",
         "rows": [("Huawei", 30, "excluded from West"), ("Ericsson", 24, "no NVIDIA tie"),
                  ("Nokia", 18, "NVIDIA $1B / AI-RAN tie"), ("Samsung", 7, ""), ("ZTE + others", 21, "")]},
        {"title": "Optical fiber — Corning's position", "source": "filings", "type": "donut", "unit": "%",
         "rows": [("Corning", 30, "#1 global; Meta $6B deal"), ("Others", 70, "Prysmian, Sumitomo, Furukawa")]},
    ],
    "L4": [
        {"title": "Custom AI ASIC (XPU) share — 2025", "source": "filings", "type": "donut", "unit": "%",
         "rows": [("Broadcom", 70, "Google TPU, Meta MTIA, OpenAI"), ("Marvell", 13, "AWS Trainium, MS Maia"),
                  ("Alchip / GUC / others", 17, "")]},
        {"title": "Data-center CPU share — 2025", "source": "filings", "type": "donut", "unit": "%",
         "rows": [("Intel (Xeon)", 55, "losing share"), ("AMD (EPYC)", 39, "gaining fast"),
                  ("Arm (Graviton etc.)", 6, "hyperscaler in-house")]},
    ],
    "L3": [
        {"title": "DRAM market share — 2025 (~$180B)", "source": "trendforce", "type": "donut", "unit": "%",
         "rows": [("SK Hynix", 36, "took #1 in 2025"), ("Samsung", 34, ""), ("Micron", 25, ""), ("Others", 5, "")]},
        {"title": "NAND flash share — 2025 (~$70B)", "source": "trendforce", "type": "donut", "unit": "%",
         "rows": [("Samsung", 33, ""), ("SK / Solidigm", 20, ""), ("Kioxia", 19, ""),
                  ("Sandisk", 14, "pure-play"), ("Micron", 11, ""), ("Others", 3, "")]},
        {"title": "HDD market share — 2025 (~$20B)", "source": "trendforce", "type": "donut", "unit": "%",
         "rows": [("Seagate", 43, ""), ("Western Digital", 37, ""), ("Toshiba", 20, "")]},
    ],
    "L1": [
        {"title": "WFE equipment share — 2025 (~$120B)", "source": "trendforce", "type": "donut", "unit": "%",
         "rows": [("ASML", 22, "sole EUV"), ("Applied Materials", 18, "broadest"), ("Tokyo Electron", 13, ""),
                  ("Lam Research", 11, "etch/memory"), ("KLA", 7, "metrology"), ("Others", 29, "")]},
        {"title": "EDA software share — 2025 (~$21B)", "source": "filings", "type": "donut", "unit": "%",
         "rows": [("Synopsys", 32, ""), ("Cadence", 30, ""), ("Siemens EDA", 14, ""), ("Others", 24, "Ansys (now SNPS), etc.")]},
    ],
}

# Small fact table rendered inside Layer 2 (TSMC capacity & AI-mix trajectory).
EXTRA_TABLES = {
    "L2": {
        "title": "TSMC capacity & AI-mix trajectory",
        "source": "filings",
        "header": ["", "2024", "2025", "2026E", "2027E"],
        "rows": [
            ["CoWoS capacity (k wafers/mo)", "35", "~75", "~130", "~170"],
            ["HPC (incl. AI) % of revenue", "51%", "~58%", "61%+", "~65%"],
            ["Revenue (US$B)", "$90", "$121", "~$160", "~$200"],
            ["Gross margin", "~53%", "~59%", "~66%", "mid-60s%"],
        ],
        "note": "CoWoS advanced-packaging capacity has tripled yet remains sold out through 2027; AI/HPC is now the majority of TSMC's revenue mix. Figures are curated estimates from TSMC guidance and disclosures.",
    },
}
