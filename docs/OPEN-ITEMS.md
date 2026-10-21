# Open items — Indiana MIP Tracker

FILE-STAMP: 2026-10-21 | rev 11

**Format contract: `Dexters-Dashboard/docs/OPEN-ITEMS-SPEC.md`.** These rows are rendered on
the dashboard's **Items** page alongside every other project's, so keep to the spec — a row
that drifts from it silently stops being indexed. This file records what is *outstanding*;
current state lives in `HANDOFF.md` (Doctrine Block v1.8 item 11 lanes).

Backfilled 2026-08-22 (Ty-ruled R5) by reading this repo's own `STATUS.md`/`HANDOFF.md` and
judging what was still live. Items recorded there but since closed were deliberately not
carried forward.

> **rev 11 (2026-10-21):** **MIP-12** closed (build `p221r1` — the MRD as the launcher for the
> sibling apps: live Sales Disclosures frame, Video Console and Cropper buttons), **MIP-13** boarded
> for Ty (the Land Presentation Map URL — item 4 of the same request), and **MIP-11** widened by one
> more line of `CLAUDE.md` drift. The 2026-10-06 closure (**MIP-10**) rotated verbatim to
> [`docs/STATUS-ARCHIVE.md`](STATUS-ARCHIVE.md) under spec rev 10 retention rule 2.
> **rev 10 (2026-10-06):** **MIP-10** closed (the laptop-retirement git reconciliation) and
> **MIP-11** boarded. The 2026-08-23..08-29 closures (**MIP-1** to **MIP-9**) rotated verbatim to
> [`docs/STATUS-ARCHIVE.md`](STATUS-ARCHIVE.md) under spec rev 10 retention rule 2.

## Needs Ty — decisions and approvals

| ID | Owner | Item | Why it matters | Blocked by |
|---|---|---|---|---|
| **MIP-13** | TY | Choose the URL behind the **Land Presentation Map** launcher in the MRD top bar's Apps group: the live build `https://map.wildhare.app` (behind Cloudflare Access; recommended) or the local dev copy `http://localhost:8080/public/` (needs `python -m http.server 8080` in `C:\Users\ty\Claude_Code\Land_Presentation_Map`, which was **not** running on 2026-10-21). | Item 4 of Ty's 2026-10-21 request is the only one not shipped in `p221r1`; an HTML comment holds its slot right after the Cropper button in `mrd-ad682070b7/index.html`. The live build answered `302` to the Access login when probed, so it works from any browser Ty is signed in on; the local copy works only while that server runs. Once chosen it is one button plus a `p221r2` marker bump — no CSP change, because new-tab launchers sit outside `frame-src`. | — |

## Claude Code can execute — say the word

