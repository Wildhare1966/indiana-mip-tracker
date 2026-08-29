# HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-08-29 | rev 6

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `../indiana-agenda-tracker/ARCHITECTURE.md` §0 is the source of truth.
> rev 1 (2026-08-28, the hub-wide configuration audit's phase-6 backfill) is in
> [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

## One line

The root now holds only load-bearing files, the last dead cross-project call is gone, `MIP-3` is
closed complete, and `CLAUDE.md` documents that **this repo receives at the git level but writes at
the app level**; served build is **`p168r2`**. **The board is empty** — eight rows closed in one session, none left open, and `STATUS.md` is retired.

## Live coordinates

| Thing | State |
|---|---|
| Repo | `main` @ **`f3c2434`**, pushed, clean — public remote `Wildhare1966/indiana-mip-tracker` |
| Served build | **`p168r2`** — `mrd-ad682070b7/index.html`, 704,284 B (probed 2026-08-29) |
| Local URL | `http://localhost:8778/mrd-ad682070b7/` via `serve-mrd.bat` (loopback only) |
| Root contents | `CLAUDE.md` · `HANDOFF.md` · `MIP_Platform.html` · `arcgis/` · `docs/` · `mrd-ad682070b7/` · `serve-mrd.bat` |
| Data lanes | `main` · `data` · `data-sales` — both non-`main` lanes are written **by other projects** |
| Operator token | `localStorage` key `mip_auth_token`, entered under Settings → Operator Access |
| Backend | lives in `../indiana-agenda-tracker` — **not** this repo |
| Board | `docs/OPEN-ITEMS.md` **rev 9** — MIP-3 through MIP-9 all closed; **nothing outstanding** |

⚠ Re-probe before relying on the build number (doctrine item 14). The marker is on line 2 of
`mrd-ad682070b7/index.html`; the `styles.css?v=` querystring on line 14 must match it.

## What shipped this session

**Three commits, all pushed, both trees clean.** `72fbfab` here (MIP-4/5/6/7/8) · `f3c2434` here
(MIP-9, the `STATUS.md` retirement) · `3614926` in `../indiana-agenda-tracker` (custody of the four
ops consoles). Nothing is uncommitted.

1. **`CLAUDE.md` rev 1 → rev 2: the outbound-write audit.** The question that started it — "does this
   repo only receive?" — has a **split answer**, now documented as its own section. At the **git**
   level it is strictly a receiver: one remote, no submodules, no workflows, no `git push` or
   `api.github.com` anywhere, and both data branches written by outside projects. At the
   **application** level it is the **primary write surface into the backend** — 23 side-effecting
   `action=` routes, three real POSTs, including a base64 document upload and a Gemini egress. Also
   documents the `data-sales` CDN relay into ArcGIS Online.
2. **MIP-4 — `MIP_Platform.html`'s header corrected, file kept.** Ty ruled delete, then reversed to
   correct-the-header mid-session; the staged deletion was reverted. One diff hunk at line 4, body
   untouched. Every stale claim fixed, plus a maintenance line telling the next deploy to re-check it.
3. **MIP-5 — root flattened.** `dashboard.html`, `sales_dashboard.html`, `styles.css` and `Data/`
   (6 CSVs) deleted after sha256 re-verification and a post-delete HTTP probe (served paths 200,
   root paths 404).
4. **MIP-6 — the `:8765` call resolved, and it was *not* dead code.** See the gotcha below. Build
   bumped `p168r1` → `p168r2` on both markers.
5. **MIP-7 — the last root leftover gone.** Root `tests/smoke.html` deleted after sha256 re-check;
   the app's **▶ Run security self-test** link is relative and always resolved to the served copy
   (probe: served **200**, root **404**). The surviving copy was **run**: 10/10 sanitizer tests pass,
   unauthenticated call returns 403. Its prose named `MIP_Platform.html` instead of the served build
   — corrected in both places.
6. **MIP-3 closed complete** on Ty's report that all three AGO clicks are done. ⚠ Closed on that
   report, **not on a probe from here** — this session has no AGO access.
7. **MIP-8 — the `.gitignore` guard fixed, and its own premise corrected.** See below.
8. **MIP-9 — `STATUS.md` retired** (Ty's ruling, doctrine item 11). Content preserved verbatim in
   `docs/STATUS-ARCHIVE.md`; its one un-migrated rule — *this working copy is the source of truth,
   edit in place, no per-session clones* — moved to `CLAUDE.md` rev 5 first. **Two lanes now:**
   `HANDOFF.md` + `docs/OPEN-ITEMS.md`. Do not recreate `STATUS.md`.

The MIP-8 narrative (why the order had to be preserve → fix → untrack) rotated to
[`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md) to stay under the 150-line cap; the full closed
row is in [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).

## Gotchas carried forward

- ⛔ **`*-ops.html` consoles are served but untracked.** Keep them on disk; do not "restore" them to
  git to protect them. Back them up to `../indiana-agenda-tracker/ops/` instead. Never re-add a
  leading slash to the `.gitignore` pattern — that anchors it to the root and was the MIP-8 bug.
- ⛔ **`refreshHearings()` is NOT dead code.** Its `fetch` was dead; the function is not. Four write
  paths call it after a successful `/exec` write — `submitManualUrlAdd`, `submitRemoveUrl`,
  `rollbackManualEntry`, `submitFlagSummary` — and three call it inside `setTimeout`, where a
  `ReferenceError` is uncaught and **silent**. Deleting it would have broken all four invisibly.
  This is the session's lesson: *grep for callers before removing anything a dead endpoint touches.*
- ⚠ **A dead endpoint hides its own blast radius.** Because that `fetch` always threw, those four
  writes have **never** been refreshing the list — the operator saw "✓ Saved" over a stale row. The
  visible symptom (a header button flashing "✗ Server offline") was the *least* of it.
- ⛔ **Public git history keeps the old token permanently.** Rotation was the fix; the scrub is
  hygiene. A scrub unpublishes nothing.
- ⛔ **Never open the app as `file://`** — `Origin: null` 404s the `/exec` POST redirect, and the CSP
  refuses `file:` siblings.
- ⛔ **Do not "restore" `MIP_Platform.html`** and do not delete it — Ty ruled it stays, header
  corrected. It no longer renders standalone (root `styles.css` is gone); that is expected.
- **`serve-mrd.bat` must use `python.exe`, not `pythonw`** — console-less stderr crashes
  `http.server` per request.
- ⚠ **Port 8765 belongs to `../Sales Disclosures`.** Do not bind it here.
- ⚠ **`indiana-mip-tracker` vs `indiana-agenda-tracker`** — one word apart, front end vs backend.
- **`data` and `data-sales` are separate lanes.** No cross-merges; never hand-publish to `data` —
  P118 force-orphan-commits it on a cron and your commit disappears.

## ✦ The reflective lesson

**Every item this session was a guard that had outlived what it guarded — and in two cases the item
describing the guard was wrong too.**

The session opened on "which repo owns `map.wildhare.app`?" and the answer turned on one project
carrying three different names (folder `Land_Presentation_Map`, repo `entitlement-reporter`, domain
`map.wildhare.app`). Everything after it was the same shape:

| The guard | What it still claimed | Reality |
|---|---|---|
| `MIP_Platform.html`'s stale-copy header | live build `p151r2`, "~71 builds behind" | `p168r2`, 88 p-numbers |
| `.gitignore`'s "NEVER commit these" | that it matched `*-ops.html` | root-anchored; matched nothing in a subdir |
| the Refresh Hearings button | "Re-fetch hearing records from Google Sheets" | called a server that no longer exists |
| `STATUS.md` | build `p151r2`, "Pages remains enabled" | `p168r2`; Pages off since 2026-08-16 |

**The operational rule that came out of it: a board row is a claim, not a coordinate** (doctrine item
14, applied to our own boards). Two rows were wrong in ways that would have caused damage if
executed literally — MIP-6 proposed deleting a function with four live callers, and MIP-8 asserted
backups existed that did not. Both were caught by probing the row's premise *before* acting on it,
which cost minutes and saved a silent breakage and a data loss. **Re-probe the item, not just the
code it points at.**

Corollary worth keeping: **a dead call hides its own blast radius.** The `:8765` fetch's visible
symptom was a button flashing an error. Its actual effect was that four write paths had never
refreshed the list since the endpoint died — "✓ Saved" over a stale row, indefinitely.

## Next session

**Nothing is gating here.** The board is empty, both repos are clean and pushed, and this repo now
runs on two state lanes. Work for this platform is normally driven from `../indiana-agenda-tracker`
— start there and treat this repo as the place the FE build lands.

If you do work here, the three things most likely to bite are all in **Gotchas** above:
`refreshHearings()` is not dead code, the `*-ops.html` consoles are served but untracked, and the
`.gitignore` pattern must stay unanchored.

⛔ **Do not recreate `STATUS.md`.** It was retired deliberately (MIP-9). A state claim goes in this
file; history goes in `docs/STATUS-ARCHIVE.md`.
