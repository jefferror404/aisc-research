#!/usr/bin/env python3
"""Restyle report/ai_supply_chain_report.html to the kaamos polar-night design system.

- Replaces the <style> block with dark-theme CSS (kaamos tokens).
- Injects Inter + JetBrains Mono font links.
- Remaps inline categorical chart colors + donut centers to a dark-friendly palette.

Idempotent-ish: re-run safe because it keys off <style>...</style> and the font marker.
"""
import re
import pathlib

SRC = pathlib.Path("report/ai_supply_chain_report.html")
html = SRC.read_text(encoding="utf-8")

# ---------------------------------------------------------------- new stylesheet
NEW_CSS = r""":root{
  /* Kaamos polar-night tokens — source of truth: kaamos/docs/DESIGN.md */
  --bg-0:#07070a;--bg-1:#0e0e12;--bg-2:#16161c;--bg-3:#1d1d24;
  --text-1:#ececf1;--text-2:#9c9ca6;--text-3:#66666f;
  --border-1:#1d1d25;--border-2:#28282f;
  --tiffany:#0ABAB5;--tiffany-dim:#088a86;--tiffany-bg:rgba(10,186,181,.08);
  --up:#00D17A;--down:#FF4D4D;--neutral:#807c78;--amber:#e0a23c;
  /* legacy aliases so existing selectors read naturally */
  --ink:var(--text-1);--muted:var(--text-2);--line:var(--border-1);
  --bg:var(--bg-0);--card:var(--bg-1);--accent:var(--tiffany);
  --green:var(--up);--red:var(--down);--hi:var(--up);
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --font-mono:'JetBrains Mono',ui-monospace,Menlo,monospace;}
*{box-sizing:border-box}
html,body{margin:0;font:15px/1.6 var(--font-sans);color:var(--text-1);background:var(--bg-0);
  font-feature-settings:'cv11','ss01';-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
a{color:var(--tiffany);text-decoration:none}a:hover{color:var(--tiffany-dim);text-decoration:underline}
code{background:var(--bg-2);color:var(--text-1);padding:1px 5px;border-radius:2px;font-size:.86em;font-family:var(--font-mono)}
/* hero — solid panel, no gradient (anti-slop), tiffany kicker */
.hero{background:var(--bg-1);border-bottom:1px solid var(--border-1);color:var(--text-1);padding:42px 0 34px}
.hero .kicker{text-transform:uppercase;letter-spacing:.14em;font-size:12px;color:var(--tiffany);font-weight:600}
.hero h1{margin:6px 0 4px;font-size:38px;letter-spacing:-.5px;color:var(--text-1)}
.hero .subtitle{color:var(--text-2);font-size:16px}
.hero .snap{margin-top:12px;font-size:13px;color:var(--text-3)}
.hero code{background:var(--bg-2);color:var(--text-1)}
.topnav{position:sticky;top:0;z-index:50;background:rgba(14,14,18,.92);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--border-1)}
.topnav .wrap{display:flex;flex-wrap:wrap;gap:3px 12px;align-items:center;padding-top:9px;padding-bottom:9px;font-size:13px}
.topnav a{padding:3px 7px;border-radius:2px;color:var(--text-2);font-weight:600}
.topnav a:hover{background:var(--tiffany-bg);color:var(--tiffany);text-decoration:none}
.topnav .sep{color:var(--text-3);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-left:6px}
main{padding:8px 0 60px}
h2{font-size:25px;margin:42px 0 10px;padding-top:10px;letter-spacing:-.3px;color:var(--text-1)}
h3{font-size:18px;margin:22px 0 8px;color:var(--text-1)}
h4{font-size:14px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-2)}
section{scroll-margin-top:58px}
.layer{border-top:1px solid var(--border-1);margin-top:26px}
.lead{font-size:16px;color:var(--text-1)}
.who,.how{background:var(--bg-2);border-left:3px solid var(--tiffany);padding:9px 13px;border-radius:0 2px 2px 0;font-size:14.5px;color:var(--text-1)}
.note{color:var(--text-2);font-size:13px}
.whatsnew{background:var(--bg-1);border:1px solid var(--border-1);border-left:3px solid var(--up);border-radius:2px;padding:14px 18px;margin:16px 0}
.whatsnew h3{margin:0 0 6px;color:var(--up)}
.whatsnew ul{margin:0;padding-left:18px}.whatsnew li{margin:3px 0;font-size:14px;color:var(--text-1)}
/* three-up block — differentiated by left-border accent, not slop fills */
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0}
.three .cell{border:1px solid var(--border-1);border-radius:2px;padding:13px 15px;background:var(--bg-1)}
.three .bn{border-left:3px solid var(--down)}
.three .ms{border-left:3px solid var(--tiffany)}
.three .va{border-left:3px solid var(--up)}
.three ul{margin:0;padding-left:17px}.three li{margin:5px 0;font-size:13.5px;color:var(--text-1)}
.sevtag{font-size:10.5px;padding:2px 7px;border-radius:2px;color:#07070a;letter-spacing:.04em;font-weight:600}
.sev-extreme{background:var(--down)}.sev-high{background:#e06a1a}.sev-med{background:var(--amber)}.sev-low{background:var(--up)}
.subseg ul{columns:2;column-gap:26px;padding-left:18px;margin:6px 0}.subseg li{margin:3px 0;font-size:13.5px;color:var(--text-1)}
/* tables */
.tablewrap{overflow-x:auto;border:1px solid var(--border-1);border-radius:2px;margin:14px 0;background:var(--bg-1)}
table.comp{border-collapse:collapse;width:100%;font-size:13px;min-width:1080px}
table.comp th,table.comp td{padding:8px 10px;border-bottom:1px solid var(--border-1);text-align:left;vertical-align:top}
table.comp thead th{position:sticky;top:0;background:var(--bg-2);z-index:3;font-size:11px;text-transform:uppercase;
  letter-spacing:.03em;color:var(--text-2);border-bottom:2px solid var(--border-2)}
table.comp td.tk{font-weight:700;font-family:var(--font-mono);font-size:12.5px;white-space:nowrap;
  position:sticky;left:0;background:var(--bg-1);z-index:2;color:var(--text-1)}
table.comp thead th:first-child{position:sticky;left:0;z-index:4}
td.co{min-width:130px;font-weight:600;color:var(--text-1)}
td.seg{min-width:300px;max-width:380px;color:var(--text-2);font-size:12.5px;line-height:1.45}
td.bk{min-width:160px;max-width:220px;font-size:12px;color:var(--text-2)}
td.num{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums;font-family:var(--font-mono);color:var(--text-1)}
td .sub{display:block;font-size:10.5px;color:var(--text-3);font-weight:400}
.num.hi{color:var(--up);font-weight:600}.num.mid{color:#3fae74}.num.lo{color:var(--text-2)}
.num.neg{color:var(--down)}
tr.subhdr td{background:var(--bg-2);font-weight:700;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--text-1);position:sticky;left:0}
.badge{font-size:9.5px;padding:1px 6px;border-radius:2px;vertical-align:middle}
.badge.pure{background:var(--tiffany-bg);color:var(--tiffany);border:1px solid var(--tiffany-dim)}
td.priv{color:var(--text-3);font-style:italic}
/* callouts, deals, glossary */
.callout{background:var(--bg-1);border:1px solid var(--border-1);border-left:3px solid var(--tiffany);border-radius:2px;padding:14px 18px;margin:16px 0}
.callout.warn{border-left-color:var(--down)}
.callout h4{color:var(--tiffany)}.callout.warn h4{color:var(--down)}
.deals{margin:14px 0}.deals p{font-size:14px;margin:8px 0;padding-left:13px;border-left:2px solid var(--border-1);color:var(--text-1)}
.chipcards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0}
.chipcard{background:var(--bg-2);border:1px solid var(--border-1);border-radius:2px;padding:13px}
.chipcard h5{margin:0 0 2px;font-size:15px;color:var(--text-1)}
.chipcard .tagline{font-size:11.5px;color:var(--text-2);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.chipcard p{font-size:12.5px;line-height:1.5;color:var(--text-2)}.chipcard .val{color:var(--up)}
.uses ul{margin:6px 0;padding-left:18px}.uses li{font-size:13.5px;margin:3px 0;color:var(--text-1)}
.gloss{margin:12px 0;background:var(--bg-1);border:1px solid var(--border-1);border-radius:2px;padding:6px 14px}
.gloss summary{cursor:pointer;font-weight:600;color:var(--tiffany);font-size:13px;padding:5px 0}
.gl{font-size:13px;padding:5px 0;border-top:1px solid var(--border-1);color:var(--text-2)}
.obs li{margin:7px 0}
table.overview{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
table.overview th,table.overview td{padding:7px 11px;border-bottom:1px solid var(--border-1);text-align:left;color:var(--text-1)}
table.overview th{color:var(--text-2);font-size:11px;text-transform:uppercase;letter-spacing:.03em}
table.overview .lcode{font-weight:700;font-family:var(--font-mono);color:var(--tiffany)}
table.overview .num,table.overview th.num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--font-mono)}
.risks{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.risk{border:1px solid var(--border-1);border-left:3px solid var(--down);border-radius:2px;padding:12px 15px;background:var(--bg-1)}
.risk h4{color:var(--down)}.risk p{font-size:13.5px;margin:0;color:var(--text-1)}
.stacks{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:12px 0}
.stack{border:1px solid var(--border-1);border-radius:2px;padding:12px 15px;background:var(--bg-1)}
.stack ul{margin:6px 0;padding-left:17px}.stack li{font-size:13px;margin:5px 0;color:var(--text-1)}
footer{margin-top:48px;padding-top:18px;border-top:1px solid var(--border-1);color:var(--text-3);font-size:12.5px}
/* Analyst's Take + stance */
.take{background:var(--bg-1);border:1px solid var(--border-1);border-left:3px solid var(--tiffany);
  border-radius:0 2px 2px 0;padding:14px 18px;margin:14px 0}
.take h4{color:var(--tiffany);margin-bottom:6px}
.take p{font-size:14.5px;margin:0;color:var(--text-1)}
.stance{margin-top:10px;font-size:13.5px;font-weight:600;color:var(--text-1);background:var(--bg-2);border:1px solid var(--border-1);
  border-radius:2px;padding:8px 12px}
.stance .stag{display:inline-block;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;
  color:#07070a;background:var(--tiffany);padding:2px 8px;border-radius:2px;margin-right:8px;vertical-align:middle}
/* per-layer key risk (red) */
.keyrisk{background:var(--bg-1);border:1px solid var(--border-1);border-left:3px solid var(--down);
  border-radius:0 2px 2px 0;padding:12px 16px;margin:12px 0}
.keyrisk h4{color:var(--down);margin-bottom:6px}
.keyrisk p{font-size:13.5px;margin:0;color:var(--text-2)}
/* capex slice inside Market Size cell */
.capexslice{background:var(--bg-2);border:1px dashed var(--border-2);border-radius:2px;padding:8px 10px;margin:0 0 9px;font-size:12.5px;color:var(--text-1)}
.capexslice .cstag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:var(--tiffany);margin-bottom:3px}
/* citations */
sup.cite{font-size:10px;line-height:0;margin-left:1px}
sup.cite a{color:var(--tiffany);font-weight:700;text-decoration:none}
sup.cite a:hover{text-decoration:underline}
.src{color:var(--text-2);font-size:12px;font-style:italic;margin:6px 0}
/* references */
.refs{list-style:none;margin:14px 0;padding:0}
.refs li{display:flex;gap:10px;padding:8px 0;border-top:1px solid var(--border-1);font-size:13px;color:var(--text-2)}
.refs li:target{background:var(--tiffany-bg);border-radius:2px;padding:8px}
.refs .rnum{font-weight:700;color:var(--tiffany);min-width:34px;font-family:var(--font-mono)}
.refs .rbody{color:var(--text-2)}
/* charts */
.charts{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0}
.chart{margin:0;border:1px solid var(--border-1);border-radius:2px;padding:13px 15px;background:var(--bg-1)}
.chart figcaption{font-size:13px;font-weight:700;color:var(--text-1);margin-bottom:10px}
.chartbody{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.chartviz{flex:0 0 auto}
.donut{width:150px;height:150px}
.bars{width:100%;max-width:440px;height:auto}
.bars .barlbl{font-size:11px;fill:var(--text-2)}
.bars .barval{font-size:11px;fill:var(--text-1);font-variant-numeric:tabular-nums}
.stackcol{width:100%;max-width:460px;height:auto}
.stackcol .coltot{font-size:10.5px;fill:var(--text-1);font-weight:700}
.stackcol .collbl{font-size:11px;fill:var(--text-2)}
/* interactive charts: tooltip + hover highlight + legend sync */
figure.chart [data-k]{cursor:pointer}
figure.chart svg [data-k]{transition:opacity .12s ease}
figure.chart.dim svg [data-k]{opacity:.32}
figure.chart.dim svg [data-k].hi{opacity:1;stroke:var(--text-1);stroke-width:1.5}
figure.chart .legend tr[data-k]{transition:background .12s}
figure.chart .legend tr[data-k].hi{background:var(--bg-3)}
.charttip{position:fixed;z-index:9999;background:var(--bg-3);color:var(--text-1);font-size:12px;font-weight:600;
  padding:5px 9px;border-radius:2px;pointer-events:none;border:1px solid var(--border-2);
  max-width:280px;display:none}
.legend{border-collapse:collapse;flex:1 1 240px;font-size:12px}
.legend td{padding:3px 6px;border-bottom:1px solid var(--border-1);vertical-align:top;color:var(--text-1)}
.legend td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap;font-family:var(--font-mono)}
.legend td.cnote{color:var(--text-2);font-size:11px}
.legend .dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:middle}
/* two-column layer head + info cards */
.layerhead{display:grid;grid-template-columns:1.05fr 0.95fr;gap:14px;margin:14px 0 4px;align-items:stretch}
.lhleft{display:flex;flex-direction:column;gap:10px}
.lhright{display:flex;flex-direction:column;gap:10px}
.infocard{border:1px solid var(--border-1);border-radius:2px;padding:11px 14px;background:var(--bg-1)}
.infocard h4{margin:0 0 5px}.infocard p{margin:0;font-size:13.5px;line-height:1.5;color:var(--text-1)}
.metricmargin{margin-top:9px;background:var(--bg-2);border:1px solid var(--border-1);border-left:3px solid var(--up);border-radius:2px;padding:7px 10px;font-size:12.5px;color:var(--text-1)}
.metricmargin .mmtag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:var(--up);margin-bottom:2px}
.metricval{margin-top:7px;background:var(--bg-2);border:1px solid var(--border-1);border-left:3px solid var(--tiffany);border-radius:2px;padding:7px 10px;font-size:12.5px;color:var(--text-1)}
.metricval .mvtag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:var(--tiffany);margin-bottom:2px}
.lhright .take{margin:0;flex:1}.lhright .keyrisk{margin:0}
/* sub-segment cards */
.subseg h4{margin:0 0 8px}
.sscards{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.sscard{border:1px solid var(--border-1);border-radius:2px;padding:10px 12px;background:var(--bg-1);font-size:12.5px;line-height:1.45}
.sscard .sshead{font-weight:700;color:var(--text-1);margin-bottom:3px}
.sscard .ssbody{color:var(--text-2)}
/* AI rev% cell + margin focus highlight */
td.ai{min-width:120px;max-width:150px;font-size:12px;font-weight:600;color:var(--text-1);white-space:normal}
table.comp th.mfocus{background:var(--tiffany-bg);color:var(--tiffany);border-bottom-color:var(--tiffany-dim)}
table.comp td.num.mfocus{background:var(--tiffany-bg);font-weight:700;box-shadow:inset 2px 0 0 var(--tiffany-dim),inset -2px 0 0 var(--tiffany-dim)}
/* extra fact table (TSMC) */
.xtable{margin:16px 0}.xtable h4{margin:0 0 8px}
table.comp.facts{min-width:520px}table.comp.facts td.lbl{font-weight:600;color:var(--text-1)}
/* GPU/CPU/ASIC feature box */
.feature{background:var(--bg-1);color:var(--text-1);border:1px solid var(--border-1);border-radius:2px;padding:18px 20px;margin:18px 0}
.feature h4{color:var(--tiffany)}.feature .flead{font-size:14.5px;color:var(--text-2)}.feature p{font-size:14px;color:var(--text-1)}.feature b{color:var(--text-1)}
.feature .chipcard{background:var(--bg-2);border:1px solid var(--border-1);border-radius:2px;padding:13px}
.feature .chipcard h5{margin:0 0 2px;font-size:15px;color:var(--text-1)}
.feature .chipcard .tagline{font-size:11.5px;color:var(--text-2);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.feature .chipcard p{font-size:12.5px;line-height:1.5;color:var(--text-2)}.feature .chipcard .val{color:var(--up)}
.feature .replace{background:var(--bg-2);border:1px solid var(--border-1);border-radius:2px;padding:11px 14px;margin:12px 0;font-size:13.5px;color:var(--text-1)}
.feature .uses ul{margin:6px 0;padding-left:18px}.feature .uses li{font-size:13.5px;margin:3px 0;color:var(--text-2)}
@media(max-width:900px){.layerhead{grid-template-columns:1fr}.sscards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:820px){.three,.chipcards,.risks,.stacks,.charts,.sscards{grid-template-columns:1fr}.subseg ul{columns:1}
  .hero h1{font-size:29px}.chartbody{flex-direction:column;align-items:flex-start}}
"""

