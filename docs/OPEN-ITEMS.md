# Open items — Indiana MIP Tracker

FILE-STAMP: 2026-08-29 | rev 5

**Format contract: `Dexters-Dashboard/docs/OPEN-ITEMS-SPEC.md`.** These rows are rendered on
the dashboard's **Items** page alongside every other project's, so keep to the spec — a row
that drifts from it silently stops being indexed. This file records what is *outstanding*;
current state lives in `HANDOFF.md` (Doctrine Block v1.7 item 11 lanes).

Backfilled 2026-08-22 (Ty-ruled R5) by reading this repo's own `STATUS.md`/`HANDOFF.md` and
judging what was still live. Items recorded there but since closed were deliberately not
carried forward.

## Needs Ty — decisions and approvals

| ID | Owner | Item | Why it matters | Blocked by |
|---|---|---|---|---|
| **MIP-4** | TY | Rule on `MIP_Platform.html` — its stale-copy warning has itself gone stale | The file is 470 KB of build `p80r4`, not served, and its header warning is **the only thing stopping someone restoring it**. That warning states the live build is `p151r2` and the file is *~71 builds behind*; the served build was probed at **`p168r1`** on 2026-08-28, so the warning now misdescribes reality. A guard that is wrong about the thing it guards is worse than no guard. Options: correct the header, or delete the file outright since nothing but the two `smoke.html` files reference it. **Left unedited because this is a PUBLIC repo** — your call. | — |
| **MIP-3** | TY | Do the three AGO clicks — schedule the sync daily, disable the arborhomes sync, delete the dead-end wildhare `LeadsDeals` | Open since the 2026-08-14 audit (decision **D2**), carried into **X-4**, and **never boarded** until the SYS-8 sweep. Until the MRD → wildhare `Projects` sync runs on a timer, the feature layer only moves when someone runs the notebook by hand — and **everything downstream inherits that staleness**: the Entitlement Reporter, and via Zonda the `Entitlement_Map` that decision **D6** promoted to the primary vehicle for external audiences. This is the shared upstream of **EMAP-1**; supplying `AGO_TOKEN` regenerates the map once, but only the schedule keeps it current. | — |

## Claude Code can execute — say the word

| ID | Owner | Item | Why it matters | Blocked by |
|---|---|---|---|---|
| **MIP-5** | CC | Clear the root leftovers of the pre-P150 layout: `dashboard.html`, `sales_dashboard.html`, `styles.css`, `Data/` (6 CSVs), and rule on `MIP_Platform.html` with `MIP-4`. | Measured 2026-08-29: the three root HTML/CSS files are **byte-identical duplicates** of their `mrd-ad682070b7/` counterparts, and root `Data/ProjectDetails.csv` is identical to both the served copy and the (now archived) Zonda copy — three copies of the same file. Not inference: `Zonda-dashboard/ARCHITECTURE.md:204` names them directly — *"The FE clone's root `dashboard.html` is likewise a leftover of the pre-P150 layout."* The equivalent stale copy in `indiana-agenda-tracker` was deleted on Ty's ruling the same day, on the P116 precedent. ⚠ **This is the public repo** — verify each file is unreferenced by the served build before deleting. | — |

## Recently closed

| ID | Closed | What happened |
|---|---|---|
| **MIP-2** | 2026-08-23 | **MOOT — Pages was already off, and had been for at least a week.** Probed three ways today: `gh api …/pages` -> `404`, `gh api repos/… --jq '.has_pages'` -> **`false`**, `curl -L https://wildhare1966.github.io/indiana-mip-tracker/` -> `404`. It was **already known**: `Dexters-Dashboard/reports/DOC-SWEEP_pages-cutover_2026-08-16.md:13` states "Phase 5 already landed. Pages is off" and proves it with a control probe against a second Pages site, so the 404s cannot be a network block. ⚠ **This row was false the day it was written** — the 8/22 backfill read this repo's stale `STATUS.md` and not the report beside it, which is the whole thesis of **SYS-8**. The repo is still `public`; that half of decision D-B stands deliberately. |
| **MIP-1** | 2026-08-23 | Closed with **MIP-2**, which it existed only to unblock. The local-server path is not merely verified but **in daily use** — `serve-mrd.bat` binds `127.0.0.1:8778` and is started at login by `serve-mrd.vbs`. There are no longer two live surfaces for one tracker. |
