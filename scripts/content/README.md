# Content builders

These scripts write the hand-made data files. Edit the script, then run it from the repository root:

| Script | Writes | Run |
|---|---|---|
| `build_insights.py` | `docs/data/insights.json` (reading-guide situations) | `python scripts/content/build_insights.py docs/data` |
| `build_sea.py` | `docs/data/sea.json` (shipping routes, chokepoints, detours) | `python scripts/content/build_sea.py docs/data` |
| `build_roadinfo.py` | `docs/data/roadinfo.json` (road descriptions, passes, ferries, borders) | `python scripts/content/build_roadinfo.py docs/data` |
| `build_geo.js` + `build_geo2.js` | `docs/data/geo/*.json` (coastlines; only needed once) | needs Node with `world-atlas`, `topojson-client`, `topojson-simplify`, `d3-geo` |

`build_sea.py` prints each route's distance so you can compare it with published figures.
