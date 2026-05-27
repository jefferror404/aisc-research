# -*- coding: utf-8 -*-
"""
4_build_report.py — Generate the scrollable HTML report from the DB + narrative.py.

Joins:
  company_layer (which names appear in which layer + curated segment/contract notes)
  + companies (entity-level flags)
  + market_data (latest snapshot: valuation + TTM margins)
  + financials (latest fiscal year: revenue + margins)
  + estimates (next-FY consensus revenue)

Output: report/ai_supply_chain_report.html  (self-contained, no external deps).
Re-run after refreshing data (3_refresh_market.py) or editing narrative.py / seeds.
"""
import html
import math
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
import narrative as N  # noqa: E402

DB = ROOT / "data" / "aisc.db"
OUT = ROOT / "report" / "ai_supply_chain_report.html"


# ----------------------------- formatting helpers -----------------------------
def esc(x):
    return html.escape(str(x)) if x is not None else ""


def b(x, dollar=True, dec=1):
    """USD from a raw USD figure. Sub-$1B shown in millions ($510M) for resolution;
    >=$1B in billions ($5.1B). Keeps small neocloud revenues legible."""
    if x is None:
        return "—"
    pre = "$" if dollar else ""
    if abs(x) < 1e9:
        return f"{pre}{x/1e6:,.0f}M"
    return f"{pre}{x/1e9:,.{dec}f}B"


def pct(x, dec=0):
    if x is None:
        return "—"
    return f"{x*100:.{dec}f}%"


def mult(x, dec=1):
    if x is None:
        return "—"
    return f"{x:.{dec}f}×"


def fy_label(period_end):
    """'2026-01-31' -> 'FYE Jan ’26'."""
    if not period_end:
        return ""
    try:
        d = datetime.fromisoformat(period_end)
        return f"FYE {d.strftime('%b ’%y')}"
    except Exception:
        return period_end


def cls_margin(x):
    if x is None:
        return ""
    if x < 0:
        return "neg"
    if x >= 0.5:
        return "hi"
    if x >= 0.2:
        return "mid"
    return "lo"


def cls_growth(x):
    if x is None:
        return ""
    return "neg" if x < 0 else ("hi" if x >= 0.4 else "")


# ----------------------------- data access -----------------------------
def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def latest_financials(con, ticker):
    return con.execute(
        "SELECT * FROM financials WHERE ticker=? ORDER BY period_end DESC LIMIT 1", (ticker,)
    ).fetchone()


def market(con, ticker):
    return con.execute(
        "SELECT * FROM market_data WHERE ticker=? ORDER BY as_of DESC LIMIT 1", (ticker,)
    ).fetchone()


def next_est_usd_b(con, ticker, country, latest_fy_usd):
    """Return (value_in_$B or None, label). Curated wins; else yfinance FY+1 if trustworthy."""
    if ticker in N.CURATED_FY_NEXT_EST_USD_B:
        return N.CURATED_FY_NEXT_EST_USD_B[ticker], "guide/curated"
    if country not in N.US_REPORTING_COUNTRIES:
        return None, ""  # foreign/ADR yfinance estimates are unreliable
    row = con.execute(
        "SELECT revenue_estimate_usd FROM estimates WHERE ticker=? AND fiscal_label='FY+1'", (ticker,)
    ).fetchone()
    if not row or not row["revenue_estimate_usd"]:
        return None, ""
    est = row["revenue_estimate_usd"]
    if not latest_fy_usd or latest_fy_usd <= 0:
        return est / 1e9, "consensus"
    ratio = est / latest_fy_usd
    big = latest_fy_usd >= 10e9
    small = latest_fy_usd < 1e9
    if small:
        return None, ""  # too noisy at <$1B base
    hi = 2.6 if big else 5.0
    if 0.5 <= ratio <= hi:
        return est / 1e9, "consensus"
    return None, ""  # implausible -> likely a units bug, suppress


# ----------------------------- HTML rendering -----------------------------
LAYER_TABLE_COLS = [
    ("Ticker", "ticker"), ("Company", "name"), ("Segment / share of revenue", "segment"),
    ("AI rev % of total", "aishare"),
    ("Revenue FY25", "fyrev"), ("Revenue 2026E", "est"), ("Δ % YoY", "chg"),
    ("Gross Margin", "gm"), ("Operating Margin", "om"), ("EBITDA Margin", "ebitda"),
    ("FCF Margin", "fcfm"),
    ("Market Cap", "mcap"), ("P/E (TTM)", "pe"), ("Fwd P/E", "fpe"), ("PEG", "peg"),
    ("P/S", "ps"), ("P/B", "pb"), ("EV/EBITDA", "evebitda"), ("P/FCF", "pfcf"),
    ("EPS Growth", "eg"), ("Backlog / RPO", "backlog"),
]
# number of columns that follow the (ticker, company, segment, AI%) lead block —
# used for the "Private — see notes" colspan.
_PRIV_COLSPAN = len(LAYER_TABLE_COLS) - 4


def _mfcls(key, focus):
    """Return the highlight class if this margin column is the layer's focus column."""
    return " mfocus" if (focus and key == focus) else ""


