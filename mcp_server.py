#!/usr/bin/env python3
"""
Rafiki MCP Server — exposes image generation as MCP tools.

Tools:
  rafiki_generate       Generate a single image (Gemini or OpenAI)
  rafiki_batch          Process an image-prompts.md file (with run isolation)
  rafiki_list_styles    List available style presets

Add to ~/.claude/settings.json (or project .claude/settings.json):

  "mcpServers": {
    "rafiki": {
      "command": "/path/to/rafiki/.venv/bin/python",
      "args": ["/path/to/rafiki/mcp_server.py"],
      "env": {
        "GOOGLE_API_KEY": "<your-key>",
        "OPENAI_API_KEY": "<your-key>"
      }
    }
  }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).parent
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
from lib.prompts import parse_image_prompts_md
from lib.styles import load_styles
from lib.models import resolve_model

mcp = FastMCP(
    "rafiki",
    instructions=(
        "AI image generation via Gemini and OpenAI. "
        "Supports single images, batch prompt files (.md), style presets, "
        "style composition (kk+bcai), model aliases (flash, gpt, pro), "
        "and parallel batch generation with run isolation."
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


@mcp.tool()
def rafiki_generate(
    prompt: str,
    output_path: str = "output.png",
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    quality: str = "high",
    style: str = "kk",
    dry_run: bool = False,
) -> str:
    """Generate a single image using Rafiki.

    Args:
        prompt: Text description of the desired image.
        output_path: Where to save the PNG (absolute or relative to cwd).
        model: Model ID or alias. Aliases: flash/nano/pro (Gemini), gpt/gpt1/dalle3 (OpenAI).
        aspect_ratio: 16:9 | 1:1 | 9:16 | linkedin | instagram | story | square.
        quality: low | medium | high — OpenAI only.
        style: kk | hopecode | bcai | upgrade | none | composed (e.g. kk+bcai).
        dry_run: Preview without calling any API.

    Returns:
        JSON string with success, output_path, model, and message.
    """
    resolved_model = resolve_model(model)
    resolved_style = style if style != "none" else None

    success = _capture(
        generate_image,
        prompt=prompt,
        output_path=output_path,
        model=resolved_model,
        aspect_ratio=aspect_ratio,
        quality=quality,
        style=resolved_style,
        dry_run=dry_run,
    )
    result: dict = {
        "success": success,
        "output_path": output_path,
        "model": resolved_model,
        "aspect_ratio": aspect_ratio,
        "style": style,
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
    quality: str = "high",
    style: str = "kk",
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
        quality: Quality level (OpenAI only).
        style: Style preset or composed spec (e.g. kk+bcai). 'none' = no style.
        workers: Parallel generation workers (1 = sequential, 4 = fast).
        dry_run: Preview without generating any images.
        no_viewer: Skip generating viewer.html gallery.

    Returns:
        JSON string with success, counts, run_dir, viewer_path, and per-image results.
    """
    prompt_path = Path(prompt_file)
    if not prompt_path.exists() and not dry_run:
        return json.dumps({"success": False, "error": f"Prompt file not found: {prompt_file}"})

    prompts = _capture(parse_image_prompts_md, str(prompt_path)) if prompt_path.exists() else []
    out_dir = Path(output_dir) if output_dir else prompt_path.parent / "images"

    resolved_model = resolve_model(model)
    resolved_style = None if style == "none" else style

    result = _capture(
        run_batch,
        prompts=prompts,
        project_dir=out_dir,
        model=resolved_model,
        aspect_ratio=aspect_ratio,
        quality=quality,
        style=resolved_style,
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
        "aspect_ratio": aspect_ratio,
        "style": style,
        "images": result.images,
    }, indent=2)


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
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
