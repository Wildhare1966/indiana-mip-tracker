# STATUS archive — Indiana MIP Tracker (MRD front end)

`STATUS.md` was **retired on 2026-08-29** on Ty's ruling. Everything it held is preserved verbatim
below; nothing was edited on the way in.

## Why it was retired

Doctrine Block v1.8 **item 11** makes `STATUS.md` optional — *"a state snapshot, never a changelog;
OPTIONAL, and a repo whose `HANDOFF.md` already carries the coordinates may retire it, but only once
`HANDOFF.md` exists."* Both conditions held: `HANDOFF.md` exists (created 2026-08-28, now rev 5) and
carries the live coordinates in its own table.

The file had also stopped being a snapshot and become a changelog — rev-delta sections stacked
newest-first — and it was **stale in three ways that actively misled**:

| Claim in the retired file | Reality on 2026-08-29 |
|---|---|
| "Build **p151r2** on `main`" | served build was `p168r2` |
| "Pages remains enabled until the verification checklist passes" | Pages was disabled on/before 2026-08-16; **MIP-2** closed as MOOT on 2026-08-23 |
| `MIP_Platform.html` "(blanked…)" | 470,244 bytes, not blank |

This is not a new observation. **MIP-2**'s closing note records that the 2026-08-22 backfill read
this stale `STATUS.md` instead of the report sitting beside it, and calls that *"the whole thesis of
SYS-8."* The file misled a session, was corrected, and then misled the start of this one too.

## Where its live content went

Nothing load-bearing was lost. Before retirement, each rule was checked against the file that now
owns it:

| Rule in the retired file | Now lives in |
|---|---|
| Bump the build marker on line 2 **and** the `styles.css?v=` querystring on every deploy | `CLAUDE.md` → *What is actually served* (already migrated at rev 4) |
| This working copy is the source of truth for FE edits — edit in place, commit, push; no per-session temporary clones | `CLAUDE.md` → *What is actually served* (migrated at rev 5) |
| Do not commit secrets; the commit-time credential guard | `CLAUDE.md` → *This is a PUBLIC repo* |
| What this repo is / current state / next actions | `HANDOFF.md` (the item-11 lane for exactly this) |

The one line deliberately **not** carried forward is *"Read tokens embedded in the front end are
public by design"* — that describes the pre-AGD-22 world. There is no `DEFAULT_AUTH_TOKEN` in this
repo any more; the operator token is entered into `localStorage` and never committed.

---

# ⬇ Retired content, verbatim (STATUS-STAMP: 2026-08-23 | rev 4)

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
