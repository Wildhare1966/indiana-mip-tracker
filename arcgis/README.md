# MRD → ArcGIS Online sync (Tracked Projects)

Autonomous, **one-way** push of MRD Tracked Project data into a hosted feature
layer, matched on a shared unique ID: MRD's **MapID** (`Tracked_Projects.map_id`,
added P94) ⇄ a field on your feature layer (`ID_FIELD`).

The logic runs **inside ArcGIS Online Notebooks** and authenticates implicitly as
the notebook owner (`GIS("home")`). MRD needs **no backend changes** — the
notebook pulls from the existing public `list_tracked_projects_detailed` endpoint.

## Files

| File | Purpose |
|---|---|
| `sync_tracked_projects.py` | Source of truth (editable, `# %%` cell markers). |
| `sync_tracked_projects.ipynb` | Generated notebook — upload this to ArcGIS Online. |
| `build_notebook.py` | Regenerates the `.ipynb` from the `.py` after edits. |

After editing the `.py`, regenerate with:
`python build_notebook.py sync_tracked_projects.py sync_tracked_projects.ipynb`

## Target & mapping (pre-filled for LeadsDeals_Arbor)

- **Item:** `c82269644ad24569aaff749f3a1d1f4a` (layer `LeadsDeals3`, index 0).
- **`ID_FIELD = GlobalID`** — the MapID you enter in MRD for each project is that
  feature's **GlobalID** (a GUID). GlobalIDs are durable (survive
  republish/overwrite). Paste it in any form — `{...}`/no braces, any case,
  stray spaces — the notebook normalizes to canonical `{UPPERCASE}` before
  matching. The edit itself still targets the feature's ObjectID, read back from
  the matched feature.

| MRD field | → Feature-layer field | Notes |
|---|---|---|
| `projectName` | `LeadsDeals` | |
| `builder` | `Builder` | **domain-constrained (List 18)** — MRD's builder text must exactly match an allowed value, or that one field's edit is rejected |
| `latestActionTaken` | `Last_Result` | |
| `latestMeetingType` + `latestMeetingDate` | `Terms` | computed: `"<type> — <date>"` |
| `driveFolderId` | `FolderLink` | computed: `https://drive.google.com/drive/folders/<id>` |

Edit `FIELD_MAP` / `DERIVED_MAP` in the notebook to add or change fields.

## One-time setup

1. **Confirm the layer is editable.** ArcGIS Online → the item → Settings →
   Editing → *Enable editing* (Update enabled). The notebook owner needs edit
   privilege on the layer.
2. **Upload the notebook.** Notebooks → New notebook → import
   `sync_tracked_projects.ipynb` (runtime **3.0 or later** — required for
   scheduled execution).
3. **Check the PARAMETERS cell** — the target + mapping are pre-filled; just
   confirm `ITEM_ID`/`ID_FIELD`, optionally set `AUTH_TOKEN`, and leave
   `DRY_RUN = True` for the first run.

> **Getting GlobalIDs:** in the layer's Data table add/show the GlobalID column,
> copy a feature's GlobalID, and paste it into that project's MapID field in MRD.
> (GlobalIDs are durable across republish, unlike FID/ObjectID.)

## Run it

1. **Dry run** (`DRY_RUN=True`): prints rows pulled, how many MapIDs matched
   features, and a per-field before→after diff. **Writes nothing.** Review it.
2. **First real push** (`DRY_RUN=False`): applies the updates; confirm in Map
   Viewer or via a query that the matched features changed.
3. **Schedule:** notebook editor → **Tasks → Schedule a task** → daily
   (15-minute minimum). Put live values (incl. `DRY_RUN=False`) in the task's
   **Parameters** cell so secrets aren't saved in the shared notebook body.
   Programmatic alternative (`gis.tasks.create(..., task_type="ExecuteNotebook",
   cron="0 7 * * *")`) is shown in the final notebook cell.

## Behavior notes

- **One-way & non-destructive:** only the mapped attributes are written; geometry
  and all other layer fields are untouched.
- **Diff-only writes:** a feature is updated only when a mapped value actually
  changed, so reruns are cheap and the log is meaningful.
- **Unmatched MapIDs** (no feature with that `ID_FIELD` value) are logged as
  skipped, not errors. A MapID that matches **multiple** features updates all of
  them.
- **`ONLY_ACTIVE=True`** restricts the sync to MRD projects with `status=active`.

## Verification checklist

- Dry run prints N pulled / M matched / 0 writes.
- Change one field on one TP row in MRD (e.g. status), rerun → that feature's
  attribute updates in ArcGIS.
- A bogus/blank MapID is skipped without raising.
- After scheduling, the next automated run's log shows expected counts and a
  known change propagates with no manual action.
