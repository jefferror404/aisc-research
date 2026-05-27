"""
1_init_db.py — Create the SQLite schema for the AI Supply Chain research database.

The DB (data/aisc.db) is the single source of truth and separates:
  - companies   : CURATED research (layer, segment, contracts, narrative). Hand-maintained
                  via data/companies_seed.json. NEVER overwritten by the market refresh.
  - market_data : AUTO-FETCHED valuation + TTM margins (one snapshot row per refresh date).
  - financials  : AUTO-FETCHED per-fiscal-year revenue / margins / net income.
  - estimates   : forward (FY+1) revenue / EPS estimates — fetched where available, else curated.
  - fx_rates    : USD conversion rates captured at refresh time (for non-USD market caps).

Run once to create the file; safe to re-run (CREATE TABLE IF NOT EXISTS).
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "aisc.db"

SCHEMA = """
-- Canonical financial entity: one row per ticker. Financials/valuation join here.
CREATE TABLE IF NOT EXISTS companies (
    ticker          TEXT PRIMARY KEY,   -- yfinance symbol (e.g. NVDA, 000660.KS)
    native_ticker   TEXT,               -- local-exchange symbol
    name            TEXT NOT NULL,
    country         TEXT,
    primary_layer   TEXT,               -- main layer for sorting
    is_public       INTEGER DEFAULT 1,
    is_pure_play    INTEGER DEFAULT 0,   -- 1 = ~pure AI exposure
    fiscal_note     TEXT,                -- fiscal-year quirks (e.g. NVDA FY ends Jan)
    narrative       TEXT                 -- company-level note for the report
);

-- A company's APPEARANCE in a given layer table. Many-to-many: AVGO sits in L4 and L6
-- with different segment context in each. This drives which tickers render in which table.
CREATE TABLE IF NOT EXISTS company_layer (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    layer           TEXT NOT NULL,       -- L0 .. L10
    layer_name      TEXT,
    sublayer        TEXT,                -- 'Hyperscaler','Neocloud','GPU','OSAT','Optics',...
    category        TEXT,
    segment_label   TEXT,                -- AI-relevant segment name in THIS layer context
    segment_rev_note TEXT,               -- segment revenue $ + % of total (curated, contextual)
    key_contracts   TEXT,                -- contracts WITH durations (curated, contextual)
    backlog_rpo     TEXT,                -- backlog / RPO (curated, from filings)
    ai_rev_share    TEXT,                -- AI-related revenue as % of total company revenue (curated estimate; '100%' = pure-play)
    note            TEXT,                -- short contextual note shown in/after the table
    sort_order      INTEGER DEFAULT 0,
    UNIQUE (ticker, layer, sublayer)
);

CREATE TABLE IF NOT EXISTS market_data (
    ticker          TEXT NOT NULL,
    as_of           TEXT NOT NULL,       -- ISO date of the refresh
    currency        TEXT,                -- reporting/quote currency
    price           REAL,
    market_cap_usd  REAL,
    market_cap_native REAL,
    pe_ttm          REAL,
    forward_pe      REAL,
    ps_ttm          REAL,
    earnings_growth REAL,                -- yoy (decimal, 0.21 = +21%)
    revenue_growth  REAL,
    gross_margin    REAL,                -- TTM (decimal)
    operating_margin REAL,
    ebitda_margin   REAL,
    profit_margin   REAL,
    total_revenue_ttm_usd REAL,
    free_cash_flow_usd    REAL,          -- TTM FCF, USD-converted (financial currency)
    ebitda_usd            REAL,          -- TTM EBITDA, USD-converted (financial currency)
    enterprise_value_usd  REAL,          -- EV, USD-converted (trading currency)
    PRIMARY KEY (ticker, as_of)
);

CREATE TABLE IF NOT EXISTS financials (
    ticker          TEXT NOT NULL,
    period_end      TEXT NOT NULL,       -- fiscal period end date (ISO)
    fiscal_label    TEXT,                -- e.g. 'FY25'
    currency        TEXT,
    revenue         REAL,
    gross_profit    REAL,
    operating_income REAL,
    ebitda          REAL,
    net_income      REAL,
    gross_margin    REAL,
    operating_margin REAL,
    ebitda_margin   REAL,
    PRIMARY KEY (ticker, period_end)
);

CREATE TABLE IF NOT EXISTS estimates (
    ticker          TEXT NOT NULL,
    fiscal_label    TEXT NOT NULL,       -- e.g. 'FY26E'
    revenue_estimate_native REAL,
    revenue_estimate_usd    REAL,
    eps_estimate    REAL,
    source          TEXT,                -- 'yfinance' | 'curated' | 'web'
    as_of           TEXT,
    PRIMARY KEY (ticker, fiscal_label)
);

CREATE TABLE IF NOT EXISTS fx_rates (
    pair            TEXT NOT NULL,       -- e.g. 'KRW' (1 KRW = rate USD)
    rate_to_usd     REAL,
    as_of           TEXT NOT NULL,
    PRIMARY KEY (pair, as_of)
);
"""


def main():
    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.commit()
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    con.close()
    print(f"Initialized {DB}")
    print("Tables:", ", ".join(tables))


if __name__ == "__main__":
    main()
