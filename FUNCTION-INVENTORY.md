# FUNCTION-INVENTORY.md — Municipal Resource Dashboard (MRD)
## Power Apps (canvas) + SharePoint Lists rebuild feasibility

**Repo:** `wildhare1966/indiana-mip-tracker` · **Branch:** `claude/pm-dashboard-inventory-feasibility-ergvm5`
**Date:** 2026-07-21 · **Inventory pass:** B · **Status:** documentation only — no application source modified.
**Architecture decision (2026-07-21):** Power Apps canvas + SharePoint Lists wins over the custom HTML Lists port. Ruling per IT: custody + scalability (Microsoft 365 tenant governance, backup, and identity beat a self-hosted Google Apps Script + Sheets stack fronted by a static HTML SPA).

---

### ⚠️ Scope reconciliation — read first

The dispatching brief describes a *"project-manager app"* backed by *"three lists (Deals, Tasks, third)"* living in a `pm-dashboard-lists` repo. **That does not match this repo.** What is actually here is the **Municipal Resource Dashboard (MRD)** — a 14-view single-page app (`index.html`, 12,160 lines) plus two embedded analytical dashboards (`dashboard.html` = Zonda market intel; `sales_dashboard.html` = Sales Disclosures), backed by a **Google Apps Script web app over Google Sheets**, not three lists.

Decisions taken so I could still deliver the real task:
- **"Three lists" → the app's actual data entities.** MRD spans ~13 logical backend entities (see the entity map below), not three. I inventoried against the real entities and mapped each to the SharePoint List it would become.
- **"Deals"** almost certainly refers to `leadsdeals-reporter.html`, which was **removed from this repo** in commit `1d068cb` ("moved to standalone repo Wildhare1966/entitlement-reporter"). It is out of scope here.
- **No `snapshot.data.js`** exists; data shapes were taken from the six CSVs in `Data/`, the backend `action=`/`fn=` surface, and the DOM.
- **No pre-existing `HANDOFF.md` or `EXECUTION-BRIEF-v2`** exists in this repo. `HANDOFF.md` is created new by this pass; the EXECUTION-BRIEF-v2 references (Steps 2/3A/3B) are recorded as deprecated pending a v3 brief.

Everything below inventories the **real** app.

---

### How to read the grades

| Grade | Meaning |
|---|---|
| **GRADE 1 — Lists-native** | Free in Microsoft Lists: views, JSON column formatting, list rules, built-in forms. No app build. |
| **GRADE 2 — Standard Power Apps** | A canvas commonplace: gallery, form, filter, search, dropdown-driven view. Any maker template covers it. |
| **GRADE 3 — Custom Power Fx** | Real logic to write: cross-list rollups, conditional cascades, computed statuses, branching. A Power Fx sketch is given. |
| **GRADE 4 — Needs redesign** | No clean equivalent. Nearest Power Platform alternative named (Power Automate flow, Power BI visual, AI Builder / Azure OpenAI, external service, export workaround) with what the user loses. |

**⚠ NON-DELEGABLE** marks any filter/sort/search whose logic SharePoint cannot delegate (`contains`/substring text search, `in`-set membership, `Distinct`, sorts/filters over lookup or computed columns, cross-list aggregates). Against the stated scale — **a few thousand Agenda/Youtube item rows** — these silently truncate at the 500–2000 row delegation ceiling and return *wrong* answers, not errors. Every Grade 1/2 item carrying a delegation problem is flagged; the fix (a stored `eq`-able key column, a pre-aggregated summary list refreshed by flow, or Power BI) is noted inline.

---

### Data-entity → SharePoint List map (the real "lists")

| # | MRD entity (today) | Backing store today | → SharePoint List | Approx. row scale | Notes |
|---|---|---|---|---|---|
| 1 | **Tracked Projects** | Sheet `Tracked_Projects` via `list_tracked_projects_detailed` | `Tracked_Projects` | 100s–1,000s | Primary editable list. Lookup targets for items. |
| 2 | **Agenda Items** | `getAgendaItemsFeedJSON` (agenda-doc stream) | `Agenda_Items` | **few thousand** | Delegation-critical. Lookup → Tracked_Projects. |
| 3 | **Youtube Items** | `getAgendaItemsFeedJSON` (video/minutes stream) | `Youtube_Items` | **few thousand** | Delegation-critical. Paired to Agenda_Items. |
| 4 | **Members** (council/PC) | muni bootstrap + `member_profiles` | `Members` | ~500–1,000 | Profile-research fields fed by external AI. |
| 5 | **Jurisdictions / Municipalities** | muni bootstrap | `Jurisdictions` | ~30 | Small — delegation moot. |
| 6 | **Hearings / Meetings** | `meeting_dates`, `refresh-hearings` | `Meetings` | 1,000s | Weekly calendar + review pipeline. |
| 7 | **Candidates** | `getAgendaCandidatesJSON` | `Agenda_Candidates` | 100s–1,000s | Auto-detected potential projects. |
| 8 | **Suggested References** | `suggested_references` | `Suggested_References` | 100s | Medium-confidence match queue. |
| 9 | **Review Queue** | `review_queue` | `Review_Queue` | 10s–100s | Operator terminal-state decisions. |
| 10 | **Parse Census** | `getAgendaParseReviewJSON` / `auditAgendaExtractionDocs` | `Parse_Census` | 1,000s | Per-document extraction outcome triage. |
| 11 | **Tagged Documents** | `list_project_documents`, `tag_document` | `Tagged_Documents` | 1,000s | Child of Tracked_Projects (attachments/links). |
| 12 | **Zonda market data** | 6 CSVs in `Data/` (up to 25,600 rows) | *Power BI dataset* (not a List) | 10,000s | See Cluster F — analytical, not transactional. |
| 13 | **Sales Disclosures** | `ExistingTransactions.csv` (7,686 rows) + data-sales branch | *Power BI dataset* (not a List) | 1,000s–10,000s | See Cluster F. |
| — | Config (theme, sources, tags, keys, operator flag) | browser `localStorage` | user-settings List / `SaveData` / Key Vault | trivial | Secrets must move to Key Vault, not canvas controls. |


---

## CLUSTER A — Shell, Navigation, Settings, Diagnostics

Source file: `index.html` (12,160 lines). Every function below is user-facing (a button, link, toggle, input, dropdown, or collapsible section). Backend calls go to a Google Apps Script web app via `getWebAppUrl()` (line 807) as `?action=…` / `&fn=…`; a few hit a **local** helper server at `http://localhost:8765`. Config marked "browser localStorage" never touches a Sheet.

### A1 — Top Navigation Bar (lines 19–52)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Switch view (14 views) | Click a nav tab to show one of 14 views (Overview, Jurisdictions, Agenda Items, Youtube Items, Candidates, Suggested Matches, Parse Status, Competitor Tracked Projects, Schedule & Requirements, Zonda, Sales Disclosures, Settings, Review Queue, + hidden Hearing Schedule) | `switchView()` L2261; nav buttons L22–39 | none/UI-only (toggles `.view`/`.active` classes; lazy-loads iframes for `market`/`salesdisclosures`; hides sidebar on those two; calls `initSettings()` on settings) | GRADE 2 | Standard multi-screen canvas app = one Screen per view + a nav component. Mobile: 14 tabs won't fit a phone width — needs a hamburger/dropdown nav. Pure UI → no delegation. |
| Toggle light/dark theme | Sun/moon button flips theme, persisted per-browser | `toggleTheme()` L2023, `applyTheme()` L2012, button L44 | browser localStorage: `mrd_theme`; re-points Zonda/SDF iframes with `?theme=` | GRADE 3 | Power Apps has no native dark mode. Emulate with a global `varTheme` context variable + color tokens on every control, persisted via `SaveData`/`LoadData`. `Set(varTheme, If(varTheme="dark","light","dark")); SaveData([varTheme],"theme")`. Per-control color logic = custom Power Fx across the whole app. |
| Refresh Hearings | Re-fetches hearing records, then reloads page | `refreshHearings()` L5278, button L49 | Calls **`http://localhost:8765/api/refresh-hearings`** (local Python helper), then `location.reload()` → Meetings entity | GRADE 4 | Depends on a **local desktop server** (`Start_MIP.bat`). No SharePoint equivalent. Nearest: scheduled Power Automate flow refreshing the Meetings list + `Refresh()`. Loses the on-demand "pull latest now" button unless wired to a manual-trigger flow. |
| Global EXPORT briefing | Downloads a Word (.doc) briefing for the selected jurisdiction (or all-jurisdictions summary) | `exportBriefing()` L3633, button L50; Blob `application/msword` L3692 | Reads in-memory `MUNICIPALITIES` → Jurisdictions + Members (name, role, party, term, notes, warn; muni: county, political, receptivity, notes) | GRADE 3 | Builds Word-XML HTML client-side + Blob download. Power Apps can't write .doc directly; use a Word-template Power Automate flow (Populate a Word document → download/email). Loses instant in-browser download unless the flow returns the file. |
| Gemini key warning banner | Amber "key not set" banner; click jumps to Settings + focuses the key field | inline `onclick` L45, `checkGeminiKeyBanner()` L1104, `showExpiredKeyBanner()` L1113 | browser localStorage: `mip_gemini_key` (read) | GRADE 4 | Tied to external Gemini key management — no SharePoint concept. Currently hard-suppressed. Nearest: a static help label. |
| Review Queue nav visibility | Operator-only nav tab, hidden until operator flag set | button L39, `_rqOperatorGate()` L10419, `isOperator()` L907 | browser localStorage: `mip_operator` | GRADE 3 | Role-gated nav. In Power Apps use `User()`/Office365 group membership or an Operators list → `Visible = varIsOperator`. Current "operator" is a DevTools-set localStorage flag (**not real auth**) — rebuild must replace with Entra/SharePoint permissions. |
| Candidates / Suggested nav badges | Small count badges on two nav tabs | spans L29–30 | Candidates / Suggested References counts | GRADE 2 | Label with `CountRows(Filter(...))` on the nav button. |
| Static topbar badges | "Central Indiana · 9 Counties" and "Apr 2026" labels | L42–43 | none/UI-only (hardcoded) | GRADE 1 | Plain static labels. |

### A2 — Left Sidebar (lines 54–65)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Municipality search filter | Type-ahead filter of the county/muni rail | `filterSidebar()` L2204 → `buildSidebar(val)`, input L60 | Filters in-memory `MUNICIPALITIES` (Jurisdictions) client-side | GRADE 2 | ~31 municipalities — small set, delegation moot. Standard gallery `Search()`/`Filter()`. |
| Collapse/expand sidebar | Toggle collapses the rail; remembered per-browser but forced open on each fresh load | `toggleSidebar()` L2211, button L56; boot reset L2228–2236 | browser localStorage: `mip_sidebar_collapsed` | GRADE 3 | Collapsible panel = container `Visible`/width bound to a context var + `SaveData`. The "persist but override-open-on-load" quirk is custom logic. |
| Sidebar rail (county/muni tree) | Rendered list of counties → municipalities | `#sidebar-content` L62, `buildSidebar()` | Jurisdictions (name, county, member counts) | GRADE 2 | Standard nested/grouped gallery. Small dataset. |

### A3 — Settings → Diagnostics card (lines 192–246, functions L9111–9220)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse Diagnostics | Collapsible card header | `toggleSettingsSection('diagnostics-body')` L1250, header L194 | none/UI-only | GRADE 2 | Container `Visible` toggle. Applies to every settings card below. |
| Run security self-test | Opens `tests/smoke.html` in a new tab | link L200 | none (separate test harness page) | GRADE 4 | In-repo JS security suite. No Power Apps equivalent; dropped or replaced by an external test process. |
| System Health check | "Check now" pings background jobs, AI quota, pending gate | `diagLoadHealth()` L9114, button L209 | `admin_run&fn=listTriggers`/`geminiQuotaStatus`/`probePendingGate` — Apps Script internals | GRADE 4 | Reports on Apps Script triggers + Gemini quota — infra that won't exist in SharePoint. Nearest: a Power Automate flow-run-history link / admin status page. |
| Meetings Needing Review (list) | "Refresh" loads uncapped review-queue meetings | `diagLoadReview()` L9152, button L219 | `action=review_queue` → Review Queue (meeting_id, jurisdiction, date, video_url, summary_doc_url) | GRADE 2 | SharePoint List gallery filtered to needs-review. Delegable via view. AI-summary context behind it is Grade 4; the display is Grade 2. |
| Resolve review decision | Accept / Redraft / No-Better-Source per meeting | `diagResolveReview()` L9175, buttons L9165–9167 | `action=resolve_review&meeting_id&decision` → Review Queue status | GRADE 3 | Patch a status column with branching outcomes. `Patch(ReviewQueue, ThisItem, {Decision:"force_redraft", Status:"resolved"})`. "force_redraft" re-triggers AI summarization (Grade 4 side-effect via flow). |
| Processing Queue | "Refresh" shows meetings still waiting to be summarized | `diagLoadQueue()` L9135, button L229 | `admin_run&fn=probePendingGate&max=25` → Apps Script gate counts | GRADE 4 | Reflects the Apps Script AI-summarization pipeline state. No SharePoint-native queue. Nearest: status column + flow surfacing pending items in a view. |
| Summary Coverage audit | "Run audit" deep-checks every meeting for a finished summary; lists missing/failed | `diagLoadSummaryAudit()` L9201, `_diagMissingTable()` L9190, button L239 | `admin_run&fn=auditMissingSummaries&include_samples=true` → Youtube Items/Meetings (has_summary, buckets, samples) | GRADE 4 | Server-side audit across ~all records tied to the AI summary pipeline (up to a minute). Cross-list rollup better in Power BI or a scheduled flow. Client-side over thousands of rows would be **⚠ NON-DELEGABLE**. |

### A4 — Settings → Research Sources card (lines 248–259, functions L5640–5688)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse Research Sources | Collapsible card | `toggleSettingsSection('research-sources-body')` L250 | none/UI-only | GRADE 2 | — |
| Render sources list | Shows each research source with FREE/PAID badge + (paid) username/password inputs | `renderSourcesList()` L5640 | browser localStorage: `mip_sources` (name, url, paid, user, pass) | GRADE 2 | Editable gallery/form over a Sources List. **Security:** paid-source passwords stored plaintext in localStorage — rebuild must use a secured column / Key Vault, not a visible field. |
| Add source | Prompts for name/paid?/URL, appends | `addSourceRow()` L5672, button L257 | browser localStorage: `mip_sources` | GRADE 2 | Uses JS `prompt()`; replace with a small add form. (No `saveSources` fn — add/delete write localStorage directly.) |
| Delete source | Removes a source row | `deleteSource()` L5683, ✕ L5652 | browser localStorage: `mip_sources` | GRADE 2 | `Remove(Sources, ThisItem)`. |

