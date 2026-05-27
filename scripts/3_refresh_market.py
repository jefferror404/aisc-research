"""
3_refresh_market.py — Pull live valuation + financial-statement data from yfinance and
write it into the DB. Re-run any time to refresh the numbers (quarterly is typical).

What it fetches per public ticker:
  market_data : market cap (USD-converted), P/E TTM, forward P/E, P/S, earnings growth,
                revenue growth, gross/operating/EBITDA/profit margins (TTM), TTM revenue.
  financials  : last ~4 fiscal years of revenue / operating income / EBITDA / net income,
                with derived margins (USD-converted from the company's reporting currency).
  estimates   : next-FY (FY+1) consensus revenue, when yfinance exposes it.
  fx_rates    : the USD conversion rates used, stamped with the run date.

Notes
-----
* Run with the sandbox disabled (network egress), e.g. inside the project venv on macOS.
* yfinance's statement/estimate endpoints intermittently throw a curl_cffi TLS error;
  every call is wrapped in retry(). Valuation (.info) is the most reliable.
* International market caps are in the trading currency; financials in the reporting
  currency. Both are converted to USD via fx_rates. (Both Yahoo & stockanalysis agree on
  the raw local figures, incl. the 2026 memory-supercycle re-rating of the Korean names.)
"""
import sqlite3
import time
from datetime import date
from pathlib import Path

import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "aisc.db"
TODAY = date.today().isoformat()

# Currencies we may encounter (trading or reporting). USD = 1.0 by definition.
FX_CURRENCIES = ["KRW", "TWD", "JPY", "HKD", "EUR", "GBP", "SEK", "CAD", "CNY"]


def retry(fn, n=6, sleep=1.5, default=None):
    last = None
    for _ in range(n):
        try:
            r = fn()
            if r is not None and (not hasattr(r, "empty") or not r.empty):
                return r
            if r is not None:
                return r
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(sleep)
    if last:
        print(f"      (retry gave up: {repr(last)[:80]})")
    return default


def fetch_fx():
    """Return {CUR: usd_per_unit}. e.g. fx['KRW'] ~ 0.00066."""
    fx = {"USD": 1.0}
    for cur in FX_CURRENCIES:
        fi = retry(lambda c=cur: yf.Ticker(f"{c}USD=X").fast_info)
        rate = None
        if fi is not None:
            try:
                rate = fi.last_price
            except Exception:  # noqa: BLE001
                rate = None
        fx[cur] = rate
        print(f"  FX {cur}->USD: {rate}")
        time.sleep(0.3)
    return fx


def margin(numer, denom):
    if numer is None or denom in (None, 0):
        return None
    return numer / denom


def row_val(df, names):
    """First matching row's most-recent value from a yfinance statement DataFrame."""
    for nm in names:
        if nm in df.index:
            try:
                v = df.loc[nm].iloc[0]
                return None if v != v else float(v)  # NaN check
            except Exception:  # noqa: BLE001
                continue
    return None


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    tickers = [r[0] for r in cur.execute(
        "SELECT ticker FROM companies WHERE is_public=1 ORDER BY primary_layer, ticker")]

    print(f"Refreshing {len(tickers)} tickers on {TODAY}\n")
    fx = fetch_fx()
    for c, rate in fx.items():
        cur.execute("INSERT OR REPLACE INTO fx_rates (pair, rate_to_usd, as_of) VALUES (?,?,?)",
                    (c, rate, TODAY))
    con.commit()

    ok, fail = 0, 0
    for i, tk in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {tk}")
        info = retry(lambda t=tk: yf.Ticker(t).info, default={})
        if not info or not info.get("symbol"):
            print("      no .info — skipped")
            fail += 1
            continue

        trade_cur = info.get("currency") or "USD"
        fin_cur = info.get("financialCurrency") or trade_cur
        fx_trade = fx.get(trade_cur)
        fx_fin = fx.get(fin_cur)

        mc_native = info.get("marketCap")
        mc_usd = mc_native * fx_trade if (mc_native and fx_trade) else None
        rev_ttm_native = info.get("totalRevenue")
        rev_ttm_usd = rev_ttm_native * fx_fin if (rev_ttm_native and fx_fin) else None

        cur.execute(
            """INSERT OR REPLACE INTO market_data
               (ticker, as_of, currency, price, market_cap_usd, market_cap_native,
                pe_ttm, forward_pe, ps_ttm, earnings_growth, revenue_growth,
                gross_margin, operating_margin, ebitda_margin, profit_margin, total_revenue_ttm_usd)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (tk, TODAY, trade_cur,
             info.get("currentPrice") or info.get("regularMarketPrice"),
             mc_usd, mc_native,
             info.get("trailingPE"), info.get("forwardPE"),
             info.get("priceToSalesTrailing12Months"),
             info.get("earningsGrowth"), info.get("revenueGrowth"),
             info.get("grossMargins"), info.get("operatingMargins"),
             info.get("ebitdaMargins"), info.get("profitMargins"), rev_ttm_usd),
        )

        # ---- per-fiscal-year financials ----
        inc = retry(lambda t=tk: yf.Ticker(t).income_stmt)
        if inc is not None and not inc.empty:
            for col in list(inc.columns)[:4]:
                pend = col.date().isoformat() if hasattr(col, "date") else str(col)
                sub = inc[[col]]
                revenue = row_val(sub, ["Total Revenue", "Operating Revenue"])
                gp = row_val(sub, ["Gross Profit"])
                oi = row_val(sub, ["Operating Income", "Total Operating Income As Reported"])
                eb = row_val(sub, ["EBITDA", "Normalized EBITDA"])
                ni = row_val(sub, ["Net Income", "Net Income Common Stockholders"])
                to_usd = lambda v: v * fx_fin if (v is not None and fx_fin) else None
                cur.execute(
                    """INSERT OR REPLACE INTO financials
                       (ticker, period_end, fiscal_label, currency, revenue, gross_profit,
                        operating_income, ebitda, net_income, gross_margin, operating_margin, ebitda_margin)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (tk, pend, f"FY{pend[:4]}", fin_cur,
                     to_usd(revenue), to_usd(gp), to_usd(oi), to_usd(eb), to_usd(ni),
                     margin(gp, revenue), margin(oi, revenue), margin(eb, revenue)),
                )

        # ---- forward (FY+1) revenue estimate ----
        rev_est = retry(lambda t=tk: yf.Ticker(t).revenue_estimate, n=3)
        if rev_est is not None and not rev_est.empty and "+1y" in rev_est.index:
            try:
                avg = rev_est.loc["+1y", "avg"]
                if avg == avg:  # not NaN
                    cur.execute(
                        """INSERT OR REPLACE INTO estimates
                           (ticker, fiscal_label, revenue_estimate_native, revenue_estimate_usd, source, as_of)
                           VALUES (?,?,?,?,?,?)""",
                        (tk, "FY+1", float(avg),
                         float(avg) * fx_fin if fx_fin else None, "yfinance", TODAY))
            except Exception:  # noqa: BLE001
                pass

        ok += 1
        con.commit()
        time.sleep(0.4)

    con.close()
    print(f"\nDone. {ok} ok, {fail} failed. Snapshot date {TODAY}.")


if __name__ == "__main__":
    main()
