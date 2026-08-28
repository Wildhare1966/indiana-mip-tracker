# CLAUDE.md — Indiana MIP Tracker (MRD front end)

The **front-end repo** for the MRD (Municipal Resource Dashboard). Holds the served build, the CSV
data lanes, and the ArcGIS sync scripts. The backend that feeds it lives in a **different repo**.

## ⛔ This is a PUBLIC repo

`https://github.com/Wildhare1966/indiana-mip-tracker` — public. Never commit a token, a key, or
client-confidential material. The global pre-commit guard at `C:\Users\ty\.githooks\pre-commit`
catches vendor prefixes, exactly-48-hex runs, and secret-named assignments, but it is a net, not a
licence.

**Git history permanently holds a previously-committed auth token.** Rotation was the fix; the
scrubbed value is inert. A scrub does not unpublish anything — do not re-run one expecting it to.

## ⚠ Name collision — fully qualify, always

`indiana-mip-tracker` (this repo, the **front end**) and `indiana-agenda-tracker` (the **Apps Script
backend**, private, where the open items and session numbering live) are one word apart. Doctrine
item 15: an unqualified path is an unverified path. Confirm which repo you are in before editing.

## Map

There is no `README.md`. Read this file → [`HANDOFF.md`](HANDOFF.md) →
[`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md). Architecture and live backend coordinates live in
`../indiana-agenda-tracker/ARCHITECTURE.md` **§0**, which is the source of truth for `@NNN` / `pXXX`.

## What is actually served

**`mrd-ad682070b7/index.html`** — served at `http://localhost:8778/mrd-ad682070b7/` by
[`serve-mrd.bat`](serve-mrd.bat).

```bash
./serve-mrd.bat
```

Idempotent: starts nothing if something already listens on 8778. Binds `127.0.0.1` only. Uses
`python.exe` with a hidden window — **not `pythonw`**, whose console-less stderr crashes
`http.server` per request.

⛔ **Never open the app as `file://`.** A `file:` page sends `Origin: null`, which makes the Apps
Script `/exec` POST redirect 404, and the page's CSP (`default-src 'self'`) cannot match a `file:`
sibling, so `styles.css` and both embedded dashboards are refused.

## ⛔ `MIP_Platform.html` at the root is a trap

470 KB of build **`p80r4`**, not served, referenced only by the two `smoke.html` files, and headed
with a STALE COPY warning. **Do not "restore" it.**

⚠ *That warning header has itself gone stale* — it states the live build is `p151r2` and that the
file is "~71 builds behind." The served build is now **`p168r1`**. Trust
`mrd-ad682070b7/index.html`'s own build marker, never the warning's account of it.

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

## Related projects

- **`../indiana-agenda-tracker`** — the Apps Script backend + `ARCHITECTURE.md` §0. Session numbering
  (`P<N>`) and most open items live there, not here.
- **`../Sales Disclosures`** — a separate local Python pipeline; embedded here as the Sales
  Disclosures tab and publishing to the `data-sales` branch.
- **`../presentation`** — the MRD explainer video toolkit, which records against the local server URL
  above.

## Session workflow

Start with `/resume`, end with `/kickoff`. State lanes per Doctrine Block v1.7 item 11:
`HANDOFF.md` = where this stands now · `docs/OPEN-ITEMS.md` = what is outstanding ·
`STATUS.md` = state snapshot. Public remote on `main` — never push without checking for secrets.
