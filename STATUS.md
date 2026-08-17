STATUS-STAMP: 2026-08-17 | rev 2

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
