# %% [markdown]
# # MRD → ArcGIS Online — Tracked Projects sync (LeadsDeals_Arbor)
#
# Autonomous, **one-way** push of MRD Tracked Project data into the
# `LeadsDeals_Arbor` hosted feature layer, matched on a shared unique ID:
# MRD `map_id` ⇄ the layer's **`GlobalID`** field.
#
# - Runs inside ArcGIS Online Notebooks; authenticates implicitly as the notebook
#   owner via `GIS("home")`.
# - Pulls MRD data from the public `list_tracked_projects_detailed` endpoint.
# - Updates only the mapped subset of attributes on matching features; geometry
#   and all other layer attributes are left untouched.
# - `DRY_RUN=True` computes and prints the diff but writes nothing.
#
# **Matching note:** the MapID you enter in MRD must be the feature's **GlobalID**
# (a GUID). GlobalIDs are durable — they survive republish/overwrite, unlike the
# ObjectID (`FID`). Values are normalized to canonical `{UPPERCASE}` brace form on
# both sides before matching, so braces/case in MRD don't matter. The actual
# edit still targets the feature's ObjectID, read back from the matched feature.

# %%
# === PARAMETERS (override the simple values in the scheduled-task cell) ========
MRD_ENDPOINT = "https://script.google.com/macros/s/AKfycbxvtkp5OZVq4sbEELnq5nN7KSXa5DCG8lYEgzL_awPbfunUsBTyr1r6CbOH1pIbgPUk/exec"
AUTH_TOKEN   = ""        # MRD admin token (optional — endpoint is public — but recommended)

# LeadsDeals_Arbor item (from arborhomes.maps.arcgis.com). Item-id path avoids
# guessing the layer index; the notebook prints the resolved layer name to confirm.
ITEM_ID      = "c82269644ad24569aaff749f3a1d1f4a"
LAYER_INDEX  = 0
LAYER_URL    = ""        # alternative to ITEM_ID:
                         #   ".../services/LeadsDeals_Arbor/FeatureServer/<n>"

ID_FIELD     = "GlobalID"  # durable GUID match field; MRD map_id holds the GlobalID

DRY_RUN      = True      # True = compute + print the diff, write NOTHING
ONLY_ACTIVE  = True      # only sync rows whose MRD status == 'active'
BATCH_SIZE   = 200       # features per edit_features call
QUERY_CHUNK  = 500       # ids per query IN(...) clause
TERMS_SEP    = " — "     # separator joining meeting type + date into "Terms"

# %%
import json
import urllib.request
import urllib.parse
from arcgis.gis import GIS
from arcgis.features import FeatureLayer


def norm(v):
    """Trim to a comparable string; None/blank -> ''."""
    return str(v).strip() if v is not None else ""


def coerce(v):
    """Empty string -> None (ArcGIS prefers null for blanks)."""
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def sql_quote(v):
    return "'" + str(v).replace("'", "''") + "'"


def _join_nonempty(parts, sep=" — "):
    """Concatenate non-empty parts (used for the 'Terms' field)."""
    joined = sep.join(norm(p) for p in parts if norm(p))
    return joined or None


def _drive_folder_url(folder_id):
    """MRD driveFolderId -> a Google Drive folder URL (for 'FolderLink')."""
    fid = norm(folder_id)
    return ("https://drive.google.com/drive/folders/" + fid) if fid else None


def fetch_mrd_rows(endpoint, token=""):
    """GET list_tracked_projects_detailed. Tolerates a bare array or a
    {result|projects|rows: [...]} envelope."""
    params = {"action": "list_tracked_projects_detailed"}
    if token:
        params["token"] = token
    url = endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    if isinstance(data, dict):
        data = data.get("result") or data.get("projects") or data.get("rows") or []
    return data


rows = fetch_mrd_rows(MRD_ENDPOINT, AUTH_TOKEN)
print("Pulled %d Tracked Project rows from MRD" % len(rows))

# %%
# === FIELD MAPPING ============================================================
# Targets may be given as the field NAME or its display ALIAS — resolved
# case-insensitively against the live layer schema below. A target that does not
# yet exist on the layer is skipped with a WARNING (create it in AGO first).
#
#   MRD (Tracked Projects JSON)  ->  LeadsDeals_Arbor field   [Competitor Tracked Projects column]
#   projectName                  ->  LeadsDeals
#   jurisdiction                 ->  Jurisdiction
#   status                       ->  Status
#   petitionerDisplay            ->  OwnerName
#   builder                      ->  Builder        (domain-constrained, coded-value List 18)
#   lots                         ->  Lots
#   latestActionTaken            ->  Last_Result    [= the "Results" column text]
#   latestRequestSummary         ->  Terms              [= the "Description" column text]
#   latestMeetingDate            ->  Hearing_Date
#   latestYtSummaryUrl           ->  Summary            (latest summary / source-doc URL)
#   driveFolderId (-> URL)       ->  FolderLink         (link to the project's tagged-documents Drive folder)
#   mapId                        ->  GlobalID           (ID_FIELD match key — not written as an attribute)
#
# NOTE — two AGO field names are REPURPOSED from the original P94/P95 draft:
#   * "Terms"      now holds latestRequestSummary (Description text), not meeting type+date.
#   * "FolderLink" now holds latestYtSummaryUrl (summary URL), not the Drive-folder link.

