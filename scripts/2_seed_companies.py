"""
2_seed_companies.py — Upsert curated data from data/companies_seed.json into the DB.

Re-run any time you edit the seed JSON. Uses INSERT .. ON CONFLICT so it updates the
curated 'companies' and 'company_layer' rows without disturbing fetched market/financial data.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "aisc.db"
SEED = ROOT / "data" / "companies_seed.json"
LAYERS = ROOT / "data" / "layers_seed.json"


def main():
    seed = json.loads(SEED.read_text())
    # company_layer appearances live in layers_seed.json (large, kept separate).
    layer_rows = []
    if LAYERS.exists():
        layer_rows = json.loads(LAYERS.read_text()).get("company_layer", [])
    con = sqlite3.connect(DB)
    cur = con.cursor()

    for c in seed.get("companies", []):
        cur.execute(
            """INSERT INTO companies (ticker, native_ticker, name, country, primary_layer,
                       is_public, is_pure_play, fiscal_note, narrative)
               VALUES (:ticker, :native_ticker, :name, :country, :primary_layer,
                       :is_public, :is_pure_play, :fiscal_note, :narrative)
               ON CONFLICT(ticker) DO UPDATE SET
                 name=excluded.name, country=excluded.country, primary_layer=excluded.primary_layer,
                 is_public=excluded.is_public, is_pure_play=excluded.is_pure_play,
                 fiscal_note=excluded.fiscal_note, narrative=excluded.narrative""",
            {
                "ticker": c["ticker"],
                "native_ticker": c.get("native_ticker", c["ticker"]),
                "name": c["name"],
                "country": c.get("country", ""),
                "primary_layer": c.get("primary_layer", ""),
                "is_public": c.get("is_public", 1),
                "is_pure_play": c.get("is_pure_play", 0),
                "fiscal_note": c.get("fiscal_note", ""),
                "narrative": c.get("narrative", ""),
            },
        )

    # Rebuild company_layer from seed (it is fully curated, safe to replace).
    cur.execute("DELETE FROM company_layer")
    for cl in layer_rows:
        cur.execute(
            """INSERT INTO company_layer (ticker, layer, layer_name, sublayer, category,
                       segment_label, segment_rev_note, key_contracts, backlog_rpo, ai_rev_share, note, sort_order)
               VALUES (:ticker, :layer, :layer_name, :sublayer, :category,
                       :segment_label, :segment_rev_note, :key_contracts, :backlog_rpo, :ai_rev_share, :note, :sort_order)""",
            {
                "ticker": cl["ticker"], "layer": cl["layer"],
                "layer_name": cl.get("layer_name", ""), "sublayer": cl.get("sublayer", ""),
                "category": cl.get("category", ""), "segment_label": cl.get("segment_label", ""),
                "segment_rev_note": cl.get("segment_rev_note", ""),
                "key_contracts": cl.get("key_contracts", ""),
                "backlog_rpo": cl.get("backlog_rpo", ""),
                "ai_rev_share": cl.get("ai_rev_share", ""), "note": cl.get("note", ""),
                "sort_order": cl.get("sort_order", 0),
            },
        )

    con.commit()
    n_co = cur.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_cl = cur.execute("SELECT COUNT(*) FROM company_layer").fetchone()[0]
    con.close()
    print(f"Seeded {n_co} companies, {n_cl} layer appearances.")


if __name__ == "__main__":
    main()
