FILE-STAMP: 2026-08-29 | rev 4

> **rev 4** — MIP-8 shipped: the `.gitignore` guard actually works now, and the four operator
> consoles are untracked-but-served, with copies preserved in the private repo.
> **rev 3** — MIP-7 shipped and MIP-3 closed complete. Root is down to load-bearing files only; the
> single surviving `smoke.html` is now inside the served build. Adds the **`.gitignore` gap** warning
> (MIP-8).
> **rev 2** — MIP-4/5/6 shipped: flattened root, corrected `MIP_Platform.html` header, resolved
> `:8765`. Served build `p168r2`.
> **rev 1** — first stamped revision; the file predates the stamp. Added the **Data flow** section,
> corrected the claim that the ArcGIS sync scripts still live here, repointed Doctrine v1.7 → v1.8.

# CLAUDE.md — Indiana MIP Tracker (MRD front end)

The **front-end repo** for the MRD (Municipal Resource Dashboard). Holds the served build and the
published data lanes. The backend that feeds it lives in a **different repo**. The ArcGIS sync
scripts are **no longer here** — see [`arcgis/README.md`](arcgis/README.md) and the Data flow section.

## ⛔ This is a PUBLIC repo

`https://github.com/Wildhare1966/indiana-mip-tracker` — public. Never commit a token, a key, or
client-confidential material. The global pre-commit guard at `C:\Users\ty\.githooks\pre-commit`
catches vendor prefixes, exactly-48-hex runs, and secret-named assignments, but it is a net, not a
licence.

**Git history permanently holds a previously-committed auth token.** Rotation was the fix; the
scrubbed value is inert. A scrub does not unpublish anything — do not re-run one expecting it to.

✅ **`.gitignore` now works at any depth** (MIP-8, fixed 2026-08-29). It was two root-anchored
patterns (`/p168-ops.html`, `/*-ops.html`) that matched nothing in a subdirectory, which is how four
`*-ops.html` consoles came to sit tracked and public in `mrd-ad682070b7/tests/`. It is now one
unanchored `*-ops.html`. **Do not re-add a leading slash** — that is the exact bug.

⛔ **The four consoles remain in this repo's public history.** They were *untracked*, not deleted —
untracking unpublishes nothing, same as the token. No rotation is needed: they carry no token (all
read `mip_auth_token` from `localStorage`) and their one `/exec` URL is byte-identical to the served
build's.

## ⚠ Name collision — fully qualify, always

`indiana-mip-tracker` (this repo, the **front end**) and `indiana-agenda-tracker` (the **Apps Script
backend**, private, where the open items and session numbering live) are one word apart. Doctrine
item 15: an unqualified path is an unverified path. Confirm which repo you are in before editing.

## Map