# 1:1 — MRD field  ->  feature-layer field (all direct string copies).
FIELD_MAP = {
    "projectName":          "LeadsDeals",
    "jurisdiction":         "Jurisdiction",
    "status":               "Status",
    "petitionerDisplay":    "OwnerName",
    "builder":              "Builder",       # domain-constrained (List 18) —
                                             # MRD builder text must match an allowed value
    "lots":                 "Lots",
    "latestActionTaken":    "Last_Result",   # "Results" column text — Agenda_Items outcome+vote;
                                             # blank when the project has no summarized hearing yet
    "latestRequestSummary": "Terms",         # "Description" column text — parsed "Request:" summary
    "latestMeetingDate":    "Hearing_Date",  # latest meeting / hearing date (M/D/YYYY text)
    "latestYtSummaryUrl":   "Summary",       # latest summary / source-doc URL
}

# Computed -> feature-layer field. Each value is a function of the MRD row.
#   FolderLink = the project's tagged-documents Google Drive folder, as a
#   clickable URL built from driveFolderId. Rows with no folder id -> None (skipped).
DERIVED_MAP = {
    "FolderLink": lambda r: _drive_folder_url(r.get("driveFolderId")),
}
# (For reference — the old derivation that is now a direct 1:1 map instead:
#   "Terms": lambda r: _join_nonempty([r.get("latestMeetingType"),
#                                      r.get("latestMeetingDate")], TERMS_SEP),)

# %%
# Filter to rows that carry a non-empty map_id (and optionally status==active).
sync_rows = []
for p in rows:
    if not norm(p.get("mapId")):
        continue
    if ONLY_ACTIVE and norm(p.get("status")).lower() != "active":
        continue
    sync_rows.append(p)
print("%d row(s) have a non-empty mapId%s"
      % (len(sync_rows), " and status=active" if ONLY_ACTIVE else ""))

# Connect as the notebook owner and resolve the target layer.
gis = GIS("home")
if LAYER_URL:
    lyr = FeatureLayer(LAYER_URL, gis)
else:
    lyr = gis.content.get(ITEM_ID).layers[LAYER_INDEX]
print("Target layer:", lyr.properties.name)

# Print the live schema (name | alias | type) and build a name/alias lookup so
# FIELD_MAP/DERIVED_MAP targets resolve whether given as a field name or alias.
oid_field = lyr.properties.objectIdField or "OBJECTID"
fl_fields = {f["name"] for f in lyr.properties.fields}
field_lookup = {}
print("Layer fields (name | alias | type):")
for f in lyr.properties.fields:
    field_lookup[f["name"].lower()] = f["name"]
    if f.get("alias"):
        field_lookup.setdefault(f["alias"].lower(), f["name"])
    print("  %-18s | %-18s | %s" % (f["name"], f.get("alias", ""), f["type"]))
print("ObjectID field:", oid_field)

# %%
# Resolve OBJECTIDs for every map_id by querying the shared ID field (chunked).
id_field_type = next((f["type"] for f in lyr.properties.fields if f["name"] == ID_FIELD),
                     "esriFieldTypeString")
is_guid_id   = id_field_type in ("esriFieldTypeGlobalID", "esriFieldTypeGUID")
is_quoted_id = is_guid_id or id_field_type == "esriFieldTypeString"


def canon(v):
    """Canonical comparison key. For GUID/GlobalID fields, normalize to the
    hosted-FL standard {UPPERCASE} brace form so braces/case in the MRD value
    don't matter. Otherwise just a trimmed string."""
    s = norm(v)
    if is_guid_id and s:
        s = s.upper()
        if not s.startswith("{"):
            s = "{" + s + "}"
    return s


def sql_val(v):
    return sql_quote(v) if is_quoted_id else str(v)


# Guard: when matching on a GUID/GlobalID field, every map_id must be a
# well-formed GUID. A stray URL or placeholder pasted into MRD map_id would
# otherwise make the whole `IN (...)` query invalid (ArcGIS 400 "Invalid query
# parameters") and abort the run. Such ids are skipped + logged, not fatal.
import re as _re
_GUID_RE = _re.compile(r"^\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}$")


def _valid_id(canon_val):
    if not canon_val:
        return False
    return bool(_GUID_RE.match(canon_val)) if is_guid_id else True


