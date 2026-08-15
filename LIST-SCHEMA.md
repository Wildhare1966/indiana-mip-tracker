# LIST-SCHEMA.md — MRD core SharePoint Lists

**Repo:** `wildhare1966/indiana-mip-tracker` · **Branch:** `claude/pm-dashboard-inventory-feasibility-ergvm5` · **Date:** 2026-07-21

> **Graph-scripted creation (EXECUTION-BRIEF-v2 Step 3A / `list-schema.json`) is DEPRECATED** by the 2026-07-21 Power Apps decision. Lists will be created via the **Microsoft Lists / SharePoint UI or the CLI (`m365`/PnP)**, not a Graph creation script. The Graph JSON format is therefore intentionally **not** produced here. This file is the human/CLI-facing column definition set only, pending a v3 brief.

## Scope note (entity mapping)

The dispatching brief's "three lists (Deals / Tasks / third + a Tasks→Deals lookup)" do not exist in this repo. The nearest real analogs — and the three most central transactional lists in MRD — are:

| Brief's placeholder | MRD list (this file) | Role |
|---|---|---|
| **Deals** (parent) | **`Tracked_Projects`** | Primary editable entity; every item links up to it. |
| **Tasks** (child, lookup→Deals) | **`Agenda_Items`** | Parsed agenda-doc items; lookup → Tracked_Projects. |
| **third** | **`Youtube_Items`** | Parsed video/minutes items; lookup → Tracked_Projects **and** a self-pair lookup → Agenda_Items. |

Supporting lookups referenced below (`Jurisdictions`, `Members`, `Meetings`) are defined briefly at the end; full schemas for the remaining ~8 entities (Candidates, Suggested_References, Review_Queue, Parse_Census, Tagged_Documents) are out of scope for this pass and belong in the v3 brief.

Column **types** use Microsoft Lists names: *Single line of text, Multiple lines of text, Number, Currency, Choice, Date and time, Hyperlink, Yes/No, Lookup, Person or Group*. `Indexed = Yes` marks columns that MUST carry a list index so delegable `eq`/`StartsWith`/date-range queries stay under the 5,000-item list-view threshold (see FUNCTION-INVENTORY.md delegation verdict). Internal (CSV header) names are given in `code`.

---

## LIST 1 — `Tracked_Projects` (the "Deals" analog)

Primary key surfaced to users = **Title** (project name). Backend id `project_id` becomes the SharePoint item ID.

| Display name | Internal (`code`) | Lists type | Required | Indexed | Choices / notes |
|---|---|---|---|---|---|
| Title (Project Name) | `project_name` | Single line of text | **Yes** | **Yes** | The one required field in the current Add form. |
| Ordinance Number | `ordinance_id` | Single line of text | No | **Yes** | e.g. `ORD-2025-14`, `RZ-24-08`. Matched against agenda items. |
| Aliases / Add'l Ord #s | `aliases` | Multiple lines of text | No | No | Comma-separated today; **prefer a related `Project_Aliases` list** (one alias per row) so matching is delegable. |
| Jurisdiction | `jurisdiction` | Lookup → `Jurisdictions.Title` | No | **Yes** | Blank = "all". Add a stored `juris_key` (normalized) for delegable filtering (rail uses a normalized name today). |
| Petitioner / Applicant | `petitioner` | Single line of text | No | No | |
| Builder | `builder` | Choice | No | **Yes** | Arbor; Beazer; Custom; David Weekly; Davis; DR Horton; Drees; Epcon; Estridge; Fischer Homes; Forestar; Hallmark; Lennar; MI Homes; Old Town; Olthof; Onyx_East; Pulte; Ryan; Taylor Morris. *(Fill-in allowed; mirror the ArcGIS coded-value domain.)* |
| Lots | `lots` | Number | No | No | Gemini-extracted, manually editable (integer ≥ 0). |
| Status | `status` | Choice | **Yes** | **Yes** | `active` (Competitor Proposed); `competitor_active` (Competitor Active); `arbor_active` (Arbor Active); `archived` (Archive); `closed`; `deleted` (soft-delete, hidden). Default `active`. |
| Map URL | `map_url` | Hyperlink | No | No | ArcGIS / parcel link. |
| Map ID | `map_id` | Single line of text | No | **Yes** | Manual ArcGIS record key for MRD→ArcGIS sync (see `arcgis/`). |
| Meeting Type (override) | `manual_meeting_type` | Choice | No | No | Council; Plan Commission; BZA; Minutes; Agenda. Overrides the derived value. |
| Meeting Date (override) | `manual_meeting_date` | Date and time | No | **Yes** | Overrides the derived latest meeting date. |
| Description (override) | `manual_description` | Multiple lines of text | No | No | Falls back to the matched Agenda Item's request summary. |
| Results (override) | `manual_results` | Multiple lines of text | No | No | Falls back to matched item Outcome + Vote. |
| Overrides As-Of | `manual_overrides_asof` | Date and time | No | No | Timestamp that auto-**expires** manual overrides once a newer AI summary lands (Power Automate-computed). |
| Created | `created_date` | Date and time | No | **Yes** | (or use the built-in Created column.) |