def render_company_row(con, cl, margin_focus=None):
    ticker = cl["ticker"]
    co = con.execute("SELECT * FROM companies WHERE ticker=?", (ticker,)).fetchone()
    f = latest_financials(con, ticker)
    m = market(con, ticker)
    is_public = co["is_public"] if co else 1
    pure = co["is_pure_play"] if co else 0

    fy_rev_usd = f["revenue"] if f else None
    est_b, est_lbl = next_est_usd_b(con, ticker, co["country"] if co else "", fy_rev_usd)

    # margins: prefer FY, fall back to TTM
    gm = (f["gross_margin"] if f and f["gross_margin"] is not None else (m["gross_margin"] if m else None))
    om = (f["operating_margin"] if f and f["operating_margin"] is not None else (m["operating_margin"] if m else None))
    eb = (f["ebitda_margin"] if f and f["ebitda_margin"] is not None else (m["ebitda_margin"] if m else None))

    ps = None
    if m and m["total_revenue_ttm_usd"] and m["market_cap_usd"]:
        ps = m["market_cap_usd"] / m["total_revenue_ttm_usd"]

    # EV/EBITDA, P/FCF, FCF margin (all from USD-converted fields).
    ev_ebitda = p_fcf = fcf_margin = None
    fcf_neg = False
    if m:
        ev, ebd, mc = m["enterprise_value_usd"], m["ebitda_usd"], m["market_cap_usd"]
        # Gate EV/EBITDA when yfinance's EV is currency-distorted (some ADRs): a sane
        # EV sits within ~0.3–3x of market cap. Outside that band we suppress to "—".
        if ev and ebd and ebd > 0 and mc and 0.3 <= ev / mc <= 3.0:
            ev_ebitda = ev / ebd
        fcf = m["free_cash_flow_usd"]
        if fcf is not None and mc:
            if fcf > 0:
                p_fcf = mc / fcf
            else:
                fcf_neg = True
        if fcf is not None and m["total_revenue_ttm_usd"]:
            fcf_margin = fcf / m["total_revenue_ttm_usd"]

    seg = cl["segment_rev_note"] or (cl["segment_label"] or "")
    pure_badge = ' <span class="badge pure">pure-play</span>' if pure else ""
    ai_share = cl["ai_rev_share"] if "ai_rev_share" in cl.keys() else ""
    ai_cell = f'<td class="ai">{esc(ai_share or "—")}</td>'

    fy_cell = "—"
    if fy_rev_usd is not None:
        fy_cell = f'{b(fy_rev_usd)}<span class="sub">{esc(fy_label(f["period_end"]))}</span>'

    est_cell = "—"
    if est_b is not None:
        est_cell = f'${est_b:,.0f}B<span class="sub">{esc(est_lbl)}</span>'

    # YoY % change FY25 -> 2026E (only when both are present)
    chg_cell, chg = "—", None
    if est_b is not None and fy_rev_usd:
        chg = (est_b * 1e9 - fy_rev_usd) / fy_rev_usd
        sign = "+" if chg >= 0 else ""
        chg_cell = f'{sign}{chg*100:.0f}%'

    # PEG shown as a plain number; P/B as a multiple.
    peg_txt = f"{m['peg_ratio']:.1f}" if (m and m["peg_ratio"] is not None) else "—"
    pb_txt = mult(m["price_to_book"]) if (m and m["price_to_book"] is not None) else "—"

    if not is_public:
        # private name — no market data
        cells = [
            f'<td class="tk">{esc(ticker)}</td>',
            f'<td class="co">{esc(cl["segment_label"] or ticker)}{pure_badge}</td>',
            f'<td class="seg">{esc_html_keep(seg)}</td>',
            ai_cell,
            f'<td colspan="{_PRIV_COLSPAN}" class="priv">Private — see notes</td>',
        ]
        return f'<tr>{"".join(cells)}</tr>'

    cells = [
        f'<td class="tk">{esc(ticker)}</td>',
        f'<td class="co">{esc(co["name"] if co else ticker)}{pure_badge}</td>',
        f'<td class="seg">{esc_html_keep(seg)}</td>',
        ai_cell,
        f'<td class="num">{fy_cell}</td>',
        f'<td class="num">{est_cell}</td>',
        f'<td class="num {cls_growth(chg)}">{chg_cell}</td>',
        f'<td class="num {cls_margin(gm)}">{pct(gm)}</td>',
        f'<td class="num {cls_margin(om)}">{pct(om)}</td>',
        f'<td class="num {cls_margin(eb)}">{pct(eb)}</td>',
        f'<td class="num {cls_margin(fcf_margin)}">{pct(fcf_margin)}</td>',
        f'<td class="num">{b(m["market_cap_usd"]) if m else "—"}</td>',
        f'<td class="num">{mult(m["pe_ttm"]) if m else "—"}</td>',
        f'<td class="num">{mult(m["forward_pe"]) if m else "—"}</td>',
        f'<td class="num">{peg_txt}</td>',
        f'<td class="num">{mult(ps)}</td>',
        f'<td class="num">{pb_txt}</td>',
        f'<td class="num">{mult(ev_ebitda)}</td>',
        f'<td class="num {"neg" if fcf_neg else ""}">{mult(p_fcf) if p_fcf is not None else ("neg" if fcf_neg else "—")}</td>',
        f'<td class="num {cls_growth(m["earnings_growth"] if m else None)}">{pct(m["earnings_growth"]) if m else "—"}</td>',
        f'<td class="bk">{esc(cl["backlog_rpo"] or "—")}</td>',
    ]
    return f'<tr>{"".join(cells)}</tr>'


def render_layer_table(con, layer, margin_focus=None):
    # Order sub-layers by the MIN sort_order within each sub-layer (so the curated
    # sort_order fully controls group order, e.g. L8: US → Chinese → Neocloud), then
    # by sort_order within the group. Keeps each sub-layer's rows contiguous.
    rows = con.execute(
        """SELECT cl.* FROM company_layer cl
           JOIN (SELECT sublayer, MIN(sort_order) AS so FROM company_layer
                 WHERE layer=? GROUP BY sublayer) g
             ON cl.sublayer = g.sublayer
           WHERE cl.layer=? ORDER BY g.so, cl.sort_order""", (layer, layer)
    ).fetchall()
    if not rows:
        return ""
    head = "".join(f"<th>{esc(c[0])}</th>" for c in LAYER_TABLE_COLS)
    body_parts, current_sub = [], None
    for cl in rows:
        sub = cl["sublayer"] or ""
        if sub != current_sub and sub:
            body_parts.append(
                f'<tr class="subhdr"><td colspan="{len(LAYER_TABLE_COLS)}">{esc(sub)}</td></tr>')
            current_sub = sub
        body_parts.append(render_company_row(con, cl, margin_focus))
    return (f'<div class="tablewrap"><table class="comp">'
            f'<thead><tr>{head}</tr></thead><tbody>{"".join(body_parts)}</tbody></table></div>')


def render_block_three(content):
    """Bottleneck / Market Size / Value-Added 3-up block."""
    bn = content["bottleneck"]
    sev = bn["severity"]
    sev_cls = "sev-" + ("extreme" if "EXTREME" in sev else "high" if "HIGH" in sev
                        else "med" if "MEDIUM" in sev else "low")
    bn_items = "".join(f"<li>{p}</li>" for p in bn["points"])
    ms_items = "".join(f"<li>{esc_html_keep(p)}</li>" for p in content["market_size"])
    va_items = "".join(f"<li>{esc_html_keep(p)}</li>" for p in content["value_added"])
    capex_slice = content.get("capex_slice")
    capex_block = (f'<div class="capexslice"><span class="cstag">Share of the $725B capex</span>'
                   f'{esc_html_keep(capex_slice)}</div>') if capex_slice else ""
    return f'''
    <div class="three">
      <div class="cell bn"><h4>Bottleneck <span class="sevtag {sev_cls}">{esc(sev)}</span></h4><ul>{bn_items}</ul></div>
      <div class="cell ms"><h4>Market Size</h4>{capex_block}<ul>{ms_items}</ul></div>
      <div class="cell va"><h4>Value Added &amp; Margins</h4><ul>{va_items}</ul></div>
    </div>'''


def esc_html_keep(s):
    """Our narrative strings contain intentional <b>/<i> tags — keep them, they're trusted."""
    return s


# ----------------------------- citations -----------------------------
CITE_RE = re.compile(r"\[\[cite:([a-z0-9_]+)\]\]")


