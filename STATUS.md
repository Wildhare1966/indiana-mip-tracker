STATUS-STAMP: 2026-08-23 | rev 4

## Rev 4 delta — the auth token is gone from this public repo

- **AGD-22 shipped here** (the item lives in `indiana-agenda-tracker`; the code is this repo's).
  `mrd-ad682070b7/index.html` no longer contains `DEFAULT_AUTH_TOKEN`. It reads `mip_auth_token` from
  `localStorage` through `getAuthToken()`, entered once in a new **Settings -> Operator Access** card.
- **A sweep of this tree for 48-hex literals now returns nothing.** Also cleaned: the stale root
  `MIP_Platform.html` (blanked, and headed with a note that it is ~71 builds behind the served build and
  must not be "restored"), both `smoke.html` files (they now read the same localStorage key), and
  `arcgis/sync_tracked_projects.py` + `.ipynb`.
- ⛔ **This does not unpublish anything.** Public git history keeps the old token permanently — that is
  why rotation was the fix and the scrub is hygiene. The rotated value is inert.
- **Verified in the live browser**, not from the diff: public actions still answer at full size
  (149,875 B) with no token in the URL; the token rides only when the operator has entered one.
- Reading the dashboard is unaffected. **Operator actions stay inert until Ty enters the token**
  (AGD-29).


## Rev 3 delta — both open items closed as MOOT; the AGO clicks finally boarded

- **MIP-2 was false the day it was written.** It asserted "Pages is still serving this tracker."
  Probed three ways today: `gh api …/pages` → `404`, `gh api repos/… --jq '.has_pages'` → **`false`**,
  `curl -L https://wildhare1966.github.io/indiana-mip-tracker/` → `404`. And it was **already known** —
  `Dexters-Dashboard/reports/DOC-SWEEP_pages-cutover_2026-08-16.md:13` says so outright and proves it
  with a control probe against a second Pages site, so the 404s cannot be a network block. The 8/22
  backfill read this repo's stale `STATUS.md` and not the report beside it. **That is the whole thesis
  of SYS-8.**
- **MIP-1 closed with it** — the local-server path is not merely verified but in daily use.
- **The repo is still `public`, deliberately** — that half of decision D-B stands.
- **MIP-3 added:** the three AGO clicks (schedule the sync daily, disable the arborhomes sync, delete
  the dead-end wildhare `LeadsDeals`). Open since the 8/14 audit's D2, carried into X-4, and never
  boarded. It is the **shared upstream of EMAP-1**: supplying `AGO_TOKEN` regenerates the map once,
  but only the schedule keeps it current.


> **Note:** this repository is **public**. Keep this file free of tokens, IDs, local paths, and any
> operational detail that shouldn't be world-readable. Working notes belong in the private
> `indiana-agenda-tracker` repo, not here.

## What this repo is
The static front end for the Municipal Resource Dashboard (MRD). The application lives at
`mrd-ad682070b7/index.html`; `styles.css` and the two embedded dashboards sit beside it. Two
non-`main` branches carry published data snapshots consumed by the app at runtime.

The backend, pipelines, and all engineering documentation live in a separate private repository.

## Current state
- Build **p151r2** on `main`. Working tree clean; in sync with the remote.
- This working copy is the **source of truth** for front-end edits (established 2026-08-15).
  Edit in place, commit, push — no per-session temporary clones.
- Served locally for development on port 8778.
- A commit-time credential guard is active and was verified working on 2026-08-17: a staged
  credential-shaped string is blocked before it can be committed. The test fixture used for that
  verification has been removed.

## In progress
- Migration of the front end from GitHub Pages hosting to a local static server. Pages remains
  enabled until the verification checklist passes.

## Blocked
- Nothing.

## Next actions
- Complete the local-server verification checklist, then disable Pages.

## Conventions
- Bump the build marker on line 2 of `mrd-ad682070b7/index.html` **and** the `styles.css?v=`
  querystring on every deploy.
- Do not commit secrets. Read tokens embedded in the front end are public by design; treat
  everything else as private.
