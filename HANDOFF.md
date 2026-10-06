# HANDOFF — Indiana MIP Tracker (MRD front end)

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
