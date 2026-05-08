#!/usr/bin/env python3
"""
Rafiki MCP Server — exposes the local Rafiki toolbox as MCP tools.

Tools:
  rafiki_status         Show local setup, env, and client config snippets
  rafiki_generate       Generate a single image
  rafiki_batch          Process an image-prompts.md file
  rafiki_list_styles    List available style presets
  rafiki_usage          Show local generation usage
  rafiki_run            Run any supported Rafiki CLI workflow

Install locally:

  codex mcp add rafiki -- /path/to/rafiki/.venv/bin/python /path/to/rafiki/mcp_server.py
  claude mcp add --scope user rafiki -- /path/to/rafiki/.venv/bin/python /path/to/rafiki/mcp_server.py

Or add to a generic MCP config:

  "mcpServers": {
    "rafiki": {
      "command": "/path/to/rafiki/.venv/bin/python",
      "args": ["/path/to/rafiki/mcp_server.py"]
    }
  }
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

def _load_dotenv(path) -> None:
    if not path.exists():
        return
    import os
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

_load_dotenv(_ROOT / ".env")

from mcp.server.fastmcp import FastMCP
from lib.core import generate_image
from lib.batch import run_batch
from lib.prompts import ASPECT_RATIOS, parse_image_prompts_md
from lib.styles import load_styles
from lib.models import resolve_model
from lib.usage import load_usage_log

_CLI_SUBCOMMANDS = {
    "view",
    "library",
    "link-projects",
    "approve",
    "canva-export",
    "clean",
    "deploy",
    "notion-export",
    "regen",
    "registry",
    "social-expand",
}
_CLI_TOP_LEVEL_FLAGS = {
    "--prompt",
    "-p",
    "--prompt-file",
    "-f",
    "--list-styles",
    "--usage",
    "--doctor",
    "--render",
    "--render-dir",
}
_CLI_BLOCKED_SUBCOMMANDS = {"serve"}
_CLI_MUTATING_SUBCOMMANDS = {
    "approve",
    "canva-export",
    "clean",
    "deploy",
    "notion-export",
    "regen",
    "social-expand",
}

mcp = FastMCP(
    "rafiki",
    instructions=(
        "AI image generation via Gemini and OpenAI. "
        "Supports single images, batch prompt files (.md), style presets, "
        "style composition (kk+bcai), model aliases (flash, gpt, pro), "
        "parallel batch generation with run isolation, and a constrained "
        "bridge to Rafiki's CLI workflows."
    ),
)


def _capture(fn, *args, **kwargs):
    """Run fn with stdout redirected to stderr (keeps MCP stdio clean)."""
    old = sys.stdout
    sys.stdout = sys.stderr
    try:
        return fn(*args, **kwargs)
    finally:
        sys.stdout = old


def _json(data: dict | list) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _normalise_aspect_ratio(value: str) -> str:
    return ASPECT_RATIOS.get(value, value)


def _style_arg(value: str) -> str | None:
    if not value:
        return None
    if value == "none":
        return "none"
    return value


def _ref_list(
    *,
    prompt_count: int,
    reference_image: str = "",
    reference_images: list[str] | None = None,
) -> list[str | None]:
    refs = [p for p in (reference_images or []) if p]
    if refs:
        if len(refs) == 1:
            return refs * prompt_count
        if len(refs) != prompt_count:
            raise ValueError(
                f"reference_images has {len(refs)} path(s) but {prompt_count} prompt(s)"
            )
        return refs
    if reference_image:
        return [reference_image] * prompt_count
    return [None] * prompt_count


def _trim(text: str, limit: int = 20000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[trimmed {len(text) - limit} chars]"


def _validate_cli_args(args: list[str]) -> tuple[bool, str]:
    if not args:
        return False, "args is required"
    for arg in args:
        if not isinstance(arg, str):
            return False, "all args must be strings"
        if "\x00" in arg:
            return False, "args may not contain NUL bytes"

    first = args[0]
    if first in _CLI_BLOCKED_SUBCOMMANDS:
        return False, "`serve` is long-running; start the portal outside MCP"
    if first in _CLI_SUBCOMMANDS:
        return True, ""
    if first.startswith("-") and first in _CLI_TOP_LEVEL_FLAGS:
        return True, ""
    if any(flag in args for flag in _CLI_TOP_LEVEL_FLAGS):
        return True, ""
    if first.endswith((".md", ".markdown")):
        return True, ""
    return False, (
        "unsupported Rafiki CLI invocation; pass generate.py arguments only, "
        "such as ['--usage'], ['view', 'project'], or ['--render', 'card.html']"
    )


def _run_generate_py(args: list[str], timeout_seconds: int) -> dict:
    ok, error = _validate_cli_args(args)
    if not ok:
        return {"success": False, "error": error, "args": args}

    timeout = max(1, min(int(timeout_seconds), 3600))
    command = [sys.executable, str(_ROOT / "generate.py"), *args]
    try:
        proc = subprocess.run(
            command,
            cwd=str(_ROOT),
            env=os.environ.copy(),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "timeout": True,
            "timeout_seconds": timeout,
            "command": command,
            "stdout": _trim(e.stdout or ""),
            "stderr": _trim(e.stderr or ""),
        }

    stdout = proc.stdout or ""
    parsed_stdout = None
    try:
        parsed_stdout = json.loads(stdout)
    except json.JSONDecodeError:
        pass

    action = args[0]
    return {
        "success": proc.returncode == 0,
        "exit_code": proc.returncode,
        "command": command,
        "cwd": str(_ROOT),
        "mutating": action in _CLI_MUTATING_SUBCOMMANDS,
        "stdout": _trim(stdout),
        "stderr": _trim(proc.stderr or ""),
        "json": parsed_stdout,
    }


@mcp.tool()
def rafiki_status() -> str:
    """Report the local Rafiki MCP setup without exposing secret values."""
    python_bin = sys.executable
    server_path = str(_ROOT / "mcp_server.py")
    result = {
        "repo_root": str(_ROOT),
        "python": python_bin,
        "mcp_server": server_path,
        "env": {
            "GOOGLE_API_KEY": bool(os.environ.get("GOOGLE_API_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
            "NOTION_API_KEY": bool(os.environ.get("NOTION_API_KEY")),
            "NOTION_DATABASE_ID": bool(os.environ.get("NOTION_DATABASE_ID")),
        },
        "common_tools": [
            "rafiki_generate",
            "rafiki_batch",
            "rafiki_list_styles",
            "rafiki_usage",
            "rafiki_run",
        ],
        "cli_bridge_subcommands": sorted(_CLI_SUBCOMMANDS),
        "blocked_cli_subcommands": sorted(_CLI_BLOCKED_SUBCOMMANDS),
        "codex_add_command": (
            f"codex mcp add rafiki -- {python_bin} {server_path}"
        ),
        "claude_add_command": (
            f"claude mcp add --scope user rafiki -- {python_bin} {server_path}"
        ),
    }
    return _json(result)


@mcp.tool()
def rafiki_generate(
    prompt: str,
    output_path: str = "output.png",
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str = "kk",
    reference_image: str = "",
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    dry_run: bool = False,
) -> str:
    """Generate a single image using Rafiki.

    Args:
        prompt: Text description of the desired image.
        output_path: Where to save the PNG (absolute or relative to cwd).
        model: Model ID or alias. Aliases: flash/nano/pro (Gemini), gpt/gpt1/dalle3 (OpenAI).
        aspect_ratio: 16:9 | 1:1 | 9:16 | linkedin | instagram | story | square.
        resolution: 1K | 2K | 4K — Gemini Pro only.
        quality: low | medium | high — OpenAI only.
        style: kk | hopecode | bcai | upgrade | none | composed (e.g. kk+bcai).
        reference_image: Optional path to a reference image.
        reference_role: style | mockup.
        composition_references: Extra reference paths for mockup composition.
        dry_run: Preview without calling any API.

    Returns:
        JSON string with success, output_path, model, and message.
    """
    resolved_model = resolve_model(model)
    resolved_style = _style_arg(style)
    resolved_aspect_ratio = _normalise_aspect_ratio(aspect_ratio)

    success = _capture(
        generate_image,
        prompt=prompt,
        output_path=output_path,
        model=resolved_model,
        aspect_ratio=resolved_aspect_ratio,
        resolution=resolution,
        quality=quality,
        style=resolved_style,
        reference_image=reference_image or None,
        reference_role=reference_role,
        composition_references=composition_references,
        dry_run=dry_run,
    )
    result: dict = {
        "success": success,
        "output_path": output_path,
        "model": resolved_model,
        "aspect_ratio": resolved_aspect_ratio,
        "resolution": resolution,
        "style": style,
        "reference_image": reference_image,
        "reference_role": reference_role,
        "dry_run": dry_run,
        "prompt_preview": prompt[:120],
    }
    if success and not dry_run:
        result["message"] = f"Image saved to {output_path}"
    elif dry_run:
        result["message"] = "Dry run — no API call made"
    else:
        result["message"] = "Generation failed — check stderr for details"
    return json.dumps(result, indent=2)


@mcp.tool()
def rafiki_batch(
    prompt_file: str,
    output_dir: str = "",
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str = "kk",
    reference_image: str = "",
    reference_images: list[str] | None = None,
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    workers: int = 1,
    dry_run: bool = False,
    no_viewer: bool = False,
) -> str:
    """Process an image-prompts.md file and generate all images in the batch.

    Creates a timestamped run-*/  subdirectory so previous runs are never
    overwritten. Generates both a per-run viewer and a project comparison viewer.

    Args:
        prompt_file: Path to the image-prompts.md file.
        output_dir: Directory for output images (default: <prompt_file_dir>/images/).
        model: Model ID or alias for all images.
        aspect_ratio: Default aspect ratio (per-prompt overrides are respected).
        resolution: Default resolution (Gemini Pro only).
        quality: Quality level (OpenAI only).
        style: Style preset or composed spec (e.g. kk+bcai). 'none' = no style.
        reference_image: Optional reference image reused for every prompt.
        reference_images: Optional per-prompt reference image paths.
        reference_role: style | mockup.
        composition_references: Extra reference paths for mockup composition.
        workers: Parallel generation workers (1 = sequential, 4 = fast).
        dry_run: Preview without generating any images.
        no_viewer: Skip generating viewer.html gallery.

    Returns:
        JSON string with success, counts, run_dir, viewer_path, and per-image results.
    """
    prompt_path = Path(prompt_file)
    if not prompt_path.exists() and not dry_run:
        return _json({"success": False, "error": f"Prompt file not found: {prompt_file}"})

    prompts = _capture(parse_image_prompts_md, str(prompt_path)) if prompt_path.exists() else []
    out_dir = Path(output_dir) if output_dir else prompt_path.parent / "images"

    resolved_model = resolve_model(model)
    resolved_style = _style_arg(style)
    resolved_aspect_ratio = _normalise_aspect_ratio(aspect_ratio)
    try:
        ref_paths = _ref_list(
            prompt_count=len(prompts),
            reference_image=reference_image,
            reference_images=reference_images,
        )
    except ValueError as e:
        return _json({"success": False, "error": str(e)})

    result = _capture(
        run_batch,
        prompts=prompts,
        project_dir=out_dir,
        model=resolved_model,
        aspect_ratio=resolved_aspect_ratio,
        resolution=resolution,
        quality=quality,
        style=resolved_style,
        ref_paths=ref_paths,
        reference_role=reference_role,
        composition_references=composition_references,
        workers=workers,
        dry_run=dry_run,
        generate_viewer_html=not no_viewer,
        prompt_file=str(prompt_path),
    )

    return json.dumps({
        "success": result.success,
        "mode": "batch",
        "dry_run": dry_run,
        "generated": result.success_count,
        "total": result.total,
        "project_dir": str(result.project_dir),
        "run_dir": str(result.run_dir),
        "run_id": result.run_id,
        "viewer_path": result.viewer_path,
        "model": resolved_model,
        "aspect_ratio": resolved_aspect_ratio,
        "resolution": resolution,
        "style": style,
        "images": result.images,
    })


@mcp.tool()
def rafiki_list_styles() -> str:
    """List all available Rafiki style presets with descriptions.

    Returns:
        JSON mapping style names to {description, default}.
        Tip: compose styles with '+', e.g. kk+bcai.
    """
    styles = load_styles()
    result = {
        name: {"description": cfg.get("description", ""), "default": cfg.get("default", False)}
        for name, cfg in styles.items()
    }
    result["_tip"] = "Compose styles with '+', e.g. style='kk+bcai'"
    return _json(result)


@mcp.tool()
def rafiki_usage() -> str:
    """Return local Rafiki usage history and recent generations."""
    return _json(load_usage_log())


@mcp.tool()
def rafiki_run(args: list[str], timeout_seconds: int = 900) -> str:
    """Run a supported Rafiki CLI workflow through generate.py.

    Use this for workflows not covered by the direct tools, such as:
    ['view', 'project', '--all-runs'], ['library'], ['registry', 'search', 'logo'],
    ['--render', '/path/to/card.html'], ['canva-export', 'project'], or ['regen', '--dry-run'].

    The server never invokes a shell. It runs:
    <this python> <repo>/generate.py <args...>

    Args:
        args: generate.py arguments only; do not include python, rafiki, or generate.py.
        timeout_seconds: Seconds before the subprocess is stopped, max 3600.
    """
    return _json(_run_generate_py(args, timeout_seconds))


if __name__ == "__main__":
    mcp.run()
