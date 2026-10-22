# Open items — Indiana MIP Tracker

FILE-STAMP: 2026-10-22 | rev 17

**Format contract: `Dexters-Dashboard/docs/OPEN-ITEMS-SPEC.md`.** These rows are rendered on
the dashboard's **Items** page alongside every other project's, so keep to the spec — a row
that drifts from it silently stops being indexed. This file records what is *outstanding*;
current state lives in `HANDOFF.md` (Doctrine Block v1.8 item 11 lanes).

Backfilled 2026-08-22 (Ty-ruled R5) by reading this repo's own `STATUS.md`/`HANDOFF.md` and
judging what was still live. Items recorded there but since closed were deliberately not
carried forward.

> **rev 17 (2026-10-22):** **MIP-18** closed (`p223r1`, the roster protocol) and **MIP-19** boarded (Update Profiles per member).
> Yesterday's closures (**MIP-12** to **MIP-17**) rotated verbatim to [`docs/STATUS-ARCHIVE.md`](STATUS-ARCHIVE.md)
> under spec rev 10 retention rule 2.
> **rev 16 (2026-10-21, same session):** **MIP-17** closed — `p222r4` keeps the first real source URL and
> renders sources as host-labelled links; records Ty's live Update Members test on Lebanon.
> **rev 15 (2026-10-21, same session):** **MIP-16** closed — `p222r3` spreads the log's Searched / Sources
> lines across members; records Ty's live Lebanon test (writes and grounded search both confirmed).
> **rev 14 (2026-10-21, same session):** **MIP-15** closed — `p222r2` wires Update Members / Update Profiles
> to the backend's @589 routes with live-search grounding; the browser overlay is gone. Corrects a MIP-14
> claim: `p222r1` did not send `tools` either.
> **rev 13 (2026-10-21, same session):** **MIP-14** closed — `p222r1`, Ty's second request of the day (Sales
> Disclosures as a launcher, Map, Zonda off, Schedule Builder, Jurisdictions split into Profiles and
> Hearings with Update Members / Update Profiles). **MIP-11** widened a second time.
> **rev 12 (2026-10-21, same session):** **MIP-13** closed — Ty chose the live build; `p221r2` ships the
> Land Presentation Map launcher. Nothing rotated: this file now holds exactly this session's closures.
> **rev 11 (2026-10-21):** **MIP-12** closed (build `p221r1` — the MRD as the launcher for the
> sibling apps: live Sales Disclosures frame, Video Console and Cropper buttons), **MIP-13** boarded
> for Ty (the Land Presentation Map URL — item 4 of the same request), and **MIP-11** widened by one
> more line of `CLAUDE.md` drift. The 2026-10-06 closure (**MIP-10**) rotated verbatim to
> [`docs/STATUS-ARCHIVE.md`](STATUS-ARCHIVE.md) under spec rev 10 retention rule 2.
> **rev 10 (2026-10-06):** **MIP-10** closed (the laptop-retirement git reconciliation) and
> **MIP-11** boarded. The 2026-08-23..08-29 closures (**MIP-1** to **MIP-9**) rotated verbatim to
> [`docs/STATUS-ARCHIVE.md`](STATUS-ARCHIVE.md) under spec rev 10 retention rule 2.

## Needs Ty — decisions and approvals

*Nothing outstanding.* (No table here deliberately — an empty header row is not a valid row under
the format contract.)

## Claude Code can execute — say the word

