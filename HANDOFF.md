# HANDOFF — Indiana MIP Tracker (MRD front end)

HANDOFF-STAMP: 2026-08-28 | rev 1

> **Created 2026-08-28** by the hub-wide configuration audit (phase 6 backfill). This repo had a
> `STATUS.md` and `docs/OPEN-ITEMS.md` but no `HANDOFF.md` and no `CLAUDE.md`. Doctrine Block v1.7
> item 11 requires the `HANDOFF.md` lane, so it was backfilled from this repo's own `STATUS.md`,
> `docs/OPEN-ITEMS.md`, `serve-mrd.bat`, the served build's own marker, and `git log` — **not** from
> carried context.
>
> **Read first:** [`CLAUDE.md`](CLAUDE.md) → this file → [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md).
> Backend coordinates: `../indiana-agenda-tracker/ARCHITECTURE.md` §0 is the source of truth.

## One line

The auth token is out of this public repo's live tree and the operator console is token-gated;
served build is **`p168r1`**.

## Live coordinates

| Thing | State |
|---|---|
| Repo | `main` @ **`4871165`**, public remote `Wildhare1966/indiana-mip-tracker` |
| Served build | **`p168r1`** — `mrd-ad682070b7/index.html`, 704,359 B (probed 2026-08-28) |
| Local URL | `http://localhost:8778/mrd-ad682070b7/` via `serve-mrd.bat` (loopback only) |
| Data lanes | `main` · `data` · `data-sales` |
| Operator token | `localStorage` key `mip_auth_token`, entered under Settings → Operator Access |
| Backend | lives in `../indiana-agenda-tracker` — **not** this repo |

⚠ Re-probe before relying on the build number (doctrine item 14). The marker is in the first lines of
`mrd-ad682070b7/index.html`.

## What shipped most recently

1. **The auth token is gone from this public repo's live tree** (AGD-22, whose item row lives in
   `indiana-agenda-tracker`; the code is this repo's). `mrd-ad682070b7/index.html` no longer contains
   `DEFAULT_AUTH_TOKEN` — it reads `mip_auth_token` from `localStorage` via `getAuthToken()`.
2. **A sweep of this tree for 48-hex literals returns nothing.** Also cleaned: the stale root
   `MIP_Platform.html`, both `smoke.html` files, and `arcgis/sync_tracked_projects.py` + `.ipynb`.
3. **Verified in the live browser, not from the diff** — public actions still answer at full size
   with no token in the URL; the token rides only when the operator has entered one.
4. **`.gitignore` added** to keep local operator consoles out of this public repo.

## Open items

**`docs/OPEN-ITEMS.md` (rev 2) is the authority.** Most work for this platform is boarded in
`../indiana-agenda-tracker`, not here — check both.

**New, found during this backfill (not yet boarded):**

- **`MIP_Platform.html`'s stale-copy warning has itself gone stale.** It states the live build is
  `p151r2` and that the file is "~71 builds behind"; the served build is now `p168r1`. The warning is
  the only thing standing between that 470 KB `p80r4` file and someone "restoring" it, so a warning
  that misdescribes reality is worth more than a cosmetic fix. **Left unedited** — this is a public
  repo and the change is Ty's call.

## Gotchas carried forward

- ⛔ **Public git history keeps the old token permanently.** Rotation was the fix; the scrub is
  hygiene. A scrub unpublishes nothing.
- ⛔ **Never open the app as `file://`** — `Origin: null` 404s the `/exec` POST redirect, and the CSP
  refuses `file:` siblings.
- ⛔ **Do not "restore" `MIP_Platform.html`.** See above.
- **`serve-mrd.bat` must use `python.exe`, not `pythonw`** — console-less stderr crashes
  `http.server` per request.
- ⚠ **`indiana-mip-tracker` vs `indiana-agenda-tracker`** — one word apart, front end vs backend.
  Confirm which repo you are in before editing.
- **`data` and `data-sales` are separate lanes.** No cross-merges; `data-sales` belongs to the
  `Sales Disclosures` project.

## Next session

Nothing gating here. Work for this platform is normally driven from `../indiana-agenda-tracker` —
start there, and treat this repo as the place the FE build lands. If Ty rules on the stale warning
header above, that is a two-minute fix.