### A5 — Settings → Intelligence Feed Categories card (lines 262–275) — marked (Disabled)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse Intel Categories | Collapsible card labeled **(Disabled)** | `toggleSettingsSection('intel-categories-body')` L263 | none/UI-only | GRADE 2 | Feature off (News/Intel feed removed, P13). |
| Render tag categories | Lists tag categories; defaults locked | `renderTagCategories()` L5656 | browser localStorage: `mip_tags` | GRADE 2 | Simple List. |
| Add tag category | Adds a category from the input | `addTagCategory()` L5690, button L272 | browser localStorage: `mip_tags` | GRADE 2 | No-op for users (feed disabled). `Collect(Tags, …)`. |
| Delete tag category | Removes a non-default category | `deleteTagCategory()` L5704, ✕ L5666 | browser localStorage: `mip_tags` | GRADE 2 | — |

### A6 — Settings → Member Profile Research card (lines 278–309, functions L5488–5588)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse Profile Research | Collapsible card | `toggleSettingsSection('profile-research-body')` L279 | none/UI-only | GRADE 2 | — |
| Web App URL input | Field to override the Apps Script backend URL | input L287; `loadProfileSettings()` L5560 / `saveProfileSettings()` L5569 | browser localStorage: `mip_webapp_url`; validated to `script.google.com/macros` | GRADE 4 | Points the app at a Google Apps Script deployment — no analog once backend is SharePoint. Removed entirely. |
| Cache Duration dropdown | Profile cache TTL (4h–7d) | select L291 | browser localStorage: `mip_profile_cache_ttl` | GRADE 3 | Client caching has no SharePoint equivalent (Lists are live). Mostly obsolete in a rebuild. |
| Fetch Profiles Now | Clears cache + re-fetches member background profiles | `refreshMemberProfiles()` L5488, button L303 | localStorage `mip_member_profiles`; backend Members research (bio, statements, votes) | GRADE 4 | Kicks off AI/scraper-driven member research. Nearest: Power Automate flow calling an external research/AI API → Members list. Loses on-demand enrichment button. |
| Clear Cache (profiles) | Clears cached profile data | `clearProfileCache()` L5503, button L304 | localStorage `mip_member_profiles`, `…_ts` | GRADE 4 | No client cache to clear. Drop in rebuild. |
| Profile stats box | Read-only "X/Y completed, last fetched, Fresh/Stale" | `updateProfileStats()` L5540 | localStorage profile cache | GRADE 3 | Computed status label; `Text`/`CountIf` over Members. |
| Save Settings (profiles) | Saves web-app URL + cache TTL | `saveProfileSettings()` L5569, button L307 | localStorage `mip_webapp_url`, `mip_profile_cache_ttl` | GRADE 4 | Persists backend-URL override (Apps Script) — no analog. |

### A7 — Settings → Jurisdiction Data Cache card (lines 312–325, functions L5511–5538)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse Jurisdiction Data | Collapsible card | `toggleSettingsSection('jurisdiction-data-body')` L313 | none/UI-only | GRADE 2 | — |
| Refresh Now (muni data) | Clears cache, re-fetches all jurisdictions/hearings, rebuilds sidebar+grid | `refreshMuniData()` L5518, button L321 | localStorage `mip_muni_data`; backend muni bootstrap → Jurisdictions + Meetings + Members | GRADE 3 | In Power Apps just `Refresh(Jurisdictions)` — the cache ceremony disappears (Lists are live). The 4-hour SWR cache is a Google-CDN workaround with no SharePoint need. |
| Clear Cache (muni data) | Clears cached jurisdiction data | `clearMuniCache()` L5511, button L322 | localStorage `mip_muni_data`, `…_ts` | GRADE 4 | No client cache in a Lists rebuild → button drops. |
| Muni cache status label | Read-only status text | `#muni-cache-status` L319 | UI-only | GRADE 1 | — |

### A8 — Settings → Meeting Schedule Scraper card (lines 328–344, function L5591)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse Schedule Scraper | Collapsible card | `toggleSettingsSection('schedule-scraper-body')` L329 | none/UI-only | GRADE 2 | — |
| Scrape All Schedules | Reads every town's website for its published meeting calendar; fills confirmed dates (runs minutes) | `runScheduleScrapeAll()` L5591, button L341 | `action=scrape_all_schedules` (6-min timeout) → `fetchMeetingDates()`; writes Meetings (MEETING_DATES) | GRADE 4 | Web-scraper on the Apps Script backend. No SharePoint-native scraping. Nearest: Power Automate (HTTP + HTML parse) or a Power BI dataflow, scheduled. Loses the one-button annual scrape. |
| Scrape stats box + status | Read-only run results | `#scrape-stats-box` L338, `#scrape-status` L342 | UI-only | GRADE 1 | — |

### A9 — Settings → AI Service Key (Gemini) card (lines 348–367, functions L1094–1108, L1242)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse AI Service Key | Collapsible card | `toggleSettingsSection('api-keys-body')` L350 | none/UI-only | GRADE 2 | — |
| Enter/save personal Gemini key | Password field; saves on input, updates status + hides banner | `saveGeminiKey()` L1096, `initGeminiKeyUI()` L1242, input L357 | browser localStorage: `mip_gemini_key` | GRADE 4 | A user-supplied external AI (Gemini) API key. Secrets should live in Azure Key Vault / env vars referenced by a flow, never a canvas control. Loses "bill AI to my own Google account" unless re-architected. |
| Key status label | "Using built-in key" / "Personal key saved" | `#gemini-key-status` L361 | localStorage `mip_gemini_key` (read) | GRADE 1 | Static/computed label. |

### A10 — Settings → Recent Manual Changes card (lines 370–384, functions L5025–5091)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Expand/collapse + auto-load Recent Changes | Collapsible header that also refreshes on open | `toggleSettingsSection('recent-changes-body');refreshRecentChanges()` L371 | none/UI-only trigger | GRADE 2 | — |
| Refresh recent changes | Loads last 50 manual changes (add/edit/remove) | `refreshRecentChanges()` L5025, button L378 | `action=recent_changes&limit=50` → Manual_Entries log (action, jurisdiction, date, actor, timestamp, target_table, before/after_json, status, note) | GRADE 2 | A change-log List with a sorted/filtered view. Delegable via view. |
| Undo / rollback a change | Operator-only "↶ rollback" per active entry; confirms, reverts, refreshes | `rollbackManualEntry()` L5069, button L5046 (gated by `isOperator()`) | `action=rollback_manual_entry&entry_id` → reverts target entity via stored before-image | GRADE 4 | True undo-history with before-image restore isn't SharePoint-native. Nearest: SharePoint list versioning (restore a prior version) or a custom flow reading a before_json column. Loses one-click cross-entity rollback; operator gate needs real auth. |
| Recent changes list render | Colored status dots, target/after preview, notes | render L5037–5063 | Manual_Entries fields | GRADE 2 | Gallery with conditional color formatting. |

### A11 — Global UI Helpers (chat panel, toasts, banners, operator concept)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Toggle chat panel | Expand/collapse an AI chat panel on member/entity cards | `toggleChatPanel()` L1496 | none/UI-only | GRADE 2 | The panel container is a `Visible` toggle. The `chatSend()` L1506 AI conversation it fronts is **GRADE 4** (external Gemini call). |
| Error toast | Auto-shows a dismissible toast for any uncaught error; auto-dismiss 12s | `showToast()` in `_installErrorHandler()` L932 | none/UI-only | GRADE 3 | Global error surfacing. Power Apps has `Notify()`, but no global `window.onerror` hook — wrap risky calls in `IfError(...)`+`Notify()`. Loses automatic catch-all error toasts. |
| Expired-key banner | Fixed banner when a saved Gemini key is rejected; one-click clear | `showExpiredKeyBanner()` L1113 | localStorage `mip_gemini_key` | GRADE 4 | External AI key handling — drop with the Gemini key feature. |
| Operator mode | `isOperator()` gates rollback, review-queue nav, project-close ✕, untag actions | `isOperator()` L907; gate L10419; consumers L5046, L5803, L6558, L7523 | localStorage `mip_operator` | GRADE 3 | The whole "operator" concept is a **fake auth flag** (DevTools-set). Rebuild must replace with real Entra ID / SharePoint group membership → control `Visible`. `Set(varIsOperator, User().Email in Operators.Email)`. Touches many screens. |

### Cluster A grade tally
- **GRADE 1:** 4 (static topbar badges, muni cache status, scrape stats box, Gemini key status)
- **GRADE 2:** 17 (switchView, nav badges, all collapse toggles + `toggleSettingsSection`, sidebar search, sidebar rail, Meetings-Needing-Review list, add/delete source, add/delete tag category, render sources/tags, recent-changes refresh + render, chat-panel toggle)
- **GRADE 3:** 8 (theme toggle, sidebar collapse persistence, EXPORT briefing, review-queue nav visibility, resolve review decision, profile cache-duration/stats, muni Refresh Now, error toast, operator mode)
- **GRADE 4:** 12 (Refresh Hearings/localhost, Gemini warning banner, System Health, Processing Queue, Summary Coverage audit, Web App URL override, Fetch Profiles Now, Clear profile cache, Save profile settings, Clear muni cache, Scrape All Schedules, Gemini key entry, rollback/undo, expired-key banner, Run security self-test)


---

## CLUSTER B — Overview, Jurisdictions, Members, Intel Feed

Scope: `#view-overview`, `#view-muni` (muni panel, Tracked-Projects rail, member profiles, council/PC/hearings sub-tabs), and `#view-intel` (currently disabled). All backend calls are `GET/POST` to the Apps Script web-app (`getWebAppUrl()`) with `action=…`. Client-only state (verify flags, notes, member edits) lives in `localStorage`/in-memory and would move to a SharePoint list or user-scoped store.

### B-1 — Overview view (`#view-overview`)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Stat card: Municipalities | Count of tracked munis (`MUNICIPALITIES.length`) | `#stat-munis`, `updateOverviewStats()` L2122 | Jurisdictions (row count) | 3 | Cross-entity count. `CountRows(Jurisdictions)`. Small set — safe. |
| Stat card: Counties | Distinct county count | `#stat-counties`, `updateOverviewStats()` L2127 | Jurisdictions.county / county-group config | 3 | `CountRows(Distinct(Jurisdictions, County))` — Distinct is ⚠ NON-DELEGABLE, tiny dataset so fine. Consider a static Counties list. |
| Stat card: Total Members | Sum across munis of `council.length + pc.length` (filters placeholder rows), rendered "N+" | `#total-members`, `updateTotalMembers()` L2110 | Members (all rows, all jurisdictions): body, name | 3 | Cross-list rollup over the entire Members list + string filter → ⚠ NON-DELEGABLE (truncates at 2000). Pre-compute via a scheduled flow into a summary item. |
| County grid tiles | One card per county: name, "N municipalities", "N members tracked"; click → Jurisdictions view + first muni | `#county-grid`, `buildCountyGrid()` L2295 | Jurisdictions (per county), Members (sum per muni) | 3 | Per-county rollup joining Jurisdictions→Members = ⚠ NON-DELEGABLE nested aggregate. Pre-aggregated summary list refreshed by flow. |
| County tile navigation | `buildSidebar(); switchView('muni'); selectMuni(first)` | onclick L2306 | Jurisdictions | 2 | `Navigate()` + set selected record. |
| `_sortedCountyGroups()` / `_muniSortKey()` | Alpha-sorts counties (Other/Regional pinned last) and munis, stripping "City of/Town of" | L2142–2155 | Jurisdictions.name | 3 | Sort on a computed (prefix-stripped) key = ⚠ NON-DELEGABLE. Add a persisted `SortName` column so `Sort()` is delegable. |

### B-2 — Sidebar (county/muni rail, shared by Overview + Jurisdictions)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `buildSidebar()` | Renders collapsible county groups; each muni shows "council / pc" counts | L2156 | Jurisdictions, Members (council/pc lengths per muni) | 3 | Per-row member-count badge = nested rollup, ⚠ NON-DELEGABLE. Pre-compute counts. |
| `filterSidebar(val)` | Free-text filter `m.name.includes(val)` → rebuilds sidebar | L2204 | Jurisdictions.name | 2 | ⚠ NON-DELEGABLE — `.includes()` = "contains"; SharePoint delegates only `StartsWith`. Juris count small, so fine. |
| `toggleCounty(header)` | Expand/collapse a county's muni list | L2197 | none (UI) | 2 | Gallery group collapse via a collection variable. |
| `toggleSidebar()` | Collapse/expand the rail; persists `mip_sidebar_collapsed`, forced open on load | L2211 | none (UI pref) | 2 | Container visibility toggle + `Set()`. Mobile: rail should become an overlay. |

