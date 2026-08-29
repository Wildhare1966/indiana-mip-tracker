# ⛔ The ArcGIS sync does not live here any more

**Canonical location:** `C:\Users\ty\Claude_Code\indiana-agenda-tracker\arcgis\`
(private repo `Wildhare1966/indiana-agenda-tracker`).

## Why this directory was emptied — 2026-08-29

Two copies of `sync_tracked_projects.py` existed and had **diverged**:

| | Lines | `LAYER_URL` | Last logic change |
|---|---|---|---|
| `indiana-agenda-tracker/arcgis/` | 832 | live `Projects/FeatureServer/0` | 2026-08-28 |
| here (deleted) | 531 | `""` — header named the retired `LeadsDeals_Arbor` | 2026-06-22 |

The copy here was **301 lines behind, pointed at a retired layer, and sitting in a PUBLIC repo**.
Ty ruled on 2026-08-29: the agenda-tracker copy is canonical. This one was deleted rather than
resynced, so there is only ever one script that writes to the live layer.

Also deleted here and present upstream: `build_notebook.py`,
`sync_tracked_projects.ipynb`, `tracked_projects_field_catalog.csv`. Upstream additionally carries
`diagnose_field_data.*` and `fix_truncated_fields.*`, which never existed here.

## If you came looking for the notebook

The sync runs as an **ArcGIS Online Notebook item** in the wildhare org, authenticating as the
notebook owner via `GIS("home")`. It is **uploaded** to AGO, not fetched from GitHub at run time —
so deleting this directory does not stop the running sync.

⚠ Archived kickoffs **P139–P141** (in `indiana-agenda-tracker/archive/`) describe importing the
notebook from the raw GitHub URL
`raw.githubusercontent.com/Wildhare1966/indiana-mip-tracker/main/arcgis/sync_tracked_projects.ipynb`.
**That URL is now dead.** If you need to re-import rather than upload, regenerate and take the
notebook from the canonical directory:

```bash
cd C:\Users\ty\Claude_Code\indiana-agenda-tracker\arcgis
python build_notebook.py sync_tracked_projects.py sync_tracked_projects.ipynb
```
