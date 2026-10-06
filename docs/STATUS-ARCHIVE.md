# STATUS archive — Indiana MIP Tracker (MRD front end)

`STATUS.md` was **retired on 2026-08-29** on Ty's ruling. Everything it held is preserved verbatim
below; nothing was edited on the way in.

## Why it was retired

Doctrine Block v1.8 **item 11** makes `STATUS.md` optional — *"a state snapshot, never a changelog;
OPTIONAL, and a repo whose `HANDOFF.md` already carries the coordinates may retire it, but only once
`HANDOFF.md` exists."* Both conditions held: `HANDOFF.md` exists (created 2026-08-28, now rev 5) and
carries the live coordinates in its own table.

The file had also stopped being a snapshot and become a changelog — rev-delta sections stacked
newest-first — and it was **stale in three ways that actively misled**:

| Claim in the retired file | Reality on 2026-08-29 |
|---|---|
| "Build **p151r2** on `main`" | served build was `p168r2` |
| "Pages remains enabled until the verification checklist passes" | Pages was disabled on/before 2026-08-16; **MIP-2** closed as MOOT on 2026-08-23 |
| `MIP_Platform.html` "(blanked…)" | 470,244 bytes, not blank |

This is not a new observation. **MIP-2**'s closing note records that the 2026-08-22 backfill read
this stale `STATUS.md` instead of the report sitting beside it, and calls that *"the whole thesis of
SYS-8."* The file misled a session, was corrected, and then misled the start of this one too.

## Where its live content went

Nothing load-bearing was lost. Before retirement, each rule was checked against the file that now
owns it:

| Rule in the retired file | Now lives in |
|---|---|
| Bump the build marker on line 2 **and** the `styles.css?v=` querystring on every deploy | `CLAUDE.md` → *What is actually served* (already migrated at rev 4) |
| This working copy is the source of truth for FE edits — edit in place, commit, push; no per-session temporary clones | `CLAUDE.md` → *What is actually served* (migrated at rev 5) |
| Do not commit secrets; the commit-time credential guard | `CLAUDE.md` → *This is a PUBLIC repo* |
| What this repo is / current state / next actions | `HANDOFF.md` (the item-11 lane for exactly this) |

The one line deliberately **not** carried forward is *"Read tokens embedded in the front end are
public by design"* — that describes the pre-AGD-22 world. There is no `DEFAULT_AUTH_TOKEN` in this
repo any more; the operator token is entered into `localStorage` and never committed.

---

# ⬇ Retired content, verbatim (STATUS-STAMP: 2026-08-23 | rev 4)

STATUS-STAMP: 2026-08-23 | rev 4

## Rev 4 delta — the auth token is gone from this public repo

