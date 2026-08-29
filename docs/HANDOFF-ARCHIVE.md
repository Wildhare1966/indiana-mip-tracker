# HANDOFF archive — Indiana MIP Tracker (MRD front end)

Rotated out of the live `HANDOFF.md` under Doctrine Block v1.8 item 11 (one session per file,
150-line cap, history rotates here). Newest first.

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