| ID | Owner | Item | Why it matters | Blocked by |
|---|---|---|---|---|
| **MIP-19** | CC | Move **Update Profiles** onto the individual member's profile, one member per click, and remove the old "AI Research Profile" block (`researchMemberProfile`, training data + meeting videos, saves nothing). Per-field source link and evidence date; Tier A (official bio / photo, employer, other board seats, past offices, INBiz governing-person roles, campaign committee, CAN-12 / Form 236 disclosures) and Tier B (LinkedIn, Facebook, X, campaign site, civic organisations) only; Tier C (family, religion, home address, characterizations) never collected; accept / reject per result before `set_member_profile`. Retire or reduce the per-jurisdiction bulk button. | The bulk button fires one billed grounded call per member with no review, and model-sourced claims about named people reach the sheet unreviewed. Vote history belongs to the platform's own minutes pipeline, not a model's memory. Ruled 2026-10-22 ("Build the roster protocol first"). | — |
| **MIP-11** | CC | Replace the stale build number `p168r2` in `CLAUDE.md` and the `MIP_Platform.html` header with a pointer to `mrd-ad682070b7/index.html` line 2 (served build probed 2026-10-06: `p210r1`; 2026-10-21: `p221r1`). **Widened 2026-10-21:** the same whole-file `CLAUDE.md` rev 6 edit must also drop `sales_dashboard.html` from the served-asset list on line 72 (the copy was removed in `p221r1`; the Sales Disclosures tab now frames `http://localhost:8765` live) and add one paragraph on the top-bar Apps group (launchers, not views — Sales Disclosures included since `p222r1`; the frame is gone), the Profiles/Hearings split (`muniMode`, two nav doors on `#view-muni`), the retired Zonda button and the `img-src https:` relaxation for member photos. | `CLAUDE.md` rev 5 line 56 and the `MIP_Platform.html` header (lines 3-34, "88 p-numbers behind") were last corrected 2026-08-29; the header's own MAINTENANCE line ("re-check this block on every deploy") has not been followed since, because FE deploys are driven from `C:\Users\ty\Claude_Code\indiana-agenda-tracker`, whose kickoff never touches this repo's docs. It is the exact failure MIP-4 closed: a guard that misdescribes what it guards. A pointer instead of a number cannot go stale. `CLAUDE.md` is an instruction file: whole-file edit with a rev bump (doctrine item 4) — which is also why the line-72 drift from `p221r1` is carried here as a named open item rather than patched in place. | — |

## Recently closed

| ID | Closed | What happened |
|---|---|---|
| **MIP-18** | 2026-10-22 | **`p223r1` (commit `0a74570`) — Update Members becomes the roster protocol (Ty's ruling 2026-10-22, after the protocol recommendations).** **Prompt:** names the jurisdiction's official hosts (derived from `agenda_landing_url`, `minutes_landing_url` and every `…Url` in `JURISDICTION_REFS`), orders the sources (own site → agendas and minutes of the last 90 days and the January reorganization meeting → county election board / Indiana Election Division → local press; no Ballotpedia for towns this size, no memory), fixes the role vocabulary (President · Vice President · Member, then the seat; PC party blank unless stated), and adds an `EVIDENCE_DATE` column (eight columns; seven-column replies still parse). **Gate:** the page grades each SOURCE itself with `_sourceTier` (1 own host or sub-host, 2 other `.gov` / `.in.us`, 4 press, 5 none / grounding redirect / Ballotpedia); a DEPARTED, NEW or CHANGED verdict with tier > 2 is downgraded to UNVERIFIED and logged as `… → UNVERIFIED · name — needs an official source, got <host>`; UNVERIFIED never writes; a press-only CONFIRMED is noted and still written as the status quo without a `source_url`. The log's first lines carry the counts incl. `downgraded N` and `Official hosts searched first: …`; every line carries `evidence YYYY-MM-DD` when given. **Review step:** NEW cards carry ✓ Accept (`status=current`) and ✕ Reject (`status=departed`), departed cards ↩ Restore — `memberStatusAction` does one `upsert_member`, updates the card and writes one log entry (Accepted / Rejected / Restored · name); `event.stopPropagation` keeps the card from opening the profile. **Verified** with no token at `http://localhost:8778/mrd-ad682070b7/`: served marker `p223r1`, `node --check` OK; Lebanon's official host resolves to `lebanon.in.gov`; tiers: own site 1, `docs.lebanon.in.gov` 1, `boonecounty.in.gov` 2, `wfyi.org` 4, Ballotpedia 5, redirect 5, none 5; a synthetic NEW card shows Accept + Reject and a departed card Restore, with the expected `memberStatusAction('lebanon','Council','Test Newcomer','departed',this)`; Reject reached the live route and logged `Roster change failed · Unauthorized`; Update Members with no token logged `Unauthorized`; `tests/smoke.html` 13/20 with the seven no-token 403s; console clean. ⚠ A live grounded run under the new prompt is Ty's first click. Backend monthly schedule proposed as a session card the same day. |
