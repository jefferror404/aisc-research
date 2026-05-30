#!/usr/bin/env python3
"""v15: Kaamos x Editorial theme on the real report.

Reuses the v14 stylesheet (which targets every real-report class), then:
  - flips :root tokens from light-paper to kaamos polar-night dark,
  - replaces hardcoded dark-on-light text colors with light-on-dark,
  - overlays Fraunces serif on headlines/section titles/exhibit captions + drop cap,
  - adds the Fraunces font, and remaps inline chart colors back to the dark palette.
"""
import re, pathlib

SRC = pathlib.Path("report/ai_supply_chain_report.html")
V14 = pathlib.Path("scripts/restyle_v14_theme.py")

# --- pull the proven v14 CSS (targets real-report selectors) ---
v14src = V14.read_text()
m = re.search(r'CSS = r"""(.*?)"""', v14src, re.DOTALL)
assert m, "could not extract v14 CSS"
css = m.group(1)

# 1) flip :root to polar-night dark + add serif
NEWROOT = """:root{
  --chrome:#16161c;--chrome-2:#1d1d24;--chrome-ink:#ececf1;--chrome-ink-2:#9c9ca6;--chrome-line:#28282f;
  --paper:#07070a;--surface:#0e0e12;--surface-2:#16161c;
  --ink:#ececf1;--ink-2:#9c9ca6;--ink-3:#66666f;
  --rule:#1d1d25;--rule-2:#28282f;
  --tiffany:#0ABAB5;--tiffany-ink:#0ABAB5;--tiffany-bg:rgba(10,186,181,.10);
  --up:#00D17A;--down:#FF4D4D;--amber:#e0a23c;
  --ink1:var(--ink);--muted:var(--ink-2);--line:var(--rule);--bg:var(--paper);--card:var(--surface);
  --accent:var(--tiffany);--green:var(--up);--red:var(--down);--hi:var(--up);
  --serif:'Fraunces',Georgia,serif;
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --font-mono:'JetBrains Mono',ui-monospace,Menlo,monospace;}"""
css = re.sub(r':root\{.*?\}', lambda _: NEWROOT, css, count=1, flags=re.DOTALL)

# 2) hardcoded dark-on-light text colors -> light-on-dark
for a, b in {
    "#2b3240": "#cfd0d6", "#34406b": "#cfd0d6", "#27313f": "#e3e4e9",
    "#11161f": "#ececf1", "#1f2733": "#ececf1", "#2c7a4d": "#3fae74",
}.items():
    css = css.replace(a, b)

# 3) editorial overlay: Fraunces serif on display text + drop cap
css += """
/* --- Kaamos x Editorial overlay --- */
.hero h1,h2,h3,.subh,.sscard .sshead,.exhibit>.ex-h .cap,.chart figcaption,.tablewrap>.ex-h .cap,.gloss summary{font-family:var(--serif);font-weight:600}
.hero h1{font-size:38px;letter-spacing:-.4px}
h2{letter-spacing:-.3px}
.chart figcaption{font-weight:600}
.lead::first-letter{font-family:var(--serif);font-size:3.4em;line-height:.78;float:left;margin:.04em .12em 0 0;color:var(--tiffany);font-weight:600}
"""

html = SRC.read_text()

# swap <style>
html, n = re.subn(r"<style>.*?</style>", lambda _: "<style>\n"+css+"</style>", html, count=1, flags=re.DOTALL)
assert n == 1

# add Fraunces to the font link
html = html.replace(
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
    1)

# remap inline chart palette light-paper -> kaamos dark
head, sep, body = html.partition("</style>")
PAL = {
    "#2f6fe0":"#4c8dff","#0a8f5b":"#00D17A","#ffffff":"#0e0e12","#c8851f":"#e0a23c",
    "#d92d20":"#FF4D4D","#7c5cf0":"#a78bfa","#5b6577":"#9c9ca6","#1597a8":"#2bc4d6",
    "#d6418f":"#f06fb0","#5a8f2a":"#8bc34a","#a06a3f":"#c08457","#1a1f2b":"#ececf1",
    "#8a94a6":"#66666f","#c0392b":"#FF4D4D","#d4499b":"#f06fb0","#8a9a5b":"#8bc34a","#a0522d":"#c08457",
}
pat = re.compile("|".join(re.escape(k) for k in PAL), re.IGNORECASE)
body = pat.sub(lambda mm: PAL[mm.group(0).lower()], body)
html = head + sep + body

SRC.write_text(html)
print("v15 Kaamos x Editorial applied; bytes:", len(html))