There is no `README.md`. Read this file → [`HANDOFF.md`](HANDOFF.md) →
[`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md). Architecture and live backend coordinates live in
`../indiana-agenda-tracker/ARCHITECTURE.md` **§0**, which is the source of truth for `@NNN` / `pXXX`.

## What is actually served

**`mrd-ad682070b7/index.html`** — build **`p168r2`** — served at
`http://localhost:8778/mrd-ad682070b7/` by [`serve-mrd.bat`](serve-mrd.bat).

```bash
./serve-mrd.bat
```

Idempotent: starts nothing if something already listens on 8778. Binds `127.0.0.1` only. Uses
`python.exe` with a hidden window — **not `pythonw`**, whose console-less stderr crashes
`http.server` per request.

⛔ **Never open the app as `file://`.** A `file:` page sends `Origin: null`, which makes the Apps
Script `/exec` POST redirect 404, and the page's CSP (`default-src 'self'`) cannot match a `file:`
sibling, so `styles.css` and both embedded dashboards are refused.

**Everything the app needs lives inside `mrd-ad682070b7/`** and is referenced **relatively** —
`styles.css`, `dashboard.html`, `sales_dashboard.html`, `Data/`, `tests/smoke.html`. There are no
absolute-root asset paths. That is what made the MIP-5 and MIP-7 root cleanups safe, and it is what
to re-verify before moving anything.

**Bump the build marker on every deploy** — line 2 (`<!-- MIP build pNNNrM -->`) **and** the
`styles.css?v=` querystring on line 14. Both, together.

**The security self-test** is `mrd-ad682070b7/tests/smoke.html`, reachable in-app from Settings via
**▶ Run security self-test**. Its sanitizers are an **inline copy** of the served build's — nothing
is imported at runtime, so keep them in sync by hand. Run it before shipping.

**The `*-ops.html` consoles beside it are served but NOT tracked** (MIP-8). They must stay on disk
and on this origin — that is how they read `mip_auth_token` from `localStorage`. Do not "restore"
them to git to make them safe; back them up to `../indiana-agenda-tracker/ops/` instead.

## ⛔ `MIP_Platform.html` at the root is a trap

470 KB of build **`p80r4`**, not served, **88 p-numbers behind**. **Do not "restore" it.**

Ty ruled on 2026-08-29 (MIP-4) to **correct its header rather than delete the file**, and that header
is now accurate — it names the live build, says who references it, and carries a maintenance line
telling the next deploy to re-check it. Trust `mrd-ad682070b7/index.html`'s own marker anyway.

⚠ **It no longer renders standalone.** Its only asset reference is root `styles.css`, deleted under
MIP-5. Opening it gives an unstyled page — expected, not a fault. It is a reference artifact.

Its only referrer is now `mrd-ad682070b7/tests/smoke.html`, and **only in prose** — the root
`tests/smoke.html` that was the second referrer was deleted under MIP-7, and the surviving copy's
prose has been corrected to name the served build instead.

## Data flow — ⚠ the REPO only receives; the APP writes

A recurring misreading. Split the two.

### Repo level — inbound only ✅

Verified 2026-08-29: **nothing in this repo pushes to any other repo or project.** One remote
(`origin` → `indiana-mip-tracker.git`), no `.gitmodules`, no `.github/workflows`, and zero hits for
`git push` or `api.github.com` anywhere in tracked content. Both non-`main` branches are written
**by outside projects**:

| Branch | Written by | Direction |
|---|---|---|
| `data` | `../indiana-agenda-tracker/apps-script/P118_CdnSnapshots.js` — force-orphan commit, one commit forever, no history | **inbound** |
| `data-sales` | the `../Sales Disclosures` Python pipeline (`sdf-refresh` skill) | **inbound** |

Never publish to `data` by hand: P118 force-orphan-commits it on a cron and your commit disappears.

### Application level — this build is the primary WRITE surface into the backend ❌

`mrd-ad682070b7/index.html` carries **23 side-effecting `action=` routes** against the Apps Script
`/exec` in `indiana-agenda-tracker`. This app is *where the backend's data gets edited from* — it is
not a read-only viewer.

| Group | Routes |
|---|---|
| Tracked projects (4) | `create_tracked_project` · `update_tracked_project` · `close_tracked_project` · `delete` |
| Documents (4) | `tag_document` · `untag_document` · `tag_documents_batch` · `tag_document_upload` |
| Agenda / review (11) | `approve_agenda` · `reject_agenda` · `cancel_agenda` · `approve_summary` · `approve_reference` · `dismiss_reference` · `flag_minutes_review` · `resolve_review` · `override_meeting_type` · `update_schedule_url` · `resummarize_hearing` |
| Ops / trigger (3) | `admin_run` · `scrape_all_schedules` · `submit_issue_report` |
| **Third-party egress (1)** | `gemini_proxy` — POSTs prompt text through the backend to Google Gemini |

Three of these are true `POST`s; the rest ride `GET` query strings:

- `gemini_proxy` — `Content-Type: text/plain` is deliberate: it keeps the request a CORS *simple*
  request, because Apps Script cannot answer `OPTIONS`.
- `tag_document_upload` — **base64 file body**. This ships document bytes off the machine.
- `submit_issue_report` — form-encoded.

All of them route through `getWebAppUrl()`, which appends `?token=…` when the operator token is
present — so the gating in **Operator access** below covers every write uniformly. Inert without a
token; live the moment one is entered. The four `*-ops.html` consoles hit `admin_run` the same way.

### Outbound by relay — the `data-sales` CDN 📡

`../Sales Disclosures/arcgis/sdf_parcels_to_ago.py` pulls the `data-sales` gzip from this repo's
**public** raw CDN and republishes it into ArcGIS Online. This repo does not *produce* that data, but
it is the public distribution point a third project consumes. Anything landed on `data-sales` is
world-readable and gets re-hosted downstream.

### Retired and dead paths — do not resurrect

- ⛔ **`arcgis/sync_tracked_projects.py` is deleted** (commit `5c2e512`, 2026-08-29). It was the one
  script here that wrote outward — a one-way push into the wildhare ArcGIS Online feature layer. The
  copy here was 301 lines behind, pointed at a retired layer, and sat in a PUBLIC repo. Canonical
  copy: `../indiana-agenda-tracker/arcgis/`. Only `arcgis/README.md` remains, as a tombstone. The
  sync itself now runs **on a timer** in AGO (MIP-3, closed 2026-08-29).
- ✅ **`http://localhost:8765/api/refresh-hearings` is gone** (MIP-6, 2026-08-29). It called a
  pre-P150 local server started by `Start_MIP.bat`, which exists nowhere under
  `C:\Users\ty\Claude_Code`; port 8765 now belongs to `../Sales Disclosures`' static `http.server`,
  so the call reached **another project's server**. The topbar button was removed.
  ⚠ **`refreshHearings()` itself was KEPT** — four write paths call it after a successful `/exec`
  write, three of them inside `setTimeout` where a `ReferenceError` would be silent. It is now just
  `location.reload()`, the old success path. **Do not "clean up" this function as dead code.**
  Do not restore the button without a real backend route behind it.

## Branches — three data lanes, do not cross them

| Branch | Purpose |
|---|---|
| `main` | the front end |
| `data` | P118's data lane |
| `data-sales` | the **Sales Disclosures** lane — that project publishes here (`../Sales Disclosures`) |

`remotes/origin/claude/*` branches are agent scratch, not lanes.

## Operator access

Operator actions are inert until Ty enters a token. It is read from `localStorage` key
`mip_auth_token` via `getAuthToken()`, entered once under **Settings → Operator Access**. Reading the
dashboard is unaffected and needs no token. There is no `DEFAULT_AUTH_TOKEN` in this repo any more —
do not reintroduce one "for convenience."

The token is stored **per origin** — one set on `http://localhost:8778` is not visible to a page
served from anywhere else.

## Related projects

- **`../indiana-agenda-tracker`** — the Apps Script backend + `ARCHITECTURE.md` §0. Receives every
  write listed above. Canonical home of the `*-ops.html` consoles (`ops/`) and of the ArcGIS sync.
  ⚠ That "canonical" claim was **half false until 2026-08-29** — `ops/` held only `p168-ops.html`
  while `p160`–`p163` existed nowhere but this public repo. MIP-8 copied them across; they are
  **uncommitted there**, awaiting Ty. Session numbering (`P<N>`) and most open items live there.
- **`../Sales Disclosures`** — a separate local Python pipeline; embedded here as the Sales
  Disclosures tab, publishing to the `data-sales` branch and re-reading it for its AGO sync. **Owns
  port 8765.**
- **`../presentation`** — the MRD explainer video toolkit, which records against the local server URL
  above.

## Session workflow

Start with `/warmup`, end with `/kickoff`. State lanes per Doctrine Block v1.8 item 11:
`HANDOFF.md` = where this stands now · `docs/OPEN-ITEMS.md` = what is outstanding ·
`STATUS.md` = state snapshot. Public remote on `main` — never push without checking for secrets.

⚠ **`STATUS.md` is stale and is a changelog, not a snapshot** — it claims build `p151r2`, says
"Pages remains enabled", and calls `MIP_Platform.html` "blanked" when it is 470 KB. All three are
false. Doctrine item 11 makes it optional and retirable once `HANDOFF.md` carries the coordinates,
which it does. Flagged for Ty; not rewritten unilaterally.