def process_citations(body_html):
    """Replace [[cite:ID]] tokens with numbered superscript links (numbered in order
    of first appearance) and return (new_html, ordered_source_ids)."""
    order = []

    def repl(m):
        sid = m.group(1)
        if sid not in N.SOURCES:
            return ""  # unknown id -> drop the marker silently
        if sid not in order:
            order.append(sid)
        n = order.index(sid) + 1
        return f'<sup class="cite"><a href="#ref-{sid}" title="{esc(N.SOURCES[sid][0])}">[{n}]</a></sup>'

    return CITE_RE.sub(repl, body_html), order


def render_references(order):
    if not order:
        return ""
    lis = ""
    for i, sid in enumerate(order, 1):
        label, detail, url = N.SOURCES[sid]
        head = (f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'
                if url else f"<b>{esc(label)}</b>")
        lis += (f'<li id="ref-{sid}"><span class="rnum">[{i}]</span> '
                f'<span class="rbody">{head} — {esc(detail)}</span></li>')
    return (f'<section id="references"><h2>6 · Sources &amp; References</h2>'
            f'<p class="note">Click any footnote number in the text to jump here. '
            f'External links open the primary source where a public URL exists.</p>'
            f'<ol class="refs">{lis}</ol></section>')


# ----------------------------- charts (inline SVG) -----------------------------
CHART_PALETTE = ["#2547d0", "#0a8f5b", "#b9770a", "#c0392b", "#7c4dff", "#0aa2c0",
                 "#d4499b", "#5b6577", "#8a9a5b", "#a0522d"]


def _fmt_val(v, unit):
    if unit == "%":
        return f"{v:g}%"
    if unit and unit.startswith("$"):
        return f"${v:g}B"
    return f"{v:g}"


def svg_donut(rows, unit):
    """rows: list of (label, value, note). Returns an SVG donut string."""
    total = sum(r[1] for r in rows) or 1
    r, cx, cy, sw = 60, 80, 80, 26
    circ = 2 * math.pi * r
    segs, offset = "", 0.0
    for i, (label, val, _note) in enumerate(rows):
        frac = val / total
        dash = frac * circ
        color = CHART_PALETTE[i % len(CHART_PALETTE)]
        segs += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
                 f'stroke-width="{sw}" stroke-dasharray="{dash:.2f} {circ - dash:.2f}" '
                 f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})" '
                 f'data-k="{i}" data-tip="{esc(label)}: {_fmt_val(val, unit)}">'
                 f'<title>{esc(label)}: {_fmt_val(val, unit)}</title></circle>')
        offset += dash
    return (f'<svg viewBox="0 0 160 160" class="donut" role="img" '
            f'aria-label="share donut chart">{segs}'
            f'<circle cx="{cx}" cy="{cy}" r="{r - sw/2 - 1}" fill="#fff"/></svg>')


def svg_bars(rows, unit):
    """rows: list of (label, value, note). Horizontal SVG bar chart."""
    maxv = max((r[1] for r in rows), default=1) or 1
    rowh, gap, lblw, barw = 26, 8, 150, 230
    h = len(rows) * (rowh + gap)
    w = lblw + barw + 60
    parts = ""
    for i, (label, val, _note) in enumerate(rows):
        y = i * (rowh + gap)
        bw = (val / maxv) * barw
        color = CHART_PALETTE[i % len(CHART_PALETTE)]
        parts += (f'<text x="{lblw - 8}" y="{y + rowh/2 + 4}" text-anchor="end" '
                  f'class="barlbl">{esc(label)}</text>'
                  f'<rect x="{lblw}" y="{y}" width="{bw:.1f}" height="{rowh}" rx="4" fill="{color}" '
                  f'data-k="{i}" data-tip="{esc(label)}: {_fmt_val(val, unit)}">'
                  f'<title>{esc(label)}: {_fmt_val(val, unit)}</title></rect>'
                  f'<text x="{lblw + bw + 6}" y="{y + rowh/2 + 4}" class="barval">{_fmt_val(val, unit)}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="bars" role="img" '
            f'aria-label="bar chart">{parts}</svg>')


def svg_stacked_cols(years, series, unit):
    """Vertical stacked columns. years: list of x labels. series: list of
    (name, [v_per_year], note?). Shows total + composition over time."""
    n = len(years)
    colw, gap, top, bottom, plot_h = 46, 26, 20, 22, 160
    totals = [sum(s[1][i] for s in series) for i in range(n)]
    maxv = max(totals) or 1
    w = gap + n * (colw + gap)
    h = top + plot_h + bottom
    parts = ""
    for i, yr in enumerate(years):
        x = gap + i * (colw + gap)
        y = top + plot_h
        for j, s in enumerate(series):
            v = s[1][i]
            seg_h = (v / maxv) * plot_h
            y -= seg_h
            color = CHART_PALETTE[j % len(CHART_PALETTE)]
            parts += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{colw}" height="{seg_h:.1f}" '
                      f'fill="{color}" data-k="{j}" data-tip="{esc(s[0])} {esc(yr)}: {_fmt_val(v, unit)}">'
                      f'<title>{esc(s[0])} {esc(yr)}: {_fmt_val(v, unit)}</title></rect>')
        ytot = top + plot_h - (totals[i] / maxv) * plot_h
        parts += (f'<text x="{x + colw/2:.1f}" y="{ytot - 5:.1f}" text-anchor="middle" '
                  f'class="coltot">{_fmt_val(totals[i], unit)}</text>')
        parts += (f'<text x="{x + colw/2:.1f}" y="{top + plot_h + 15:.1f}" text-anchor="middle" '
                  f'class="collbl">{esc(yr)}</text>')
    return (f'<svg viewBox="0 0 {w:.0f} {h}" class="stackcol" role="img" '
            f'aria-label="stacked column chart">{parts}</svg>')


