#!/usr/bin/env python3
"""v14 theme: convert the report to 'dark chrome + light paper' research-document theme.

Step 1 of the redesign (CSS + chart palette only; masthead/rail/exhibit structure
are applied separately). Replaces the <style> block with a light-paper stylesheet
covering every existing class, and re-tunes inline chart colors for the light surface.
"""
import re, pathlib

SRC = pathlib.Path("report/ai_supply_chain_report.html")
html = SRC.read_text(encoding="utf-8")

CSS = r""":root{
  /* dark chrome (masthead / topnav / panel + exhibit headers) */
  --chrome:#0e0e12;--chrome-2:#16161c;--chrome-ink:#ececf1;--chrome-ink-2:#9c9ca6;--chrome-line:#24242c;
  /* light paper */
  --paper:#f6f7f9;--surface:#ffffff;--surface-2:#eef1f5;
  --ink:#1a1f2b;--ink-2:#5b6577;--ink-3:#8a94a6;
  --rule:#dfe3ea;--rule-2:#c8cfda;
  /* accent + semantics tuned for light paper */
  --tiffany:#0ABAB5;--tiffany-ink:#067f7b;--tiffany-bg:#e6f7f6;
  --up:#0a8f5b;--down:#c0392b;--amber:#b9770a;
  /* aliases used by legacy selectors */
  --ink1:var(--ink);--muted:var(--ink-2);--line:var(--rule);--bg:var(--paper);--card:var(--surface);
  --accent:var(--tiffany-ink);--green:var(--up);--red:var(--down);--hi:var(--up);
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --font-mono:'JetBrains Mono',ui-monospace,Menlo,monospace;}
*{box-sizing:border-box}
html,body{margin:0;font:15px/1.62 var(--font-sans);color:var(--ink);background:var(--paper);
  font-feature-settings:'cv11','ss01';-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.wrap{max-width:1320px;margin:0 auto;padding:0 28px}
a{color:var(--tiffany-ink);text-decoration:none}a:hover{text-decoration:underline}
code{background:var(--surface-2);color:var(--ink);padding:1px 5px;border-radius:2px;font-size:.86em;font-family:var(--font-mono)}
b{color:#11161f}
/* ===== dark chrome: masthead ===== */
.hero{background:var(--chrome);color:var(--chrome-ink);border-bottom:2px solid var(--tiffany);padding:0}
.hero .wrap{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;padding-top:24px;padding-bottom:20px}
.hero .mhleft{min-width:0}
.hero .kicker{font-family:var(--font-mono);text-transform:uppercase;letter-spacing:.16em;font-size:11px;color:var(--tiffany)}
.hero h1{margin:6px 0 3px;font-size:30px;letter-spacing:-.4px;color:var(--chrome-ink);font-weight:700}
.hero .subtitle{color:var(--chrome-ink-2);font-size:14px}
.hero .snap{margin-top:9px;font-size:12px;color:var(--chrome-ink-2)}
.hero code{background:#22222a;color:#dfe7ff}
.ratingbox{flex:0 0 auto;border:1px solid var(--chrome-line);background:var(--chrome-2);min-width:240px;border-radius:2px;align-self:stretch}
.ratingbox .rb-h{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--chrome-ink-2);padding:7px 12px;border-bottom:1px solid var(--chrome-line)}
.ratingbox .rb-row{display:flex;justify-content:space-between;gap:14px;padding:5px 12px;font-size:12px}
.ratingbox .rb-row .k{color:var(--chrome-ink-2)}.ratingbox .rb-row .v{font-family:var(--font-mono);color:var(--chrome-ink)}
.ratingbox .rb-call{padding:8px 12px;border-top:1px solid var(--chrome-line);font-size:12px;color:var(--chrome-ink)}
.ratingbox .rb-call b{color:var(--tiffany)}
/* ===== dark chrome: sticky topnav ===== */
.topnav{position:sticky;top:0;z-index:50;background:rgba(14,14,18,.97);backdrop-filter:blur(8px);border-bottom:1px solid var(--chrome-line)}
.topnav .wrap{display:flex;flex-wrap:wrap;gap:3px 13px;align-items:center;padding-top:9px;padding-bottom:9px;font-size:12.5px}
.topnav a{padding:3px 7px;border-radius:2px;color:var(--chrome-ink-2);font-weight:600}
.topnav a:hover{background:#22222b;color:var(--chrome-ink);text-decoration:none}
.topnav a.active{background:var(--tiffany);color:#07070a}
.topnav .sep{color:#5b5b66;font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-left:6px}
.readprog{position:fixed;top:0;left:0;height:2px;background:var(--tiffany);width:0;z-index:60}
/* ===== layout: rail + content grid ===== */
main.wrap{display:grid;grid-template-columns:208px minmax(0,1fr);gap:36px;padding-top:10px;padding-bottom:60px;align-items:start}
.tocrail{position:sticky;top:54px;align-self:start;font-size:12.5px}
.tocrail .t-h{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--rule)}
.tocrail a{display:flex;gap:8px;padding:3px 0;color:var(--ink-2)}
.tocrail a:hover{color:var(--ink)}
.tocrail a.active{color:var(--tiffany-ink);font-weight:600}
.tocrail a .tn{font-family:var(--font-mono);color:var(--ink-3);min-width:24px}
.tocrail a.active .tn{color:var(--tiffany-ink)}
.doc{min-width:0;max-width:900px}
@media(max-width:1040px){main.wrap{grid-template-columns:1fr}.tocrail{display:none}}
/* ===== document typography ===== */
main{padding:0}
h2{font-size:23px;margin:38px 0 10px;padding-top:10px;letter-spacing:-.3px;color:var(--ink);border-top:2px solid var(--ink)}
h3{font-size:17px;margin:22px 0 8px;color:var(--ink)}
h4{font-size:13px;margin:0 0 7px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-2)}
section{scroll-margin-top:56px}
.layer{margin-top:30px}
.lead{font-size:16.5px;line-height:1.55;color:#2b3240}
.who,.how{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--tiffany);padding:9px 13px;border-radius:0 2px 2px 0;font-size:14px;color:#2b3240}
.note{color:var(--ink-2);font-size:13px}
.whatsnew{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--up);border-radius:2px;padding:14px 18px;margin:16px 0}
.whatsnew h3{margin:0 0 6px;color:var(--up)}
.whatsnew ul{margin:0;padding-left:18px}.whatsnew li{margin:3px 0;font-size:13.5px;color:#2b3240}
/* three-up */
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0}
.three .cell{border:1px solid var(--rule);border-radius:2px;padding:12px 14px;background:var(--surface)}
.three .bn{border-left:3px solid var(--down)}.three .ms{border-left:3px solid var(--tiffany)}.three .va{border-left:3px solid var(--up)}
.three ul{margin:0;padding-left:17px}.three li{margin:5px 0;font-size:13px;color:#2b3240}
.sevtag{font-size:10px;padding:2px 8px;border-radius:2px;color:#fff;letter-spacing:.04em;font-weight:600;font-family:var(--font-mono)}
.sev-extreme{background:var(--down)}.sev-high{background:#e06a1a}.sev-med{background:var(--amber)}.sev-low{background:var(--up)}
.subseg ul{columns:2;column-gap:26px;padding-left:18px;margin:6px 0}.subseg li{margin:3px 0;font-size:13px;color:#2b3240}
/* tables */
.tablewrap{overflow-x:auto;border:1px solid var(--rule);border-radius:2px;margin:14px 0;background:var(--surface)}
table.comp{border-collapse:collapse;width:100%;font-size:12.5px;min-width:1080px}
table.comp th,table.comp td{padding:7px 10px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
table.comp thead th{position:sticky;top:0;background:var(--surface-2);z-index:3;font-size:10px;text-transform:uppercase;letter-spacing:.03em;color:var(--ink-2);border-bottom:2px solid var(--rule-2);font-family:var(--font-mono)}
table.comp td.tk{font-weight:700;font-family:var(--font-mono);font-size:12px;white-space:nowrap;position:sticky;left:0;background:var(--surface);z-index:2;color:var(--ink)}
table.comp thead th:first-child{position:sticky;left:0;z-index:4}
td.co{min-width:130px;font-weight:600;color:var(--ink)}
td.seg{min-width:300px;max-width:380px;color:var(--ink-2);font-size:12px;line-height:1.45}
td.bk{min-width:160px;max-width:220px;font-size:12px;color:var(--ink-2)}
td.num{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums;font-family:var(--font-mono);color:var(--ink)}
td .sub{display:block;font-size:10.5px;color:var(--ink-3);font-weight:400}
.num.hi{color:var(--up);font-weight:600}.num.mid{color:#2c7a4d}.num.lo{color:var(--ink-3)}
.num.neg{color:var(--down)}
tr.subhdr td{background:var(--surface-2);font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#34406b;position:sticky;left:0}
.badge{font-size:9.5px;padding:1px 6px;border-radius:2px;vertical-align:middle}
.badge.pure{background:var(--tiffany-bg);color:var(--tiffany-ink);border:1px solid #b7e3e1}
td.priv{color:var(--ink-3);font-style:italic}
/* callouts / deals / glossary */
.callout{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--tiffany);border-radius:2px;padding:14px 18px;margin:16px 0}
.callout.warn{border-left-color:var(--down)}
.callout h4{color:var(--tiffany-ink)}.callout.warn h4{color:var(--down)}
.deals{margin:14px 0}.deals p{font-size:14px;margin:8px 0;padding-left:13px;border-left:2px solid var(--rule);color:#2b3240}
.chipcards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0}
.chipcard{background:var(--surface);border:1px solid var(--rule);border-radius:2px;padding:13px}
.chipcard h5{margin:0 0 2px;font-size:15px;color:var(--ink)}.chipcard .tagline{font-size:11.5px;color:var(--ink-2);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.chipcard p{font-size:12.5px;line-height:1.5;color:var(--ink-2)}.chipcard .val{color:var(--up)}
.uses ul{margin:6px 0;padding-left:18px}.uses li{font-size:13.5px;margin:3px 0;color:#2b3240}
.gloss{margin:12px 0;background:var(--surface);border:1px solid var(--rule);border-radius:2px;padding:6px 14px}
.gloss summary{cursor:pointer;font-weight:600;color:var(--tiffany-ink);font-size:13px;padding:5px 0}
.gl{font-size:13px;padding:5px 0;border-top:1px solid var(--rule);color:var(--ink-2)}
.obs li{margin:7px 0}
table.overview{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
table.overview th,table.overview td{padding:7px 11px;border-bottom:1px solid var(--rule);text-align:left;color:var(--ink)}
table.overview th{color:var(--ink-2);font-size:11px;text-transform:uppercase;letter-spacing:.03em}
table.overview .lcode{font-weight:700;font-family:var(--font-mono);color:var(--tiffany-ink)}
table.overview .num,table.overview th.num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--font-mono)}
.risks{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.risk{border:1px solid var(--rule);border-left:3px solid var(--down);border-radius:2px;padding:12px 15px;background:var(--surface)}
.risk h4{color:var(--down)}.risk p{font-size:13.5px;margin:0;color:#2b3240}
.stacks{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:12px 0}
.stack{border:1px solid var(--rule);border-radius:2px;padding:12px 15px;background:var(--surface)}
.stack ul{margin:6px 0;padding-left:17px}.stack li{font-size:13px;margin:5px 0;color:#2b3240}
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--rule);color:var(--ink-3);font-size:12px}
/* analyst take + stance + keyrisk */
.take{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--tiffany);border-radius:0 2px 2px 0;padding:13px 16px;margin:13px 0}
.take h4{color:var(--tiffany-ink);margin-bottom:6px}
.take p{font-size:14px;margin:0;color:#2b3240}
.stance{margin-top:9px;font-size:13px;font-weight:600;color:#1f2733;background:var(--surface-2);border:1px solid var(--rule);border-radius:2px;padding:7px 11px}
.stance .stag{display:inline-block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:#fff;background:var(--tiffany-ink);padding:2px 8px;border-radius:2px;margin-right:8px;vertical-align:middle;font-family:var(--font-mono)}
.keyrisk{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--down);border-radius:0 2px 2px 0;padding:12px 16px;margin:12px 0}
.keyrisk h4{color:var(--down);margin-bottom:6px}
.keyrisk p{font-size:13.5px;margin:0;color:var(--ink-2)}
.capexslice{background:var(--surface-2);border:1px dashed var(--rule-2);border-radius:2px;padding:8px 10px;margin:0 0 9px;font-size:12.5px;color:#2b3240}
.capexslice .cstag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:var(--tiffany-ink);margin-bottom:3px;font-family:var(--font-mono)}
/* citations / refs */
sup.cite{font-size:10px;line-height:0;margin-left:1px}
sup.cite a{color:var(--tiffany-ink);font-weight:700;text-decoration:none}
sup.cite a:hover{text-decoration:underline}
.src{color:var(--ink-2);font-size:12px;font-style:italic;margin:6px 0}
.refs{list-style:none;margin:14px 0;padding:0}
.refs li{display:flex;gap:10px;padding:8px 0;border-top:1px solid var(--rule);font-size:13px;color:var(--ink-2)}
.refs li:target{background:var(--tiffany-bg);border-radius:2px;padding:8px}
.refs .rnum{font-weight:700;color:var(--tiffany-ink);min-width:34px;font-family:var(--font-mono)}
.refs .rbody{color:var(--ink-2)}
/* charts */
.charts{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0}
.chart{margin:0;border:1px solid var(--rule);border-radius:2px;padding:13px 15px;background:var(--surface)}
.chart figcaption{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:10px}
.chartbody{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.chartviz{flex:0 0 auto}
.donut{width:150px;height:150px}
.bars{width:100%;max-width:440px;height:auto}
.bars .barlbl{font-size:11px;fill:var(--ink-2)}
.bars .barval{font-size:11px;fill:var(--ink);font-variant-numeric:tabular-nums}
.stackcol{width:100%;max-width:460px;height:auto}
.stackcol .coltot{font-size:10.5px;fill:var(--ink);font-weight:700}
.stackcol .collbl{font-size:11px;fill:var(--ink-2)}
figure.chart [data-k]{cursor:pointer}
figure.chart svg [data-k]{transition:opacity .12s ease}
figure.chart.dim svg [data-k]{opacity:.30}
figure.chart.dim svg [data-k].hi{opacity:1;stroke:var(--ink);stroke-width:1.5}
figure.chart .legend tr[data-k]{transition:background .12s}
figure.chart .legend tr[data-k].hi{background:var(--surface-2)}
.charttip{position:fixed;z-index:9999;background:var(--chrome);color:var(--chrome-ink);font-size:12px;font-weight:600;padding:5px 9px;border-radius:2px;pointer-events:none;border:1px solid var(--chrome-line);max-width:280px;display:none}
.legend{border-collapse:collapse;flex:1 1 240px;font-size:12px}
.legend td{padding:3px 6px;border-bottom:1px solid var(--rule);vertical-align:top;color:var(--ink)}
.legend td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap;font-family:var(--font-mono)}
.legend td.cnote{color:var(--ink-2);font-size:11px}
.legend .dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:middle}
/* layer head + info cards */
.layerhead{display:grid;grid-template-columns:1.05fr 0.95fr;gap:14px;margin:0;align-items:stretch}
.lhleft{display:flex;flex-direction:column;gap:10px}
.lhright{display:flex;flex-direction:column;gap:10px}
.infocard{border:1px solid var(--rule);border-radius:2px;padding:11px 14px;background:var(--surface)}
.infocard h4{margin:0 0 5px}.infocard p{margin:0;font-size:13px;line-height:1.5;color:#2b3240}
.metricmargin{margin-top:9px;background:var(--surface-2);border:1px solid var(--rule);border-left:3px solid var(--up);border-radius:2px;padding:7px 10px;font-size:12.5px;color:#2b3240}
.metricmargin .mmtag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:var(--up);margin-bottom:2px;font-family:var(--font-mono)}
.metricval{margin-top:7px;background:var(--surface-2);border:1px solid var(--rule);border-left:3px solid var(--tiffany);border-radius:2px;padding:7px 10px;font-size:12.5px;color:#2b3240}
.metricval .mvtag{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;color:var(--tiffany-ink);margin-bottom:2px;font-family:var(--font-mono)}
.lhright .take{margin:0;flex:1}.lhright .keyrisk{margin:0}
/* sub-segment cards */
.subseg h4{margin:0 0 8px}
.sscards{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.sscard{border:1px solid var(--rule);border-radius:2px;padding:10px 12px;background:var(--surface);font-size:12.5px;line-height:1.45}
.sscard .sshead{font-weight:700;color:#27313f;margin-bottom:3px}
.sscard .ssbody{color:var(--ink-2)}
td.ai{min-width:120px;max-width:150px;font-size:12px;font-weight:600;color:var(--ink);white-space:normal}
table.comp th.mfocus{background:var(--tiffany-bg);color:var(--tiffany-ink);border-bottom-color:#9ad7d4}
table.comp td.num.mfocus{background:var(--tiffany-bg);font-weight:700;box-shadow:inset 2px 0 0 var(--tiffany),inset -2px 0 0 var(--tiffany)}
.xtable{margin:16px 0}.xtable h4{margin:0 0 8px}
table.comp.facts{min-width:520px}table.comp.facts td.lbl{font-weight:600;color:#34406b}
/* feature box */
.feature{background:var(--surface);color:var(--ink);border:1px solid var(--rule);border-radius:2px;padding:18px 20px;margin:18px 0}
.feature h4{color:var(--tiffany-ink)}.feature .flead{font-size:14.5px;color:var(--ink-2)}.feature p{font-size:14px;color:#2b3240}.feature b{color:var(--ink)}
.feature .chipcard{background:var(--surface-2);border:1px solid var(--rule);border-radius:2px;padding:13px}
.feature .chipcard h5{margin:0 0 2px;font-size:15px;color:var(--ink)}
.feature .chipcard .tagline{font-size:11.5px;color:var(--ink-2);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.feature .chipcard p{font-size:12.5px;line-height:1.5;color:var(--ink-2)}.feature .chipcard .val{color:var(--up)}
.feature .replace{background:var(--surface-2);border:1px solid var(--rule);border-radius:2px;padding:11px 14px;margin:12px 0;font-size:13.5px;color:#2b3240}
.feature .uses ul{margin:6px 0;padding-left:18px}.feature .uses li{font-size:13.5px;margin:3px 0;color:var(--ink-2)}
/* ===== research-document components (panel + exhibit) ===== */
.lprofile{border:1px solid var(--rule-2);border-radius:2px;background:var(--surface);margin:14px 0}
.lprofile>.ph{display:flex;justify-content:space-between;align-items:center;background:var(--chrome);color:var(--chrome-ink);padding:8px 15px;font-family:var(--font-mono);font-size:11px;letter-spacing:.07em}
.lprofile>.ph .pn{color:var(--tiffany)}
.lprofile>.ph .pr{color:var(--chrome-ink-2)}
.lprofile>.pb{padding:15px}
.exhibit{background:var(--surface);border:1px solid var(--rule);border-radius:2px;margin:14px 0;overflow:hidden}
.exhibit>.ex-h{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:8px 14px;background:var(--chrome);border-bottom:1px solid var(--chrome-line)}
.exhibit>.ex-h .lbl{font-family:var(--font-mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--tiffany);font-weight:600}
.exhibit>.ex-h .cap{font-size:12.5px;font-weight:600;color:var(--chrome-ink)}
.exhibit>.ex-body{padding:13px}
.exhibit>.ex-body .charts{margin:0}
.exhibit>.ex-body .tablewrap,.exhibit>.ex-body .chart{border:none;margin:0}
.exhibit>.ex-src{padding:6px 14px;border-top:1px solid var(--rule);font-size:10.5px;color:var(--ink-3);font-style:italic}
.subh{font-family:var(--font-mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:18px 0 7px}
@media(max-width:900px){.layerhead{grid-template-columns:1fr}.sscards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:820px){.three,.chipcards,.risks,.stacks,.charts,.sscards{grid-template-columns:1fr}.subseg ul{columns:1}
  .hero .wrap{flex-direction:column;align-items:flex-start}.hero h1{font-size:25px}.chartbody{flex-direction:column;align-items:flex-start}}
"""

