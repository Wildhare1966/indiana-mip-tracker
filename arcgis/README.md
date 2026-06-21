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
| `jurisdiction` | `Jurisdiction` | |
| `status` | `Status` | |
| `petitionerDisplay` | `OwnerName` | |
| `builder` | `Builder` | **domain-constrained (List 18)** — MRD's builder text must exactly match an allowed value, or that one field's edit is rejected |
| `lots` | `Lots` | |
| `latestActionTaken` | `Last_Result` | = the **Results** column text on Competitor Tracked Projects (blank when no summarized hearing yet) |
| `latestRequestSummary` | `Terms` | = the **Description** column text (parsed "Request:" summary) |
| `latestMeetingDate` | `Hearing_Date` | latest meeting / hearing date (M/D/YYYY text) |
| `latestYtSummaryUrl` | `Summary` | latest summary / source-doc URL |
| `driveFolderId` (→ URL) | `FolderLink` | computed `https://drive.google.com/drive/folders/<id>` — link to the project's tagged-documents Drive folder |

> **Two field names are REPURPOSED** from the original draft: `Terms` now holds the
> Description text (not meeting type+date) and `FolderLink` now holds the summary URL
> (not the Drive-folder link). Check the AGO field **aliases** read sensibly.

**Create these layer fields first** (String unless noted) if they don't already
exist: `Jurisdiction`, `Status`, `OwnerName`, `Lots`, `Hearing_Date` (String 20),
`Summary` (String 400), plus confirm `LeadsDeals`, `Builder`, `Last_Result`, `Terms`,
`FolderLink`. Any target missing on the layer is
skipped with a `WARNING` during the dry run — that's your schema check.

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
3. **Schedule:** in ArcGIS Online a scheduled task runs the notebook **exactly as
   saved**, so set `DRY_RUN = False` in the PARAMETERS cell and **Save** the
   notebook first. Then notebook editor → **Tasks** pane → **Create task / Schedule**
   → *Run notebook* → **Daily** (15-minute minimum). `AUTH_TOKEN` stays blank (the
   endpoint is public), so there's no secret to keep out of the body. Programmatic
   alternative (`gis.tasks.create(..., task_type="ExecuteNotebook", cron="0 7 * * *")`)
   is shown in the final notebook cell.

## Behavior notes

- **One-way & non-destructive:** only the mapped attributes are written; geometry
  and all other layer fields are untouched.
- **Diff-only writes:** a feature is updated only when a mapped value actually
  changed, so reruns are cheap and the log is meaningful.
- **Unmatched MapIDs** (no feature with that `ID_FIELD` value) are logged as
  skipped, not errors. A MapID that matches **multiple** features updates all of
  them.
- **Invalid MapIDs:** when matching on a GUID/GlobalID field, a `map_id` that is
  not a well-formed GUID (e.g. a map URL pasted into the wrong field) is skipped
  with a `WARNING` rather than aborting the query. Fix the value in MRD.
- **`ONLY_ACTIVE=True`** restricts the sync to MRD projects with `status=active`.

## Verification checklist

- Dry run prints N pulled / M matched / 0 writes.
- Change one field on one TP row in MRD (e.g. status), rerun → that feature's
  attribute updates in ArcGIS.
- A bogus/blank MapID is skipped without raising.
- After scheduling, the next automated run's log shows expected counts and a
  known change propagates with no manual action.
