# MCP Output Contract (Proposed)

Status: **proposed — pending maintainer ratification** (issue #212).
Scope: a stable, agent-readable JSON output contract for the typed MCP tools in
[`mcp_server.py`](../mcp_server.py). This satisfies roadmap
[Phase 5 P2](ROADMAP.md): "Tools return stable JSON with paths, URLs, counts, errors,
and mutation flags."

This document **describes and formalizes the envelope that already exists** in the tool
returns. It does not change any tool output. Normalization of the gaps catalogued below is
tracked by the follow-up issues in the last section. See [MCP.md](MCP.md) for the tool
surface and usage examples.

## Design constraints

1. **Flat, not nested.** Every known consumer reads tool output by top-level key — see
   [Consumers](#consumers-and-compatibility). Wrapping the payload under a `data` key would
   break all of them. The contract therefore keeps every field at the top level; the
   common envelope fields and the tool-specific fields are flat siblings.
2. **Additive only.** `success` is retained as a legacy alias of `ok`; migration adds or
   normalizes fields but does not remove or relocate existing ones. Zero breaking changes.
3. **Built on existing helpers.** The contract is defined in terms of the helpers already
   in `mcp_server.py`: `_json()` (serialization), `_error_payload()` (errors), and
   `_path_info()` (path/url pairs). No new response framework.

## The envelope

Every typed tool returns a JSON **object** (serialized by `_json()` →
`json.dumps(indent=2, ensure_ascii=False)`). Fields:

| Field | Type | Status | Meaning |
|---|---|---|---|
| `ok` | bool | **required** | Canonical success flag. New clients read this. |
| `success` | bool | **required** | Legacy alias of `ok`, kept for existing clients. Always equals `ok`. |
| `tool` | string | **required** | The tool name (e.g. `"rafiki_render"`). |
| `error` | string \| null | required on failure | Human-readable error message when `ok` is `false`; absent/null on success. |
| `mutating` | bool | recommended | `true` if the call wrote to disk / changed state. |
| `external` | bool | recommended | `true` if the call reached an external service (e.g. Notion, Replicate). |
| `dry_run` | bool | when applicable | `true` if the call previewed without performing the action. |
| `count` | int | when applicable | Cardinality of the primary collection in the response. |

**Paths and URLs.** A single primary output uses the flat pair `path` + `url`, produced by
`**_path_info(p)` (which resolves the path and emits a `file://` URL). Multiple outputs use
parallel arrays `*_paths` + `*_urls`. (Today some tools prefix the pair, e.g.
`result_path`/`result_url`, `viewer_path`/`viewer_url` — normalization is a follow-up.)

**Tool-specific fields** (e.g. `images`, `results`, `jobs`, `recommendations`) are flat
siblings of the envelope fields.

### Success example (`rafiki_registry_export`, captured dry-run)

```json
{
  "success": true,
  "ok": true,
  "tool": "rafiki_registry_export",
  "format": "json",
  "dry_run": true,
  "mutating": false,
  "external": false,
  "count": 293,
  "path": "/Users/.../data/asset-registry.json",
  "url": "file:///Users/.../data/asset-registry.json"
}
```

### Error example (`rafiki_job_status` with empty id, captured)

```json
{
  "success": false,
  "ok": false,
  "tool": "rafiki_job_status",
  "error": "job_id is required",
  "mutating": false,
  "external": false
}
```

Errors are built by `_error_payload(tool, error, **extra)`, which always sets
`success`/`ok` to `false` and includes `tool` and `error`. The contract requires error
returns to also carry the same flag fields (`mutating`, `external`, `dry_run` where
relevant) and enough context to identify the call.

## Per-tool catalogue and gaps

Sourced from the tool returns in `mcp_server.py` and real dry-run samples. "Gap" = delta
from the envelope above. (Tools sharing a gap are grouped.)

### Conformant (full envelope: `ok`/`success`/`tool` + flags)

| Tool | Notes |
|---|---|
| `rafiki_registry_search` | `count`, `results[]`. Conformant. |
| `rafiki_registry_export` | flat `path`+`url`, `count`. Conformant. |
| `rafiki_media_index` | spreads `index()` payload; has flags + `registry_path`. |
| `rafiki_media_search` | `count`, `results[]`. Conformant. |
| `rafiki_media_warnings` | `warning_count`, `warnings[]`. Conformant. |
| `rafiki_subjects` | `count`, `subjects[]`. Conformant. |
| `rafiki_jobs` | `count`, `jobs[]`. Conformant. |
| `rafiki_job_status` | full status fields; clean error path. Conformant. |
| `rafiki_archive_health` | rich counts; `errors` is an object, not a string. |
| `rafiki_style_anchors` | flags + `style`. Conformant. |
| `rafiki_train_lora` | spreads planner result; `mutating:true`, `external` reflects `execute`. |
| `rafiki_video_generate` | spreads planner result; same pattern as train_lora. |
| `rafiki_status` | gained `ok`/`success`/`tool` (#249). Conformant. |
| `rafiki_generate` | gained `tool` (#249); outcome still also in `message`. Conformant. |
| `rafiki_list_styles` | restructured under `styles` + `count` with `ok`/`success`/`tool` (#249). Conformant. |
| `rafiki_usage` | gained `ok`/`success`/`tool` (#249). Conformant. |
| `rafiki_batch` | error paths now carry the full flag set via `_error_payload` (#250). Conformant. |
| `rafiki_run` | three error shapes unified to one key set (flag-distinguished); gained `tool` (#250). Conformant. |

### Gaps

| Tool | Gap |
|---|---|
| `rafiki_render` | Parallel arrays `output_paths`/`output_urls`; error path shape differs from success. |
| `rafiki_viewer_rebuild` | Merges preview + run dicts → **shape varies**; prefixed `viewer_path`/`viewer_url`. |
| `rafiki_library_rebuild` | Merges preview + run dicts → shape varies; prefixed `library_path`/`library_url`. |
| `rafiki_canva_export` | Merges base + run; prefixed `result_path`/`result_url`; success/error shapes differ. |
| `rafiki_notion_export` | Spreads `notion.export()` result; `external:true`; shape depends on result dict. |

Cross-cutting gaps: (a) `path`/`url` prefix naming is inconsistent; `registry_path` has no
`url` sibling. (b) count fields are named per-tool (`count`, `warning_count`,
`project_count`, `image_count`, …) rather than by one convention. (c) merged preview+run
returns make exact shape hard to predict on error.

## Consumers and compatibility

Four consumers read tool output today, **all by top-level key** — establishing the flat
constraint:

| Consumer | Reads | Breaks if nested? |
|---|---|---|
| `scripts/dry-run-smoke.py` (:182–186) | `success`, `exit_code`, `json`, `mutating`; nested batch keys | Yes |
| `.claude/skills/run-rafiki/driver.sh` (:289–290) | `repo_root`, `common_tools` from `rafiki_status` | Yes |
| `tests/test_mcp_server.py` (23 tests) | `success`/`ok` + every tool-specific top-level key | Yes |
| `tests/test_cli_surfaces.py` (:273–277) | `success`, `exit_code`, `json`, `stdout` | Yes |

Implication: migration must be **additive at the top level**. Adding `tool`/`ok` to tools
that lack them, or adding a missing `url` sibling, is safe. Renaming or nesting is not (it
would require coordinated consumer updates and is out of scope for the additive path).

## Migration approach

- Keep `success` as a permanent alias of `ok`.
- Bring the gap tools up to the envelope by **adding** `ok`/`success`/`tool` and the flag
  fields — never removing existing keys.
- Normalize path/url naming and count naming as additive aliases first; only consider
  removing a legacy name in a later, explicitly-breaking pass with consumer updates.
- A machine-readable JSON Schema for the envelope is **deferred** to the contract-validation
  follow-up (it backs the output-format eval). Illustrative shape, for reference only:

```jsonc
// Deferred — authored in the contract-validation follow-up, not now.
{
  "type": "object",
  "required": ["ok", "success", "tool"],
  "properties": {
    "ok": {"type": "boolean"},
    "success": {"type": "boolean"},
    "tool": {"type": "string"},
    "error": {"type": ["string", "null"]},
    "mutating": {"type": "boolean"},
    "external": {"type": "boolean"},
    "dry_run": {"type": "boolean"}
  }
}
```

## Follow-up implementation issues

Filed after envelope ratification; each is one-issue-one-PR and additive.

| Issue | Work | Size |
|---|---|---|
| [#249](https://github.com/WalksWithASwagger/rafiki/issues/249) | Add `ok`/`success`/`tool` to the gap tools (`rafiki_status`, `rafiki_generate`, `rafiki_list_styles`, `rafiki_usage`) | XS |
| [#250](https://github.com/WalksWithASwagger/rafiki/issues/250) | Normalize error paths to carry the full flag set; unify `rafiki_run`'s three error shapes | S |
| [#251](https://github.com/WalksWithASwagger/rafiki/issues/251) | Standardize path/url output (single `path`+`url`, multiple `*_paths`+`*_urls`); add missing siblings | M |
| [#252](https://github.com/WalksWithASwagger/rafiki/issues/252) | Standardize count-field naming across list/search/export tools | S |
| [#253](https://github.com/WalksWithASwagger/rafiki/issues/253) | Contract-validation test + output-format eval (schema-validate each tool against the envelope) | M |
| [#254](https://github.com/WalksWithASwagger/rafiki/issues/254) | Align #196 (MCP mirror) outputs to this contract | S |

Out of scope here: changing any tool output, writing the validation tests/eval, and
implementing the above — those are the follow-up PRs.
