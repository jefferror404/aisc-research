#!/usr/bin/env python3
"""Roll the L4 template across the other 10 layers:
  - wrap each layer's .layerhead in a dark-headed "Layer Profile" panel
  - add a dark "Exhibit" header bar to each comp table (.tablewrap)
Idempotent: skips a layer already wrapped (lprofile present in its slice).
"""
import re, pathlib
p = pathlib.Path("report/ai_supply_chain_report.html")
s = p.read_text()

# short labels for the Layer Profile header (right side)
LABEL = {
 "L10":"L10 · APPS & AGENTS","L9":"L9 · FOUNDATION MODELS","L8":"L8 · CLOUD",
 "L7":"L7 · DC REAL ESTATE","L6":"L6 · NETWORKING","L5":"L5 · SERVERS",
 "L3":"L3 · MEMORY & STORAGE","L2":"L2 · FOUNDRY & PACKAGING","L1":"L1 · EDA & EQUIPMENT",
 "L0":"L0 · POWER & COOLING",
}
# comp-table exhibit captions (per layer; L2 gets two)
CAP = {
 "L10":["Apps & agents comps"],"L9":["Foundation-model labs"],"L8":["Cloud & neocloud comps"],
 "L7":["REIT & contractor comps"],"L6":["Networking & optics comps"],"L5":["Server & power-supply comps"],
 "L3":["Memory & storage comps"],"L2":["Foundry comps","Advanced-packaging / OSAT comps"],
 "L1":["EDA, equipment & materials comps"],"L0":["Power & cooling comps"],
}
ORDER=["L10","L9","L8","L7","L6","L5","L3","L2","L1","L0"]
END=s.index('<section id="dealweb"')

def bounds(k):
    a=s.index(f'<section id="{k}"')
    after=[s.index(f'<section id="{x}"') for x in (["L10","L9","L8","L7","L6","L5","L4","L3","L2","L1","L0"]) ]
    nxt=min([x for x in after if x>a]+[END])
    return a,nxt

# process from the end backwards so indices stay valid
done=0
for k in sorted(ORDER, key=lambda x: s.index(f'<section id="{x}"'), reverse=True):
    a,b=bounds(k); chunk=s[a:b]
    if 'class="lprofile"' in chunk:
        continue
    assert chunk.count('<div class="layerhead">')==1, f"{k}: layerhead count off"
    LOPEN=(f'<div class="lprofile"><div class="ph"><span class="pn">Layer Profile</span>'
           f'<span class="pr">{LABEL[k]}</span></div><div class="pb">')
    chunk=chunk.replace('<div class="layerhead">', LOPEN+'<div class="layerhead">',1)
    # close panel right before the three-up row (every layer has one)
    assert chunk.count('<div class="three">')>=1, f"{k}: no three-up"
    chunk=chunk.replace('<div class="three">', '</div></div>\n<div class="three">',1)
    # dark exhibit header on each comp table
    caps=CAP[k]; idx=[0]
    def add_hdr(m):
        i=idx[0]; idx[0]+=1
        cap=caps[i] if i<len(caps) else caps[-1]
        return (f'<div class="tablewrap"><div class="ex-h"><span class="lbl">Exhibit · {k}</span>'
                f'<span class="cap">{cap}</span></div>')
    chunk=re.sub(r'<div class="tablewrap">', add_hdr, chunk)
    s=s[:a]+chunk+s[b:]
    done+=1

p.write_text(s)
print(f"converted {done} layers; lprofile total now {s.count(chr(34)+'lprofile'+chr(34))}")
