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
AUTH_TOKEN   = "457091386b65a26b4d11fb3b9fee7bd5233c952ceb5d4a41"
                         # MRD read token. list_tracked_projects_detailed is public,
                         # but the `hearings` wire (used to resolve the Summary doc
                         # URL — see _summary_doc_for) requires it. This token is
                         # already public in the MRD frontend; blank it to skip the
                         # Summary-doc resolution (Summary then stays blank).

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
import re
import urllib.request
import urllib.parse
from datetime import datetime
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


def _lots_num(v):
    """MRD 'lots' is free text but the layer 'Lots' field is Double. Extract the
    first numeric token; null-ish / non-numeric -> None (so the value is simply
    not written, rather than failing the whole edit batch on a type error).
    e.g. '96' -> 96.0, '~630 (322 single-family...)' -> 630.0, 'null' -> None."""
    s = norm(v).lower()
    if s in ("", "null", "none", "n/a", "na", "tbd", "?"):
        return None
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None


def _date_only(v):
    """MRD 'latestMeetingDate' is M/D/YYYY text; the layer 'Hearing_Date' field is
    esriFieldTypeDateOnly, which the REST API writes as a 'YYYY-MM-DD' string.
    Unparseable -> None. e.g. '5/26/2026' -> '2026-05-26'."""
    s = norm(v)
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


# MRD stores `status` as a CODE; the MRD UI (and the layer's Status field) want
# the human label. Mirrors the FE dropdown in index.html. With ONLY_ACTIVE=True
# only 'active' rows sync, so synced features read "Competitor Proposed".
_STATUS_LABELS = {
    "active":            "Competitor Proposed",
    "competitor_active": "Competitor Active",
    "archived":          "Archive",
}


def _status_label(v):
    """MRD status code -> the label shown in the MRD Status dropdown / layer."""
    s = norm(v).lower()
    return _STATUS_LABELS.get(s) or (norm(v) or None)


def _mrd_get(endpoint, action, token="", **extra):
    """GET an MRD endpoint action -> parsed JSON (unwrapped from a {result:…}
    envelope when present)."""
    params = {"action": action}
    if token:
        params["token"] = token
    params.update(extra)
    url = endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    if isinstance(data, dict) and "result" in data:
        return data["result"]
    return data


def fetch_mrd_rows(endpoint, token=""):
    """GET list_tracked_projects_detailed. Tolerates a bare array or a
    {result|projects|rows: [...]} envelope."""
    data = _mrd_get(endpoint, "list_tracked_projects_detailed", token)
    if isinstance(data, dict):
        data = data.get("projects") or data.get("rows") or []
    return data


# --- Summary-doc resolution ---------------------------------------------------
# The MRD `latestYtSummaryUrl` field is really "latest SOURCE url" — a YouTube
# video link when the latest ref is a video, or the agenda/portal URL otherwise
# (inconsistent). The actual "YouTube Summary" is the Gemini summary Google Doc,
# which lives on the `hearings` wire as `summary_doc` (keyed by jurisdiction +
# date). Build a (juris_id, yyyy-mm-dd) -> summary_doc index and resolve each
# project by jurisdiction + latestMeetingDate — mirroring the FE's
# _tpFindSummaryDocFor() exactly (first hearing on that date with a doc).
def _build_summary_index(endpoint, token):
    """Returns (index, name_to_id). index[(juris_id, ymd)] = summary_doc URL."""
    index, name_to_id = {}, {}
    if not token:
        print("  (no AUTH_TOKEN -> skipping Summary-doc resolution; Summary stays blank)")
        return index, name_to_id
    try:
        munis = _mrd_get(endpoint, "municipalities", token)
        if isinstance(munis, dict):
            munis = munis.get("municipalities") or munis.get("rows") or []
        for m in munis or []:
            mid = norm(m.get("id")).lower()
            if mid:
                name_to_id[mid] = mid
                if norm(m.get("name")):
                    name_to_id[norm(m.get("name")).lower()] = mid
        hearings = _mrd_get(endpoint, "hearings", token)
        if isinstance(hearings, dict):
            for k, arr in hearings.items():
                if not isinstance(arr, list):
                    continue
                for h in arr:
                    d = _date_only(h.get("date") or h.get("meeting_date"))
                    sd = norm(h.get("summary_doc"))
                    if d and sd:
                        index.setdefault((k.lower(), d), sd)
        print("  summary-doc index: %d (juris,date) entries" % len(index))
    except Exception as e:                                   # noqa: BLE001
        print("  WARNING: could not build summary-doc index (%s) -> Summary blank" % e)
    return index, name_to_id


def _summary_doc_for(r):
    """Resolve a project's YouTube Summary doc URL from the hearings index by
    jurisdiction + latestMeetingDate. No match -> None (blank, rather than the
    misleading video/agenda URL in latestYtSummaryUrl)."""
    d = _date_only(r.get("latestMeetingDate"))
    if not d:
        return None
    jr = norm(r.get("jurisdiction")).lower()
    for k in (jr, _MUNI_NAME_TO_ID.get(jr, "")):
        if k and (k, d) in _SUMMARY_INDEX:
            return _SUMMARY_INDEX[(k, d)]
    return None