**Derived / rollup columns (do NOT store as free-text; compute via Power Automate into a materialized column or show in Power BI):** `latest_meeting_date`, `latest_ref_date`, `latest_request_summary`, `latest_action_taken`, `latest_yt_summary_url`, `summary_is_detailed`, `agenda_refs[]`, `tagged_doc_count`. These come from the 4-entity `list_tracked_projects_detailed` join and are the app's core delegation problem (see FUNCTION-INVENTORY Cluster C).

---

## LIST 2 — `Agenda_Items` (the "Tasks" analog — lookup → Tracked_Projects)

One row per item parsed from a Council / Plan-Commission **agenda document**. **~few thousand rows → index aggressively.**

| Display name | Internal (`code`) | Lists type | Required | Indexed | Choices / notes |
|---|---|---|---|---|---|
| Title (Item) | `item_title` | Single line of text | **Yes** | No | Short item label. |
| Item ID | `item_id` | Single line of text | **Yes** | **Yes** | Stable backend id. |
| **Matched Project** | `matched_project_id` | **Lookup → `Tracked_Projects` (ID)** | No | **Yes** | **This is the "Tasks→Deals" lookup.** Null when unmatched. |
| Auto-Linked | `auto_linked` | Yes/No | No | **Yes** | Whether the match was auto-applied. High-but-not-linked = the "auto-match gap". |
| Match Confidence | `match_confidence` | Choice | No | **Yes** | `High`; `Medium`; `None`. *(AI/rules-computed — non-delegable to recompute in-app.)* |
| Match Criteria | `match_criteria` | Multiple lines of text | No | No | Human-readable reason for the match. |
| Match Count | `match_count` | Number | No | No | >1 signals ambiguity ("+N more"). |
| Candidate Confidence | `candidate_confidence` | Choice | No | **Yes** | `high`; `low`. |
| Candidate Criteria | `candidate_criteria` | Multiple lines of text | No | No | |
| Jurisdiction | `jurisdiction` | Lookup → `Jurisdictions.Title` | No | **Yes** | |
| Project Name (parsed) | `project_name` | Single line of text | No | **Yes** | As seen on the agenda (pre-match). |
| Ordinance Number (parsed) | `ordinance_number` | Single line of text | No | **Yes** | |
| Request Type | `request_type` | Single line of text | No | No | Rezoning / Plat / Variance / etc. |
| Description (Request Summary) | `description` | Multiple lines of text | No | No | The "Request:" line. |
| Petitioner | `petitioner` | Single line of text | No | No | |
| Meeting | `meeting_id` | Lookup → `Meetings` (ID) | No | **Yes** | |
| Meeting Date | `meeting_date` | Date and time | No | **Yes** | Enables delegable date-range (weekly calendar, "past week"). |
| Body | `body` | Choice | No | **Yes** | `Council`; `Plan Commission`; `BZA`. |
| Source URL | `source_url` | Hyperlink | No | No | Agenda document. |
| Review State | `review_status` | Choice | No | **Yes** | `new`; `tracked`; `added`; `dismissed`. Dismiss is reversible. |

---

## LIST 3 — `Youtube_Items` (the "third" list — lookup → Tracked_Projects + self-pair → Agenda_Items)

