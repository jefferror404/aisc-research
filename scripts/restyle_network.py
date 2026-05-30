#!/usr/bin/env python3
"""Restyle ai_deal_network_layered.html to the kaamos polar-night design system.

- Rewrites the <style> block (dark theme, Inter, Tiffany accent).
- Keeps node-category CSS var names (JS reads them via var(--<category>)).
- Swaps the Google Fonts link to Inter + JetBrains Mono.
- Updates the one inline JS font-family (node labels) to Inter.
"""
import re
import pathlib

SRC = pathlib.Path("ai_deal_network_layered.html")
html = SRC.read_text(encoding="utf-8")

NEW_CSS = r""":root {
  /* Kaamos polar-night tokens — source of truth: kaamos/docs/DESIGN.md */
  --bg-0:#07070a;--bg-1:#0e0e12;--bg-2:#16161c;--bg-3:#1d1d24;
  --text-1:#ececf1;--text-2:#9c9ca6;--text-3:#66666f;
  --border-1:#1d1d25;--border-2:#28282f;
  --tiffany:#0ABAB5;--tiffany-dim:#088a86;--tiffany-bg:rgba(10,186,181,.08);
  --up:#00D17A;--down:#FF4D4D;--neutral:#807c78;
  /* legacy UI aliases (kept so existing selectors resolve) */
  --ink:var(--text-1);--ink-2:var(--text-2);
  --paper:var(--bg-0);--paper-2:var(--bg-2);
  --rule:var(--border-1);--muted:var(--text-2);--accent:var(--tiffany);
  /* node-category palette — referenced by JS as var(--<category>); dark-readable */
  --equity:#00D17A;--compute:#FF5C5C;--chip:#e0a23c;
  --hyperscaler:#4c8dff;--llm:#a78bfa;--chipmaker:#8bc34a;
  --neocloud:#2bc4d6;--foundry:#c08457;--equipment:#5fb3b3;
  --power:#f0883e;--other:#9c9ca6;
  --font-sans:'Inter',-apple-system,system-ui,sans-serif;
  --font-mono:'JetBrains Mono',ui-monospace,monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  height: 100%; background: var(--bg-0); color: var(--text-1);
  font-family: var(--font-sans); font-feature-settings: "ss01","cv11"; overflow: hidden;
}
.app {
  display: grid; grid-template-columns: 320px 1fr; grid-template-rows: auto 1fr; height: 100vh;
  grid-template-areas: "header header" "sidebar canvas";
}
header.topbar {
  grid-area: header; border-bottom: 1px solid var(--border-1); padding: 18px 28px 14px;
  background: var(--bg-1); color: var(--text-1);
  display: flex; align-items: baseline; justify-content: space-between; gap: 24px;
}
.brand { display: flex; align-items: baseline; gap: 14px; }
.brand h1 { font-family: var(--font-sans); font-weight: 700; font-size: 22px; letter-spacing: -0.02em; color: var(--text-1); }
.brand .small {
  font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--tiffany);
}
.search {
  display: flex; align-items: center; gap: 8px; background: var(--bg-2); border: 1px solid var(--border-1);
  border-radius: 2px; padding: 6px 10px; min-width: 280px;
}
.search input {
  background: none; border: none; color: var(--text-1);
  font-family: var(--font-mono); font-size: 12px; outline: none; width: 100%;
}
.search input::placeholder { color: var(--text-3); }
aside.sidebar {
  grid-area: sidebar; border-right: 1px solid var(--border-1); background: var(--bg-1);
  overflow-y: auto; padding: 24px 22px; font-size: 13px;
}
.section-title {
  font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--text-2); margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid var(--border-1);
}
.legend { margin-bottom: 22px; }
.legend .item {
  display: flex; align-items: center; gap: 10px; margin-bottom: 8px; cursor: pointer; padding: 4px 6px;
  border-radius: 2px; transition: background 0.12s; user-select: none;
}
.legend .item:hover { background: var(--bg-2); }
.legend .item.disabled { opacity: 0.35; }
.legend .swatch { width: 26px; height: 4px; border-radius: 1px; flex-shrink: 0; }
.legend .label { font-size: 12px; font-weight: 500; color: var(--text-1); }
.filters { margin-bottom: 22px; }
.chip {
  display: inline-block; padding: 4px 9px; font-family: var(--font-mono);
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em;
  border: 1px solid var(--border-1); border-radius: 2px; margin: 0 4px 4px 0; cursor: pointer; user-select: none;
  background: var(--bg-2); color: var(--text-2); transition: all 0.12s;
}
.chip:hover { background: var(--bg-3); color: var(--text-1); border-color: var(--border-2); }
.chip.active { background: var(--tiffany-bg); color: var(--tiffany); border-color: var(--tiffany-dim); }
.detail { margin-top: 16px; }
.detail.empty { font-style: italic; color: var(--text-3); font-size: 12px; }
.entity-card { border: 1px solid var(--border-1); background: var(--bg-2); border-radius: 2px; padding: 14px; margin-bottom: 12px; }
.entity-card .name { font-family: var(--font-sans); font-size: 18px; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 2px; color: var(--text-1); }
.entity-card .meta { font-family: var(--font-mono); font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--tiffany); margin-bottom: 10px; }
.entity-card .desc { font-size: 12px; line-height: 1.5; color: var(--text-2); margin-bottom: 12px; }
.entity-card .deal-list-title { font-family: var(--font-mono); font-size: 9px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-3); margin-bottom: 6px; }
.deal-item { font-size: 11px; padding: 6px 0; border-top: 1px solid var(--border-1); line-height: 1.4; color: var(--text-2); }
.deal-item:first-child { border-top: none; }
.deal-item .deal-meta { font-family: var(--font-mono); font-size: 9px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-3); margin-bottom: 2px; }
.deal-item .deal-amount { font-weight: 600; color: var(--text-1); }
.deal-item .deal-arrow { font-family: var(--font-mono); color: var(--text-3); }
main.canvas { grid-area: canvas; position: relative; overflow: hidden; background: var(--bg-0); }
#graph { width: 100%; height: 100%; }
.layer-band { fill: rgba(255,255,255,0.015); }
.layer-band-divider { stroke: var(--border-1); stroke-width: 1; stroke-dasharray: 4 4; fill: none; }
.layer-label {
  font-family: var(--font-mono); font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em;
  fill: var(--text-3); font-weight: 600;
}
.layer-label-bg { fill: var(--bg-0); opacity: 0.85; }
.node rect, .node circle { cursor: pointer; transition: filter 0.2s; }
.node:hover rect, .node:hover circle { filter: brightness(1.15); }
.node text { pointer-events: none; user-select: none; }
.link { cursor: pointer; transition: opacity 0.2s; }
.link.faded { opacity: 0.05; }
.link-label {
  pointer-events: none; user-select: none; font-family: var(--font-mono); font-size: 9px; font-weight: 600;
  fill: var(--text-2); paint-order: stroke; stroke: var(--bg-0); stroke-width: 3px; stroke-linejoin: round;
}
.node.faded { opacity: 0.18; }
.node.faded text { opacity: 0.4; }
.controls { position: absolute; top: 18px; right: 18px; display: flex; flex-direction: column; gap: 6px; z-index: 10; }
.controls button {
  background: var(--bg-1); border: 1px solid var(--border-1); color: var(--text-1);
  width: 32px; height: 32px; border-radius: 2px; cursor: pointer;
  font-family: var(--font-mono); font-size: 14px; font-weight: 600;
  display: flex; align-items: center; justify-content: center; transition: all 0.12s;
}
.controls button:hover { background: var(--bg-3); border-color: var(--border-2); }
.summary-stats {
  position: absolute; top: 18px; left: 18px; background: var(--bg-1); border: 1px solid var(--border-1);
  color: var(--text-2); padding: 12px 16px; border-radius: 2px;
  font-family: var(--font-mono); font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em;
  display: flex; gap: 24px; z-index: 10;
}
.summary-stats .stat { display: flex; flex-direction: column; gap: 2px; }
.summary-stats .stat .num {
  font-size: 16px; font-family: var(--font-mono); font-weight: 600; letter-spacing: -0.01em;
  text-transform: none; color: var(--tiffany);
}
.hint {
  position: absolute; bottom: 18px; right: 18px; background: var(--bg-1); border: 1px solid var(--border-1);
  padding: 8px 12px; border-radius: 2px; font-family: var(--font-mono); font-size: 10px; color: var(--text-3); z-index: 10;
}
aside::-webkit-scrollbar { width: 8px; }
aside::-webkit-scrollbar-track { background: var(--bg-1); }
aside::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 4px; }
aside::-webkit-scrollbar-thumb:hover { background: var(--neutral); }
"""

# 1. swap <style> block
new_block = "<style>\n" + NEW_CSS + "</style>"
html, n = re.subn(r"<style>.*?</style>", lambda m: new_block, html, count=1, flags=re.DOTALL)
assert n == 1, f"expected 1 <style>, replaced {n}"

# 2. swap font link
html, nf = re.subn(
    r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
    html, count=1,
)
assert nf == 1, f"expected 1 font link, replaced {nf}"

# 3. JS node-label font-family
html = html.replace('"Inter Tight, sans-serif"', '"Inter, sans-serif"')

SRC.write_text(html, encoding="utf-8")
print("network restyled OK; bytes:", len(html), "| font links swapped:", nf)