- **AGD-22 shipped here** (the item lives in `indiana-agenda-tracker`; the code is this repo's).
  `mrd-ad682070b7/index.html` no longer contains `DEFAULT_AUTH_TOKEN`. It reads `mip_auth_token` from
  `localStorage` through `getAuthToken()`, entered once in a new **Settings -> Operator Access** card.
- **A sweep of this tree for 48-hex literals now returns nothing.** Also cleaned: the stale root
  `MIP_Platform.html` (blanked, and headed with a note that it is ~71 builds behind the served build and
  must not be "restored"), both `smoke.html` files (they now read the same localStorage key), and
  `arcgis/sync_tracked_projects.py` + `.ipynb`.
- ⛔ **This does not unpublish anything.** Public git history keeps the old token permanently — that is
  why rotation was the fix and the scrub is hygiene. The rotated value is inert.
- **Verified in the live browser**, not from the diff: public actions still answer at full size
  (149,875 B) with no token in the URL; the token rides only when the operator has entered one.
- Reading the dashboard is unaffected. **Operator actions stay inert until Ty enters the token**
  (AGD-29).


## Rev 3 delta — both open items closed as MOOT; the AGO clicks finally boarded

- **MIP-2 was false the day it was written.** It asserted "Pages is still serving this tracker."
  Probed three ways today: `gh api …/pages` → `404`, `gh api repos/… --jq '.has_pages'` → **`false`**,
  `curl -L https://wildhare1966.github.io/indiana-mip-tracker/` → `404`. And it was **already known** —
  `Dexters-Dashboard/reports/DOC-SWEEP_pages-cutover_2026-08-16.md:13` says so outright and proves it
  with a control probe against a second Pages site, so the 404s cannot be a network block. The 8/22
  backfill read this repo's stale `STATUS.md` and not the report beside it. **That is the whole thesis
  of SYS-8.**
- **MIP-1 closed with it** — the local-server path is not merely verified but in daily use.
- **The repo is still `public`, deliberately** — that half of decision D-B stands.
- **MIP-3 added:** the three AGO clicks (schedule the sync daily, disable the arborhomes sync, delete
  the dead-end wildhare `LeadsDeals`). Open since the 8/14 audit's D2, carried into X-4, and never
  boarded. It is the **shared upstream of EMAP-1**: supplying `AGO_TOKEN` regenerates the map once,
  but only the schedule keeps it current.


> **Note:** this repository is **public**. Keep this file free of tokens, IDs, local paths, and any
> operational detail that shouldn't be world-readable. Working notes belong in the private
> `indiana-agenda-tracker` repo, not here.

## What this repo is
The static front end for the Municipal Resource Dashboard (MRD). The application lives at
`mrd-ad682070b7/index.html`; `styles.css` and the two embedded dashboards sit beside it. Two
non-`main` branches carry published data snapshots consumed by the app at runtime.

The backend, pipelines, and all engineering documentation live in a separate private repository.

## Current state
- Build **p151r2** on `main`. Working tree clean; in sync with the remote.
- This working copy is the **source of truth** for front-end edits (established 2026-08-15).
  Edit in place, commit, push — no per-session temporary clones.
- Served locally for development on port 8778.
- A commit-time credential guard is active and was verified working on 2026-08-17: a staged
  credential-shaped string is blocked before it can be committed. The test fixture used for that
  verification has been removed.

## In progress
- Migration of the front end from GitHub Pages hosting to a local static server. Pages remains
  enabled until the verification checklist passes.

## Blocked
- Nothing.

## Next actions
- Complete the local-server verification checklist, then disable Pages.

## Conventions
- Bump the build marker on line 2 of `mrd-ad682070b7/index.html` **and** the `styles.css?v=`
  querystring on every deploy.
- Do not commit secrets. Read tokens embedded in the front end are public by design; treat
  everything else as private.

---

## Board closures rotated 2026-10-06 — closed 2026-08-23 to 2026-08-29

Moved **verbatim** out of `docs/OPEN-ITEMS.md` `## Recently closed` at the 2026-10-06 close-out
(`OPEN-ITEMS-SPEC.md` rev 10, retention rule 2: that section holds one session's closures). Nothing
was edited on the way in.

| ID | Closed | What happened |
|---|---|---|
| **MIP-9** | 2026-08-29 | **`STATUS.md` retired on Ty's ruling** — doctrine item 11 makes it optional *"once `HANDOFF.md` exists"*, and it does (rev 5, carrying the live coordinates in its own table). The file had stopped being a snapshot and become a stacked changelog, and was stale three ways that actively misled: build `p151r2` (served was `p168r2`), "Pages remains enabled" (disabled on/before 2026-08-16 — **MIP-2** closed MOOT 2026-08-23), and `MIP_Platform.html` "blanked" (470,244 bytes). Not a new fault: MIP-2's closing note already records the 2026-08-22 backfill reading this same stale file instead of the report beside it, *"the whole thesis of SYS-8"* — it then misled the start of this session too. Retired the item-11 way: content preserved **verbatim** in `docs/STATUS-ARCHIVE.md` under a note explaining why, plus a table mapping each live rule to the file that now owns it. One rule was still only in `STATUS.md` — *the working copy is the source of truth for FE edits; edit in place, no per-session clones* — and was migrated to `CLAUDE.md` rev 5 before deletion. One line deliberately dropped: *"read tokens embedded in the front end are public by design"*, which describes the pre-AGD-22 world. No external tooling read the file (hub-wide grep: only historical prose references). This repo now runs on two lanes. |
| **MIP-8** | 2026-08-29 | **Fixed — after the item's own premise turned out to be half false.** The item repeated `.gitignore`'s claim that *"canonical copies live in indiana-agenda-tracker/ops/"*. Probed before touching anything (doctrine item 14): that private `ops/` held **only `p168-ops.html`**, and a hub-wide `find` for `p16[0-3]-ops.html` returned **four hits, all of them in this repo**. The tracked public copies were the **only copies in existence** — untracking them first would have left them backed up nowhere. Sequence actually run: (1) **preserve** — the four copied to `../indiana-agenda-tracker/ops/` (private, clean tree, left uncommitted for Ty), sha256-verified after the copy; (2) **fix the guard** — `/p168-ops.html` + `/*-ops.html` replaced with a single unanchored `*-ops.html`, since a leading slash anchors to the repo root and `*` never crosses a `/`; `git check-ignore -v` now confirms it catches both `mrd-ad682070b7/tests/p160-ops.html` and root `p168-ops.html`; (3) **untrack, do not delete** — `git rm --cached` on all four, so they stay on disk and still serve at `:8778`, which is the whole point of them (same origin ⇒ they can read `mip_auth_token` from `localStorage`). All four still probe **200**, as does root `p168-ops.html`. The `.gitignore` comment was rewritten to record why the old patterns failed rather than just asserting the rule. ⛔ **Untracking does not unpublish** — they remain in this public repo's history, exactly like the old auth token. No rotation needed: they carry no token, and their one `/exec` URL is byte-identical to the served build's. |
| **MIP-7** | 2026-08-29 | **Done on Ty's ruling** — root `tests/smoke.html` deleted and the empty `tests/` directory removed. Identity re-verified by full sha256 immediately before deleting (`aac3e974…c01b31`, both copies, 10,634 B). Non-reference verified at the source of the doubt: the app's **▶ Run security self-test** link (`mrd-ad682070b7/index.html:316`) is `href="tests/smoke.html"` — **relative**, so it resolves to `mrd-ad682070b7/tests/smoke.html`, never the root copy. Post-delete probe: served path **200**, root `/tests/smoke.html` **404**. The surviving copy was then **run in-browser**: 10/10 sanitizer tests pass and "Unauthenticated call returns 403" passes; the authenticated case stays pending, correctly, because no operator token is in that browser profile. Its prose was corrected as the item anticipated — both the visible line and the inline-copy comment named `MIP_Platform.html`, the stale `p80r4` root copy, instead of the served build. The root is now down to files that are all load-bearing. ⚠ This item surfaced **MIP-8**. |
| **MIP-3** | 2026-08-29 | **Closed complete on Ty's ruling** — all three AGO clicks done: the `Projects` sync scheduled (ruled first, which broke the staleness chain feeding the Entitlement Reporter and, via Zonda, the `Entitlement_Map` that decision **D6** made the primary external vehicle), the arborhomes sync disabled, and the dead-end wildhare `LeadsDeals` deleted. **EMAP-1**'s shared upstream is no longer stale-by-default: supplying `AGO_TOKEN` regenerates the map once, but it is the schedule that keeps it current, and the schedule now exists. Open since the 2026-08-14 audit (decision **D2**), carried through **X-4**, boarded in the SYS-8 sweep, narrowed to two clicks earlier the same day and closed outright hours later. ⚠ Closed on Ty's report, **not on a probe from here** — this session has no AGO access. |
| **MIP-6** | 2026-08-29 | **Fixed — and the fix is not the one the item proposed.** The item offered "delete the button and `refreshHearings()`" as option 1. Deleting the function would have **broken four live callers**: `submitManualUrlAdd`, `submitRemoveUrl`, `rollbackManualEntry` and `submitFlagSummary` all call it to refresh the list after a successful Apps Script write. Three of the four sit inside `setTimeout` callbacks, where a `ReferenceError` is uncaught and silent. So this was **not dead code** — and because its `fetch` always threw, **none of those four writes has actually been refreshing the list**: the operator saw "✓ Saved" over a stale row. Shipped: the **button** removed from the topbar (it advertised "Re-fetch hearing records from Google Sheets" and could not do it), the function **kept** and reduced to the old success path, `location.reload()`; the vestigial `#refresh-btn` local-only hide at the boot handler removed. Build bumped **`p168r1` → `p168r2`** on both markers per the STATUS.md convention. Verified in-browser: page loads, 41 municipalities, `typeof refreshHearings === 'function'`, `#refresh-btn` absent, **zero console errors**. |
| **MIP-5** | 2026-08-29 | **Done on Ty's ruling** — root `dashboard.html`, `sales_dashboard.html`, `styles.css` and `Data/` (6 CSVs) deleted, and the empty `Data/` directory removed. Byte-identity re-verified by sha256 immediately before deleting, not taken from the item text: all three HTML/CSS files and **all six** CSVs matched their `mrd-ad682070b7/` counterparts exactly. Non-reference verified two ways: the served build's asset references are all **relative** (`styles.css`, `dashboard.html?theme=`, `sales_dashboard.html?theme=`), so they resolve inside `mrd-ad682070b7/`, and a `grep` for absolute-root `src="/` / `href="/` in the served directory returns nothing. Post-delete HTTP probe: `/mrd-ad682070b7/` + its three assets all **200**, root `/dashboard.html`, `/styles.css`, `/MIP_Platform.html` all **404** — nothing was reaching the root copies. ⚠ Root `tests/smoke.html` was **not** swept in (unenumerated) — boarded as **MIP-7**. |
| **MIP-4** | 2026-08-29 | **Header corrected; the file survives.** Ty first ruled "delete", then reversed to "correct the header instead of deleting" mid-session — the deletion was staged and un-staged, so `MIP_Platform.html` is intact and only its header block changed (one diff hunk at line 4, 30 insertions / 8 deletions, body untouched). The corrected block fixes every stale claim: live build `p151r2` → **`p168r2`**, "~71 builds behind" → **88 p-numbers**, and it records that the two `smoke.html` files reference this file **in prose only** (they inline-copy the sanitizers; nothing loads it). It also records a consequence MIP-5 created: this file's only asset reference is root `styles.css`, now deleted, so **it no longer renders standalone** — expected, since it is a reference artifact and not a runnable page. Closes with a maintenance line telling the next deploy to re-check the block, which is the whole lesson of this item. |
| **MIP-2** | 2026-08-23 | **MOOT — Pages was already off, and had been for at least a week.** Probed three ways today: `gh api …/pages` -> `404`, `gh api repos/… --jq '.has_pages'` -> **`false`**, `curl -L https://wildhare1966.github.io/indiana-mip-tracker/` -> `404`. It was **already known**: `Dexters-Dashboard/reports/DOC-SWEEP_pages-cutover_2026-08-16.md:13` states "Phase 5 already landed. Pages is off" and proves it with a control probe against a second Pages site, so the 404s cannot be a network block. ⚠ **This row was false the day it was written** — the 8/22 backfill read this repo's stale `STATUS.md` and not the report beside it, which is the whole thesis of **SYS-8**. The repo is still `public`; that half of decision D-B stands deliberately. |
| **MIP-1** | 2026-08-23 | Closed with **MIP-2**, which it existed only to unblock. The local-server path is not merely verified but **in daily use** — `serve-mrd.bat` binds `127.0.0.1:8778` and is started at login by `serve-mrd.vbs`. There are no longer two live surfaces for one tracker. |
