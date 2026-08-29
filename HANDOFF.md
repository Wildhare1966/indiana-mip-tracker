# HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-08-29 | rev 4

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `../indiana-agenda-tracker/ARCHITECTURE.md` §0 is the source of truth.
> rev 1 (2026-08-28, the hub-wide configuration audit's phase-6 backfill) is in
> [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

## One line

The root now holds only load-bearing files, the last dead cross-project call is gone, `MIP-3` is
closed complete, and `CLAUDE.md` documents that **this repo receives at the git level but writes at
the app level**; served build is **`p168r2`**. **The board is empty** — seven rows closed in one session, none left open.

## Live coordinates

| Thing | State |
|---|---|
| Repo | `main` @ **`5bd2e59`** + **uncommitted work** (see below), public remote `Wildhare1966/indiana-mip-tracker` |
| Served build | **`p168r2`** — `mrd-ad682070b7/index.html`, 704,284 B (probed 2026-08-29) |
| Local URL | `http://localhost:8778/mrd-ad682070b7/` via `serve-mrd.bat` (loopback only) |
| Root contents | `CLAUDE.md` · `HANDOFF.md` · `STATUS.md` · `MIP_Platform.html` · `arcgis/` · `docs/` · `mrd-ad682070b7/` · `serve-mrd.bat` |
| Data lanes | `main` · `data` · `data-sales` — both non-`main` lanes are written **by other projects** |
| Operator token | `localStorage` key `mip_auth_token`, entered under Settings → Operator Access |
| Backend | lives in `../indiana-agenda-tracker` — **not** this repo |
| Board | `docs/OPEN-ITEMS.md` **rev 8** — MIP-3 through MIP-8 all closed; **nothing outstanding** |

⚠ Re-probe before relying on the build number (doctrine item 14). The marker is on line 2 of
`mrd-ad682070b7/index.html`; the `styles.css?v=` querystring on line 14 must match it.

## What shipped this session

**Nothing is committed.** Everything below is in the working tree, on `main`, public remote — review
before pushing.

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

## Next session

1. **Review and commit the working tree** — it is all uncommitted, on a public remote. Check for
   secrets first.
2. **`STATUS.md` needs Ty's ruling.** It is a changelog, not a snapshot (doctrine item 11), and it is
   stale in ways that misled this session's start: it claims build `p151r2`, says "Pages remains
   enabled", and describes `MIP_Platform.html` as "blanked" when it is 470 KB. Item 11 makes it
   optional and retirable once `HANDOFF.md` carries the coordinates — which it now does. **Retire it,
   or rewrite it as a snapshot.** Not done unilaterally.
3. **`../indiana-agenda-tracker/ops/` has four uncommitted files** — `p160`–`p163-ops.html`, copied
   there by MIP-8 so this public repo could stop tracking them. Commit them in that private repo.
4. **The board here is empty.** Most work for this platform is driven from
   `../indiana-agenda-tracker` — start there.
