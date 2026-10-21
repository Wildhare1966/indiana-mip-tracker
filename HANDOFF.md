# HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-10-21 | rev 8

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `C:\Users\ty\Claude_Code\indiana-agenda-tracker\ARCHITECTURE.md` §0 is the
> source of truth. rev 7 (2026-10-06, MIP-10), rev 6 and rev 1 are in
> [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

## One line

Build **`p221r1`**: the MRD is now the launcher for the sibling apps — the Sales Disclosures tab
frames the **live** dashboard on port 8765 (the in-repo copy is gone) and a top-bar **Apps** group
opens the Video Console and the Cropper in new tabs. Item 4 of Ty's request, the Land Presentation
Map button, waits on his URL choice: **MIP-13**.

## Live coordinates (probed 2026-10-21 on this desktop)

| Thing | State |
|---|---|
| Repo | `main` @ **`38b6c4d`** (`p221r1`) plus this close-out commit, pushed — public remote `Wildhare1966/indiana-mip-tracker` |
| Served build | **`p221r1`** on both markers — `mrd-ad682070b7/index.html` line 2 and `styles.css?v=` line 14; served at `http://localhost:8778/mrd-ad682070b7/` (listener `127.0.0.1:8778`, answering `200`) |
| Sales Disclosures tab | `#sd-frame` → `http://localhost:8765/sales_dashboard.html?theme=…`, **live** from `C:\Users\ty\Claude_Code\Sales Disclosures` (`tools\serve_nocache.py`, bound `0.0.0.0:8765`, running at probe time, file at `c3eb983` 2026-10-20). `mrd-ad682070b7/sales_dashboard.html` **removed** |
| Apps group | **Video Console** → `http://127.0.0.1:8766/` (`market-video-pipeline\tools\console-server.mjs`, running) · **Cropper** → `http://127.0.0.1:8756/` (`Skill-cropper\crop.py`, **not** running; `Start Cropper.bat`) · **Land Presentation Map**: slot is an HTML comment after Cropper, pending **MIP-13** |
| CSP | `frame-src` and `connect-src` each gained `http://localhost:8765`; nothing else changed |
| Data lanes | `main` · `data` · `data-sales` — unchanged; both non-`main` lanes are written **by other projects** |
| Operator token | `localStorage` key `mip_auth_token`, Settings → Operator Access; **none in the built-in browser pane's profile** |
| Board | `docs/OPEN-ITEMS.md` **rev 11** — **MIP-13** (TY) and **MIP-11** (CC) open; **MIP-12** closed this session |
| Untracked | `serve-mrd.log` (server log, left alone) |

⚠ Re-probe before relying on the build number (doctrine item 14).
⛔ `CLAUDE.md` still says `p168r2` (line 56) and still lists `sales_dashboard.html` as a served asset
(line 72) — both are **MIP-11**, not the truth. Instruction files are edited whole (doctrine item 4),
so the drift is carried as that named item rather than patched.

## What shipped this session

Ty's 2026-10-21 request, items 1-3 of 4. Full record: **MIP-12** in `docs/OPEN-ITEMS.md`.

1. **Probed before building.** The embedded copy was 336,471 B (2026-10-06); the live file was
   434,231 B (`c3eb983`, 2026-10-20) and served on 8765 with `200`, no `X-Frame-Options`, no
   `frame-ancestors`. It reads `?theme=` at its line 3088, so the existing theme sync still works.
2. **Sales Disclosures frames the live server.** One constant `SD_DASHBOARD_URL` feeds both the view
   init and `applyTheme()`. A `HEAD` probe (`no-cors`) gates the frame; a refused connection shows a
   plain notice naming `Start Sales Dashboard.bat` with a Retry button instead of a blank frame.
   `git rm mrd-ad682070b7/sales_dashboard.html` after the grep came back empty (`tests/smoke.html`: 0).
3. **Apps group.** `.topbar-sep` divider, then Video Console and Cropper, each `openApp(url)` =
   `window.open(url, '_blank', 'noopener')`. Launchers, not views: no `switchView`, no view element.
4. **Verified in the built-in browser.** Served marker `p221r1`; the frame renders the 10-20 build
   (Tile Studio button, 354,107 of 373,843 transactions); theme toggle re-fetched `?theme=light`
   then `?theme=dark`; Video Console opened the console; Cropper opened to a connection error (its
   server was not running and was not started). Smoke: 13/20, 7 fail, all `Unauthorized` (no token).
   Console: no CSP violations from the build.
5. **Board rotated.** MIP-10's closure moved verbatim to `docs/STATUS-ARCHIVE.md`; rev 7 of this
   file to `docs/HANDOFF-ARCHIVE.md`. **MIP-12** closed, **MIP-13** boarded, **MIP-11** widened.

## Gotchas carried forward

- ⚠ **The Sales frame is `localhost:8765`, not `127.0.0.1:8765`, on purpose.** That repo's
  `Start Sales Dashboard.bat` documents that review edits live in `localStorage` for the origin
  `http://localhost:8765`; `127.0.0.1` is a different origin and shows none of them. The CSP lists
  the origin under **both** `frame-src` and `connect-src` — drop either and the tab goes blank or
  the probe fails closed.
- ⚠ **The MRD never starts another repo's server.** Down → notice + Retry. The view init runs
  once per page load, so Retry is the only re-check short of a reload.
- ⚠ **The built-in browser pane navigates the same tab on `window.open`.** Verified with a plain
  `window.open(url, '_blank')` from the console (returned `null`). Chrome opens a new tab. Do not
  "fix" `openApp()` for the pane.
- ⚠ **Line endings.** `core.autocrlf=true`. Probed 2026-10-21 with `file`: `index.html` and
  `styles.css` sit **LF** on disk, the Markdown lanes **CRLF**. Git normalizes on commit either way;
  preserve whatever each file already has rather than converting.
- ⚠ **The smoke test fails, not skips, without a token.** 7 failures reading `Unauthorized` (or
  `Expected array, got: object`, the same 403 body) mean "no token in this browser profile," not a
  regression. Claude never enters the token.
- ⛔ **`*-ops.html` consoles are served but untracked.** Keep them on disk; back them up to
  `C:\Users\ty\Claude_Code\indiana-agenda-tracker\ops\`. Never re-add a leading slash to the
  `.gitignore` pattern.
- ⛔ **`refreshHearings()` is NOT dead code.** Four write paths call it, three inside `setTimeout`.
- ⛔ **Public git history keeps the old token and the stale dashboard copy permanently.** Rotation
  was the fix for the token; removal unpublishes nothing.
- ⛔ **Never open the app as `file://`.** ⛔ **Do not "restore" or delete `MIP_Platform.html`.**
- **`serve-mrd.bat` must use `python.exe`, not `pythonw`.** ⚠ **Port 8765 belongs to
  `C:\Users\ty\Claude_Code\Sales Disclosures`**, 8766 to `market-video-pipeline`, 8756 to
  `Skill-cropper`.
- ⚠ **`indiana-mip-tracker` vs `indiana-agenda-tracker`** — one word apart, front end vs backend.
- **`data` and `data-sales` are separate lanes.** Never hand-publish to `data`.

## ✦ The reflective lesson

**A copy is a snapshot pretending to be a link.** The Sales dashboard copy was refreshed by hand in
`p207r2` and `p209r2` and then fell fourteen days behind without anyone noticing, in a public repo.
Framing the live server deletes the sync chore and the exposure in one move — at the price of a
runtime dependency that must fail *loudly*, which is what the notice is for. A dependency you cannot
see failing is worse than the copy was.

Second: the brief's recommended URL was wrong in a way only the **neighbouring** repo's launcher
documented. Doctrine item 14 reaches past your own artifact — probe the thing you are about to
depend on, not just the thing you are editing.

## Next session

1. **MIP-13** — Ty picks the map URL; add the button in the Apps slot, bump to `p221r2`.
2. **MIP-11** — `CLAUDE.md` rev 6, whole-file: the `p168r2` pointer, the line-72 asset list, the
   Apps group paragraph.
3. Reported, not boarded here (other repos' concerns): Sales Disclosures' spare launch config names
   8766 (the Video Console's port); Permit-Resources documents 8770, which Tile Studio holds; Sales
   Disclosures binds `0.0.0.0`; auto-starting the four servers belongs in `C:\Users\ty\Claude_Code\_serve`.
   The MRD is local to this desktop and not reachable from the laptop over Remote Control.

⛔ **Do not recreate `STATUS.md`.** It was retired deliberately (MIP-9).