# 1. swap style block
new_block = "<style>\n" + CSS + "</style>"
html, n = re.subn(r"<style>.*?</style>", lambda m: new_block, html, count=1, flags=re.DOTALL)
assert n == 1, f"style swap n={n}"

# 2. re-tune inline chart palette for light paper (body only)
head, sep, body = html.partition("</style>")
# donut center: was card-dark -> white
body = body.replace('fill="#0e0e12"', 'fill="#ffffff"')
PALETTE = {
    # categorical chart series -> darker for white bg
    "#4c8dff": "#2f6fe0", "#00D17A": "#0a8f5b", "#e0a23c": "#c8851f",
    "#FF4D4D": "#d92d20", "#a78bfa": "#7c5cf0", "#2bc4d6": "#1597a8",
    "#f06fb0": "#d6418f", "#8bc34a": "#5a8f2a", "#c08457": "#a06a3f",
    # dark-theme text fills -> light-paper ink
    "#ececf1": "#1a1f2b", "#9c9ca6": "#5b6577", "#66666f": "#8a94a6",
}
PALETTE_L = {k.lower(): v for k, v in PALETTE.items()}
pat = re.compile("|".join(re.escape(k) for k in PALETTE), re.IGNORECASE)
body = pat.sub(lambda m: PALETTE_L[m.group(0).lower()], body)
html = head + sep + body

SRC.write_text(html, encoding="utf-8")
print("v14 theme applied; bytes:", len(html))