### B-3 — Jurisdiction (Municipality) view — panel & sub-tabs (`#view-muni`)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `selectMuni(id)` | Sets current muni, default tab=hearings, clears member, renders panel/detail | L2319 | Jurisdictions (by id) | 2 | `Set(gMuni, LookUp(Jurisdictions, ID=id))`. Delegable `eq`. |
| `renderMuniPanel()` | Master render: title, county, summary box, intel feed (empty), members tabs, TP rail | L2336 | Jurisdictions (name, county, political, receptivity, notes), Members, Meetings | 2 | Form/detail screen bound to selected Jurisdiction. |
| Municipality Summary box | Collapsible; PC size, Council size, political, receptivity dot+label, strategic notes | L2370 | Jurisdictions.political/receptivity/notes; Members (pc/council length) | 3 | Static fields Grade 1/2; PC/Council **size** are per-muni member rollups (delegable `eq` counts, fine at scale). |
| `toggleMuniSummary(muniId)` | Toggle summary open state, re-render | L3155 | UI state | 2 | Context variable toggle. |
| Receptivity dot | Colored dot from `recColors[m.receptivity]` (high/med/low/mixed) | L2341 | Jurisdictions.receptivity | 1 | Lists-native: JSON column formatting / choice column with color. |
| Report Issue box | Free-text issue submit per muni; POST `submit_issue_report`; 2000-char cap; graceful fallback | L2361, `submitReportIssue()` L3181 | Issue_Reports list (new row) | 2 | `SubmitForm`/`Patch` to a list, or flow. Built-in Lists form covers it. |
| Members tabs (Council / PC / Hearings) | Tab buttons with live counts; Council/PC hidden if empty; Hearings count from `PUBLIC_HEARINGS[m.id]` | L2405 | Members (council/pc lengths), Meetings count | 3 | Tab counts are per-muni rollups (delegable `eq` counts). |
| `switchTab(tab)` | Set `currentTab`, re-render panel + clear member detail; swaps rails | L3256 | UI state | 2 | Tabbed container via a variable. |
| `applyMuniDetailVisibility()` | Hearings tab → hide member-detail, show TP rail full-width; Council/PC → member rail, hide TP rail | L3165 | UI state | 2 | Conditional `Visible`. Mobile: side rails must stack. |
| `renderMemberCards(members)` | Member tiles for council/pc tab: name, role, body/party/term tags; click→`showMemberDetail` | L3229 | Members (name, role, body, party, term) | 2 | Standard gallery. Party/body/term = choice columns. |
| Council/PC sub-tab | `renderMemberCards(m.council | m.pc)` | L2418 | Members filtered by muni + body | 2 | `Filter(Members, Muni=id, Body="Council")` — delegable. |
| Hearings sub-tab | `renderHearingsContent(m.id)` (full hearings table — detailed logic in Cluster E) | L2418 | Meetings, Agenda/Youtube Items for muni | 2 | Gallery filtered by muni; the hearings table is graded in Cluster E. |
| `toggleMuniIntel(muniId)` | Toggles intel expand — but `renderMuniIntelFeed()` returns `''` (feed disabled) | L5358; `renderMuniIntelFeed` L5316 | Intel items (none — disabled) | 4 | ⚠ Currently-off dead toggle. Revived = live scraping feed = Grade 4. |

### B-4 — Tracked Projects rail (`#muni-tp-rail`, `renderTpRail`)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `renderTpRail(m)` | Sticky right rail: filters `tpProjects` cache to this muni by **normalized** juris name; hides closed/archived/deleted/competitor_active; sorts by latest date | L2502 | Tracked Projects (jurisdiction, status, projectName, ordinanceId, latestMeetingDate, lastNature, createdDate) | 3 | Filter on a **normalized** name = ⚠ NON-DELEGABLE (function-wrapped column). Add a stored `JurisKey` column for delegable `eq`. |
| `tpLoad()` data source | Loads all projects via `list_tracked_projects_detailed&jurisdiction=*` (cached) | L6192 | Tracked Projects (all) | 3 | Full-table pull = ⚠ NON-DELEGABLE at scale; truncates. Filter server-side per juris. |
| `tprToggleAddForm()` | Open/close inline "Add Project" form | `_tprRenderAddForm` L2583 | UI state | 2 | Form show/hide. |
| Add Project form | Ord#/Docket, Project name (req), alias chips (multi), alias autosuggest; Save→`tprSubmitProject()` | L2591 | Tracked Projects (new: ordinanceId, projectName, aliases[]) | 3 | Multi-value alias chips = custom Power Fx over a collection. Base create Grade 2; alias autosuggest Grade 3. |
| `_tprRenderProjectCard(p)` | Per-project card: name+ord, tag button, meta, tagged-docs, descriptions, tag form | L2615 | Tracked Projects; Tagged Documents | 2 | Gallery item. |
| Tag-document affordance | Per-project "+" toggles tag form (URL / display name / file upload) | L2624, `_tprRenderTagForm` | Tagged Documents (project_id, url, filename, description) | 3 | File upload + async description status = attachment + flow-driven cascade. |
| Tagged-docs inventory | Lazy-fetches per-project doc list; collapsible ">5 more"; active links | L2559, `_tprFetchProjectDocs` | Tagged Documents (doc_id, filename, url) | 3 | Per-project lazy join + count gate. `Filter(TaggedDocuments, ProjectId=pid)` delegable. |
| Descriptions list | Session-only AI doc descriptions; collapsible | `_tprRenderDescriptions` L2654 | Tagged Documents.description/status | 3/4 | Auto AI descriptions = Grade 4; display+collapse Grade 3. |
| `toggleProjectTimeline(projectId)` | Expand/collapse a project's meeting timeline; lazy load on first open | L6063 | Tracked Projects → Agenda Items / Meetings | 3 | Cross-list timeline join per project. Delegable `eq` on project_id. |
| `closeProjectConfirm(id,name)` | `confirm()` then `close_tracked_project`; refreshes | L6073 | Tracked Projects.status → closed | 2 | `Patch` status field. |