# ---------------------------------------------------------------- 1. swap <style>
new_block = "<style>\n" + NEW_CSS + "</style>"
html, n = re.subn(r"<style>.*?</style>", lambda m: new_block, html, count=1, flags=re.DOTALL)
assert n == 1, f"expected 1 <style> block, replaced {n}"

# ---------------------------------------------------------------- 2. inject fonts
FONT_LINKS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
)
if "fonts.googleapis.com" not in html.split("<style>")[0]:
    html = html.replace("</title>", "</title>\n" + FONT_LINKS, 1)

# ---------------------------------------------------------------- 3. body color remap
head, sep, body = html.partition("</style>")

# donut center hole: white -> card bg
body = body.replace('fill="#fff"', 'fill="#0e0e12"')

# categorical chart palette + stray dark label fills -> dark-theme palette
PALETTE = {
    "#2547d0": "#4c8dff",  # blue
    "#0a8f5b": "#00D17A",  # green -> up
    "#b9770a": "#e0a23c",  # amber
    "#c0392b": "#FF4D4D",  # red -> down
    "#7c4dff": "#a78bfa",  # violet (single categorical, not a gradient)
    "#0aa2c0": "#2bc4d6",  # cyan
    "#d4499b": "#f06fb0",  # pink
    "#8a9a5b": "#8bc34a",  # olive
    "#a0522d": "#c08457",  # brown
    "#1f5740": "#00D17A",  # dark green text -> up
    # dark slate label fills -> light text tokens
    "#3a4254": "#9c9ca6",
    "#34406b": "#9c9ca6",
    "#1c2c5e": "#ececf1",
    "#1a1f2b": "#ececf1",
    "#5b6577": "#9c9ca6",
    "#6a7280": "#9c9ca6",
    "#243a73": "#9c9ca6",
    "#0f1b3d": "#0e0e12",
}
pat = re.compile("|".join(re.escape(k) for k in PALETTE), re.IGNORECASE)
body = pat.sub(lambda m: PALETTE[m.group(0).lower()], body)

html = head + sep + body

SRC.write_text(html, encoding="utf-8")
print("report restyled OK; bytes:", len(html))