def render_charts(charts):
    """Render a layer's chart list: SVG (donut/bar/stacked) + a legend table beside it."""
    if not charts:
        return ""
    out = '<div class="charts">'
    for ch in charts:
        unit = ch.get("unit", "")
        cite = ""
        sid = ch.get("source")
        if sid and sid in N.SOURCES:
            cite = f' [[cite:{sid}]]'  # processed later in the global citation pass
        ctype = ch.get("type")
        leg = ""
        if ctype == "stacked":
            series = ch["series"]
            chart_svg = svg_stacked_cols(ch["years"], series, unit)
            for i, s in enumerate(series):
                name, vals = s[0], s[1]
                note = s[2] if len(s) > 2 else ""
                color = CHART_PALETTE[i % len(CHART_PALETTE)]
                leg += (f'<tr data-k="{i}" data-tip="{esc(name)}: {_fmt_val(vals[-1], unit)}">'
                        f'<td><span class="dot" style="background:{color}"></span>{esc(name)}</td>'
                        f'<td class="num">{_fmt_val(vals[-1], unit)}</td>'
                        f'<td class="cnote">{esc(note)}</td></tr>')
        else:
            rows = ch["rows"]
            chart_svg = svg_bars(rows, unit) if ctype == "bar" else svg_donut(rows, unit)
            for i, (label, val, note) in enumerate(rows):
                color = CHART_PALETTE[i % len(CHART_PALETTE)]
                leg += (f'<tr data-k="{i}" data-tip="{esc(label)}: {_fmt_val(val, unit)}">'
                        f'<td><span class="dot" style="background:{color}"></span>{esc(label)}</td>'
                        f'<td class="num">{_fmt_val(val, unit)}</td>'
                        f'<td class="cnote">{esc(note)}</td></tr>')
        out += (f'<figure class="chart"><figcaption>{esc(ch["title"])}{cite}</figcaption>'
                f'<div class="chartbody"><div class="chartviz">{chart_svg}</div>'
                f'<table class="legend"><tbody>{leg}</tbody></table></div></figure>')
    out += "</div>"
    return out


def render_glossary(items):
    if not items:
        return ""
    rows = "".join(f"<div class='gl'><b>{esc(t)}</b> — {esc_html_keep(d)}</div>" for t, d in items)
    return f'<details class="gloss"><summary>Glossary — {len(items)} terms</summary>{rows}</details>'


def render_subsegments(items):
    """Render sub-segments as a compact card grid. Each item is split on the first
    ' — ' into a bold lead and the detail, so it reads like a labelled card."""
    if not items:
        return ""
    cards = ""
    for s in items:
        sep = " — " if " — " in s else (" - " if " - " in s else None)
        if sep:
            head, _, rest = s.partition(sep)
            cards += (f'<div class="sscard"><div class="sshead">{esc_html_keep(head)}</div>'
                      f'<div class="ssbody">{esc_html_keep(rest)}</div></div>')
        else:
            cards += f'<div class="sscard"><div class="ssbody">{esc_html_keep(s)}</div></div>'
    return f'<div class="subseg"><h4>Sub-segments</h4><div class="sscards">{cards}</div></div>'


