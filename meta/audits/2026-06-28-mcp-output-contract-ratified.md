# MCP Output Contract Ratified (2026-06-28)

Dated record of the agent-readable MCP output contract decision (roadmap Phase 5 P2) and
the conformance work that closed it. The living spec is
[`docs/MCP-OUTPUT-CONTRACT.md`](../../docs/MCP-OUTPUT-CONTRACT.md); this file is the
point-in-time decision snapshot.

## Decision

The de-facto envelope already emitted by the typed MCP tools in `mcp_server.py` is
**ratified as the contract**, formalized rather than redesigned:

- Required: `ok`, `success` (legacy alias of `ok`), `tool`.
- Flags: `mutating`, `external`, `dry_run` (where applicable).
- Conventions: `error` (string | null); `count` = primary-collection size; single output
  as flat `path`+`url`, multiple outputs as parallel `*_paths`+`*_urls`.
- **Flat, not nested.** All four known consumers read top-level keys, so the contract
  forbids a `data` wrapper. Migration is additive only — zero breaking changes.

Ratified by Kris Krüg on 2026-06-28.

## Why

Issue #196 ("MCP mirror") and future wrappers were about to push more tool state through
MCP. Agreeing on one envelope first prevented N inconsistent formats that would be
expensive to retrofit. The spike (#212) catalogued all 23 tools from real dry-run samples
(not guesses), inventoried the consumers, and proposed the minimal additive envelope.

## What shipped

| Issue | PR | Result |
|---|---|---|
| #212 | #255 | Contract doc + per-tool catalogue + consumer inventory |
| #249 | #256 | `ok`/`success`/`tool` added to the 4 gap tools |
| #250 | #257 | Error-path normalization; `rafiki_run`'s 3 shapes unified |
| #252 | #258 | Count-field naming convention |
| #251 | #259 | path/url `*_url` siblings across tools |
| #253 | #260 | JSON Schema (`tests/mcp_envelope_schema.json`) + output-format eval |
| #254 | (this PR) | #196 tools (`media_warnings`, `job_status`) confirmed conformant; eval coverage completed |

The eval (`tests/test_mcp_envelope_contract.py`) validates 21 of the 23 typed tools plus
error paths against the schema. It immediately caught real drift — `rafiki_batch`'s success
path was missing `tool` — which #253 fixed.

## Notable decision

`rafiki_list_styles` was restructured (presets nested under `styles`) rather than kept
strictly additive, because it had zero consumers and the additive form would have polluted
a name-keyed map. All *consumed* tools stayed strictly additive.

## Still open / not covered here

- `rafiki_media_index` and `rafiki_notion_export` are validated by their own tests, not the
  eval loop (non-hermetic / external).
- Merged preview+run shape unpredictability (viewer/library/canva) is documented as a known
  characteristic, not a contract violation.
