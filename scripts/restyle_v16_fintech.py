#!/usr/bin/env python3
"""v16: Modern Fintech theme (light + depth) on the real report.

Reuses the v14 light stylesheet (targets every real-report class) and overlays
fintech craft: soft elevation shadows, rounded cards, richer teal accent, navy
masthead/exhibit headers, bright-teal exhibit labels. No serif (Inter). Remaps
inline chart colors from the dark set back to a vivid light-paper palette.
"""
import re, pathlib

SRC = pathlib.Path("report/ai_supply_chain_report.html")
V14 = pathlib.Path("scripts/restyle_v14_theme.py")

css = re.search(r'CSS = r"""(.*?)"""', V14.read_text(), re.DOTALL).group(1)

# ---- Modern Fintech overlay (later rules win the cascade) ----
css += """
/* ===== Modern Fintech overlay (light + depth) ===== */
:root{
  --paper:#eef1f6;--surface:#ffffff;--surface-2:#f4f6fa;
  --ink:#0f172a;--ink-2:#5b6678;--ink-3:#94a0b3;
  --rule:#e7ebf2;--rule-2:#dfe4ee;
  --tiffany:#0e9f93;--tiffany-ink:#0b7d73;--tiffany-bg:#e3f6f3;
  --up:#0b9a5b;--down:#dc2b2b;--amber:#d97706;
  --chrome:#0f172a;--chrome-2:#16203a;--chrome-ink:#eef2f8;--chrome-ink-2:#9fb0c7;--chrome-line:#26314d;
  --shadow:0 1px 2px rgba(16,24,40,.06),0 4px 14px rgba(16,24,40,.05);
}
html,body{background:var(--paper)}
.topnav{background:rgba(15,23,42,.97)}
.readprog{background:var(--tiffany)}
/* depth + rounded on card-like containers */
.infocard,.three .cell,.callout,.feature,.chipcard,.risk,.stack,.take,.keyrisk,.sscard,.gloss,.exhibit,.tablewrap,.lprofile,.whatsnew,.who,.how{border-radius:12px;box-shadow:var(--shadow)}
.ratingbox{border-radius:12px;box-shadow:0 12px 34px rgba(2,8,23,.30)}
.exhibit,.lprofile,.tablewrap{overflow:hidden}
.metricmargin,.metricval,.capexslice,.stance,.chip{border-radius:9px}
.badge,.sevtag,.stance .stag,.badge.pure{border-radius:20px}
/* soften the section rule */
h2{border-top:1px solid var(--rule);padding-top:16px}
.sechead{}
/* bright teal exhibit labels on navy headers */
.exhibit>.ex-h .lbl,.tablewrap>.ex-h .lbl,.lprofile>.ph .pn,.hero .kicker{color:#5fe3d6}
.chart figcaption::before{color:#5fe3d6}
.ratingbox .rb-call b{color:#5fe3d6}
/* active rail item as a soft pill */
.tocrail a.active{background:var(--tiffany-bg);border-radius:8px;padding:2px 8px;margin-left:-8px}
/* tiffany-tinted metric chip backgrounds for a touch of color */
.metricval{background:var(--tiffany-bg)}
.take{border-radius:12px}
/* display typeface: Space Grotesk on headlines/section titles/captions */
:root{--display:'Space Grotesk',var(--font-sans)}
.hero h1,h2,h3,.exhibit>.ex-h .cap,.tablewrap>.ex-h .cap,.chart figcaption,.lprofile>.ph .pn,.sscard .sshead,.chipcard h5{font-family:var(--display);font-weight:700;letter-spacing:-.01em}
.hero h1{font-weight:700}
"""

html = SRC.read_text()
html, n = re.subn(r"<style>.*?</style>", lambda _: "<style>\n"+css+"</style>", html, count=1, flags=re.DOTALL)
assert n == 1

# revert font link to Inter + JetBrains Mono (drop Fraunces)
html = re.sub(
    r'<link href="https://fonts\.googleapis\.com/css2\?family=Fraunces[^"]*" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
    html, count=1)

# remap inline chart palette: current dark set -> vivid light-paper palette
head, sep, body = html.partition("</style>")
PAL = {
    "#4c8dff":"#3b82f6","#00d17a":"#0a9b5e","#e0a23c":"#d97706","#ff4d4d":"#dc2b2b",
    "#a78bfa":"#7c5cf0","#2bc4d6":"#0891b2","#f06fb0":"#db2777","#8bc34a":"#65a30d","#c08457":"#b45309",
    "#0e0e12":"#ffffff",
    "#ececf1":"#0f172a","#9c9ca6":"#5b6678","#66666f":"#94a0b3",
}
pat = re.compile("|".join(re.escape(k) for k in PAL), re.IGNORECASE)
body = pat.sub(lambda m: PAL[m.group(0).lower()], body)
html = head + sep + body

SRC.write_text(html)
print("v16 Fintech applied; bytes:", len(html))
