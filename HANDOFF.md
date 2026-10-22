# HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-10-22 | rev 14

> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `C:\Users\ty\Claude_Code\indiana-agenda-tracker\ARCHITECTURE.md` §0 is the
> source of truth. rev 13 (2026-10-21, the p221r1 → p222r4 day: launchers, Profiles / Hearings, the
> backend wiring) and earlier are in [`docs/HANDOFF-ARCHIVE.md`](docs/HANDOFF-ARCHIVE.md).

## One line

Build **`p223r1`**: Update Members is now the **roster protocol** — an evidence-bound monthly check
(official site → minutes → county election board → press; no Ballotpedia, no memory) where only an
official source can save a DEPARTED, NEW or CHANGED verdict, with **Accept / Reject / Restore** on the
member cards as the review step. Next: **MIP-19**, Update Profiles moves onto the member profile, one
member at a time, replacing the old AI Research block. Backend monthly schedule proposed as a card.

## Live coordinates (probed 2026-10-22 on this desktop)

| Thing | State |
|---|---|
| Repo | `main` @ **`0a74570`** (`p223r1`; yesterday's `a628982` `p222r4` … `38b6c4d` `p221r1`) plus this close-out commit, pushed — public remote `Wildhare1966/indiana-mip-tracker` |
| Served build | **`p223r1`** on both markers — `mrd-ad682070b7/index.html` line 2 and `styles.css?v=` line 14; `http://localhost:8778/mrd-ad682070b7/` (listener `127.0.0.1:8778`, `200`) |
| Nav | Overview · **Profiles** · **Hearings** · Agenda Items · Youtube Items · Candidates · Jurisdiction Status · Tracked Projects · Tracked Topics · **Schedule Builder** · ┃ Sales Disclosures ↗ · Video Console ↗ · Cropper ↗ · Map ↗ · ⚙ Settings. Zonda commented out, view retained |
| Apps group | Sales Disclosures → `http://localhost:8765/sales_dashboard.html` (never a frame: the dashboard switches datasets when framed) · Video Console → `127.0.0.1:8766` · Cropper → `127.0.0.1:8756` · Map → `https://map.wildhare.app/` |
| Profiles / Hearings | two nav doors on one DOM (`#view-muni`, `muniMode`); the profile renders inline below the member list; Update Profiles / Update Members at the right of the tab row; update log under the Municipality Summary |
| Backend | `C:\Users\ty\Claude_Code\indiana-agenda-tracker`, deploy **@589** (P224): grounded `gemini_proxy`, `upsert_member` (GET) / `set_member_profile` (POST) on the `Members` sheet; P225 (HEAD only): the weekly research batch skips `departed`, researches `new` first |
| Operator token | `localStorage` `mip_auth_token`, Settings → Operator Access; present in Ty's Chrome on `localhost:8778`, none in the built-in browser pane |
| Board | `docs/OPEN-ITEMS.md` **rev 17** — **MIP-19** (CC) and **MIP-11** (CC) open; **MIP-18** closed today; MIP-12..17 rotated to the archive |
| Untracked | `serve-mrd.log` |

⚠ Re-probe before relying on the build number (doctrine item 14).
⛔ `CLAUDE.md` still says `p168r2` and lists the removed `sales_dashboard.html` — **MIP-11**.

## What shipped this session

1. **Roster protocol** (`updateMembersRoster`). The prompt names the jurisdiction's official hosts
   (learned from its agenda / minutes / reference URLs), orders the sources, fixes the role vocabulary
   (President · Vice President · Member, then the seat) and adds an `EVIDENCE_DATE` column. The page
   grades every SOURCE itself (`_sourceTier`: 1 own site, 2 other `.gov` / `.in.us`, 4 press, 5
   none / redirect / Ballotpedia) and downgrades a DEPARTED, NEW or CHANGED verdict without tier ≤ 2 to
   UNVERIFIED, which never writes. The log shows the hosts searched, the evidence date per line and
   the downgrade count.
2. **Review step.** NEW cards carry ✓ Accept (status `current`) and ✕ Reject (status `departed`);
   departed cards carry ↩ Restore. One `upsert_member` each, one log entry, no search.
3. **Verified** with no token: Lebanon's official host resolves to `lebanon.in.gov`; tiers grade
   own-site 1, a sub-host 1, `boonecounty.in.gov` 2, press 4, Ballotpedia and redirects 5; a synthetic
   NEW card shows both buttons and a departed card shows Restore; Reject reaches the live route and
   logs `Unauthorized`; smoke 13/20 with the seven no-token 403s; no console errors. Full record
   **MIP-18**. ⚠ A live grounded run with the new prompt is Ty's first click.

## Gotchas carried forward

- ⚠ **A verdict is only as good as its source tier.** The page, not the model, decides what counts;
  if a town's own site is not among `agenda_landing_url`, `minutes_landing_url` or its
  `JURISDICTION_REFS` URLs, only `.gov` / `.in.us` pages rank as official there — check the log's
  "Official hosts searched first" line when everything downgrades.
- ⚠ **Writes never retry; the first `Unauthorized` stops them.** A successful write drops the four
  warm caches so the next load re-reads the sheet. Only the update log is browser-local.
- ⚠ **`callGeminiProxy` forwards named fields only** — a new Gemini option must be added to the body
  it builds. `grounding` lands on `callGeminiProxy.lastGrounding`.
- ⛔ **Do not re-embed the Sales Disclosures dashboard**, and keep its launcher on `localhost`, not
  `127.0.0.1` (review edits live in that origin's `localStorage`).
- ⚠ **The built-in browser pane is not a launcher test bed**: loopback `window.open` navigates the
  same tab, external ones are blocked. Verify launchers by `curl`.
- ⚠ **Line endings.** `index.html` / `styles.css` sit LF on disk, the Markdown lanes CRLF; preserve
  whatever each file has. ⚠ **Smoke fails, not skips, without a token** (7 × 403 is the documented
  result). ⛔ `*-ops.html` stay untracked. ⛔ `refreshHearings()` is not dead code. ⛔ Never `file://`.
  ⛔ Do not restore or delete `MIP_Platform.html`. ⚠ `indiana-mip-tracker` ≠ `indiana-agenda-tracker`.

## ✦ The reflective lesson

**Let the model report; let the page decide.** Yesterday's prompt accepted any URL as evidence and
the sheet got a Google redirect as a source. Today the gate lives in code that grades the host, and
the model's only job is to say what it saw and where. The same split belongs in the profiles work:
the operator's Accept is the write, never the model's confidence.

## Next session

1. **MIP-19** — Update Profiles per member: move the button onto the profile, one member per click,
   per-field source links, accept / reject before the sheet, remove the old "AI Research Profile" block.
2. **Backend monthly roster schedule** — proposed as a session card 2026-10-22 (two jurisdictions a
   day, all 41 in early January and after the November 2027 election, minutes-keyword re-queue).
3. **MIP-11** — `CLAUDE.md` rev 6, whole-file.

⛔ **Do not recreate `STATUS.md`.** It was retired deliberately (MIP-9).