def render_extra_table(layer):
    t = N.EXTRA_TABLES.get(layer) if hasattr(N, "EXTRA_TABLES") else None
    if not t:
        return ""
    head = "".join(f'<th class="{"num" if i else ""}">{esc(h)}</th>'
                   for i, h in enumerate(t["header"]))
    body = ""
    for row in t["rows"]:
        tds = "".join(f'<td class="{"num" if i else "lbl"}">{esc(c)}</td>'
                      for i, c in enumerate(row))
        body += f"<tr>{tds}</tr>"
    cite = f'[[cite:{t["source"]}]]' if t.get("source") else ""
    note = f'<p class="src">{esc_html_keep(t["note"])}{cite}</p>' if t.get("note") else ""
    return (f'<div class="xtable"><h4>{esc(t["title"])}</h4>'
            f'<div class="tablewrap"><table class="comp facts" style="min-width:520px">'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>{note}</div>')


def render_deals_detail(items):
    if not items:
        return ""
    paras = "".join(f"<p>{esc_html_keep(p)}</p>" for p in items)
    return f'<div class="deals"><h4>Notes, deals &amp; disclosures</h4>{paras}</div>'


def render_gpu_cpu_asic():
    g = N.GPU_CPU_ASIC
    # light-theme cards, one accent per chip type for legibility
    accents = ["#0a8f5b", "#2547d0", "#b9770a"]  # CPU / GPU / ASIC
    cards = ""
    for i, c in enumerate(g["cards"]):
        ac = accents[i % len(accents)]
        cards += f'''<div class="chipcard" style="border-top:3px solid {ac}">
          <h5 style="color:{ac}">{esc(c["name"])}</h5><div class="tagline">{esc(c["tagline"])}</div>
          <p>{esc_html_keep(c["body"])}</p>
          <p class="val"><b>Value:</b> {esc_html_keep(c["value"])}</p></div>'''
    uses = "".join(f"<li><b>{esc(k)}:</b> {esc_html_keep(v)}</li>" for k, v in g["use_cases"])
    return f'''<div class="feature">
      <h4>{esc(g["heading"])}</h4>
      <p class="flead">{esc_html_keep(g["intro"])}</p>
      <div class="chipcards">{cards}</div>
      <div class="replace"><b>Can one replace another?</b> {esc_html_keep(g["can_they_replace"])}</div>
      <div class="uses"><b>Use cases</b><ul>{uses}</ul></div>
    </div>'''


# ----------------------------- sections -----------------------------
def render_capex(con):
    c = N.CAPEX
    q = c["takeaway"]
    body = "".join(f"<p>{esc_html_keep(p)}</p>" for p in q["body"])
    alloc_rows = "".join(
        f'<tr><td>{esc(cat)}</td><td class="num">{esc(pc)}</td><td class="num">{esc(dol)}</td>'
        f'<td class="seg">{esc(ben)}</td></tr>' for cat, pc, dol, ben in c["allocation"])
    alloc = (f'<div class="tablewrap"><table class="comp" style="min-width:640px">'
             f'<thead><tr><th>Category</th><th class="num">% of capex</th>'
             f'<th class="num">$ allocation</th><th>Primary beneficiaries</th></tr></thead>'
             f'<tbody>{alloc_rows}</tbody></table></div>')
    return f'''<section id="capex"><h2>2 · Hyperscaler Capex — the $725B keystone flow</h2>
      <p>{esc_html_keep(c["intro"])}</p>
      <h3>2.1 Where the $725B goes</h3>
      <p>{esc_html_keep(c["allocation_intro"])}</p>
      {alloc}
      <p class="src">{esc_html_keep(c["allocation_source"])}</p>
      <p class="note">{esc_html_keep(c["allocation_note"])}</p>
      {render_charts(c.get("charts"))}
      <div class="callout"><h4>{esc(q["heading"])}</h4>{body}</div></section>'''


def margin_for(con, ticker, mtype):
    """Live margin (op or gross) for a ticker: FY first, else TTM. Returns (text, value)."""
    f = latest_financials(con, ticker)
    m = market(con, ticker)
    key = "operating_margin" if mtype == "om" else "gross_margin"
    val = None
    if f and f[key] is not None:
        val = f[key]
    elif m and m[key] is not None:
        val = m[key]
    label = "op" if mtype == "om" else "GM"
    co = con.execute("SELECT name FROM companies WHERE ticker=?", (ticker,)).fetchone()
    nm = co["name"].split()[0] if co else ticker
    return (f"{nm} {pct(val)} {label}" if val is not None else nm), val


def render_connect(con):
    c = N.CONNECT
    obs = "".join(f"<li>{esc_html_keep(o)}</li>" for o in c["observations"])
    flow_rows = "".join(
        f'<tr><td><b>{esc(step)}</b></td><td>{esc(who)}</td><td class="seg">{esc(ex)}</td></tr>'
        for step, who, ex in c["money_flow"])
    flow = (f'<div class="tablewrap"><table class="comp" style="min-width:720px">'
            f'<thead><tr><th>Step</th><th>Who pays whom</th><th>Example flow</th></tr></thead>'
            f'<tbody>{flow_rows}</tbody></table></div>')
    vc_rows = ""
    for label, wallet, tk, mtype, pp, take in c["value_capture"]:
        mtext, mval = margin_for(con, tk, mtype)
        vc_rows += (f'<tr><td><b>{esc(label)}</b></td><td class="num">{esc(wallet)}</td>'
                    f'<td class="num {cls_margin(mval)}">{esc(mtext)}</td>'
                    f'<td class="num">{esc(pp)}</td><td class="seg">{esc_html_keep(take)}</td></tr>')
    vc = (f'<div class="tablewrap"><table class="comp" style="min-width:820px">'
          f'<thead><tr><th>Layer</th><th class="num">Wallet share</th>'
          f'<th class="num">Representative margin (live)</th><th class="num">Pricing power</th>'
          f'<th>What it tells us</th></tr></thead><tbody>{vc_rows}</tbody></table></div>')
    return f'''<section id="connect"><h2>3 · How the Layers Connect &amp; Who Captures Value</h2>
      <p>{esc_html_keep(c["intro"])}</p>
      <h3>3.1 The money flow — a capex dollar’s journey down the stack</h3>
      {flow}
      <h3>3.2 Value capture — who keeps the most of each capex dollar</h3>
      <p>{esc_html_keep(c["value_capture_intro"])}</p>
      {vc}
      <h3>3.3 What I take away from this</h3>
      <ul class="obs">{obs}</ul></section>'''


def render_risks():
    items = "".join(f'<div class="risk"><h4>{esc(t)}</h4><p>{esc_html_keep(d)}</p></div>'
                    for t, d in N.RISKS)
    return f'<section id="risks"><h2>5 · Key Risks &amp; Debates</h2><div class="risks">{items}</div></section>'


def render_deal_web():
    d = N.DEAL_WEB
    def stack(title, rows):
        lis = "".join(f"<li><b>{esc(c)}</b> — {esc_html_keep(t)}</li>" for c, t in rows)
        return f'<div class="stack"><h4>{esc(title)}</h4><ul>{lis}</ul></div>'
    return f'''<section id="dealweb"><h2>5 · The AI Deal Web</h2>
      <p>{esc_html_keep(d["intro"])}</p>
      <div style="margin:1.5rem 0 2rem;">
        <a href="ai_deal_network_layered.html" target="_blank"
           style="display:inline-flex;align-items:center;gap:0.6rem;background:#2563eb;color:#fff;font-weight:700;font-size:0.95rem;padding:0.75rem 1.4rem;border-radius:8px;text-decoration:none;box-shadow:0 2px 8px rgba(37,99,235,0.35);transition:background 0.15s;">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          Launch Interactive Deal Network Map
        </a>
        <span style="margin-left:1rem;font-size:0.82rem;color:#6b7280;">Opens in a new tab — explore deal flows across all 11 layers</span>
      </div>
      <div class="stacks">{stack("OpenAI's deal stack", d["openai_stack"])}{stack("Anthropic's deal stack", d["anthropic_stack"])}</div>
      <div class="callout"><h4>NVIDIA — the "AI banker"</h4><p>{esc_html_keep(d["nvidia_portfolio_note"])}</p></div>
      <div class="callout warn"><h4>Circular financing</h4><p>{esc_html_keep(d["circular_note"])}</p></div></section>'''


def render_layer_head(lc, layer):
    """Two-column opener: left = 3 info cards (What it does / Who pays whom /
    Key Metrics to Track), right = Analyst's Take + stance."""
    mf = N.MARGIN_FOCUS.get(layer) if hasattr(N, "MARGIN_FOCUS") else None
    margin_line = ""
    if mf:
        margin_line = (f'<div class="metricmargin"><span class="mmtag">Margin that matters</span>'
                       f'{esc_html_keep(mf[1])}</div>')
    vf = N.VALUATION_FOCUS.get(layer) if hasattr(N, "VALUATION_FOCUS") else None
    val_line = ""
    if vf:
        val_line = (f'<div class="metricval"><span class="mvtag">Valuation lens that matters</span>'
                    f'{esc_html_keep(vf)}</div>')
    left = (
        f'<div class="infocard"><h4>What this layer does</h4>'
        f'<p>{esc_html_keep(lc["what_it_does"])}</p></div>'
        f'<div class="infocard"><h4>Who pays whom</h4>'
        f'<p>{esc_html_keep(lc["who_pays_whom"])}</p></div>'
        f'<div class="infocard"><h4>Key Metrics to Track</h4>'
        f'<p>{esc_html_keep(lc["how_to_analyze"])}</p>{margin_line}{val_line}</div>'
    )
    stance = (f'<div class="stance"><span class="stag">My stance</span>'
              f'{esc_html_keep(lc["stance"])}</div>') if lc.get("stance") else ""
    take = ""
    if lc.get("analyst_take"):
        take = (f'<div class="take"><h4>Analyst’s Take</h4>'
                f'<p>{esc_html_keep(lc["analyst_take"])}</p>{stance}</div>')
    kr = N.KEY_RISKS.get(layer) if hasattr(N, "KEY_RISKS") else None
    risk = ""
    if kr:
        risk = (f'<div class="keyrisk"><h4>Key risk</h4>'
                f'<p>{esc_html_keep(kr)}</p></div>')
    return (f'<div class="layerhead"><div class="lhleft">{left}</div>'
            f'<div class="lhright">{take}{risk}</div></div>')


def render_layer_section(con, layer_row):
    layer, name = layer_row["layer"], layer_row["name"]
    lc = N.LAYER_CONTENT.get(layer)
    if not lc:
        return ""
    num = layer[1:]
    title = f"Layer {num} — {esc(name)}"
    mf = N.MARGIN_FOCUS.get(layer) if hasattr(N, "MARGIN_FOCUS") else None
    margin_key = mf[0] if mf else None
    parts = [f'<section id="{layer}" class="layer"><h2>{title}</h2>']
    parts.append(render_layer_head(lc, layer))
    parts.append(render_block_three(lc))
    # charts: layer's own + v12 extras
    charts = list(lc.get("charts") or [])
    if hasattr(N, "EXTRA_CHARTS"):
        charts += N.EXTRA_CHARTS.get(layer, [])
    parts.append(render_charts(charts))
    # Sub-segment cards only where no chart covers the breakdown (user decision).
    if layer in ("L10", "L7", "L0"):
        parts.append(render_subsegments(lc.get("sub_segments")))
    parts.append(render_extra_table(layer))
    if layer == "L4":
        parts.append(render_gpu_cpu_asic())
    parts.append(render_layer_table(con, layer, margin_key))
    parts.append(render_deals_detail(lc.get("deals_detail")))
    parts.append(render_glossary(lc.get("glossary")))
    parts.append("</section>")
    return "".join(parts)


# layer order from the seed
def load_layers():
    import json
    data = json.loads((ROOT / "data" / "layers_seed.json").read_text())
    return sorted(data["layers"], key=lambda x: -x["order"])


N_LAYERS = load_layers()


def build():
    con = connect()
    snap = con.execute("SELECT MAX(as_of) FROM market_data").fetchone()[0]
    nav = "".join(f'<a href="#{L["layer"]}">L{L["layer"][1:]}</a>' for L in N_LAYERS)
    whatsnew = "".join(f"<li>{esc_html_keep(x)}</li>" for x in N.META["whats_new"])

    # exec summary 11-layer table
    ov_rows = ""
    for L in N_LAYERS:
        cnt = con.execute("SELECT COUNT(*) FROM company_layer WHERE layer=?", (L["layer"],)).fetchone()[0]
        ov_rows += (f'<tr><td class="lcode"><a href="#{L["layer"]}">L{L["layer"][1:]}</a></td>'
                    f'<td>{esc(L["name"])}</td><td class="num">{cnt}</td></tr>')

    layer_sections = "".join(render_layer_section(con, L) for L in N_LAYERS)

    # Assemble the citable body first, then run one global citation pass so footnote
    # numbers run in document order, then append the References section.
    body = f'''
  <section id="summary">
    <div class="whatsnew"><h3>What’s new in v13</h3><ul>{whatsnew}</ul></div>
    <h2>1 · Executive Summary</h2>
    <p>This is my map of the AI supply chain, eleven layers deep — from the apps people pay for (L10)
    down to the electricity that powers it all (L0). Each layer opens with what it does, then <b>my
    Analyst’s Take and investment stance</b>, an expanded Bottleneck / Market-Size / Value-Added
    analysis (now showing each layer’s slice of the $725B capex funnel), a live comp table for every
    public name, and the key deals. Every headline figure carries a clickable source footnote.</p>
    <table class="overview"><thead><tr><th>Layer</th><th>Function</th><th class="num">Names</th></tr></thead>
      <tbody>{ov_rows}</tbody></table>
    <p class="note">{esc_html_keep(N.META["data_note"])}</p>
  </section>
  {render_capex(con)}
  {render_connect(con)}
  <section id="layers-intro"><h2>4 · The Supply Chain — Layer by Layer</h2>
    <p class="note">Each table is horizontally scrollable. Margins use the latest fiscal year (TTM
    where FY is stale). P/S = market cap ÷ TTM revenue. Market cap converted to USD. “—” = not
    available / not meaningful.</p></section>
  {layer_sections}
  {render_deal_web()}'''

    body, cite_order = process_citations(body)
    references = render_references(cite_order)

    html_doc = f'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(N.META["title"])} — {esc(N.META["subtitle"])}</title>
<style>{CSS}</style></head><body>
<header class="hero">
  <div class="wrap">
    <div class="kicker">{esc(N.META["tagline"])}</div>
    <h1>{esc(N.META["title"])}</h1>
    <div class="subtitle">{esc(N.META["subtitle"])} · Coverage {esc(N.META["coverage_date"])}</div>
    <div class="snap">Market data snapshot: <b>{esc(snap)}</b> · refresh with <code>3_refresh_market.py</code></div>
  </div>
</header>
<nav class="topnav"><div class="wrap">
  <a href="#summary">Summary</a><a href="#capex">Capex</a><a href="#connect">Value</a>
  <span class="sep">Layers</span>{nav}
  <a href="#dealweb">Deals</a><a href="#references">Sources</a>
</div></nav>
<main class="wrap">
  {body}
  {references}
  <footer><p><b>Disclaimer.</b> Information synthesis for educational and research purposes; not
    investment advice, and the Analyst’s Take sections are the author’s opinion. Valuation/margin
    data via Yahoo Finance (snapshot {esc(snap)}); segment, contract and backlog data from company
    filings and earnings releases. Figures are estimates and may contain errors — verify against
    primary sources before acting.</p>
    <p class="note">Generated {esc(datetime.now().strftime('%Y-%m-%d %H:%M'))} from data/aisc.db + data/narrative.py.</p></footer>
</main>
<script>{CHART_JS}</script>
</body></html>'''

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    con.close()
    size = OUT.stat().st_size
    print(f"Wrote {OUT} ({size/1024:.0f} KB)")


CSS = """
:root{--ink:#1a1f2b;--muted:#5b6577;--line:#e3e7ee;--bg:#fbfcfe;--card:#fff;
  --accent:#2547d0;--green:#0a8f5b;--amber:#b9770a;--red:#c0392b;--hi:#0a8f5b;}
*{box-sizing:border-box}
body{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
code{background:#eef1f7;padding:1px 5px;border-radius:4px;font-size:.86em}
.hero{background:linear-gradient(135deg,#0f1b3d,#23306b);color:#fff;padding:42px 0 34px}
.hero .kicker{text-transform:uppercase;letter-spacing:.14em;font-size:12px;color:#aebbe6}
.hero h1{margin:6px 0 4px;font-size:38px;letter-spacing:-.5px}
.hero .subtitle{color:#cdd6f2;font-size:16px}
.hero .snap{margin-top:12px;font-size:13px;color:#9fb0e0}
.hero code{background:rgba(255,255,255,.14);color:#dfe7ff}
.topnav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.95);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line)}
.topnav .wrap{display:flex;flex-wrap:wrap;gap:3px 12px;align-items:center;padding-top:9px;padding-bottom:9px;font-size:13px}
.topnav a{padding:3px 7px;border-radius:6px;color:var(--muted);font-weight:600}
.topnav a:hover{background:#eef1f7;color:var(--accent);text-decoration:none}
.topnav .sep{color:#b3bccd;font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-left:6px}
main{padding:8px 0 60px}
h2{font-size:25px;margin:42px 0 10px;padding-top:10px;letter-spacing:-.3px}
h3{font-size:18px;margin:22px 0 8px}
h4{font-size:14px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
section{scroll-margin-top:58px}
.layer{border-top:1px solid var(--line);margin-top:26px}
.lead{font-size:16px}
.who,.how{background:#f3f6fc;border-left:3px solid var(--accent);padding:9px 13px;border-radius:0 7px 7px 0;font-size:14.5px}
.note{color:var(--muted);font-size:13px}
.whatsnew{background:#eff8f2;border:1px solid #cfe9d9;border-radius:11px;padding:14px 18px;margin:16px 0}
.whatsnew h3{margin:0 0 6px;color:var(--green)}
.whatsnew ul{margin:0;padding-left:18px}.whatsnew li{margin:3px 0;font-size:14px}
/* three-up block */
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0}
.three .cell{border:1px solid var(--line);border-radius:11px;padding:13px 15px;background:var(--card)}
.three .bn{background:#fff7f4;border-color:#f3d9cf}
.three .ms{background:#f4f8ff;border-color:#d6e2f7}
.three .va{background:#f3faf5;border-color:#cfe9d9}
.three ul{margin:0;padding-left:17px}.three li{margin:5px 0;font-size:13.5px}
.sevtag{font-size:10.5px;padding:2px 7px;border-radius:20px;color:#fff;letter-spacing:.04em}
.sev-extreme{background:var(--red)}.sev-high{background:#e06a1a}.sev-med{background:var(--amber)}.sev-low{background:var(--green)}
.subseg ul{columns:2;column-gap:26px;padding-left:18px;margin:6px 0}.subseg li{margin:3px 0;font-size:13.5px}
/* tables */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:11px;margin:14px 0;background:var(--card)}
table.comp{border-collapse:collapse;width:100%;font-size:13px;min-width:1080px}
table.comp th,table.comp td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.comp thead th{position:sticky;top:0;background:#f4f6fb;z-index:3;font-size:11px;text-transform:uppercase;
  letter-spacing:.03em;color:var(--muted);border-bottom:2px solid #dde3ee}
table.comp td.tk{font-weight:700;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;white-space:nowrap;
  position:sticky;left:0;background:var(--card);z-index:2}
table.comp thead th:first-child{position:sticky;left:0;z-index:4}
td.co{min-width:130px;font-weight:600}
td.seg{min-width:300px;max-width:380px;color:#3a4254;font-size:12.5px;line-height:1.45}
td.bk{min-width:160px;max-width:220px;font-size:12px;color:#3a4254}
td.num{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums}
td .sub{display:block;font-size:10.5px;color:#9aa3b4;font-weight:400}
.num.hi{color:var(--green);font-weight:600}.num.mid{color:#2c7a4d}.num.lo{color:#6a7280}
.num.neg{color:var(--red)}
tr.subhdr td{background:#eef2fa;font-weight:700;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;
  color:#34406b;position:sticky;left:0}
.badge{font-size:9.5px;padding:1px 6px;border-radius:20px;vertical-align:middle}
.badge.pure{background:#e3f0ff;color:#2153c7;border:1px solid #c4dbff}
td.priv{color:var(--muted);font-style:italic}
/* callouts, deals, glossary */
.callout{background:#f4f8ff;border:1px solid #d6e2f7;border-radius:11px;padding:14px 18px;margin:16px 0}
.callout.warn{background:#fff7f4;border-color:#f3d9cf}
.callout h4{color:var(--accent)}.callout.warn h4{color:var(--red)}
.deals{margin:14px 0}.deals p{font-size:14px;margin:8px 0;padding-left:13px;border-left:2px solid var(--line)}
.feature{background:#0f1b3d;color:#e8edff;border-radius:13px;padding:18px 20px;margin:18px 0}
.feature h4{color:#aebbe6}.feature p{font-size:14px}.feature b{color:#fff}
.chipcards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0}
.chipcard{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:13px}
.chipcard h5{margin:0 0 2px;font-size:15px;color:#fff}.chipcard .tagline{font-size:11.5px;color:#9fb0e0;margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.chipcard p{font-size:12.5px;line-height:1.5}.chipcard .val{color:#bfe9d2}
.uses ul{margin:6px 0;padding-left:18px}.uses li{font-size:13.5px;margin:3px 0}
.gloss{margin:12px 0;background:#f7f9fc;border:1px solid var(--line);border-radius:9px;padding:6px 14px}
.gloss summary{cursor:pointer;font-weight:600;color:var(--accent);font-size:13px;padding:5px 0}
.gl{font-size:13px;padding:5px 0;border-top:1px solid var(--line);color:#3a4254}
.obs li{margin:7px 0}
table.overview{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
table.overview th,table.overview td{padding:7px 11px;border-bottom:1px solid var(--line);text-align:left}
table.overview .lcode{font-weight:700;font-family:ui-monospace,monospace}
table.overview .num,table.overview th.num{text-align:right}
.risks{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.risk{border:1px solid var(--line);border-radius:10px;padding:12px 15px;background:var(--card)}
.risk h4{color:var(--red)}.risk p{font-size:13.5px;margin:0}
.stacks{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:12px 0}
.stack{border:1px solid var(--line);border-radius:10px;padding:12px 15px;background:var(--card)}
.stack ul{margin:6px 0;padding-left:17px}.stack li{font-size:13px;margin:5px 0}
footer{margin-top:48px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:12.5px}
/* Analyst's Take + stance */
.take{background:linear-gradient(135deg,#f4f7ff,#eef3ff);border:1px solid #d3defa;border-left:4px solid var(--accent);
  border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
.take h4{color:var(--accent);margin-bottom:6px}
.take p{font-size:14.5px;margin:0}
.stance{margin-top:10px;font-size:13.5px;font-weight:600;color:#1c2c5e;background:#fff;border:1px solid #d3defa;
  border-radius:8px;padding:8px 12px}
.stance .stag{display:inline-block;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;
  color:#fff;background:var(--accent);padding:2px 8px;border-radius:20px;margin-right:8px;vertical-align:middle}
/* per-layer key risk (red) */
.keyrisk{background:#fff6f4;border:1px solid #f3d9cf;border-left:4px solid var(--red);
  border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0}
.keyrisk h4{color:var(--red);margin-bottom:6px}
.keyrisk p{font-size:13.5px;margin:0;color:#3a4254}
/* capex slice inside Market Size cell */
.capexslice{background:#fff;border:1px dashed #b9c8ec;border-radius:8px;padding:8px 10px;margin:0 0 9px;font-size:12.5px;color:#243a73}
.capexslice .cstag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:#5670c4;margin-bottom:3px}
/* citations */
sup.cite{font-size:10px;line-height:0;margin-left:1px}
sup.cite a{color:var(--accent);font-weight:700;text-decoration:none}
sup.cite a:hover{text-decoration:underline}
.src{color:var(--muted);font-size:12px;font-style:italic;margin:6px 0}
/* references */
.refs{list-style:none;margin:14px 0;padding:0;counter-reset:none}
.refs li{display:flex;gap:10px;padding:8px 0;border-top:1px solid var(--line);font-size:13px}
.refs li:target{background:#fff7e6;border-radius:6px;padding:8px}
.refs .rnum{font-weight:700;color:var(--accent);min-width:34px}
.refs .rbody{color:#3a4254}
/* charts */
.charts{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0}
.chart{margin:0;border:1px solid var(--line);border-radius:12px;padding:13px 15px;background:var(--card)}
.chart figcaption{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:10px}
.chartbody{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.chartviz{flex:0 0 auto}
.donut{width:150px;height:150px}
.bars{width:100%;max-width:440px;height:auto}
.bars .barlbl{font-size:11px;fill:#3a4254}
.bars .barval{font-size:11px;fill:var(--muted);font-variant-numeric:tabular-nums}
.stackcol{width:100%;max-width:460px;height:auto}
.stackcol .coltot{font-size:10.5px;fill:var(--ink);font-weight:700}
.stackcol .collbl{font-size:11px;fill:var(--muted)}
/* interactive charts: tooltip + hover highlight + legend sync */
figure.chart [data-k]{cursor:pointer}
figure.chart svg [data-k]{transition:opacity .12s ease}
figure.chart.dim svg [data-k]{opacity:.32}
figure.chart.dim svg [data-k].hi{opacity:1;stroke:#1a1f2b;stroke-width:1.5}
figure.chart .legend tr[data-k]{transition:background .12s}
figure.chart .legend tr[data-k].hi{background:#eef2fb}
.charttip{position:fixed;z-index:9999;background:#1a1f2b;color:#fff;font-size:12px;font-weight:600;
  padding:5px 9px;border-radius:6px;pointer-events:none;box-shadow:0 3px 12px rgba(0,0,0,.28);
  max-width:280px;display:none}
.legend{border-collapse:collapse;flex:1 1 240px;font-size:12px}
.legend td{padding:3px 6px;border-bottom:1px solid #f0f2f7;vertical-align:top}
.legend td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}
.legend td.cnote{color:var(--muted);font-size:11px}
.legend .dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:middle}
/* ---- v12: two-column layer head + info cards ---- */
.layerhead{display:grid;grid-template-columns:1.05fr 0.95fr;gap:14px;margin:14px 0 4px;align-items:stretch}
.lhleft{display:flex;flex-direction:column;gap:10px}
.lhright{display:flex}
.infocard{border:1px solid var(--line);border-radius:11px;padding:11px 14px;background:var(--card)}
.infocard h4{margin:0 0 5px}.infocard p{margin:0;font-size:13.5px;line-height:1.5}
.metricmargin{margin-top:9px;background:#f7faf8;border:1px solid #d7e7df;border-radius:8px;padding:7px 10px;font-size:12.5px;color:#1f5740}
.metricmargin .mmtag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:#0a8f5b;margin-bottom:2px}
.metricval{margin-top:7px;background:#f4f7fe;border:1px solid #d3defa;border-radius:8px;padding:7px 10px;font-size:12.5px;color:#27407e}
.metricval .mvtag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:#2547d0;margin-bottom:2px}
.lhright .take{margin:0;width:100%;display:flex;flex-direction:column;justify-content:center}
/* ---- sub-segment cards ---- */
.subseg h4{margin:0 0 8px}
.sscards{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.sscard{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--card);font-size:12.5px;line-height:1.45}
.sscard .sshead{font-weight:700;color:#34406b;margin-bottom:3px}
.sscard .ssbody{color:#3a4254}
/* ---- AI rev% cell + margin focus highlight ---- */
td.ai{min-width:120px;max-width:150px;font-size:12px;font-weight:600;color:#1c2c5e;white-space:normal}
table.comp th.mfocus{background:#eaf2ff;color:#1c2c5e;border-bottom-color:#9bb8ee}
table.comp td.num.mfocus{background:#f3f8ff;font-weight:700;box-shadow:inset 2px 0 0 #b9c8ec,inset -2px 0 0 #b9c8ec}
/* ---- extra fact table (TSMC) ---- */
.xtable{margin:16px 0}.xtable h4{margin:0 0 8px}
table.comp.facts{min-width:520px}table.comp.facts td.lbl{font-weight:600;color:#34406b}
/* ---- GPU/CPU/ASIC feature box: light theme (was dark navy) ---- */
.feature{background:#f6f8fe;color:var(--ink);border:1px solid #d6e0f5;border-radius:13px;padding:18px 20px;margin:18px 0}
.feature h4{color:var(--accent)}.feature .flead{font-size:14.5px;color:#3a4254}.feature b{color:var(--ink)}
.feature .chipcard{background:#fff;border:1px solid var(--line);border-radius:10px;padding:13px}
.feature .chipcard h5{margin:0 0 2px;font-size:15px}
.feature .chipcard .tagline{font-size:11.5px;color:var(--muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.feature .chipcard p{font-size:12.5px;line-height:1.5;color:#3a4254}.feature .chipcard .val{color:#1f5740}
.feature .replace{background:#fff;border:1px solid var(--line);border-radius:10px;padding:11px 14px;margin:12px 0;font-size:13.5px}
.feature .uses ul{margin:6px 0;padding-left:18px}.feature .uses li{font-size:13.5px;margin:3px 0;color:#3a4254}
@media(max-width:900px){.layerhead{grid-template-columns:1fr}.sscards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:820px){.three,.chipcards,.risks,.stacks,.charts,.sscards{grid-template-columns:1fr}.subseg ul{columns:1}
  .hero h1{font-size:29px}.chartbody{flex-direction:column;align-items:flex-start}}
"""


# Vanilla-JS chart interactivity (no framework). For each chart figure: hovering any
# SVG segment/bar OR its legend row shows a styled tooltip, highlights the matching
# data series, and dims the rest. Legend <-> chart sync is by the shared data-k key.
CHART_JS = """
(function(){
  var tip=document.createElement('div');tip.className='charttip';document.body.appendChild(tip);
  function show(t,x,y){tip.textContent=t;tip.style.display='block';tip.style.left=(x+14)+'px';tip.style.top=(y+14)+'px';}
  function hide(){tip.style.display='none';}
  document.querySelectorAll('figure.chart').forEach(function(fig){
    var els=fig.querySelectorAll('[data-k]');
    function setHi(k,on){
      fig.classList.toggle('dim',on);
      els.forEach(function(e){e.classList.toggle('hi',on&&e.getAttribute('data-k')===k);});
    }
    els.forEach(function(el){
      var k=el.getAttribute('data-k'),t=el.getAttribute('data-tip')||'';
      el.addEventListener('mouseenter',function(ev){setHi(k,true);if(t)show(t,ev.clientX,ev.clientY);});
      el.addEventListener('mousemove',function(ev){if(t)show(t,ev.clientX,ev.clientY);});
      el.addEventListener('mouseleave',function(){setHi(k,false);hide();});
    });
  });
})();
"""


if __name__ == "__main__":
    build()