| ID | Owner | Item | Why it matters | Blocked by |
|---|---|---|---|---|
| **MIP-11** | CC | Replace the stale build number `p168r2` in `CLAUDE.md` and the `MIP_Platform.html` header with a pointer to `mrd-ad682070b7/index.html` line 2 (served build probed 2026-10-06: `p210r1`; 2026-10-21: `p221r1`). **Widened 2026-10-21:** the same whole-file `CLAUDE.md` rev 6 edit must also drop `sales_dashboard.html` from the served-asset list on line 72 (the copy was removed in `p221r1`; the Sales Disclosures tab now frames `http://localhost:8765` live) and add one paragraph on the top-bar Apps group (launchers, not views; the Sales frame's `localhost`-not-`127.0.0.1` rule). | `CLAUDE.md` rev 5 line 56 and the `MIP_Platform.html` header (lines 3-34, "88 p-numbers behind") were last corrected 2026-08-29; the header's own MAINTENANCE line ("re-check this block on every deploy") has not been followed since, because FE deploys are driven from `C:\Users\ty\Claude_Code\indiana-agenda-tracker`, whose kickoff never touches this repo's docs. It is the exact failure MIP-4 closed: a guard that misdescribes what it guards. A pointer instead of a number cannot go stale. `CLAUDE.md` is an instruction file: whole-file edit with a rev bump (doctrine item 4) — which is also why the line-72 drift from `p221r1` is carried here as a named open item rather than patched in place. | — |

## Recently closed

| ID | Closed | What happened |
|---|---|---|
| **MIP-12** | 2026-10-21 | **`p221r1` — the MRD becomes the launcher for the sibling apps (Ty's 2026-10-21 request, items 1-3 of 4; commit `38b6c4d`).** Probed first (doctrine item 14): served marker `p220r1`; the embedded copy `mrd-ad682070b7/sales_dashboard.html` was 336,471 B dated 2026-10-06 while `C:\Users\ty\Claude_Code\Sales Disclosures\sales_dashboard.html` was 434,231 B at `c3eb983` (2026-10-20), served live on port 8765 — `curl -sI` gave `200`, `Cache-Control: no-cache`, no `X-Frame-Options`, no `frame-ancestors`; the dashboard reads `?theme=light\|dark` at its line 3088. **(1) Sales Disclosures:** `#sd-frame` now loads `http://localhost:8765/sales_dashboard.html?theme=…` through one constant, `SD_DASHBOARD_URL`, used by both the view init and the theme sync. It is `localhost`, not the brief's `127.0.0.1`, because that repo's own `Start Sales Dashboard.bat` states that review edits live in `localStorage` for the origin `http://localhost:8765` and `127.0.0.1` would show none of them. CSP `frame-src` and `connect-src` each gained `http://localhost:8765`. First open runs a `HEAD` probe (`no-cors`, `no-store`): reachable → the frame; refused → a plain notice naming `Start Sales Dashboard.bat` in `C:\Users\ty\Claude_Code\Sales Disclosures` with a Retry button. Tested by pointing the probe at a dead port and retrying: notice shown, then `offline:none, frame:block, src=…?theme=dark`. The stale copy was `git rm`'d after a grep showed its only remaining references were prose in `CLAUDE.md` line 72 and the archives (`tests/smoke.html`: 0 hits); the served path now answers `404`. **(2)(3) Apps group:** after Sales Disclosures and before Settings, a thin `.topbar-sep` divider, then **Video Console** → `http://127.0.0.1:8766/` and **Cropper** → `http://127.0.0.1:8756/`, each via `openApp()` = `window.open(url, '_blank', 'noopener')`; no `switchView`, no view element, no new dependency. **Verified** in the built-in browser at `http://localhost:8778/mrd-ad682070b7/`: served line 2 `<!-- MIP build p221r1 -->` and `styles.css?v=p221r1`; the Sales Disclosures tab renders the 10-20 build (title `Sales Disclosure — Validation Dashboard`, a **Tile Studio** button the 10-06 copy does not contain, `354,107 of 373,843 transactions`); the theme toggle re-requested `?theme=light` then `?theme=dark`, both `200`; Video Console opened `Market Video Console (local)` at `127.0.0.1:8766`; Cropper opened `127.0.0.1:8756` to a connection error because that server was not running (not started — not asked). ⚠ In the desktop app's built-in browser pane `window.open` navigated the **same** tab, and so did a plain `window.open(url, '_blank')` from the console (returned `null`) — that is the pane's popup handling, not the build's; Chrome opens a new tab. `tests/smoke.html`: **13/20, 7 failed**, every failure `{"error":"Unauthorized","code":403}` or its `Expected array, got: object` form — the documented no-token result, same count as 2026-10-06; sanitizers 10/10, CSP integrity pass. Console: no CSP violations from the build; the only two were the ones the dead-port simulation deliberately caused. Item 4 is **MIP-13**. Out of scope and reported only: Sales Disclosures' spare launch config names 8766 (the Video Console's port) and Permit-Resources documents 8770 (held by Tile Studio); Sales Disclosures binds `0.0.0.0`; auto-starting the four servers belongs in `C:\Users\ty\Claude_Code\_serve`; the MRD remains local to this desktop, unreachable from the laptop over Remote Control. |
