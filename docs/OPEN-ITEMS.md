# Open items — Indiana MIP Tracker

FILE-STAMP: 2026-10-06 | rev 10

**Format contract: `Dexters-Dashboard/docs/OPEN-ITEMS-SPEC.md`.** These rows are rendered on
the dashboard's **Items** page alongside every other project's, so keep to the spec — a row
that drifts from it silently stops being indexed. This file records what is *outstanding*;
current state lives in `HANDOFF.md` (Doctrine Block v1.8 item 11 lanes).

Backfilled 2026-08-22 (Ty-ruled R5) by reading this repo's own `STATUS.md`/`HANDOFF.md` and
judging what was still live. Items recorded there but since closed were deliberately not
carried forward.

> **rev 10 (2026-10-06):** **MIP-10** closed (the laptop-retirement git reconciliation) and
> **MIP-11** boarded. The 2026-08-23..08-29 closures (**MIP-1** to **MIP-9**) rotated verbatim to
> [`docs/STATUS-ARCHIVE.md`](STATUS-ARCHIVE.md) under spec rev 10 retention rule 2.

## Needs Ty — decisions and approvals

*Nothing outstanding.* (No table here deliberately — an empty header row is not a valid row under
the format contract.)

## Claude Code can execute — say the word

| ID | Owner | Item | Why it matters | Blocked by |
|---|---|---|---|---|
| **MIP-11** | CC | Replace the stale build number `p168r2` in `CLAUDE.md` and the `MIP_Platform.html` header with a pointer to `mrd-ad682070b7/index.html` line 2 (served build probed 2026-10-06: `p210r1`). | `CLAUDE.md` rev 5 line 56 and the `MIP_Platform.html` header (lines 3-34, "88 p-numbers behind") were last corrected 2026-08-29; the header's own MAINTENANCE line ("re-check this block on every deploy") has not been followed since, because FE deploys are driven from `C:\Users\ty\Claude_Code\indiana-agenda-tracker`, whose kickoff never touches this repo's docs. It is the exact failure MIP-4 closed: a guard that misdescribes what it guards. A pointer instead of a number cannot go stale. `CLAUDE.md` is an instruction file: whole-file edit with a rev bump (doctrine item 4). | — |

## Recently closed

| ID | Closed | What happened |
|---|---|---|
| **MIP-10** | 2026-10-06 | **Laptop-retirement git reconciliation — two divergent FE commits landed on `main` in sequence.** Probed first (doctrine item 14): `origin/main` = `4cebe80` (`p209r1`); local `main` carried unpushed `81cbe77` (`p210r1`, the one-retry-on-a-lost-read change, `index.html` only); the retired laptop's `943404b` (`p209r2`, Sales Disclosures dashboard to sales-disclosures `7236884`, `sales_dashboard.html` + the two `index.html` marker lines) sat on GitHub as `origin/laptop/943404b`. Both on `4cebe80`; neither contained the other. Ty-authorized: `main` rebased onto `943404b`; the only conflict was the two build-marker lines (line 2 and `styles.css?v=` on line 14), resolved to `p210r1` since the markers were already in sequence. The retry code merged without conflict. Result `4cebe80` → `943404b` → **`13d98a6`** (the rebased `p210r1`; `81cbe77` no longer exists on any ref). Checks: `index.html` byte-identical to `81cbe77`'s, `sales_dashboard.html` byte-identical to `943404b`'s, secret-pattern scan of `4cebe80..HEAD` clean. Served build at `http://localhost:8778/mrd-ad682070b7/` reads **`p210r1`** on both markers and both files hash-match `HEAD`; page renders 41 municipalities, `typeof refreshHearings === 'function'`. `tests/smoke.html`: **13 pass, 7 fail** — all 7 are token-gated suites returning `{"error":"Unauthorized","code":403}` because that browser profile holds no operator token, which `smoke.html` lines 39-41 document as the expected no-token result; all 10 sanitizer tests, both unauthenticated-403 checks and CSP integrity pass. Pushed as a fast-forward (`4cebe80..13d98a6`, `ls-remote` = local `HEAD`), then `laptop/943404b` deleted from GitHub (`ls-remote refs/heads/laptop/*` empty). GitHub Pages still off (`has_pages` false), so the local server is the only deploy. ⚠ The authenticated smoke suites were **not** exercised: that needs Ty's token in the browser profile. |
