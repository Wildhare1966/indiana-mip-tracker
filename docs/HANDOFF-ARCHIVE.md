# HANDOFF archive — Indiana MIP Tracker (MRD front end)

Rotated out of the live `HANDOFF.md` under Doctrine Block v1.8 item 11 (one session per file,
150-line cap, history rotates here). Newest first.

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
