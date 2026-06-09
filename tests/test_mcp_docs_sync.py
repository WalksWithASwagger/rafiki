"""Ensure docs/MCP.md documents every registered MCP tool."""

from __future__ import annotations

import asyncio
from pathlib import Path

import mcp_server

REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_DOCS = REPO_ROOT / "docs" / "MCP.md"

# Tools intentionally omitted from public docs (none today).
ALLOWLIST: set[str] = set()


def _registered_tool_names() -> set[str]:
    tools = asyncio.run(mcp_server.mcp.list_tools())
    return {tool.name for tool in tools}


def test_mcp_docs_cover_all_registered_tools():
    docs = MCP_DOCS.read_text(encoding="utf-8")
    registered = _registered_tool_names()
    missing = sorted(name for name in registered if name not in docs and name not in ALLOWLIST)
    assert not missing, f"docs/MCP.md missing tool sections for: {', '.join(missing)}"


def test_mcp_docs_do_not_reference_unknown_tools():
    docs = MCP_DOCS.read_text(encoding="utf-8")
    registered = _registered_tool_names()
    documented = {
        line.strip().strip("-").strip().split(":", 1)[0].strip().strip("`")
        for line in docs.splitlines()
        if line.strip().startswith("- `rafiki_")
    }
    stale = sorted(name for name in documented if name not in registered and name not in ALLOWLIST)
    assert not stale, f"docs/MCP.md documents unregistered tools: {', '.join(stale)}"