One row per item parsed from a **YouTube hearing video / minutes summary**. Same core columns as `Agenda_Items` plus outcome fields and the cross-stream pairing.

| Display name | Internal (`code`) | Lists type | Required | Indexed | Choices / notes |
|---|---|---|---|---|---|
| Title (Item) | `item_title` | Single line of text | **Yes** | No | |
| Item ID | `item_id` | Single line of text | **Yes** | **Yes** | |
| **Matched Project** | `matched_project_id` | **Lookup → `Tracked_Projects` (ID)** | No | **Yes** | The "→Deals" lookup. |
| **Paired Agenda Item** | `agenda_item_id` | **Lookup → `Agenda_Items` (ID)** | No | **Yes** | Cross-stream twin for the same meeting (AI/heuristic pairing). |
| Agenda Match How | `agenda_match_how` | Single line of text | No | No | Why the twin was paired (ord#/name). |
| Match Confidence | `match_confidence` | Choice | No | **Yes** | `High`; `Medium`; `None`. |
| Candidate Confidence | `candidate_confidence` | Choice | No | **Yes** | `high`; `low`. |
| Outcome / Action Taken | `outcome` | Single line of text | No | No | Vote / result parsed from the hearing. |
| Additional Notes | `additional_notes` | Multiple lines of text | No | No | |
| Jurisdiction | `jurisdiction` | Lookup → `Jurisdictions.Title` | No | **Yes** | |
| Project Name (parsed) | `project_name` | Single line of text | No | **Yes** | |
| Ordinance Number (parsed) | `ordinance_number` | Single line of text | No | **Yes** | |
| Description | `description` | Multiple lines of text | No | No | |
| Petitioner | `petitioner` | Single line of text | No | No | |
| Meeting | `meeting_id` | Lookup → `Meetings` (ID) | No | **Yes** | |
| Meeting Date | `meeting_date` | Date and time | No | **Yes** | |
| Summary Doc | `summary_doc_url` | Hyperlink | No | No | AI-generated summary document link. |
| Video URL | `youtube_url` | Hyperlink | No | No | |
| Video Title | `video_title` | Single line of text | No | No | |
| Review State | `review_status` | Choice | No | **Yes** | `new`; `tracked`; `added`; `dismissed`. |

---

## Supporting lookup lists (referenced above — brief definitions)

**`Jurisdictions`** — `Title` (name, **indexed**), `juris_key` (normalized, **indexed**), `county` (Choice: Hamilton; Boone; Johnson; Hancock; Hendricks; Tippecanoe; Shelby; Madison; Delaware — **indexed**), `political` (text), `receptivity` (Choice: high; med; low; mixed), `notes` (multi-line), URL columns (`udo_url`, `rezoning_app_url`, `plat_url`, `schedule_url`). ~30 rows — delegation moot.

**`Members`** — `Title` (name), `member_key` (`muniId::body::name`, **indexed**), `Jurisdiction` (Lookup, **indexed**), `body` (Choice: Council; Plan Commission; BZA — **indexed**), `role`, `party` (Choice: R; D; I; NP), `term`, `notes` (multi-line), `verified` (Yes/No — **replaces the current localStorage-only flag**), profile-research fields (`professional_background`, `_last_researched`, `_profile_confidence`) populated by a flow.

**`Meetings`** — `Title` (meeting label), `meeting_id` (**indexed**), `Jurisdiction` (Lookup, **indexed**), `meeting_date` (Date, **indexed**), `body_type` (Choice), `meeting_type` (Choice: Council; Plan Commission; BZA; Minutes; Agenda), `youtube_url`, `video_title`, `summary_doc_url`, `minutes_url`, `coverage_state` (Choice), `cancelled` (Yes/No).

## Seed data

Representative seed CSVs (headers = the internal `code` names above) accompany this file at repo root, each with **≥2 rows containing HTML-special characters** (`&`, `<`, `>`, `"`, `'`) to exercise column formatting / escaping on import:

- `seed-tracked-projects.csv` (25 rows)
- `seed-agenda-items.csv` (22 rows; `matched_project_id` references the tracked-project rows)
- `seed-youtube-items.csv` (20 rows; references both tracked projects and agenda items)
