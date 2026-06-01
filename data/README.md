# Data Directory

This directory contains the InducedSeismic-Bench dataset.

## Files

| File | Description |
|------|-------------|
| `schema.json` | JSON Schema (draft-07) defining the structure of each benchmark item |
| `dataset.json` | Full dataset — all benchmark items in machine-readable JSON |
| `dataset.csv` | Same data in CSV format for human inspection and spreadsheet analysis |
| `cases/` | Background documentation for each seismicity case |

## Quick Load

```python
import json

with open("data/dataset.json") as f:
    items = json.load(f)

print(f"{len(items)} items loaded")
for item in items:
    print(item["item_id"], item["tier_label"])
```

## Dataset Statistics (v0.2.0-draft)

| Case | Case ID | Operation Type | Items | Tiers Covered |
|------|---------|----------------|-------|---------------|
| Prague, Oklahoma, 2011 | PRAGUE | wastewater_disposal | 4 | 1–4 |
| Pohang, South Korea, 2017 | POHANG | geothermal | 4 | 1–4 |
| Raton Basin, Colorado, 2001–2011 | RATON | wastewater_disposal | 4 | 1–4 |
| Groningen, Netherlands | GRONING | reservoir_impoundment | 4 | 1–4 |
| Pawnee, Oklahoma, 2016 | PAWNEE | wastewater_disposal | 4 | 1–4 |
| Guy-Greenbrier, Arkansas, 2010–2011 | GUYGRB | wastewater_disposal | 3 | 1–3 |
| Youngstown, Ohio, 2011–2012 | YTOWN | wastewater_disposal | 4 | 1–4 |
| Basel, Switzerland, 2006 | BASEL | geothermal | 4 | 1–4 |
| Preese Hall, Lancashire, UK, 2011 | PREESE | hydraulic_fracturing | 3 | 1–3 |
| Paradox Valley, Colorado | PARADOX | wastewater_disposal | 4 | 1–4 |
| The Geysers, California | GEYSERS | geothermal | 4 | 1–4 |
| Koyna, India | KOYNA | reservoir_impoundment | 3 | 1–3 |
| Fox Creek, Alberta, Canada | FOXCRK | hydraulic_fracturing | 3 | 1–3 |
| Castor, Spain, 2013 | CASTOR | reservoir_impoundment | 3 | 1–3 |
| Dallas-Fort Worth, Texas, 2008–2009 | DFW | wastewater_disposal | 3 | 1–3 |
| Azle, Texas, 2013–2014 | AZLE | wastewater_disposal | 3 | 1–3 |
| Cushing, Oklahoma, 2016 | CUSHING | wastewater_disposal | 3 | 1–3 |
| Poland Township, Ohio | POLNDTWP | hydraulic_fracturing | 2 | 1–2 |
| Landau, Germany | LANDAU | geothermal | 3 | 1–3 |
| Preston New Road, Lancashire, UK, 2018–2019 | PRSNRD | hydraulic_fracturing | 3 | 1–3 |
| **Total** | | | **68** | |

## Schema Validation

To validate all items against the schema:

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('data/schema.json'))
items = json.load(open('data/dataset.json'))
for item in items:
    jsonschema.validate(item, schema)
print(f'All {len(items)} items valid.')
"
```

## Case Background Files

Each file in `data/cases/` documents the real-world case behind the benchmark items:

- `prague_ok.md` — Prague, Oklahoma earthquake sequence (2011)
- `pohang_sk.md` — Pohang, South Korea geothermal-induced earthquake (2017)
- `raton_basin_co.md` — Raton Basin, Colorado earthquake swarms (2001–2011)
- `groningen_nl.md` — Groningen, Netherlands gas-extraction seismicity

These files include source publications, geological setting, attribution conclusions from
the literature, and notes on any scientific controversy. They are for reference only —
the benchmark items use anonymized evidence descriptions that do not name the locations.
