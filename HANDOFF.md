# HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-10-21 | rev 11

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `C:\Users\ty\Claude_Code\indiana-agenda-tracker\ARCHITECTURE.md` §0 is the
> source of truth. rev 7 (2026-10-06, MIP-10), rev 6 and rev 1 are in
> [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

## One line

Build **`p222r2`**: the MRD is the launcher for the sibling apps — a top-bar **Apps** group opens
Sales Disclosures (standalone tab, no frame), Video Console, Cropper and Map — and **Jurisdictions is
split into Profiles and Hearings**, with the member profile inline below the list and **Update Members /
Update Profiles** buttons that search live (Google Search grounding through the backend proxy, @589)
and **write the Members sheet**. Zonda is off the nav; Schedule & Requirements is **Schedule Builder**.
One item open: **MIP-11**. ⚠ The grounded search and a real write are untested without the token.

## Live coordinates (probed 2026-10-21 on this desktop)

| Thing | State |
|---|---|
| Repo | `main` @ **`b0f6fbc`** (`p222r2`; `685cd3e` `p222r1`, `11d5e9d` `p221r2`, `38b6c4d` `p221r1`) plus this close-out commit, pushed — public remote `Wildhare1966/indiana-mip-tracker` |
| Served build | **`p222r2`** on both markers — `mrd-ad682070b7/index.html` line 2 and `styles.css?v=` line 14; served at `http://localhost:8778/mrd-ad682070b7/` (listener `127.0.0.1:8778`, answering `200`) |
| Sales Disclosures | a **launcher** (first in the Apps group) → `http://localhost:8765/sales_dashboard.html` in a new tab. The `p221r1` iframe is gone: the dashboard detects a frame and switches to its published two-year dataset, hiding Tile Studio. `mrd-ad682070b7/sales_dashboard.html` remains removed |
| Apps group | Sales Disclosures → `localhost:8765` · **Video Console** → `http://127.0.0.1:8766/` (`market-video-pipeline`) · **Cropper** → `http://127.0.0.1:8756/` (`Skill-cropper`, start it with `Start Cropper.bat`) · **Map** → `https://map.wildhare.app/` (Cloudflare Access) |
| CSP | the `localhost:8765` entries are gone again; `img-src` is now `'self' data: https:` (member photos). Nothing else changed |
| Data lanes | `main` · `data` · `data-sales` — unchanged; both non-`main` lanes are written **by other projects** |
| Operator token | `localStorage` key `mip_auth_token`, Settings → Operator Access; **none in the built-in browser pane's profile** |
| Backend | `C:\Users\ty\Claude_Code\indiana-agenda-tracker` — **not** this repo. Deploy **@589** (its P224, 2026-10-21): `gemini_proxy` forwards `tools:[{googleSearch:{}}]` and replies with `grounding`; `upsert_member` (GET) and `set_member_profile` (POST) write the `Members` sheet; `member_profiles` and the roster wire carry `status`, `photo_url`, `photo_source`, `civic_affiliations`, `other_public` |
| Board | `docs/OPEN-ITEMS.md` **rev 14** — **MIP-11** (CC) open; **MIP-12** to **MIP-15** closed this session |
| Untracked | `serve-mrd.log` (server log, left alone) |

⚠ Re-probe before relying on the build number (doctrine item 14).
⛔ `CLAUDE.md` still says `p168r2` (line 56) and still lists `sales_dashboard.html` as a served asset
(line 72) — both are **MIP-11**, not the truth. Instruction files are edited whole (doctrine item 4),
so the drift is carried as that named item rather than patched.

## What shipped this session

Ty's 2026-10-21 request, all four items (rev 8 of this file closed items 1-3; rev 9, same session,
adds item 4). Full record: **MIP-12** and **MIP-13** in `docs/OPEN-ITEMS.md`.

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
6. **`p221r2` — Land Presentation Map.** Ty chose the live build over the local `:8080` copy. One
   button through the same `openApp()`, marker bump only, no CSP change. The built-in browser pane
   blocked the popup (automation may not open popups there), so the destination was verified by
   `curl` (302 to the Access login) rather than rendered. Smoke re-run unchanged: 13/20, all 403.
