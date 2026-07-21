# HANDOFF — Municipal Resource Dashboard (MRD) → Power Apps rebuild

_Last updated: 2026-07-21 · Branch: `claude/pm-dashboard-inventory-feasibility-ergvm5`_

## Architecture decision (2026-07-21) — RECORDED

**Chosen path: Power Apps (canvas) + SharePoint Lists.** This wins over the previously-floated custom HTML Lists port.

**Rationale (per IT ruling): custody + scalability.**
- **Custody** — the data and app live inside the Microsoft 365 tenant: Entra ID identity, tenant backup/retention, list versioning, and governance. Today's stack (a static HTML SPA calling a personal Google Apps Script deployment over Google Sheets, with a `localStorage`-set "operator" flag standing in for auth) has no real custody story.
- **Scalability** — SharePoint Lists + Power Automate + (where analytical) Power BI is the supported, load-bearing path; the Apps Script/Sheets backend and the fetch-whole-list-then-filter-in-browser SPA pattern do not scale cleanly to the stated few-thousand-row item volume.

## What was produced this pass (Inventory B)

- **`FUNCTION-INVENTORY.md`** — exhaustive, view-by-view inventory of every user-facing function across the real MRD app (`index.html`, 14 views) and the two embedded dashboards (`dashboard.html` Zonda, `sales_dashboard.html` Sales Disclosures), each graded 1–4 for the Power Apps / Lists rebuild, with **Power Apps delegation limits explicitly evaluated against the few-thousand-row scale** (every non-delegable filter/sort/search flagged). Includes the two required extra functions (printable meeting report; scheduled backup export) and a summary scorecard.
- **Scope note:** the dispatching brief assumed a "Deals/Tasks/third-list project manager" — that does not describe this repo. MRD spans ~13 real data entities; the inventory maps each to its future SharePoint List. ("Deals" = the removed `leadsdeals-reporter.html`, now in `Wildhare1966/entitlement-reporter`.) No `snapshot.data.js` exists here.

## Deprecations — EXECUTION-BRIEF-v2

The Power Apps decision deprecates the following, pending a **v3 brief**:
- **Step 2** — (HTML Lists port work) — deprecated; the custom HTML port is not the chosen path.
- **Step 3A** — Graph-scripted list creation (`list-schema.json` Graph format) — **deprecated**; lists will be created via the Lists/SharePoint UI or CLI, not a Graph creation script.
- **Step 3B** — (dependent on 3A) — deprecated with 3A.
- Note: no `EXECUTION-BRIEF-v2` file exists in this repo; these references come from the external project context and are recorded here for continuity.

## Next (needs a v3 brief before any build)

1. Author EXECUTION-BRIEF-v3 targeting Power Apps + Lists (UI/CLI list creation, not Graph).
2. Stand up the SharePoint Lists per the entity map + `LIST-SCHEMA.md` (this pass, if schema step ran).
3. Address the delegation redesign up front: the read path must move server-side (indexed key columns, pre-aggregated summary lists, or Power BI for analytics) — a like-for-like client-filter port will silently truncate.
4. Replace the fake `localStorage` operator flag with real Entra/SharePoint permissions.
5. Decide the fate of the Grade 4 "intelligence" surfaces (Gemini summaries, member profile research, scrapers) — each is a separate Power Automate + external-AI build or an accepted loss.

## Standing rules (unchanged)

- Nothing deploys. `Data/` is never committed. Stop and report verbatim on any auth prompt or error.