### B-5 — Member profile detail (`#member-detail`, `renderMemberDetail`)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `showMemberDetail(idx)` / `renderMemberDetail(mem)` | Full profile pane: name, role, verified badge, key stats, notes, affiliations, professional bg, employment/political history, social links, research timestamp | L3384 | Members (name, role, body, party, term, notes, professional_background, employment_history[], political_history[], social links, _last_researched, _profile_confidence) | 2 | Standard detail form. Multi-value history arrays = child list. Party→label = Grade 1 choice. |
| Verified badge / `verifyMember(key)` | Marks member verified in `localStorage`, re-renders | L3404, L5366 | client `localStorage` (no backend) | 4 | ⚠ Client-only, per-browser — lost on device change. Power Apps has no localStorage; move to a `Verified` column (Grade 2 `Patch`). No server persistence today. |
| `unverifyMember(key)` | Removes verify flag | L5374 | client `localStorage` | 4 | Needs a real column to persist. |
| `saveMemberNotes(key)` | Saves relationship notes to `localStorage` | L3459, L5380 | client `localStorage` | 4 | ⚠ Per-browser only, not team-shared despite "team notes" label. Should be a Members column. |
| `toggleMemberEditForm()` / `cancelMemberEdit()` | Show/hide inline edit form | L5388 | UI state | 2 | EditForm visibility. |
| `saveMemberEdits()` | Writes name/role/term/party to the **in-memory** object + re-render (no backend POST) | L5398 | Members (in-memory only — NOT persisted) | 4 | ⚠ Edits lost on reload — no server write. Must `Patch` the Members list (Grade 2 once wired). |
| Social links | LinkedIn/Facebook/Twitter/Campaign — link or "—" | L3485 | Members social fields | 1 | Hyperlink columns; JSON formatting. |
| Research metadata footer | "PROFILE RESEARCHED: {date} · {confidence}" | L3495 | Members._last_researched, _profile_confidence | 1 | Date/text display. |
| "Update Profile" (`researchMemberProfile`) | Calls external Gemini (`callGeminiProxy`, gemini-2.5-flash) with structured prompt + up to 2 hearing YouTube videos; parses sections; caches in `localStorage` | L1345, invoked L3531 | Members profile fields via **external AI**; reads Youtube Items, Hearings YouTube URLs | 4 | ⚠ External AI research (LLM). Nearest: Power Automate → Azure OpenAI / AI Builder writing to Members. Loses inline live call + YouTube video multimodal grounding (AI Builder can't ingest video); non-deterministic. |
| `renderProfileResearch()` | Parses AI freeform text into sections + vote-history table | L1404 | derived from AI text | 4 | Regex parse of LLM output — belongs in the flow, not the app. |
| `fetchAndMergeMemberProfiles()` / `mergeMemberProfiles()` | On load, GET `member_profiles` (30s, TTL-cached), merges completed profiles by `member_key` | L5430 | Members ↔ external profile store, keyed `muniId::body::name` | 4 | Batch AI-pipeline sync = scheduled flow populating Members. |
| `exportBriefing()` | Printable HTML/Word briefing for current muni (fields, notes, roster, flagged members) | L3633 | Jurisdictions, Members | 3 | Print/export = flow → Word/PDF template, or client print. (Also listed A1.) |

### B-6 — Intelligence Feed view (`#view-intel`) — ⚠ CURRENTLY DISABLED

Nav button removed (P13); data is a **hardcoded JS array** `INTEL_ITEMS` (L1696), not live; Settings labels it "(Disabled)". Grades are for a *revived/live* version.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `buildIntelFeed()` | Sets "last updated", populates muni dropdown from distinct items, sorts newest-first | L3548 | Intel items (static): muni, county, date, type, headline, url, source, isNew | 4 | ⚠ Off. Live version = news/social/vote scraping = Grade 4. Distinct-muni dropdown = ⚠ NON-DELEGABLE. |
| `renderFeed(items)` | Renders feed items: type dot, headline link, tags; NEW badge; click opens url | L3570 | Intel items | 2 | If list-backed, standard gallery. |
| `filterFeed()` | Filters by county (`==`), muni (`==`), active tag set; newest-first | L3606 | Intel items.county/muni/type/dateSort | 2 | county/muni `eq` delegable; tag membership `in`-set = ⚠ NON-DELEGABLE. |
| `filter-county` dropdown | Hardcoded county options → `filterFeed()` | L128 | Intel items.county | 2 | Hardcoded list should be a Choice column. |
| `filter-muni` dropdown | Populated from distinct feed munis | L135, L3557 | Intel items.muni (distinct) | 3 | Distinct-value dropdown = ⚠ NON-DELEGABLE; use a Jurisdictions dropdown. |
| `toggleTagFilter(tag, btn)` | Multi-select tag toggle (vote/news/election/social) | L138, L3618 | Intel items.type | 2 | Toggle-button filter group. |

### Cluster B grade tally
- **Grade 1:** 4 (receptivity dot, social links, party/body choice labels, research-metadata footer)
- **Grade 2:** ~22 (selectMuni, renderMuniPanel, switchTab, member cards/detail form, report-issue submit, tracked-project create/close, sidebar toggles, feed render/filter/tag-toggle, etc.)
- **Grade 3:** ~14 (all Overview rollups, sidebar member-count badges, TP rail normalized-name filter, timeline join, doc inventory, alias-chip form, prefix-strip sort)
- **Grade 4:** ~8 (member profile research pipeline ×3, verify/unverify + saveMemberNotes + saveMemberEdits client-only, disabled muni intel toggle, disabled Intelligence Feed)


---

## CLUSTER C — Competitor Tracked Projects

Scope: `#view-tracked` (DOM lines 393–470) plus all backing JS. All rows are fetched in one shot via `list_tracked_projects_detailed&jurisdiction=*` (`tpLoad`, L6192) into the in-browser `tpProjects` array, then **every** filter/search/sort runs client-side in `tpRenderTable` (L6239). This whole-list-then-filter pattern is the central delegation risk: it works only while the list stays under Power Apps' data-row limit (default 500, max 2000). Everything below inherits that ceiling.

### C.1 — Filters, Sort & Search

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Jurisdiction filter | Dropdown `tp-filter-juris`; options auto-built with per-juris counts. Exact-match `p.jurisdiction === value`. | L401; `tpRenderTable` L6270 | Tracked Projects.jurisdiction | 2 | `eq` delegable. Count labels computed from the fetched set → non-delegable if counts required (Grade 3). |
| Status / recency filter | Dropdown `tp-state-filter`: all / past_week / active(=Competitor Proposed) / competitor_active / arbor_active / archived. `deleted` always hidden. | L402–409; `tpRenderTable` L6256 | Tracked Projects.status; latestRefDate/latestMeetingDate | 3 | `status eq` delegable; code→label mapping + hide `deleted` = small Power Fx. **⚠ past_week NON-DELEGABLE** — filters on cross-list rollup dates (from Agenda Items/Meetings), not a stored column. |
| Free-text search | `tp-filter-text`; `indexOf` **contains** across projectName + petitioner + builder + ordinanceId + aliases | L410; `tpRenderTable` L6271 | Tracked Projects: projectName, petitioner, builder, ordinanceId, aliases | 4 | **⚠ NON-DELEGABLE.** Multi-field `contains`/`Search()` does not delegate; Power Apps silently truncates to 500/2000 rows. Redesign: pre-indexed searchable column, `StartsWith`, or push search to Dataverse/Power Automate. |
| Sort dropdown | `tp-sort-key`: default / project / jurisdiction / builder / meeting_date(newest) / status. Secondary sort by normalized jurisdiction on ties. | L411–418; `tpRenderTable` L6283 | projectName, jurisdiction(normalized), builder, status; effective meeting date | 3/4 | project/builder/status sorts on stored cols = Grade 2. **⚠ meeting_date sort NON-DELEGABLE** — key = `manualMeetingDate || latestRefDate || latestMeetingDate` (override-aware, cross-list). jurisdiction sort uses `_normJurisName` (computed) — non-delegable. |
| Refresh | `↺ Refresh` → `tpLoad(true)` force re-fetch (bypasses 60s cache). | L419; `tpLoad` L6164 | full detailed read | 2 | `Refresh(datasource)`. |
| Result count status | `tp-status` "N projects (of M)" | L438; `tpRenderTable` L6321 | count filtered vs total | 2 | Label formula; "of M" reflects the (possibly truncated) total. |
| Cold-open snapshot paint | Optimistic paint from CDN `tracked_detailed.json` before live fetch (guarded) | `tpLoad` L6176 | snapshot copy | 4 | No Power Apps equivalent; static CDN pre-paint is a perf hack. Drop it (feature lost). |

### C.2 — Add / Create (global "+ Track Project" form)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Toggle add form | `+ Track Project` shows/hides `tp-add-form`; focuses name; wires ord onblur → alias suggestions | L420,423; `tpToggleAddForm` L7074 | — | 2 | Form visibility toggle. |
| Create tracked project | Fields: name*, ord#, jurisdiction, petitioner, aliases, map url. Validates name; `create_tracked_project`; then `tpLoad(true)`. | L425–436; `tpSubmitNew` L7117 | Tracked Projects: projectName, ordinanceId, jurisdiction, petitioner, aliases, mapUrl | 2 | Standard form/`Patch`. Jurisdiction free-text here — a Lists form would prefer a choice column. |
| Alias auto-suggest | On ord blur, `admin_run&fn=suggestAliases`; fills empty aliases box with format variants | `tpFetchAliasSuggestions` L7091 | Muni_Naming_Conventions → suggestions | 4 | Server-side heuristic generator. No native equivalent — Power Automate flow returning suggestions, or drop. |

### C.3 — Inline Edits (per-row, in-table)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Lots (inline expand + edit) | Column shows Gemini-extracted lot count; edit via Edit dropdown `tpe-lots` | cell L6520; save `tpSaveEditRow` L6772 | Tracked Projects.lots | 4 | The **value origin** = Gemini AI extraction from transcript = Grade 4. Manual override of the number = Grade 2. |
| Builder dropdown | Inline `<select>` (20-value `TP_BUILDERS` mirroring ArcGIS domain). Optimistic + rollback. | cell L6400; `tpBuilderChange` L6133 | Tracked Projects.builder | 2 | Lists choice column + inline gallery edit. Keep options synced with ArcGIS domain. |
| Status dropdown | Inline `<select>`: Competitor Proposed/Active/Arbor Active/Archive. Changing to a hidden status makes the row disappear. | cell L6485; `tpStatusChange` L6982 | Tracked Projects.status | 3 | Delegable `eq` write, but status carries lifecycle semantics (hide + ArcGIS-sync gating) → cascade = small Power Fx; "row vanishes" is a re-filter. |
| Map URL (inline) | Empty: bare input `onblur=tpInlineSave` (map_url). Set: "Map ↗" link + ✎ that swaps back to input | cell L6546; `tpEditMap` L6617 | Tracked Projects.mapUrl | 2 | Inline edit + hyperlink render. |
| MapID (inline) | Always-editable input; ArcGIS record key for future MRD→ArcGIS sync | cell L6554; `tpInlineSave` L7022 | Tracked Projects.mapId | 2 | Inline text edit. |
| Edit dropdown (expand row) | ✎ toggles a full-width edit sub-row: name, ord#, aliases, petitioner, lots, **Meeting Type/Date/Description/Results overrides**. Single `update_tracked_project` save. | ✎ L6511; `tpToggleEditRow` L6608; `tpSaveEditRow` L6705 | projectName, ordinanceId, aliases, petitioner, lots, manualMeetingType/Date, manualResults, manualDescription, manual_overrides_asof | 3 | Form/`Patch` = Grade 2, but the **override precedence** is Grade 3: effective = `manual || derived`, stamped with `manual_overrides_asof` so the backend auto-**expires** the manual value once a newer AI summary lands. That "manual wins until superseded by a fresher AI summary" cascade has no clean Lists equivalent — Power Automate + a computed effective-value column. |
| Description cell (expand/collapse) | 2-line clamp; text = `manualDescription || latestRequestSummary` (from matched Agenda Item) | cell L6438; `tpToggleAction` L6632 | Tracked Projects.manualDescription; Agenda Items.item_summary | 3 | Derived source is a cross-list rollup from Agenda Items. Expand toggle Grade 2. |
| Results cell (expand/collapse) | 2-line clamp; text = `manualResults || (latestActionTaken + latestAdditionalNotes)` = Outcome+Vote | cell L6453; `tpToggleAction` L6632 | Tracked Projects.manualResults; Agenda/Youtube Items | 3 | Composed from cross-list Item fields. |
| Meeting Type / Meeting Date cells | Effective = `manualOverride || derived`. Future dates orange; "⏳ pending {date}" badge when a newer un-summarized agenda exists | cells L6410–6430 | manual overrides; Meetings.meeting_type/date; PUBLIC_HEARINGS.summary_doc | 4 | Pending-summary detection walks a cross-list hearings map with date/juris normalization + AI-summary existence checks — no native equivalent; Power Automate computed flag. |
| Summary cell ("Detailed Summary" vs "Summary") | Links to item-scoped AI detailed-summary doc else full-hearing doc | cell L6376; `_tpFindSummaryDocFor` L6914 | Tracked Projects.latestYtSummaryUrl/summaryIsDetailed; Meetings.summary_doc | 4 | AI-generated summary documents = Grade 4. Link render trivial; the artifact isn't reproducible in Power Apps/Lists. |
| Agendas cell (+N expand) | Lists all agenda docs the project appeared on as #-links (newest first), 4/row, "+N" toggles rest | cell L6352 | Tracked Projects.agendaRefs[] (url,date) | 3 | Cross-list rollup of agenda references (delegation-sensitive if large). |

### C.4 — Per-row Actions

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Soft-delete record | 🗑 in edit dropdown; `prompt()` requires retyping exact name; sets `status=deleted` | `tpDeleteRow` L6818 | Tracked Projects.status='deleted' | 2 | Soft-delete = status write; type-to-confirm = Power Apps confirm popup. |
| Close tracking (operator) | ✕ (operator only); `confirm()` then `close_tracked_project`; refreshes | ✕ L6558; `tpCloseProject` L7161 | Tracked Projects (close_tracked_project) | 2/3 | Distinct backend action from soft-delete; if it cascades (unlinks refs) it's Grade 3. Operator-only gate = Power Apps security role. |
| Edit toggle (✎) | Opens/closes the inline edit sub-row (one at a time) | ✎ L6511; `tpToggleEditRow` L6608 | — | 2 | Gallery edit-mode toggle. |
| Map edit toggle (✎) | Swaps the Map link cell back to an input and focuses it | ✎ L6548; `tpEditMap` L6617 | — | 2 | Inline edit affordance. |
| Cell expand/collapse | Generic `.expanded` toggle (Lots/Description/Results) | `tpToggleAction` L6632 | — | 2 | Container toggle. |
| Sticky horizontal scrollbar | Proxy scrollbar pinned to viewport bottom mirrors the wide table's `scrollLeft` both ways | `tpSyncHScroll` L6578; DOM L468 | — | 4 | **Mobile/wide-table concern.** A 16-column table with per-cell controls doesn't fit canvas/phone; galleries don't horizontally scroll a fixed grid. Redesign: responsive card layout or Power BI table. Bespoke scroll-sync lost. |

### C.5 — Document Tagging (global banner + table popup)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Tagged Docs count + popup | Column "N docs"; click opens popup listing docs via `list_project_documents`, status badges, Drive/orig links | cell L6495; `tpOpenDocsPopup` L7480 | Tagged Documents: filename, status, drive_file_url, source_url, size, folder_url | 3 | Related-list rollup + detail popup. Counts loaded separately. Cross-list join Grade 3; Drive folder integration Grade 4 (SharePoint doc library instead). |
| Untag document (operator) | ✕ in popup; `confirm()` then `untag_document` (archives) | `tpUntagDoc` L7536 | Tagged Documents.status→archived | 2 | Status write. Operator gate. |
| Inline "+ Tag" (table) | Per-row "+ Tag" toggles an inline tag-form sub-row (paste URL / upload PDF) | tagBtn L6504; `tprToggleTagInput` L2958 | Tagged Documents (new) | 3 | Inline form Grade 2; upload path Grade 3/4. |
| Global tag-mode banner | Fixed top banner: project picker, "Tag all on this page", exit. Injects ✚ after every taggable link; persisted across view switches via a `switchView` hook + `MutationObserver` | L7189–7466 | — | 4 | DOM-scraping decoration of arbitrary links + MutationObserver has **no Power Apps equivalent**. Redesign the "✚ on any link" model — a per-doc gallery with a Tag button. Feature substantially lost. |
| Tag one doc | ✚ → `tag_document`; backend downloads to Drive (active/url-only/failed); inline ✓/🔗/⚠ | `tagOneDoc` L7366 | Tagged Documents; Drive download | 4 | Server-side fetch-and-archive to Drive = external integration (Power Automate + SharePoint/OneDrive). |
| Tag all on page (batch) | POST `tag_documents_batch` up to 25 links; reports counts | `tagAllOnPage` L7400 | Tagged Documents (batch); Drive | 4 | Batch server download job → Power Automate. |
| Client audit id | Stable per-browser UUID for tag attribution | `tagClientId` L7194 | client_id on tag writes | 2 | Use `User().Email` instead. |

### C.6 — Muni-rail Tracked Project add/tag (tpr* family)

These render on the per-municipality rail but write to the **same Tracked Projects / Tagged Documents entities** and re-render `#view-tracked`.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Toggle rail add form | Opens/closes the rail's "add project" form | `tprToggleAddForm` L2780 | — | 2 | Form toggle. |
| Alias chips input | Type-to-add chips (Enter/comma adds, Backspace removes) | `tprAliasKeyDown` L2823; `tprRemoveChip` L2837 | alias list (client) | 2 | Chip/collection UI; store as delimited string or child list. |
| Rail alias auto-suggest | On ord blur, `admin_run&fn=suggestAliases`; appends chips | `tprFetchAliasSuggestions` L2800 | Muni_Naming_Conventions | 4 | Same server heuristic — no native equivalent. |
| Submit rail project | Validates name; flushes alias draft; **client-side dup detection** against `tpProjects`; `create_tracked_project`; then `tpLoad(true)` | `tprSubmitProject` L2842 | Tracked Projects: projectName, ordinanceId, jurisdiction, aliases | 3 | Create Grade 2, but the **dup-check scans the whole fetched list** (`contains`-style) → ⚠ NON-DELEGABLE; unreliable if truncated. Move server-side. |
| Toggle rail/table tag input | Opens the shared inline tag form for one project | `tprToggleTagInput` L2958; `_tprRenderTagForm` L2915 | — | 2 | Form toggle shared across surfaces. |
| Select / clear tag file | File input, PDF-only, 25 MB client cap | `tprSelectFile` L2973; `tprClearFile` L2989 | client file | 2 | Power Apps attachment control (own limits). |
| Submit tag (URL or upload) | File → base64 `tag_document_upload`; URL → `tag_document`; validates | `tprSubmitTag` L2994; `_tprFinishTagSuccess` L3076 | Tagged Documents; Drive upload | 4 | Base64 upload to a Drive-backed store = external. SharePoint doc-library upload Grade 3; Drive-folder-per-project + auto-naming Grade 4. |
| Rail tagged-docs list | Lazily fetches `list_project_documents`, renders links, collapse/expand | `_tprFetchProjectDocs` L2698; `_tprRenderTaggedDocs` L2723 | Tagged Documents | 3 | Related-list rollup + expand toggle. |
| Rail description expand | Toggles rail description clamp | `tprToggleDescExpand` L2690 | — | 2 | Container toggle. |

### Cross-reference / derived-data functions (backend actions feeding the view)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Meeting-type override (agenda docs) | Popover on scraped agenda docs; `override_meeting_type`; feeds Meeting Type on tracked rows | `submitChangeType` L4022 | Scraped Docs.meeting_type_override | 3 | Override write on a scraped-doc entity a Tracked row derives from — computed cascade. |
| Project timeline | `project_timeline&project_id` returns all Project_References across meetings | `loadProjectTimeline` L5979; `toggleProjectTimeline` L6094 | Project References ⋈ Meetings ⋈ Agenda/Youtube Items | 4 | Cross-list timeline across 4 entities — Power BI or a flow-built related view. |
| Detailed read (backing fetch) | `list_tracked_projects_detailed` joins Tracked Projects ⋈ Project_References ⋈ Meetings ⋈ Agenda_Items → every derived column | `tpLoad` L6192 | 4-entity join | 4 | The entire detailed row is a server-side multi-list join with AI-derived fields. In Power Apps this is the core delegation problem: cannot join 4 lists client-side over thousands of rows. Needs Dataverse relationships or a pre-materialized/flow-refreshed table. |

### Cluster C grade tally (~40 distinct user-facing functions)
- **Grade 1:** 0 — even the simplest controls sit on a computed/joined dataset, not a plain list view.
- **Grade 2:** ~15 (juris filter, Refresh, count label, add-form toggle, create project, Builder select, Map URL/MapID inline, soft-delete, edit/map/cell toggles, untag, alias chips, file select/clear, rail form toggles, client-id→User())
- **Grade 3:** ~11 (status filter+mapping, sort project/juris/builder, status-change cascade, edit-dropdown override-precedence, Description/Results/Agendas rollup cells, tagged-docs popup/list, rail dup-check, meeting-type override)
- **Grade 4:** ~14 (free-text multi-field search, past_week + meeting_date sort, cold-open snapshot, alias auto-suggest ×2, Lots Gemini extraction, Summary AI docs, pending-summary detection, sticky h-scroll/wide-table, global tag-mode banner + link-scraping, tag-one/tag-all Drive download, base64 upload, project timeline, the 4-entity detailed join)


---

## CLUSTER D — Candidates, Suggested Matches, Agenda Items, Youtube Items

Backend base call: `getWebAppUrl()` + `&action=…`. All four queues **fetch the entire result set, then filter/search/sort/paginate in the browser** — the central delegation risk for a SharePoint rebuild.

### D.1 — CANDIDATES (`#view-candidates`, DOM 472–494)

Entity **Candidates**: `candidate_id, status, confidence(high/low), jurisdiction, project_name, request_type, description, petitioner, ordinance_id, hearing_count, bodies, last/first_seen_date, agenda_urls, summary_urls, primary_url, suggested_project_id/name`.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| candLoad | Fetch candidate queue (`status=new`); optimistic CDN snapshot then live fetch | L9316 | Candidates (read) via `admin_run&fn=getAgendaCandidatesJSON&status=new` | 2 | ⚠ NON-DELEGABLE if detection stays server-side. Snapshot pattern has no Power Apps equivalent. Whole set pulled to client. |
| candRender | Build counts, bulk bar, table, pager | L9388 | Candidates (read) | 2 | Full-set client render = perf risk at thousands. |
| candSetJuris | Jurisdiction dropdown (exact match); options w/ per-muni counts | L9509 | Candidates.jurisdiction | 1 | Delegable equality filter. Count labels = ⚠ non-delegable. |
| candSetSearch | Free-text over project_name+petitioner+ordinance_id (`contains`) | L9510 | Candidates fields | 2 | ⚠ NON-DELEGABLE — multi-field "contains"; truncates at 500–2000; client pagination hides it. |
| candToggleHigh | "High-confidence only" → `confidence==='high'` | L9508 | Candidates.confidence | 2/4 | ⚠ NON-DELEGABLE if confidence is AI-computed (it is). Underlying column is a computed score. |
| candSetPageSize | Rows/page 50/100/250/all | L9511 | — | 2 | Client paging over full set; "Show all" heavy; SharePoint won't return >500 anyway. |
| candGoPage | Prev/Next pagination | L9512 | — | 2 | ⚠ Client-side pagination masks delegation truncation. |
| candToggleAllDesc | Expand/collapse every Description | L9496 | Candidates.description | 2 | CSS toggle; print shows collapsed unless expanded. |
| candTrack / candOpenTrackModal / candTrackConfirm | "＋ Track" — modal, then **create a NEW Tracked Project AND auto-associate all backend-matched sibling agenda items** | L9541/9546/9570 | WRITE Tracked Projects (+ associations) via `fn=trackAgendaCandidate`; refreshes `tpLoad` | 3 | ⚠ NON-DELEGABLE + expensive: auto-association scans ALL agenda/youtube items server-side. Power Fx: `Set(gP,Patch(TrackedProjects,Defaults(...),{...})); ForAll(Filter(AgendaItems, OrdinanceId=cand.OrdinanceId Or ProjectName=cand.ProjectName), Patch(Associations,Defaults(...),{ProjectId:gP.ID,ItemId:ID}))`. The `ForAll(Filter())` scan is delegation-limited — batch via a flow. |
| candApprove | "✓ Approve" (pre-matched) — associate with the pre-matched project | L9585 | WRITE via `fn=addCandidateToTrackedProject`; returns `also_associated[]` | 3 | Cross-list write + sibling cascade. Pre-match itself is AI (Grade 4 upstream). |
| candOpenAddToExisting / candAddToExisting | "Add to… ▾" — dropdown of active projects in same normalized jurisdiction; merge candidate | L9908/9939 | READ TrackedProjects; WRITE `fn=addCandidateToTrackedProject` | 3 | Jurisdiction normalization + status filter. Cascade write. |
| candDismiss | Per-row "Dismiss" | L9598 | WRITE `fn=dismissAgendaCandidate` (status flip) | 1 | Single-record Patch. Delegable. |
| candBulkDismiss | "Dismiss selected" — sequential over checked | L9955 | WRITE `dismissAgendaCandidate` ×N | 2 | Multi-select bulk; slow at thousands → flow preferable. |
| candToggleSel / SelectAllPage / SelectAllFiltered / ClearSel | Checkbox selection sets | L9515/9516/9524/9529 | selection state | 2 | Standard gallery multi-select. |
| candRailToggle / candRailToggleMuni / candRenderRail | Right "Tracked Projects" rail grouped by normalized muni, collapsible | L9241/9242/9255 | READ TrackedProjects (`tpProjects`) | 2 | Second gallery grouped by `GroupBy`. Mobile: collapse to a tab. |
| _candLinkCell / AG/YT badges / Youtube+Agendas cols | Numbered source links, primary green vs others blue | L9379 | Candidates.agenda_urls/summary_urls/primary_url | 2 | Link rendering; `inlineViewerUrl` doc-viewer wrap = custom URL columns. |
| _candUpdateBadge | Nav badge = new high-confidence count | L9501 | Candidates.confidence/status | 2/4 | Count over full set; confidence computed (Grade 4 dependency). |
| Candidate confidence pill | HIGH/low colored pill | L9436 | Candidates.confidence | 4 | ⚠ AI/heuristic score; display trivial, value not Lists-native. |

### D.2 — SUGGESTED MATCHES (`#view-suggested`, DOM 543–567)

Entity **Suggested References**: `refId, jurisdiction, projectId, projectName, petitioner, excerpt, meetingDate, sourceStream/docType, sourceUrl, meetingId`.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| suggLoad | Fetch pending medium matches; build agenda-ref map from `tpProjects` | L9661 | Suggested References via `action=suggested_references`; TrackedProjects | 2 | Full set fetched; join done client-side. |
| suggRender | Summary + fixed-layout table | L9763 | Suggested References | 2 | `_suggSplitExcerpt` parses Petitioner via regex — needs a computed/flow-populated column. |
| Juris filter | `sugg-juris-filter` exact match | L9696 | Suggested Refs.jurisdiction | 1 | Delegable equality. |
| Sort | `sugg-sort`: Date desc or Jurisdiction asc, other as secondary | L9696/9704 | Suggested Refs.meetingDate/jurisdiction | 2 | ⚠ Multi-key client sort; date via `new Date()`. Single-column `SortByColumns` delegable. |
| suggBulk('approve') | "✓ Approve checked" — parallel approve (flips to New+High) | L9730 | WRITE `approve_reference` ×N parallel | 3 | Bulk cross-list state change → batched apply-to-each flow. Drives downstream Description/Results. |
| suggBulk('dismiss') | "✕ Dismiss checked" — parallel dismiss | L9730 | WRITE `dismiss_reference` ×N | 2 | Multi-select bulk write. |
| Checkboxes / select-all / bulk count | Per-row + select-all; live "N checked" | L9722/9723/9728 | selection state | 2 | Standard selection. |
| suggToggleAllDesc | Expand/collapse all excerpt cells | L9674 | Suggested Refs.excerpt | 2 | CSS toggle. |
| suggApprove | Per-row "✓ Approve" | L9828 | WRITE `approve_reference` | 3 | Single cross-list association + status flip. |
| suggDismiss | Per-row "✕ Dismiss" (reversible) | L9836 | WRITE `dismiss_reference` | 1 | Single status Patch. |
| suggOpenAddToExisting / suggAddToExisting | "Add to… ▾" — **re-points** ref to a different project then approves | L9853/9886 | READ TrackedProjects; WRITE `approve_reference&project_id` | 3 | Cross-list re-point + approve cascade. `Patch(SuggestedRefs, ref, {ProjectId:…, Status:"New", Confidence:"High"})` + association write. |
| _suggAgendaCell | Agendas column: up to 6 doc-links (+N) from matched project | L9635 | TrackedProjects.agendaRefs | 2 | Client join by projectId. |
| Source cell (summary-doc link) | Links Source to Gemini summary doc via `meeting_id→summary_doc` map | L9751/9791 | Suggested Refs.meetingId/sourceUrl; Meetings.summary_doc | 2 | Client-side map; `inlineViewerUrl` wrap = custom. |

### D.3 — AGENDA ITEMS (`#view-agendaitems`) & D.4 — YOUTUBE ITEMS (`#view-youtubeitems`)

Shared `ai*` code keyed by `stream` (`'ag'`/`'yt'`), state in `_aiState` (L10004). Entities **Agenda Items** / **Youtube Items**: `item_id, candidate_confidence+criteria, match_confidence(High/Medium/None)+criteria, auto_linked, match_count, matched_project_id/name, jurisdiction, project_name, ordinance_number, request_type, description, petitioner, meeting_date, source_url`. YT-only: `outcome/action_taken, agenda_item_id/url/ord/name/date, agenda_match_how`. Defaults: conf=High, dateDays=7, pageSize=50.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| aiLoad(stream,force) | Fetch entire parsed-item feed for the stream (cached until Refresh) | L10020 | Agenda/Youtube Items via `admin_run&fn=getAgendaItemsFeedJSON&stream=` | 2 | ⚠ NON-DELEGABLE at scale — whole stream (thousands) pulled, all filtering client-side. Core re-grade driver for both views. |
| aiRender(stream) | Summary counts, bulk-accept bar, per-stream table (yt adds Agenda Item + Action cols), pager | L10113 | Agenda/Youtube Items | 2 | Full-set render; yt table wide → poor mobile/print. |
| aiSetJuris | Jurisdiction dropdown (exact); options w/ per-muni counts | L10065 | .jurisdiction | 1 | Delegable equality; counts need full set. |
| aiSetConf | Match-confidence filter: High(default)/Medium/None | L10066 | .match_confidence | 4 | ⚠ NON-DELEGABLE — computed/AI auto-match score. Default High hides most rows; truncation invisible. |
| aiSetDate | Date filter Past Week/30/90/Custom (`meeting_date >= cutoff`) | L10067 | .meeting_date | 2 | Date `>=` delegable, but computed client-side from a rolling cutoff. |
| aiSetCustom | Custom range from/to (inclusive string compare) | L10074 | .meeting_date | 2 | ⚠ NON-DELEGABLE when combined with the free-text search. |
| aiSetSearch | Free-text over project_name+petitioner+ordinance_number+matched_project_name+description (`contains`) | L10079 | .fields | 2 | ⚠ NON-DELEGABLE — 5-field "contains". Truncates silently. |
| aiSetPageSize | Rows/page 50/100/250/all | L10080 | — | 2 | Client paging; "Show all" heavy. |
| aiGoPage | Prev/Next pagination | L10081 | — | 2 | ⚠ Pagination over full set hides truncation. |
| aiToggleAllDesc | Expand/collapse all Description cells | L10082 | .description | 2 | CSS toggle. |
| _aiCandPill | Candidate-confidence pill w/ criteria tooltip | L10089 | .candidate_confidence/criteria | 4 | Computed confidence + criteria = AI/heuristic. |
| _aiMatchPill / _aiMatchedCell | Match pill High/Medium/None w/ criteria; matched-project name, ● linked/○ not, "(+N more)", yellow "auto-match gap" | L10093/10099 | .match_confidence/criteria/auto_linked/match_count/matched_project_name | 4 | ⚠ Entire auto-match layer is AI/rules matching. Display standard; data not Lists-native. |
| aiTrack / aiOpenTrackModal / aiTrackConfirm | "＋ Track" — modal, then **create a NEW Tracked Project** | L10243/10247/10272 | WRITE TrackedProjects via `create_tracked_project`; refresh tpLoad | 3 | Cross-list create (+alias fold + downstream re-scan). `Patch(TrackedProjects,Defaults(...),{Name,OrdinanceId,Jurisdiction,Aliases,Notes})`. |
| aiOpenAddTo / aiAddTo | "Add to… ▾" — dropdown of active projects (same normalized jurisdiction); attach item | L10296/10327 | READ TrackedProjects; WRITE `fn=addAgendaItemToProject`; refresh tpLoad | 3 | Attach folds aliases + re-scans references server-side. |
| aiDismiss | "✕ Dismiss" — reversible; row spliced | L10344 | WRITE `fn=dismissAgendaItem` (`&undo=true`) | 1 | Single status Patch. |
| aiToggleSel / SelectAllPage / ClearSel | Bulk-accept checkboxes (only on "acceptable" rows: has matched_project_id, not auto_linked, not resolved) | L10362/10367/10375 | selection; .matched_project_id/auto_linked | 2 | Multi-select gated by computed acceptability (Grade 4 dependency). |
| aiBulkAccept | "✓ Accept selected" — sequential; attach each to ITS matched project | L10378 | WRITE `addAgendaItemToProject&project_id=matched_project_id` ×N | 3 | ⚠ Each accept folds aliases + re-scans (expensive); sequential. Many rows → long-running; use a flow. Depends on AI matched_project_id (Grade 4). |
| YT: Agenda Item twin cell | Shows the paired parsed agenda-document item for the same meeting (matched by ord#/name), w/ `agenda_match_how` | L10186 | YoutubeItems.agenda_item_id/url/ord/name/date/agenda_match_how | 4 | Cross-stream twin match is AI/heuristic pairing. |
| YT: Action/Outcome cell | Parsed `outcome`/`action_taken` (vote, result) | L10195 | YoutubeItems.outcome/action_taken | 4 | Parsed from video/minutes by Gemini — not native. |
| toggleYtTitle | Expand/collapse long YouTube titles | L5235 | video_title | 2 | CSS toggle. |
| ytResubmit | "↻ Resubmit" — re-summarize a hearing video; swaps in ✦ Summary link | L3760 | via `action=resummarize_hearing` → `summary_doc` | 4 | ⚠ Triggers Gemini re-summarization → Power Automate + AI Builder/external LLM. Loses on-demand transcript summarization. |
| ytToggleSummary / ytLoadSummary | Toggle & lazy-fetch a hearing's Gemini summary text (first 4000 chars, cached) via proxy | L3749/3730 | Hearing summary doc via `action=fetch_url` | 2 | Proxy fetch of external doc; in Power Apps a link-out or pre-imported summary column is simpler. |

### Cluster D grade tally
- **Grade 1:** 6 (candDismiss, suggDismiss, aiDismiss, candSetJuris, suggApplyControls-jurisfilter, aiSetJuris — equality dropdowns + single-record status Patches)
- **Grade 2:** ~30 (all Load/Render, page-size, pagination, expand-all, sort, checkbox-selection sets, bulk-dismiss, rail toggles, link/agenda cells, date filters, toggleYtTitle, ytToggle/LoadSummary, source cells)
- **Grade 3:** 9 (candTrack+cascade, candApprove, candAddToExisting, suggBulk-approve, suggApprove, suggAddToExisting re-point, aiTrack, aiAddTo, aiBulkAccept — each writes Tracked Projects + associations; Track auto-association → Power Automate)
- **Grade 4:** 9 (candidate-confidence scoring/pill + badge, candidate detection itself, aiSetConf computed filter, _aiCandPill, _aiMatchPill/_aiMatchedCell, YT twin pairing, YT outcome/vote extraction, ytResubmit — all AI Builder / flow + external LLM)


---

## CLUSTER E — Schedule & Requirements, Public Hearings, Review Queue, Parse Status

Scope: `#view-schedule`, `#view-publichearings`, `#view-reviewqueue`, `#view-parsestatus`.

### E.1 — Schedule & Requirements (`#view-schedule`, DOM 569–666)

This view is an **AI generator, not a data store** — nothing it produces is persisted. Its only durable state is `mrd_schedule_stages` localStorage. The results section is the "printable report," but there is **no print button and no `@media print` stylesheet** — printing relies on the Word export or the browser's Ctrl-P over `#sched-results-wrap`.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `sched-jurisdiction` select + `buildSchedDropdown`/`onSchedJurisdictionChange` | Jurisdiction picker grouped by county; onchange shows a ref-doc count | DOM 582; fn 8517, 8551 | Reference config (id, name, county, udoUrl, rezoningAppUrl, plat/schedule URLs) — client constant | 2 | Grouped combo box → a Jurisdictions Lists lookup with county grouping. |
| Entitlement Stages dropdown — `toggleStageDropdown` / `closeStageDropdownOutside` | Opens/closes the custom multi-select panel; outside-click closes | DOM 590; fn 8411, 8422 | UI only | 2 | Native combo box open/close. |
| **8 preset stage checkboxes** (Rezoning, Annexation, PUD, Preliminary Plat, Secondary/Final Plat, Variance BZA, Special Exception BZA, Development Plan) — `getSelectedStages`/`updateStageSelection` | Multi-select group; each `onchange` recomputes selection, updates button label, renders removable chips, persists | DOM 595; fn 8430, 8444 | localStorage `mrd_schedule_stages` `{preset[], customChecked, customText}` | 3 | Multi-select Grade 2, but the live label + chip-tag state + persistence is custom. `UpdateContext({stages: Filter(colStages, chk.Value)})`. |
| Custom stage text input + `stage-custom-check` | Free-text "Custom stage…"; focusing auto-checks its box; added if non-empty | DOM 603; fn 8435 | localStorage `.customText` | 3 | Combo can't natively fold in an ad-hoc value; needs a text input + Collect. |
| Stage tag chips + `removeStage` | Selected stages as chips with ✕ that unchecks the matching box | fn 8452, 8486 | same localStorage | 3 | Gallery of chips; ✕ = `Remove(colSelStages, ThisItem)`. |
| `restoreStageSelection` | On init, rehydrates checkboxes + custom text | fn 8468 | localStorage `mrd_schedule_stages` | 3 | `OnVisible` reads a stored setting → combo `DefaultSelectedItems`. |
| Additional Details textarea | Free-text project detail concatenated into the AI prompt | DOM 616; fn 8496 | Prompt input only | 2 | Multiline text input. |
| Target Approval Date | Date picker; defaults today+90; schedule computed backward | DOM 625; fn 8509 | Prompt input only | 2 | Date picker `DefaultDate = Today()+90`. |
| **Run Schedule & Requirements** (`runScheduleGeneration`) | Validates; fetches live UDO/PC/BZA pages; builds prompts; calls **Gemini 2.5 Pro** (temp 0.2, 8192 tok) via proxy; parses JSON → `{schedule[], requirements[], assumptions[], warnings[]}`; 30–60s | DOM 630; fn 8677, 8566 | Live web scrapes + Gemini call; result held in `window.currentScheduleResults`, **not persisted** | 4 | Core AI feature. Redesign: Power Automate + AI Builder / Azure OpenAI from the canvas app; the backward-scheduling statutory math (IC 36-7-4 notice periods, business-day offsets, aligning to real meeting dates) is heavy logic best in the flow. Live-URL scraping needs the flow (HTTP). Loses synchronous UX (becomes async) and fragile live grounding. |
| Timeline render + Timeline/Gantt toggle (`renderScheduleTimeline`, `renderGanttChart`, `scheduleTimelineView`) | Dated step list w/ type badges + "days before target"; toggle to inline CSS Gantt | fn 8791, 8826 | AI `schedule[]` (date, milestone, description, type, days_before_target, notes, warning) | 3 | Timeline list = gallery (Grade 2). The Gantt (computed left%/width%, date axis) is custom Power Fx layout or a Power BI visual. |
| Checklist render (`renderScheduleChecklist`) | Groups `requirements[]` by category into cards | fn 8866 | AI `requirements[]` (category, item, detail, source) | 2 | Grouped gallery (`GroupBy`). |
| Assumptions/Warnings render | `warnings[]` (amber) and `assumptions[]` | fn 8892 | AI `assumptions[]`, `warnings[]` | 2 | Two galleries. |
| Reference-doc links (`renderScheduleRefLinks`) | Chips linking UDO/rezoning/plat/PC/BZA URLs | fn 8764 | `JURISDICTION_REFS[id]` URLs | 2 | Gallery of hyperlinks. |
| **↓ Word Doc export** (`exportScheduleDoc`) | Full Word-flavored HTML report (Timeline table, Requirements table, Warnings/Assumptions); downloads `.doc` (`application/msword`). **Primary printable/shareable deliverable.** | DOM 654; fn 8907 | `currentScheduleResults` | 4 | No native "export to Word" in Power Apps. Redesign: Power Automate "Populate a Word template" (Word Online) → SharePoint/OneDrive or return for download. Gains a real .docx template. Because there's no print CSS, this doc IS the print path — high priority. |
| **↓ CSV export** (`exportScheduleCSV`) | Two-section CSV (timeline, requirements) w/ quote-escaping; `.csv` Blob | DOM 655; fn 8946 | `currentScheduleResults` | 4 | No client CSV download in canvas. Flow builds CSV (`CreateCSVTable`) → email/SharePoint, or export from a view. |
| **Copy** (`copyScheduleToClipboard`) | Plain-text report (timeline + checklist w/ `[ ]` + assumptions) to clipboard | DOM 656; fn 8968 | `currentScheduleResults` | 3 | `Copy()` exists in newer Power Apps; else a text box the user copies. |

### E.2 — Public Hearings / Hearing Schedule (`#view-publichearings`, DOM 150–185; currently hidden, code retained)

The "Tracked Projects" here has been **migrated off localStorage to a backend list** (`create/update_tracked_project`, shared `tpProjects`); `mip_ph_tracked` remains only for a one-shot legacy migration; `mip_ph_reviewed` persists reviewed-state keys.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Add New Tracked Project form (`ph-ord`, `ph-name`, `phAddProject`) | Ordinance # + Project Name (req) + Add. Validates; **dedupes** (case-insensitive) by ordinance and name; offers "add as alias" on dup; POST `create_tracked_project`; then `tpLoad(true)` | DOM 156; fn 7644 | Tracked Projects (projectId, projectName, ordinanceId, jurisdiction, aliases, status, dates) | 3 | Form + Patch Grade 2, but the case-insensitive dup-check across name+ordinance with an alias-merge branch is custom Power Fx. |
| `phAddAlias` | On dup confirm, appends new name/ord to `aliases`; POST `update_tracked_project` | fn 7712 | Tracked Projects.aliases | 3 | String-split/merge of a delimited alias field (ideally a related Aliases list). |
| Tracked Projects list + collapse toggle (`ph-tracked-list`, `phRenderTracked`, `phToggleChips`) | Active projects (excludes archived/closed/deleted) as chips sorted by latest date; collapse past a threshold | DOM 167; fn 7747, 7789 | Tracked Projects (filtered by status) | 2 | Gallery w/ Filter + Sort + show-more toggle. |
| `phMigrateLegacyLocalStorage` | One-shot: reads legacy `mip_ph_tracked`, de-dupes, POSTs each as `create_tracked_project`, clears key | fn 7798 | localStorage `mip_ph_tracked` → Tracked Projects | 3 | One-time migration/data-import step, not an app function. |
| Weekly calendar nav (`phWeekShift(-1/+1/0)`, `ph-week-label`) | Prev/Next/This-Week shift `phWeekOffset`; label shows Mon–Thu range | DOM 175; fn 7869 | UI state | 2 | Context var + date-range gallery. |
| Weekly grid render (`phRenderWeeklyHearings`, `phMondayOf`, `phCollectAllCouncilPcEntries`) | Computes Mon–Thu; aggregates Council + PC meetings across ALL munis via `buildUnifiedDateSet` (±1-day fuzzy match); buckets by day; per-day cards w/ Agenda/Summary/Minutes links, coverage-state badges, inline YouTube title | DOM 180; fn 7903, 7877 | Meetings (date, muniId/name, body_type, meeting_type, agendas, youtube_url, video_title, summary_doc, minutes_url, meeting_id, coverage_state) | 3 | Calendar range **is delegable** if meeting date is a real column. BUT the ±1-day cross-source fuzzy unification (`buildUnifiedDateSet`) and coverage_state → badge branching are client-side over the full set — custom Power Fx and **⚠ NON-DELEGABLE** as written. Pre-unify meetings into one list server-side. |
| Reviewed-state (`phSaveReviewed` / `phReviewedKeys`) | Persists "reviewed" meeting keys to localStorage | fn 7628 | localStorage `mip_ph_reviewed` | 2 | Per-user flag; better as a Lists column or user-state list. |

### E.3 — Review Queue (`#view-reviewqueue`, DOM 668–698, operator-only)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| `loadReviewQueue` + `rq-refresh` (↺ Reload) | Fetch `action=review_queue` (uncapped); render table: meeting id, jurisdiction, date, attempts, last retry, exhaustion/strategy, video, summary/draft | DOM 676; fn 9013 | Review Queue (meeting_id, jurisdiction, meeting_date, retry_attempt_count, last_retry_at, retry_strategy, video_url, summary_doc_url) | 2 | Gallery bound to a Review Queue list. **⚠ Potentially NON-DELEGABLE** if it grows to thousands (endpoint returns whole set, no server paging). Add delegable `Filter(status="pending")` + paging. |
| Per-row Decision buttons (`resolveReview(meetingId, decision)` × 3: **Accept Partial** `accept_as_partial`, **Force Redraft** `force_redraft`, **No Better Source** `no_better_source`) | POST `resolve_review`; fades+removes the row; sets the terminal state of an AI-summary recovery item | DOM 691; fn 9066 | Review Queue.status/decision | 4 | The click = a Patch (Grade 2/3), but each decision drives an **AI-summary retry/redraft pipeline**. "Force Redraft" re-triggers a Gemini job. Redesign: Patch a decision column; a Power Automate/AI Builder flow performs the redraft. The tightly-coupled recovery loop must be rebuilt. |

*(The `diagLoadReview`/`diagResolveReview` Diagnostics mirror at fn 9152+ reuses the same entity — see Cluster A.)*

### E.4 — Agenda Parse Status (`#view-parsestatus`, DOM 700–771, operator-only)

Backed by a **Parse Census** (per-document extraction outcome for every in-scope agenda, Council/PC ≥ 2025-01-01). Fetched whole, filtered client-side.

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Status filter (`ps-status`, 7 options) + `loadParseStatus` | unreviewed/needs_fix/empty_ok/requeued/ignored/cancelled/all. onchange refetches `fn=getAgendaParseReviewJSON&status=…`; handles not-built | DOM 712; fn 10444 | Parse Census (doc_id, source_url, pdf_url, jurisdiction, date, body, title, bucket, marker, review_status, note) | 2 | The **status filter passes to the backend** (`&status=`) → delegable server-side. Standard dropdown-bound gallery. |
| Jurisdiction filter (`ps-juris`) + `psApplyFilter` | Free-text box; oninput filters the **already-fetched** set by `jurisdiction contains term` | DOM 721; fn 10502 | Parse Census.jurisdiction | 3 | **⚠ NON-DELEGABLE** — client-side "contains" over a census of thousands; only the status-filtered subset is loaded. Fix: make jurisdiction a real column + push into the delegable query (`StartsWith`) or a jurisdiction lookup. |
| Reload (`ps-refresh-btn`) | Re-invokes `loadParseStatus` | DOM 722 | Parse Census | 2 | `Refresh(Census)`. |
| **⟳ Rebuild from scan** (`psRebuild`) | `fn=flagUnparsedAgendas` (~15s) re-derives parse outcome for every in-scope agenda; adds new, preserves triage, drops parsed; reloads | DOM 723; fn 10469 | Parse Census (server re-derivation over all agendas) | 4 | Heavy census recomputation over thousands of docs. Rebuild as a scheduled/on-demand Power Automate flow or Azure Function writing the census list. |
| Summary bar (`psRenderSummary`) | Counts per status | DOM 726; fn 10485 | Census `by_status` aggregates | 3 | Computed tallies. `CountRows(Filter(...))` per bucket — ⚠ delegation risk over thousands. Better as a grouped view or Power BI card. |
| Select-all (`ps-selall`) + `psToggleAll` | Header checkbox toggles all visible | DOM 744; fn 10547 | Selection state | 2 | Gallery select-all (`Collect`/`Clear`). |
| Row checkboxes + `psSelChanged` / `psSelectedDocs` / `psClearSel` | Per-row checkbox; "N selected"; show/hide bulk bar; Clear | DOM 727; fn 10538 | Selection state (doc_ids) | 2 | Standard multi-select. |
| **Bulk bar** — `ps-bulk-status` (5 options) + **Apply** (`psBulkApply`) | empty_ok/needs_fix/requeued/ignored/unreviewed. Confirms; POST `fn=setAgendaParseReviewBatch&doc_ids=csv`; warns on oversized-requeue reroute; reloads | DOM 730; fn 10556 | Parse Census.review_status (batch write) | 3 | Bulk via `ForAll(Selected, Patch(...))` or a single flow call. **⚠ NON-DELEGABLE risk**: `ForAll+Patch` capped/slow. Prefer a flow taking the id list. Oversized→needs_fix branch is custom logic. |
| Per-row triage — `psSetReview`/`_psActionBtn` (**Ignore/Empty-OK/Needs-fix/Re-queue**) | Four per-row buttons POST `fn=setAgendaParseReview&doc_id&status`; disables row; closes drawer; handles oversized reroute; reloads | fn 10506, 10638 | Parse Census.review_status | 3 | Single-row Patch Grade 2; the requeue→needs_fix reroute (packet too large) is computed cross-condition logic = Grade 3. |
| Per-row **Can** (Cancel) — `psCancel` / `psCancelFromBtn` | Confirms; POST `action=cancel_agenda` **then** `setAgendaParseReview status=cancelled` — a **two-list write** | fn 10607, 10614 | Meetings (cancel flag) + Parse Census.review_status=cancelled | 3 | Cross-list cascade write: two sequential `Patch` (or one flow) that must both succeed. |
| **Open** doc drawer (`psOpenDoc` / `psOpenDocFromBtn`) | Fixed right-side drawer w/ **iframe preview**; frames via `docs.google.com/viewer?embedded=true&url=…`; "Open in tab" to source | DOM 759; fn 10579, 10598 | Parse Census.source_url / pdf_url / title | 4 | **Web-doc iframe preview** — canvas Power Apps can't embed arbitrary web pages/PDFs inline. Redesign: store PDF in SharePoint + built-in PDF viewer, or launch in a new tab via `Launch()`. Loses inline side-by-side preview while triaging. |
| Close drawer (`psCloseDoc`) | Hides drawer, resets iframe; auto-called by every triage/bulk action | DOM 766; fn 10602 | UI only | 2 | Trivial. |

### Cluster E grade tally

| View | G1 | G2 | G3 | G4 | Rows |
|---|---|---|---|---|---|
| E.1 Schedule & Requirements | 0 | 6 | 6 | 3 | 15 |
| E.2 Public Hearings | 0 | 3 | 4 | 0 | 7 |
| E.3 Review Queue | 0 | 1 | 0 | 1 | 2 |
| E.4 Parse Status | 0 | 4 | 5 | 3 | 12 |
| **Total** | **0** | **14** | **15** | **7** | **36** |


---

## CLUSTER F — Embedded Dashboards (Zonda Market + Sales Disclosures)

Both dashboards are **read-only, client-side analytical apps**. Neither writes back. Both load full CSVs into browser memory via **Papa Parse** and render with **Chart.js**, computing every KPI, chart, and rollup in-browser over the entire dataset. `dashboard.html` fetches 5 core CSVs (286 / 1,474 / **25,600** / 5,444 / 5,987 rows) plus optional `ExistingTransactions.csv` (7,686 rows). `sales_dashboard.html` auto-loads a **gzipped** metro export from a GitHub raw CDN (`data-sales` branch, decompressed via `DecompressionStream`), de-duped by `SDF_ID` to ~thousands of priced transactions. Every aggregate/filter/chart runs over the **whole in-memory table** — in Power Apps + SharePoint that is far past the 500/2,000 delegation ceiling, so each is **⚠ NON-DELEGABLE**.

### F.1 — `dashboard.html` (Zonda Dashboard — Indianapolis New Home Market, ~1,107 lines)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Auto-load CSVs | Loading overlay fetches 5 core + 1 optional CSV, Papa-parses | `autoLoad`,`tryFetch`,`finishLoad` | All 5 CSVs + ExistingTransactions | 4 | ⚠ ~44k rows into memory. Becomes a dataflow/dataset refresh. |
| Manual folder/file picker | Fallback: `webkitdirectory` folder or multi-file select | `loadFromFiles`,`matchFile` | Same CSVs | 4 | No analog once data lives in Lists/PBI; drop. |
| Compare mode | Segmented control: Submarket / Communities / Floor Plan Pricing | `#modeSeg`,`setMode` | ProjectDetails; FP tables | 2 | Radio → context variable driving which visual shows. |
| Submarket level | City / County / School District grouping | `#smLevelSeg`,`submarketGroups` | City,County,School District | 3 | Regroups + re-aggregates the whole set. PBI slicer feeding a measure. |
| View toggle | Table vs Graphics | `#viewSeg`,`setView` | — | 2 | UI state. |
| Rail collapse / KPI hide | Collapse controls; hide/show KPI strip | `#railToggle`,`#kpiToggle` | — | 2 | Pure UI. |
| Optional multi-select filters (×8) | Custom checkbox dropdowns w/ search + Select-all/Clear for School District, City (cascades on County), County, Status, Builders, Parent Builder, Product Type, Product Style | `FILTER_DEFS`,`buildMultiSelect` | ProjectDetails columns | 2 | Combobox controls; City-depends-on-County cascade standard. ⚠ Filtered-set recompute non-delegable at scale. |
| Time Period from/to | Two month selectors bound the history charts; auto-clamp | `#periodFrom`,`#periodTo`,`inPeriod` | `Period` of Sales/PriceHist/FPPrice/Exist | 3 | Month keys derived by scanning 25.6k+ rows. PBI relative-date slicer. ⚠ NON-DELEGABLE. |
| Minimum Mo. Supply | Numeric threshold (FPP mode) | `#minMoS`,`computeFiltered` | Inventory Months of Supply | 2 | Numeric filter. |
| Apply / Clear filters | Commit pending filter state; reset | `applyFilters`,`cloneApplied` | — | 2 | Button → recompute. |
| Matching-count badge | Live count of communities passing filters | `#matchCount` | Filtered ProjectDetails | 3 | `CountRows(Filter(...))` — ⚠ delegation; move measure to PBI. |
| KPI stat cards (×8) | Communities, Units Planned/Sold/Remaining, Avg Sales Rate, Avg List Price, Monthly Sales (latest), Avg Months of Supply | `renderKpis` | ProjectDetails sums/avgs + latest-month scan of SalesHistory | 3 | Sums/avgs individually delegable, but latest-month Monthly Sales cross-joins Sales history (5,987) → ⚠ NON-DELEGABLE. PBI cards. |
| Data table — Submarket | Grouped rollup (10 cols) | `buildSubmarketTable` | ProjectDetails grouped | 3 | GroupBy + AddColumns aggregations; delegation-limited. PBI matrix. |
| Data table — Communities | 33-column per-community table | `buildCommunitiesTable` | ProjectDetails (33 fields) | 2/3 | Gallery/data-table can show 33 cols; derived money columns are row-level → Grade 2 feasible. |
| Data table — FPP | Per-community floorplan rollup | `buildFppTable`,`DB.fpById` | ProjectFloorplanDetails (1,474) ⋈ Details | 3 | Per-parent aggregation of child rows. ⚠ NON-DELEGABLE; PBI or pre-aggregated List. |
| Column sort | Click any header asc/desc | `renderTableInto` | current model | 2 | `SortByColumns`. |
| Column drag-reorder | Drag headers, persisted per mode | `reorderCols`,`ST.colOrder` | — | 4 | No native canvas equivalent; custom component. Usually dropped. |
| Row include/exclude checkboxes + Select-all | Excluded rows drop out of every chart | `ST.excluded`,`activeIds` | current model | 4 | Selection feeds all analytics; recompute is PBI-side. |
| Export filtered CSV | Downloads filtered ProjectDetails | `Papa.unparse` | Filtered ProjectDetails | 2 | Export/Office Script or PBI "Export data". ⚠ Full-set export bypasses paging. |
| Graphics tabs (×11) | Sales Trend, Avg Price, Avg Price Change, Median $/SqFt, Home Sales by Price, School Rating, All Home Sales, Starts & Closings, Lot Pipeline, Price History, Price vs SqFt | `TAB_DEFS`,`renderGraphicsView` | see each chart | 4 | Whole block → Power BI report pages. |
| Chart: Sales Trend | Monthly units-sold line; aggregate or per-group | `chartSalesTrend` | SalesHistory Monthly Sales × Period | 4 | Time-series over 5,987 rows. ⚠ NON-DELEGABLE. |
| Chart: Avg New Home Price | Horizontal bar, top-30 | `chartAvgPrice` | Avg. List Price | 3/4 | Group-avg + top-N. PBI bar. |
| Chart: Avg Price Change | Δ price vs 1/3/5 yr ago | `chartPriceDelta`,`deltaSeries` | ProjectPriceHistory (5,444) | 4 | Per-community time-lag lookup — heavy. ⚠ NON-DELEGABLE. |
| Chart: Median $/SqFt | Median sale price/sqft by level | `chartMedPPSF`,`medianOf` | ExistingTransactions Sale Price/Unit Size | 4 | No native delegable median over 7,686 rows. PBI. |
| Chart: Home Sales by Price Band | Stacked $20k bands, new vs resale | `chartTxnBands` | ExistingTransactions | 4 | Histogram binning. PBI. |
| Chart: School Rating | Avg elem/mid/high per district | `chartSchoolRating`,`ratingNums` | School Ratings columns | 3/4 | Parse+avg of delimited strings. PBI or pre-computed column. |
| Chart: All Home Sales + drill | New vs resale stacked; **click bar → $10k band drill** | `chartAllHomes`,`ST.allHomesDrill` | ExistingTransactions | 4 | Interactive drill-down; native PBI drill; lost in plain canvas. |
| Chart: Starts & Closings | Stacked bar, Annual/Quarterly | `chartStartsClosings` | Annual/Quarterly Starts/Closings | 4 | PBI. |
| Chart: Lot Pipeline | Finished Vacant + Future Inventory stacked | `chartLotPipeline` | Finished Vacant / Future Inventory | 4 | PBI. |
| Chart: Price History | Avg list price/month | `chartPriceHistory` | ProjectPriceHistory (5,444) | 4 | ⚠ NON-DELEGABLE time-series. PBI. |
| Chart: Price vs SqFt scatter | Floorplan lines + txn overlays + user plan series | `chartFppLines` | FloorplanDetails + ExistingTransactions | 4 | Multi-series scatter w/ join overlays. PBI scatter. |
| "Add Plans" modal | Manual paste of builder floor-plan prices drawn on scatter | `openPlanModal`,`PLAN_SERIES` | In-memory (`ST.planPrices`) | 4 | Entry form Grade 2, but paste-to-grid + live overlay custom; entry could be a Power Apps form → List, chart stays PBI. |
| Chart control toggles | Aggregate/By-group, Annual/Quarterly, 5/3/1yr, Labels, overlays, Back | `buildChartControls` | per chart | 4 | Map to PBI slicers/field toggles; several have no canvas analog. |
| Export PNG | Download current chart | `chart.toBase64Image` | current chart | 4 | PBI visual "export image". |
| Chart tooltips | Formatted $ / sqft / counts | Chart.js callbacks | per chart | 4 | Native PBI tooltips. |
| School-district fuzzy join | Normalizes abbreviated vs expanded district names to join Details ↔ ExistingTransactions | `schoolKey`,`DISTRICT_ABBR/ALIAS` | both sources | 3 | Token-signature join impractical in Power Fx. Do in a dataflow/PBI relationship. |
| Dark theme via `?theme=dark` | Reads query param, restyles for MRD embed | inline IIFE | — | 2 | Cosmetic embed detail. |

### F.2 — `sales_dashboard.html` (Sales Disclosure — Validation Dashboard, ~849 lines)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Auto-load gz dataset | Fetch `data-sales` CDN gzip, decompress, Papa-parse | `autoLoadData`,`DATA_URL_DEFAULT` | `sales_enriched_metro.min.csv.gz` | 4 | ⚠ Whole dataset in memory. Scheduled dataflow into a List/PBI dataset. |
| Manual CSV picker | File input fallback w/ schema validation | `#file` handler | uploaded CSV | 4 | Drop after migration. |
| Row de-dup by SDF_ID | Collapse join fan-out to one row per disclosure | `mapRows`,`seen` | all rows | 3 | Do in source/dataflow. |
| City canonicalization | Levenshtein + alias table fixes typos to standard city | `canonCity`,`_lev`,`CITY_ALIAS` | rep_city → _city | 3 | Fuzzy cleanup — impractical in Power Fx; do in Power Query/dataflow. |
| County dropdown | All-counties select | `#fCounty` | County_Name | 2 | Distinct → dropdown. |
| Property-city combobox | Type-or-pick datalist | `#fCity`,`#cityList` | _city | 2 | Combobox. |
| Transaction-type dropdown | New Construction / Vacant Land / Resale-other | `#fKind` | transaction_kind | 2 | Dropdown. |
| Builder (seller) dropdown | Per-builder counts + "any" | `#fBuilder` | builder_canonical | 2 | Dropdown w/ counts (counts a Grade 3 rollup). |
| Land-buyer dropdown | Per-buyer counts + "any" | `#fLandBuyer` | buyer_builder_canonical | 2 | As above. |
| Subdivision combobox | Only builder/land-buyer-active subdivisions | `#fSubdiv`,`SUB_ACTIVE` | subdiv_canonical | 2/3 | Active-set is a pre-pass over all rows. |
| School-district dropdown | Alphabetical w/ counts | `#fSchool` | school_district | 2 | Dropdown. |
| Property-class multi-select | Checkbox dropdown, search + Select-all/Clear | `initClassMultiselect`,`selClasses` | primary_class_code,prop_class_descs | 2 | Combobox multi-select. |
| Date range | From/To conveyance-date filter | `#fFrom`,`#fTo` | conveyance_date → _date | 2 | Date pickers. |
| Free-text search | Substring across street/city/buyers/sellers/preparers/parcels/SDF_ID/builder/subdiv/school | `#fSearch` (`hay`) | ~10 columns | 3 | Multi-field concat → ⚠ NON-DELEGABLE `Search()` over thousands; PBI/Dataverse better. |
| Reset filters | Clears all 10 controls + class set | `#reset` | — | 2 | Button. |
| `apply()` filter engine | Combines all filters; **always excludes $0/null-price**; recomputes stats+charts+table | `apply`,`VIEW` | all filter columns | 3 | ⚠ NON-DELEGABLE full-table Filter over thousands. Core case for PBI. |
| Stat cards (×4–6) | Transactions, Median price, Single-family %, Premium-vs-AV %, New-construction %, Vacant-land % | `renderStats` | _price,sale_vs_AV,_sf,transaction_kind | 3 | Median + %-of-filtered = measures. ⚠ non-delegable median. PBI cards. |
| Chart: Sales by month | Bar of counts by month | `barChart('chMonth')` | _date | 4 | Time bucket over full VIEW. PBI. |
| Chart: Top counties | Horizontal bar, top-12 | `barChart('chCounty')` | County_Name | 4 | PBI. |
| Chart: Top property classes | Horizontal bar, top-10 | `barChart('chClass')` | prop_class_descs | 4 | PBI. |
| Chart: Top builders | Horizontal bar, top-12 | `barChart('chBuilder')` | builder_canonical | 4 | PBI. |
| Chart: Transaction type | New Construction vs Vacant Land | `kindChart('chKind')` | transaction_kind | 4 | PBI. |
| Chart: County submission recency | Per-county latest filing date + counts; over **RAW** (unfiltered), stalest-first | `recencyChart`,`_doy` | County_Name,_date | 4 | Custom max/count-by-group + label plugin. PBI. |
| Charts lazy-render | Charts computed only when `<details>` expanded | `#chartsBox` toggle | — | 2 | Perf detail; PBI page loads on demand. |
| Transactions table | Paged data table, formatted money/acres/date, pill badges | `render`,`COLS` | 16 columns | 2 | Gallery/data-table per-row. |
| Column sort | Click header, type-aware | `buildThead` | current cols | 2 | `SortByColumns`. |
| Column drag-reorder | Drag headers | `dragIdx` | — | 4 | No native canvas equivalent. |
| Pagination | Prev/Next + "page x/y" | `#prev`,`#next` | VIEW slice | 2 | Native gallery paging. |
| Rows-per-page | 50/100/250/500/1,000/2,500 | `#perPage` | — | 2 | ⚠ 1,000/2,500 exceed delegation cap; would truncate silently in canvas. |
| Export CSV | Filtered rows in current column order/sort | `exportCSV`,`Papa.unparse` | VIEW | 2 | ⚠ Exports full filtered set (thousands) — beyond canvas capacity; use PBI export/Office Script. |
| Theme follow `?theme` | Light/dark via query param | inline IIFE | — | 2 | Embed detail. |

### Cluster F recommendation

**These two dashboards should NOT be rebuilt as Power Apps canvas screens over SharePoint Lists — they should stay as Power BI reports embedded via the Power BI tile/visual (or Power BI Embedded) inside the app's "Zonda" and "Sales Disclosures" tabs.** They are read-only, high-cardinality analytical visualizations: `dashboard.html` computes time-series, medians, per-parent floorplan rollups, price-lag deltas, histogram binning, and fuzzy cross-dataset joins over **~44,000 rows** (25,600 in price history alone); `sales_dashboard.html` filters, aggregates, and charts **thousands** of de-duped disclosures with median/percentage measures and a multi-field free-text search. Essentially **every KPI, chart, filter recompute, and export here is ⚠ NON-DELEGABLE** against SharePoint's 500–2,000-row limit — a canvas rebuild would either silently truncate results (wrong medians, wrong "top-N", wrong monthly trends) or require pulling everything into collections, which SharePoint cannot sustain at this volume. Power BI is the correct home: its dataset model handles the row counts, delegable-free DAX measures replace the in-browser aggregations, native slicers replace the dropdowns/date-range/multi-selects, and native drill-down + tooltips + "export data/image" replace the custom drill, PNG export, and tooltip code. Migrate the CSV ingestion and the two heavy data-cleaning routines — **city canonicalization (Levenshtein) and school-district fuzzy join** — into a **Power Query dataflow** feeding the PBI model, since neither is expressible in Power Fx. The only pieces that belong in the Power Apps + Lists layer are small write-back/entry affordances if desired (e.g., the "Add Plans" price entry could become a Power Apps form writing to a List the PBI scatter reads). Treat Cluster F as a **Power BI workstream, priced separately** from the Power Apps + Lists rebuild.

Mobile/print: both are desktop-first — wide multi-column tables (16–33 cols), fixed-height Chart.js canvases, and hover-only tooltips do not degrade gracefully on phones, and **canvas charts do not print** cleanly from an iframe; Power BI's responsive/phone layouts and export-to-PDF resolve both.

### Cluster F grade tally

| Grade | Zonda | Sales | Cluster F total |
|---|---|---|---|
| GRADE 1 | 0 | 0 | **0** |
| GRADE 2 | ~9 | ~13 | **~22** |
| GRADE 3 | ~7 | ~5 | **~12** |
| GRADE 4 (→ Power BI) | ~16 | ~9 | **~25** |
| **Functions** | **~32** | **~27** | **~59** |

Zero Lists-native functions; GRADE 4 is the single largest bucket — confirming these embedded dashboards are analytics that belong in Power BI, not a Power Apps + SharePoint canvas rebuild.


---

## CLUSTER G — Required functions (graded even though not in the current app)

These two were mandated by the brief. Neither exists in MRD today; both are priced for the rebuild.

### G-1 — Printable meeting report (export to Excel with a saved format, then print)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Printable meeting report | Operator picks a meeting (or jurisdiction + date range); system emits a formatted report of the hearing — agenda items, matched Tracked Projects, outcomes/votes, AI summary — as an Excel workbook with a saved layout, which the user then prints. | New. Nearest current analog: `exportBriefing()` (Word briefing) and `exportScheduleCSV()`/`exportScheduleDoc()`. | Reads **Meetings** (id, jurisdiction, date, body, video, summary doc), **Agenda_Items** + **Youtube_Items** (request summary, outcome, vote, notes), **Tracked_Projects** (name, ordinance, builder, lots). | **GRADE 3** (export mechanism itself is Grade 2–3; the underlying cross-list gather is Grade 3) | See mechanism assessment below. |

**Grading the export mechanism (Excel-with-saved-format → print):**
- **The Excel generation is a solved, low-risk pattern — GRADE 2/3.** Best implementation is a **Power Automate flow** using the *Excel Online (Business) → "Add a row into a table"* actions against a **template workbook** stored in the SharePoint/OneDrive doc library. The template carries the saved format (column widths, header band, print area, page setup, repeating header rows). The flow: (1) trigger from a canvas button (`meetingId` param) or a scheduled/manual run; (2) `Get items` from `Meetings`, then `Agenda_Items`/`Youtube_Items` filtered by `MeetingId eq …` and `Tracked_Projects` by the matched IDs; (3) copy the template to a new file; (4) populate the table rows; (5) return the file to the app (or email/save to a "Reports" library).
- **Why not "just print the screen":** Power Apps canvas has no reliable pixel-accurate print; the Excel-template route gives a **repeatable, pre-formatted, print-area-defined** artifact — which is exactly why the brief specifies it.
- **What pushes it to Grade 3:** the report is a **cross-list join** (Meeting → its Agenda/Youtube items → their Tracked Projects → AI summary), not a single-list dump. That gather is real logic. Power Fx sketch (if assembled client-side before handing to the flow):
  ```
  Set(gRptItems,
    AddColumns(
      Filter(Agenda_Items, MeetingId = gMeeting.ID),
      "Project", LookUp(Tracked_Projects, ID = MatchedProjectId).Title,
      "Outcome", LookUp(Youtube_Items, AgendaItemId = ThisRecord.ID).Outcome));
  // then pass gRptItems to the 'Generate Meeting Report' flow
  ```
- **Delegation:** the per-meeting item filters are `eq` on a lookup ID → **delegable**. Safe at scale *if* the join key is a stored indexed column (index `MeetingId` on Agenda/Youtube).
- **Print/mobile:** printing happens in Excel, not the app — clean, consistent, and mobile-independent. The user gets a real saved artifact. **Loss vs. today:** an extra click (open the returned workbook) instead of an in-browser one-shot download; formatting lives in a template file someone must maintain.

### G-2 — Scheduled backup export (recurring automated export of all three — here, all — lists)

| Function | Description | Location | Data touched | Grade | Notes |
|---|---|---|---|---|---|
| Scheduled backup export | A recurring, unattended job that exports every list to timestamped files so data survives any interface failure. | New. No analog today (today's "backup" is implicitly Google Sheets version history). | **All** lists: Tracked_Projects, Agenda_Items, Youtube_Items, Members, Jurisdictions, Meetings, Agenda_Candidates, Suggested_References, Review_Queue, Parse_Census, Tagged_Documents. | **GRADE 3** (a maker-level flow, but real logic: pagination past delegation, per-list loop, dated foldering) | Flow sketch below. |

**Flow sketch (Power Automate — "MRD Nightly List Backup"):**
1. **Trigger:** *Recurrence* — daily 02:00 tenant time.
2. **Compose** a run stamp: `formatDateTime(utcNow(),'yyyy-MM-dd')`.
3. **Create folder** `/Backups/{stamp}/` in a SharePoint "Backups" library (retention/versioning on).
4. **For each list** (array variable of the 11 list names): *Get items* with **`$top` + pagination / a Do-Until on `skiptoken`** so it pulls **beyond the 5,000-item list-view threshold** (this is the real work — a naïve *Get items* silently caps and would back up a truncated dataset, defeating the purpose).
5. *Create CSV table* from the item array → *Create file* `/{stamp}/{listName}.csv`.
6. Optional: *Create sharing link* / zip via Office Scripts; **email a success/failure digest** to the operator so a silent backup failure is visible.
7. **Error path:** configure *Run after* on failure → *Post to Teams / email* so a broken backup is loud, not silent.

**Grade rationale & notes:**
- **GRADE 3, not 4** — Power Automate does this natively; no external service needed. It is above Grade 2 only because correct handling of the **5,000-item pagination ceiling** and the per-list loop is genuine logic a template won't hand you.
- **Delegation/scale:** the pagination Do-Until is precisely what defends against the delegation ceiling that plagues the *interactive* views — the backup must not inherit the 2,000-row truncation. Call this out to whoever builds it.
- **What it buys:** interface-independent durability — even if the canvas app or a flow breaks, the raw lists are on disk daily. This is the custody argument that won the architecture decision, made concrete.
- **Loss vs. today:** none — it is strictly better than relying on Google Sheets revision history; adds tenant-governed, dated, restorable copies.


---

## SUMMARY SCORECARD

### Functions per grade (all clusters)

| Cluster | G1 | G2 | G3 | G4 | Subtotal |
|---|---|---|---|---|---|
| A — Shell / Nav / Settings / Diagnostics | 4 | 17 | 8 | 12 | ~41 |
| B — Overview / Jurisdictions / Members / Intel | 4 | 22 | 14 | 8 | ~48 |
| C — Competitor Tracked Projects | 0 | 15 | 11 | 14 | ~40 |
| D — Candidates / Suggested / Agenda / Youtube | 6 | 30 | 9 | 9 | ~54 |
| E — Schedule / Hearings / Review Queue / Parse Status | 0 | 14 | 15 | 7 | 36 |
| F — Embedded dashboards (Zonda + Sales Disclosures) | 0 | 22 | 12 | 25 | ~59 |
| G — Required (printable report, scheduled backup) | 0 | 0 | 2 | 0 | 2 |
| **TOTAL** | **14** | **120** | **71** | **75** | **~280** |

**Read the shape, not the decimals.** ~280 distinct user-facing functions. Only **5% (14) are free in Lists**; **43% (120) are canvas commonplaces**; but **52% (146) are Grade 3 or 4** — real Power Fx, cross-list logic, or full redesign. Many rows are dual-graded (a Grade 2 control whose underlying rollup/confidence is Grade 3/4); counts are honest approximations, not a precise census. The headline: this is **not** a like-for-like port — over half the surface carries genuine build risk, concentrated in the AI/derived-data "intelligence" layer, the delegation-hostile read paths, and the analytics dashboards.

### Delegation verdict (against the stated few-thousand-row scale)

The app's core pattern everywhere — **fetch the whole list, then filter/search/sort/paginate in the browser** — is precisely what Power Apps punishes. The following are **⚠ NON-DELEGABLE** and will silently truncate at 500–2,000 rows (returning *wrong* results, not errors), so they are re-flagged out of any naïve Grade 1/2:
- **All multi-field free-text searches** — Tracked Projects (5-field), Candidates, Agenda Items, Youtube Items (5-field), Sales Disclosures (~10-field). `contains`/`Search()` never delegates.
- **All computed/AI-column filters & sorts** — match-confidence (High/Medium/None), candidate-confidence, `past_week` recency, `meeting_date`/normalized-jurisdiction sorts (override-aware, cross-list).
- **All cross-list rollups & counts** — Overview stats, per-muni member counts, tracked-doc counts, parse-census tallies, and the entire 4-entity `list_tracked_projects_detailed` join.
- **Client-side pagination** across every queue **hides** the truncation from the operator.
- **Everything in Cluster F** — analytics over 44k / thousands of rows.
The mandated fix is architectural: move the read path server-side (indexed `eq`-able key columns, pre-aggregated summary lists refreshed by Power Automate, and Power BI for analytics). Budget this before any screen work — it is the single biggest hidden cost.

### Top 5 highest-effort items

1. **The AI / derived-data "intelligence" layer (Grade 4, spans A/B/C/D/E).** Gemini hearing summaries + item-scoped detailed summaries, member-profile research (with YouTube-video multimodal grounding), auto-match confidence scoring + criteria, candidate auto-detection, lot extraction, alias suggestion, and the Schedule-&-Requirements generator. None has a Lists/Power Fx equivalent; each is a separate **Power Automate + AI Builder / Azure OpenAI** build, and the video-grounded profile research and statutory backward-scheduling are the hardest. This is the largest and least-certain bucket.
2. **Cluster F analytics → Power BI workstream.** Two full dashboards (~59 functions, ~44k rows) that must be re-authored as Power BI datasets/reports with Power Query dataflows for the Levenshtein city-canonicalization and school-district fuzzy joins. Priced separately; substantial.
3. **Delegation-safe read redesign of Tracked Projects + the three item queues.** The 4-entity server-side join, indexed key columns, server-side search/filter, and pre-aggregated summary lists — foundational plumbing that everything else depends on.
4. **Document tagging + Google Drive integration + live-DOM link decoration (Cluster C.5).** The "✚ on any link on the page" MutationObserver model has no canvas equivalent; rebuild on SharePoint document libraries with a per-doc gallery and server-side fetch-and-archive flows.
5. **Export / print + backup deliverables, including the two required functions.** There is **no `@media print` and no print button anywhere today** — every Word/CSV export (`exportBriefing`, `exportScheduleDoc/CSV`, detailed-summary export) must be rebuilt as Word Online "Populate template" / CSV flows, plus the new **printable meeting report** and the **scheduled backup export** flow (with correct 5,000-item pagination). Individually modest, collectively a real slice.

### Honest effort estimate

Treat these as **hours-scale ranges for a competent Power Platform maker+dev pairing**, deliberately wide because the AI layer dominates the uncertainty — not a fixed bid.

- **Foundation** — 11 SharePoint Lists + relationships + indexed columns + the delegation-safe read redesign (server-side filter/search, pre-aggregated summary lists): **~60–120 hrs**.
- **Canvas app core** — 12–14 screens with the Grade 1/2 galleries, forms, filters, dropdowns, inline edits, navigation, theme, and real Entra/SharePoint auth to replace the fake operator flag: **~120–220 hrs**.
- **Grade 3 custom Power Fx** — override-precedence cascades, weekly-calendar unification, alias-chip UIs, cross-list write actions (Track / Approve / Add-to), status lifecycle, rollup displays: **~80–150 hrs**.
- **Grade 4 rebuilds as Power Automate + AI Builder / Azure OpenAI** — summaries, profile research, auto-match, schedule generation, scrapers, Drive→SharePoint tagging, undo-history: **~180–360 hrs** (the dominant unknown; a decision to *drop* rather than rebuild some of these could cut this sharply).
- **Power BI workstream (Cluster F)** — dataflows (incl. fuzzy joins), dataset modeling, two report rebuilds, embedding: **~90–170 hrs**.
- **Required extras + hardening** — printable meeting report flow, nightly backup flow, exports, testing/UAT/migration: **~50–90 hrs**.

**Rolled up: roughly 580–1,110 hours — call it a ~4–7 person-month build**, with the Grade 4 intelligence layer and the Power BI analytics accounting for well over half. A defensible *minimum viable* rebuild — the Lists, the transactional Grade 1/2/3 surfaces, Power BI for analytics, and backups, while **deferring or dropping the heaviest AI features** (accepting their loss or keeping the existing pipeline running alongside) — lands nearer the **low end (~580–700 hrs)**. A full like-for-like rebuild that reproduces every AI-derived behavior pushes toward and past the **high end**. The right next step is a v3 brief that explicitly decides, feature by feature, which Grade 4 items to rebuild, defer, or retire — that single set of decisions moves the estimate more than anything else here.