7. **`p222r1` — second request.** Sales Disclosures became a launcher (the frame could never show the
   standalone dashboard: `FRAMED` switches datasets and hides Tile Studio); Map; Zonda off; Schedule
   Builder; Jurisdictions → **Profiles** (summary, members, inline full-width profile, Update Profiles /
   Update Members, update log under the summary) and **Hearings** (no summary). Full record **MIP-14**.
8. **`p222r2` — wired to the backend.** `callGeminiProxy` now really sends `tools` (p222r1 dropped it
   FE-side too) and keeps `grounding`; `mipMemberWrite` carries every verdict to `upsert_member` and
   every profile find to `set_member_profile`; the log lists queries and sources; the overlay is gone.
   Both routes answered `Unauthorized` from the page without a token. Full record **MIP-15**.

## Gotchas carried forward

- ⛔ **Do not re-embed the Sales Disclosures dashboard.** It tests `window.self !== window.top`
  and, framed, loads the published two-year CDN file and hides Tile Studio and Review records on
  purpose (Ty, 2026-10-07 and 2026-10-20). The launcher must stay `localhost`, not `127.0.0.1`:
  that repo keeps review edits in `localStorage` for the `localhost:8765` origin.
- ⚠ **Profiles and Hearings are one DOM.** Both nav buttons activate `#view-muni`; `muniMode`
  decides what `renderMuniPanel` draws. Legacy `switchView('muni')` means Hearings. Member cards
  and the inline profile are only rendered in Profiles mode; `#member-detail` (the old right rail)
  is still in the DOM but always hidden.
- ⚠ **Update Members / Update Profiles write the sheet and never retry.** `mipMemberWrite` throws the
  backend's `error` text; the first `Unauthorized` stops further writes and the log says which rows
  were not saved. A successful write drops the four warm caches (`mip_muni_data*`,
  `mip_member_profiles*`) so the next load re-reads the sheet. Only the update log itself
  (`mip_muni_update_log_v1`) is browser-local. Photo URLs are model-sourced, https-only.
- ⚠ **`callGeminiProxy` only forwards named fields.** Adding a Gemini option means adding it to the
  body it builds — `tools` was silently dropped there for a whole build (p222r1). `grounding` from
  the proxy lands on `callGeminiProxy.lastGrounding` after each call.
- ⚠ **The built-in browser pane is not a launcher test bed.** Loopback `window.open` targets
  navigated the *same* tab; an external one (`map.wildhare.app`) was **blocked** outright — popups
  open there only from the user's own clicks. Chrome opens a new tab for all three. Do not "fix"
  `openApp()` for the pane; verify launchers by `curl` plus the pane's popup notice.
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

1. **Ty's first live click** on Update Members with the token entered is the test `p222r2` could not
   run: expect `saved N` and a Sources line in the log; a `not saved` line names the backend error.
   Backend side done 2026-10-21 (@589); its `ARCHITECTURE.md` §0 did not yet name @589 when probed.
2. **MIP-11** — `CLAUDE.md` rev 6, whole-file: the `p168r2` pointer, the line-72 asset list, the
   Apps group paragraph.
3. Reported, not boarded here (other repos' concerns): Sales Disclosures' spare launch config names
   8766 (the Video Console's port); Permit-Resources documents 8770, which Tile Studio holds; Sales
   Disclosures binds `0.0.0.0`; auto-starting the four servers belongs in `C:\Users\ty\Claude_Code\_serve`.
   The MRD is local to this desktop and not reachable from the laptop over Remote Control.

⛔ **Do not recreate `STATUS.md`.** It was retired deliberately (MIP-9).
