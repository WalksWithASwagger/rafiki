# Product scope

## v1: CLI + local portal

This repository (**Rafiki**) ships as a **command-line tool** (`npx rafiki` / `rafiki`; alias `npx image-gen`) plus a **localhost-only HTTP portal** (`generate.py serve`). There is no multi-user auth, hosted service, or job queue in scope.

Rationale:

- Keeps deployment and security surface minimal (one API key on the operator’s machine; portal binds to 127.0.0.1 only).
- Matches how the tool is used today: agents and humans run batch jobs from a checkout.
- The local portal enables persistent ratings, cross-project search/filter, and (future) in-browser regen — none of which are possible with file:// viewers alone.

## Out of scope (for now)

- Hosted image generation as a SaaS
- Per-seat billing, rate limiting, or shared usage logs across machines
- Tight coupling to any one knowledge base repository layout (consumers pass paths explicitly)
- In-browser regen (Phase 3 — `POST /api/regen` endpoint is a 501 stub; planned)

## MCP server (`mcp_server.py`)

Rafiki ships an MCP server so any Claude session can invoke image generation as a structured tool call (no subprocess needed).

Add to `~/.claude/settings.json` or a project's `.claude/settings.json`:

```json
"mcpServers": {
  "rafiki": {
    "command": "/absolute/path/to/rafiki/.venv/bin/python",
    "args": ["/absolute/path/to/rafiki/mcp_server.py"],
    "env": {
      "GOOGLE_API_KEY": "...",
      "OPENAI_API_KEY": "..."
    }
  }
}
```

Tools exposed: `rafiki_generate`, `rafiki_batch`, `rafiki_list_styles`.

## Claude Code skill

`.claude/skills/rafiki.md` (in this repo) teaches Claude Code when and how to invoke Rafiki from any project that has this checkout on the path.

## Future extension

If you need Slack, webhooks, or an internal dashboard, add a thin HTTP layer that shells out to `generate.py` or imports it as a module—**do not duplicate** the Gemini client and prompt assembly.
