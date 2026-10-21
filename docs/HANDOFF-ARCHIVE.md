# HANDOFF archive — Indiana MIP Tracker (MRD front end)

Rotated out of the live `HANDOFF.md` under Doctrine Block v1.8 item 11 (one session per file,
150-line cap, history rotates here). Newest first.

---


## rev 6 — 2026-08-29 — the full live file, rotated 2026-10-06

Rotated out of `HANDOFF.md` when rev 7 replaced it (one session per file). Verbatim except that every
heading is demoted one level to nest under this one.

## HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-08-29 | rev 6

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `../indiana-agenda-tracker/ARCHITECTURE.md` §0 is the source of truth.
> rev 1 (2026-08-28, the hub-wide configuration audit's phase-6 backfill) is in
> [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

### One line

The root now holds only load-bearing files, the last dead cross-project call is gone, `MIP-3` is
closed complete, and `CLAUDE.md` documents that **this repo receives at the git level but writes at
the app level**; served build is **`p168r2`**. **The board is empty** — eight rows closed in one session, none left open, and `STATUS.md` is retired.

### Live coordinates

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

### What shipped this session

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

### Gotchas carried forward

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

### ✦ The reflective lesson

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

### Next session

**Nothing is gating here.** The board is empty, both repos are clean and pushed, and this repo now
runs on two state lanes. Work for this platform is normally driven from `../indiana-agenda-tracker`
— start there and treat this repo as the place the FE build lands.

If you do work here, the three things most likely to bite are all in **Gotchas** above:
`refreshHearings()` is not dead code, the `*-ops.html` consoles are served but untracked, and the
`.gitignore` pattern must stay unanchored.

⛔ **Do not recreate `STATUS.md`.** It was retired deliberately (MIP-9). A state claim goes in this
file; history goes in `docs/STATUS-ARCHIVE.md`.

---
## rev 6 detail — 2026-08-29 — MIP-8 narrative

Rotated out of `HANDOFF.md` rev 6 under the 150-line cap. The session summary and the reflective
lesson stay in the live file; this is the supporting detail.

## MIP-8 — a broken guard, and a premise that was half false

`.gitignore` claimed *"NEVER commit these: this repo is PUBLIC"* about `*-ops.html` consoles while
its two patterns (`/p168-ops.html`, `/*-ops.html`) were **root-anchored** and matched nothing in a
subdirectory. Four consoles sat tracked and public in `mrd-ad682070b7/tests/` (`p160`–`p163`).

**The item's own premise did not survive probing.** It repeated `.gitignore`'s claim that canonical
copies live in `../indiana-agenda-tracker/ops/`. That directory held **only `p168-ops.html`**; a
hub-wide `find` for `p16[0-3]-ops.html` returned four hits, **all in this repo**. The public copies
were the only copies — untracking first would have left them backed up nowhere.

So the order mattered: **preserve → fix → untrack.** The four were copied to the private repo's
`ops/` (sha256-verified, left uncommitted for Ty), the pattern collapsed to one unanchored
`*-ops.html`, and the files `git rm --cached`'d but **kept on disk** — they must stay on this origin
to read `mip_auth_token` from `localStorage`. All four still serve **200**.

⛔ **Untracking does not unpublish.** They stay in this public repo's history, like the old token.
No rotation needed: no token in them, and their one `/exec` URL is byte-identical to the served
build's.

---

## rev 1 — 2026-08-28

Created by the hub-wide configuration audit (phase 6 backfill). The repo had a `STATUS.md` and
`docs/OPEN-ITEMS.md` but no `HANDOFF.md` and no `CLAUDE.md`; item 11 requires the `HANDOFF.md` lane,
so it was backfilled from this repo's own `STATUS.md`, `docs/OPEN-ITEMS.md`, `serve-mrd.bat`, the
served build's own marker, and `git log` — **not** from carried context.

**One line:** the auth token is out of this public repo's live tree and the operator console is
token-gated; served build was `p168r1`.

**Coordinates as of rev 1:** `main` @ `4871165`; served build `p168r1`, 704,359 B (probed
2026-08-28); local URL `http://localhost:8778/mrd-ad682070b7/`; lanes `main` / `data` / `data-sales`.

**What had shipped:**

1. The auth token is gone from this public repo's live tree (AGD-22, boarded in
   `indiana-agenda-tracker`; the code is this repo's). `mrd-ad682070b7/index.html` no longer contains
   `DEFAULT_AUTH_TOKEN` — it reads `mip_auth_token` from `localStorage` via `getAuthToken()`.
2. A sweep of the tree for 48-hex literals returns nothing. Also cleaned: the stale root
   `MIP_Platform.html`, both `smoke.html` files, and `arcgis/sync_tracked_projects.py` + `.ipynb`.
3. Verified in the live browser, not from the diff — public actions still answer at full size with no
   token in the URL; the token rides only when the operator has entered one.
4. `.gitignore` added to keep local operator consoles out of this public repo.

**Open item found during the backfill, not yet boarded at the time:** `MIP_Platform.html`'s
stale-copy warning had itself gone stale — it stated the live build was `p151r2` and the file
"~71 builds behind" while the served build was `p168r1`. Left unedited as Ty's call. This became
**MIP-4**, ruled on and closed 2026-08-29.

---

## rev 7 — 2026-10-06 — the full live file, rotated 2026-10-21

Verbatim copy of `HANDOFF.md` rev 7 (MIP-10, the laptop-retirement reconciliation), moved here when rev 8 was written.

## HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-10-06 | rev 7

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `C:\Users\ty\Claude_Code\indiana-agenda-tracker\ARCHITECTURE.md` §0 is the
> source of truth. rev 6 (2026-08-29, MIP-3..9) and rev 1 are in
> [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

## One line

The laptop's last FE commit and the desktop's unpushed one are reconciled: `main` reads `p209r1` →
`p209r2` → **`p210r1`**, pushed as a fast-forward, the `laptop/943404b` side branch is deleted, and the
served build is **`p210r1`**. One item open: **MIP-11**, two guards that still name `p168r2`.

## Live coordinates (probed 2026-10-06 on Dexters-Machine)

| Thing | State |
|---|---|
| Repo | `main` @ **`13d98a6`** (`p210r1`) plus this close-out commit, pushed — public remote `Wildhare1966/indiana-mip-tracker` |
| Remote heads | `main` · `data` · `data-sales` · four `claude/*` agent-scratch branches; **no `laptop/*`** |
| Served build | **`p210r1`** on both markers — `mrd-ad682070b7/index.html`, 757,777 B in the working copy; served `index.html` and `sales_dashboard.html` hash-match `HEAD` |
| Local URL | `http://localhost:8778/mrd-ad682070b7/` via `serve-mrd.bat` (loopback only) — answering **200** |
| GitHub Pages | off (`gh api … --jq .has_pages` → `false`) — the local server is the only deploy |
| Data lanes | `main` · `data` · `data-sales` — both non-`main` lanes are written **by other projects** |
| Operator token | `localStorage` key `mip_auth_token`, entered under Settings → Operator Access; **none in the built-in browser pane's profile** |
| Backend | lives in `C:\Users\ty\Claude_Code\indiana-agenda-tracker` — **not** this repo |
| Board | `docs/OPEN-ITEMS.md` **rev 10** — **MIP-11** open (CC); MIP-10 closed this session |
| Untracked | `serve-mrd.log` (server log, not part of any change; left alone) |

⚠ Re-probe before relying on the build number (doctrine item 14). The marker is on line 2 of
`mrd-ad682070b7/index.html`; the `styles.css?v=` querystring on line 14 must match it.
⛔ `CLAUDE.md` line 56 still says `p168r2` — that is **MIP-11**, not the truth.

## What shipped this session

A Ty-authorized git reconciliation after the laptop's retirement (the desktop is now the primary
machine). Full record: **MIP-10** in `docs/OPEN-ITEMS.md`.

1. **Probed before acting.** `origin/main` = `4cebe80` (`p209r1`). Local `main` had unpushed
   `81cbe77` (`p210r1`: a GET read to the web app gets one retry; writes never retry). The laptop's
   `943404b` (`p209r2`: Sales Disclosures dashboard to sales-disclosures `7236884`) was on GitHub as
   `origin/laptop/943404b`. Both on `4cebe80`, neither containing the other.
2. **Rebased `main` onto `943404b`.** The one conflict was the two marker lines; kept `p210r1`
   (already in sequence, so no renumbering). Rebased `p210r1` is **`13d98a6`** — `81cbe77` is gone
   from every ref. `index.html` = `81cbe77`'s byte for byte; `sales_dashboard.html` = `943404b`'s.
3. **Verified.** Secret-pattern scan of `4cebe80..HEAD` clean. Served page renders (41
   municipalities, `refreshHearings` still a function). `tests/smoke.html`: 13 pass, 7 fail — every
   failure is a token-gated suite answering `403 Unauthorized` with no token in the profile, the
   documented no-token result (`smoke.html` lines 39-41). Sanitizers 10/10, CSP integrity pass.
4. **Pushed** `4cebe80..13d98a6` as a fast-forward; `ls-remote` = local `HEAD`. Then **deleted**
   `laptop/943404b` from GitHub; `ls-remote refs/heads/laptop/*` is empty.
5. **Board rotated.** MIP-1..9 moved verbatim to `docs/STATUS-ARCHIVE.md`; this file's rev 6 moved
   to `docs/HANDOFF-ARCHIVE.md`. **MIP-11** boarded.

## Gotchas carried forward

- ⚠ **Line endings.** `core.autocrlf=true` (system gitconfig): the index is LF, the working copy
  CRLF. A tool that rewrites a file through Git Bash `awk`/`sed` can leave it LF on disk; git
  normalizes on commit, but re-checkout the file afterwards (`rm` it, `git checkout -- <file>`) so the
  working copy matches its neighbours.
- ⚠ **The smoke test fails, not skips, without a token.** 7 failures with `Unauthorized` in the
  message mean "no token in this browser profile," not a regression. To exercise them, Ty enters the
  token under Settings → Operator Access in the same profile. Claude never enters it.
- ⛔ **`*-ops.html` consoles are served but untracked.** Keep them on disk; back them up to
  `C:\Users\ty\Claude_Code\indiana-agenda-tracker\ops\`. Never re-add a leading slash to the
  `.gitignore` pattern — that anchors it to the root and was the MIP-8 bug.
- ⛔ **`refreshHearings()` is NOT dead code.** Four write paths call it after a successful `/exec`
  write, three inside `setTimeout` where a `ReferenceError` would be silent.
- ⛔ **Public git history keeps the old token permanently.** Rotation was the fix; a scrub
  unpublishes nothing.
- ⛔ **Never open the app as `file://`** — `Origin: null` 404s the `/exec` POST redirect, and the CSP
  refuses `file:` siblings.
- ⛔ **Do not "restore" or delete `MIP_Platform.html`** — Ty ruled it stays (MIP-4). It no longer
  renders standalone; that is expected.
- **`serve-mrd.bat` must use `python.exe`, not `pythonw`.** ⚠ **Port 8765 belongs to
  `C:\Users\ty\Claude_Code\Sales Disclosures`.**
- ⚠ **`indiana-mip-tracker` vs `indiana-agenda-tracker`** — one word apart, front end vs backend.
- **`data` and `data-sales` are separate lanes.** Never hand-publish to `data` — P118
  force-orphan-commits it on a cron. (It moved during this session: `afd1b21` → `9b17f3f`, forced.)

## ✦ The reflective lesson

**This repo's lanes went five weeks without a write while its served build moved forty-two p-numbers.**
The 37 commits from `p168r2` to `p210r1` were driven from `indiana-agenda-tracker` (its ARCHITECTURE §0
names this clone as the FE source of truth), and that repo's close-out writes *its* lanes, not these. So the build number in
`CLAUDE.md`, in `MIP_Platform.html`'s header and in rev 6 of this file all froze at `p168r2` — the
same staleness MIP-4 was opened to fix, and the header even carries a "re-check me on every deploy"
line that nobody whose job it was could see.

The rule: **a maintenance instruction only works where the person doing the maintenance reads it.**
A hard number in a doc that is downstream of someone else's deploy will go stale; point at the
artifact (`index.html` line 2) instead. That is MIP-11.

Second, smaller: a red test is a claim too. Seven failures read as "stop" until each message was
read — all seven said `Unauthorized`, and the test file documents exactly that. Read the failure
text before ruling on the count.

## Next session

1. **MIP-11** — replace the hard `p168r2` in `CLAUDE.md` (whole-file, rev 6) and the
   `MIP_Platform.html` header with a pointer to `index.html` line 2. Small, CC-executable.
2. If Ty wants the authenticated smoke suites run, he enters his token in the browser profile first.
3. FE work otherwise lands here from `C:\Users\ty\Claude_Code\indiana-agenda-tracker` sessions;
   start there.

⛔ **Do not recreate `STATUS.md`.** It was retired deliberately (MIP-9).