_all_ids = sorted({canon(p.get("mapId")) for p in sync_rows})
ids      = [x for x in _all_ids if _valid_id(x)]
_bad_ids = [x for x in _all_ids if not _valid_id(x)]
if _bad_ids:
    _bad_names = sorted({norm(p.get("projectName")) for p in sync_rows
                         if not _valid_id(canon(p.get("mapId")))})
    print("WARNING: skipping %d map_id value(s) that are not valid %s GUIDs "
          "(fix these in MRD):" % (len(_bad_ids), ID_FIELD))
    for _b in _bad_ids[:20]:
        print("    ", _b[:90])
    print("    affected projects:", ", ".join(_bad_names[:20]))

id_to_features = {}   # canon(id) -> list of current attribute dicts (>1 if id not unique)
for chunk in chunked(ids, QUERY_CHUNK):
    where = "%s IN (%s)" % (ID_FIELD, ",".join(sql_val(x) for x in chunk))
    fs = lyr.query(where=where, out_fields="*", return_geometry=False)
    for feat in fs.features:
        id_to_features.setdefault(canon(feat.attributes.get(ID_FIELD)), []).append(feat.attributes)

matched = [m for m in ids if m in id_to_features]
unmatched = [m for m in ids if m not in id_to_features]
print("Matched %d / %d mapIds to features; %d unmatched (skipped)"
      % (len(matched), len(ids), len(unmatched)))
if unmatched:
    print("  unmatched mapIds:", unmatched[:20], "..." if len(unmatched) > 20 else "")

# %%
# Build the update set — only features whose mapped attributes actually changed.
def resolve(label):
    return field_lookup.get(str(label).strip().lower())


resolved_1to1 = {}
for src, label in FIELD_MAP.items():
    real = resolve(label)
    if real:
        resolved_1to1[src] = real
    else:
        print("WARNING: FIELD_MAP target not on layer, skipped:", label)

resolved_derived = {}
for label, fn in DERIVED_MAP.items():
    real = resolve(label)
    if real:
        resolved_derived[real] = fn
    else:
        print("WARNING: DERIVED_MAP target not on layer, skipped:", label)


def diff_into(attrs, diffs, dst, new_val, cur):
    old_val = cur.get(dst)
    old_norm = None if (isinstance(old_val, str) and old_val.strip() == "") else old_val
    if new_val != old_norm:
        attrs[dst] = new_val
        diffs[dst] = (old_norm, new_val)


row_by_id = {canon(p.get("mapId")): p for p in sync_rows}
updates, changed_log = [], []
for mid in matched:
    src_row = row_by_id[mid]
    for cur in id_to_features[mid]:          # one map_id may hit >1 feature
        attrs = {oid_field: cur[oid_field]}
        diffs = {}
        for src, dst in resolved_1to1.items():
            diff_into(attrs, diffs, dst, coerce(src_row.get(src)), cur)
        for dst, fn in resolved_derived.items():
            diff_into(attrs, diffs, dst, coerce(fn(src_row)), cur)
        if diffs:
            updates.append({"attributes": attrs})
            changed_log.append((mid, cur[oid_field], diffs))

print("%d feature(s) need updating (changed fields only)" % len(updates))
for mid, oid, diffs in changed_log[:25]:
    print("  FID %s:" % oid)
    for dst, (o, n) in diffs.items():
        print("      %s: %r -> %r" % (dst, o, n))
if len(changed_log) > 25:
    print("  ... and %d more" % (len(changed_log) - 25))

# %%
# Apply (gated by DRY_RUN), chunked.
if DRY_RUN:
    print("DRY_RUN=True — no writes performed. Set DRY_RUN=False to apply.")
elif not updates:
    print("Nothing to update — all matched features already current.")
else:
    ok = err = 0
    for batch in chunked(updates, BATCH_SIZE):
        try:
            res = lyr.edit_features(updates=batch)
            for r in res.get("updateResults", []):
                if r.get("success"):
                    ok += 1
                else:
                    err += 1
                    print("  update failed:", r)
        except Exception as e:                       # noqa: BLE001
            err += len(batch)
            print("  batch error:", e)
    print("Applied: %d updated, %d failed" % (ok, err))

# %% [markdown]
# ## Scheduling
#
# 1. Run manually with `DRY_RUN=True`; review the printed schema + diff.
# 2. Flip `DRY_RUN=False`, run once, verify in the layer's Data table / Map Viewer.
# 3. Notebook editor → **Tasks → Schedule a task** → daily (15-minute minimum).
#    Put live values (`AUTH_TOKEN`, `DRY_RUN=False`) in the task's **Parameters**
#    cell. Runtime must be **3.0 or later** for automated execution.
#
# Programmatic alternative (run once):
# ```python
# gis = GIS("home")
# nb_item = gis.content.get("<this notebook's item id>")
# gis.tasks.create(item=nb_item, task_type="ExecuteNotebook",
#                  cron="0 7 * * *", title="MRD->ArcGIS daily sync")
# ```