rows = fetch_mrd_rows(MRD_ENDPOINT, AUTH_TOKEN)
print("Pulled %d Tracked Project rows from MRD" % len(rows))
_SUMMARY_INDEX, _MUNI_NAME_TO_ID = _build_summary_index(MRD_ENDPOINT, AUTH_TOKEN)

# %%
# === FIELD MAPPING ============================================================
# Targets may be given as the field NAME or its display ALIAS — resolved
# case-insensitively against the live layer schema below. A target that does not
# yet exist on the layer is skipped with a WARNING (create it in AGO first).
#
#   MRD (Tracked Projects JSON)  ->  LeadsDeals_Arbor field   [Competitor Tracked Projects column]
#   projectName                  ->  LeadsDeals
#   jurisdiction                 ->  Jurisdiction
#   status                       ->  Status         (code -> label: active=Competitor Proposed,
#                                                     competitor_active=Competitor Active, archived=Archive)
#   petitionerDisplay            ->  OwnerName
#   builder                      ->  Builder        (domain-constrained, coded-value List 18)
#   lots                         ->  Lots           (Double — first numeric token; non-numeric -> blank)
#   latestActionTaken            ->  Last_Result    [= the "Results" column text]
#   latestRequestSummary         ->  Terms              [= the "Description" column text]
#   latestAgendaUrl              ->  Recent_Agenda      (latest agenda document URL)
#   latestMeetingType            ->  Recent_Hearing     (latest meeting/hearing body type)
#   latestMeetingDate            ->  Hearing_Date   (DateOnly — coerced M/D/YYYY -> YYYY-MM-DD)
#   (hearings.summary_doc)       ->  Summary            (Gemini summary DOC, resolved by juris+date;
#                                                        NOT latestYtSummaryUrl, which is the video/agenda URL)
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
    "petitionerDisplay":    "OwnerName",
    "builder":              "Builder",       # domain-constrained (List 18) —
                                             # MRD builder text must match an allowed value
    "latestActionTaken":    "Last_Result",   # "Results" column text — Agenda_Items outcome+vote;
                                             # blank when the project has no summarized hearing yet
    "latestRequestSummary": "Terms",         # "Description" column text — parsed "Request:" summary
    "latestAgendaUrl":      "Recent_Agenda",  # latest agenda document URL (latest_* cache)
    "latestMeetingType":    "Recent_Hearing",  # latest meeting/hearing body type (e.g. Plan Commission)
}
# NOTE: `lots` and `latestMeetingDate` are NOT in FIELD_MAP — their targets are
# typed (Lots=Double, Hearing_Date=DateOnly), so they go through DERIVED_MAP with
# a type-coercing function instead of a raw string copy (a raw string write would
# fail the edit batch on a non-numeric / non-date value).

# Computed -> feature-layer field. Each value is a function of the MRD row.
#   FolderLink = the project's tagged-documents Google Drive folder, as a
#   clickable URL built from driveFolderId. Rows with no folder id -> None (skipped).
DERIVED_MAP = {
    "FolderLink":   lambda r: _drive_folder_url(r.get("driveFolderId")),
    "Lots":         lambda r: _lots_num(r.get("lots")),                # Double — numeric token only
    "Hearing_Date": lambda r: _date_only(r.get("latestMeetingDate")),  # DateOnly — YYYY-MM-DD
    "Status":       lambda r: _status_label(r.get("status")),          # code -> MRD Status label
    "Summary":      lambda r: _summary_doc_for(r),                     # Gemini summary DOC (not video/agenda)
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
# Print the exact write target so it can be confirmed against the layer you view
# in AGO (a "success but nothing changed" symptom is usually a wrong target/view
# or a stale table cache — the read-back below disambiguates).
print("Write target -> layer:", lyr.properties.name, "| url:", lyr.url)
if DRY_RUN:
    print("DRY_RUN=True — no writes performed. Set DRY_RUN=False to apply.")
elif not updates:
    print("Nothing to update — all matched features already current.")
else:
    ok = err = 0
    edited_oids = []
    for bi, batch in enumerate(chunked(updates, BATCH_SIZE)):
        try:
            res = lyr.edit_features(updates=batch)
            if bi == 0:
                print("Raw edit_features response (first batch, truncated):")
                print("   ", json.dumps(res)[:1500])
            for r in res.get("updateResults", []):
                if r.get("success"):
                    ok += 1
                    edited_oids.append(r.get("objectId"))
                else:
                    err += 1
                    print("  update failed:", r)
        except Exception as e:                       # noqa: BLE001
            err += len(batch)
            print("  batch error:", e)
    print("Applied: %d updated, %d failed" % (ok, err))

    # Read-back verification — re-query the just-edited features and confirm the
    # write actually persisted on THIS layer. If Status here shows the new value
    # ('active') + a fresh EditDate, the write landed (you were viewing a cache);
    # if it still shows the OLD value, the edit did not persist to this layer.
    oids = [o for o in edited_oids if o is not None]
    if oids:
        vq = lyr.query(where="%s IN (%s)" % (oid_field, ",".join(str(o) for o in oids)),
                       out_fields="%s,Status,EditDate" % oid_field,
                       return_geometry=False)
        print("Read-back of %d edited feature(s):" % len(vq.features))
        for f in vq.features:
            a = f.attributes
            print("   FID %s  Status=%r  EditDate=%r"
                  % (a.get(oid_field), a.get("Status"), a.get("EditDate")))

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
