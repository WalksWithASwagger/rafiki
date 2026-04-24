#!/usr/bin/env python3
"""
Rafiki MCP Server — exposes image generation as MCP tools.

Tools:
  rafiki_generate       Generate a single image (Gemini or OpenAI)
  rafiki_batch          Process an image-prompts.md file
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

# Ensure rafiki root is importable
_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))

from mcp.server.fastmcp import FastMCP
import generate as _rafiki

mcp = FastMCP(
    "rafiki",
    instructions=(
        "AI image generation via Gemini (Nano Banana) and OpenAI (gpt-image-2). "
        "Supports single images, batch prompt files, style presets, and reference images."
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
        model: Model to use. Gemini: gemini-2.5-flash-image, gemini-3-pro-image-preview.
               OpenAI: gpt-image-2, gpt-image-1, dall-e-3.
        aspect_ratio: 16:9 | 1:1 | 9:16 | linkedin | instagram | story | square.
        quality: low | medium | high — OpenAI only, ignored by Gemini.
        style: kk | hopecode | bcai | upgrade | none.
        dry_run: Preview without calling any API.

    Returns:
        JSON string with success, output_path, model, and message.
    """
    success = _capture(
        _rafiki.generate_image,
        prompt=prompt,
        output_path=output_path,
        model=model,
        aspect_ratio=aspect_ratio,
        quality=quality,
        style=style if style != "none" else None,
        dry_run=dry_run,
    )
    result = {
        "success": success,
        "output_path": output_path,
        "model": model,
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
    dry_run: bool = False,
    no_viewer: bool = False,
) -> str:
    """Process an image-prompts.md file and generate all images in the batch.

    Args:
        prompt_file: Path to the image-prompts.md file.
        output_dir: Directory for output images (default: <prompt_file_dir>/images/).
        model: Model to use for all images in the batch.
        aspect_ratio: Aspect ratio for all images.
        quality: Quality level (OpenAI only).
        style: Style preset to apply to all prompts.
        dry_run: Preview without generating any images.
        no_viewer: Skip generating viewer.html gallery.

    Returns:
        JSON string with success, counts, output_dir, viewer_path, and per-image results.
    """
    from datetime import datetime
    import re

    prompt_path = Path(prompt_file)
    if not prompt_path.exists() and not dry_run:
        return json.dumps({"success": False, "error": f"Prompt file not found: {prompt_file}"})

    prompts = _capture(_rafiki.parse_image_prompts_md, str(prompt_path)) if prompt_path.exists() else []
    out_dir = Path(output_dir) if output_dir else prompt_path.parent / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    resolved_style = None if style == "none" else style
    viewer_items: list[dict] = []
    success_count = 0

    for i, item in enumerate(prompts, 1):
        safe = re.sub(r"[^a-z0-9]+", "-", item["name"].lower()).strip("-")
        out_path = out_dir / f"{i:02d}-{safe}.png"

        ok = _capture(
            _rafiki.generate_image,
            prompt=item["prompt"],
            output_path=str(out_path),
            model=model,
            aspect_ratio=aspect_ratio,
            quality=quality,
            style=resolved_style,
            dry_run=dry_run,
        )
        if ok:
            success_count += 1
        viewer_items.append({
            "name": item["name"],
            "prompt": item["prompt"],
            "output_path": str(out_path),
        })

    viewer_path_str = ""
    if not no_viewer:
        from lib.renderers.viewer import generate_viewer
        vp = generate_viewer(
            output_dir=out_dir,
            items=viewer_items,
            title=prompt_path.stem.replace("-", " ").replace("_", " ").title(),
            run_meta={
                "model": model,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "prompt_file": str(prompt_path),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            },
        )
        viewer_path_str = str(vp)

    return json.dumps({
        "success": success_count == len(prompts),
        "mode": "batch",
        "dry_run": dry_run,
        "generated": success_count,
        "total": len(prompts),
        "output_dir": str(out_dir),
        "viewer_path": viewer_path_str,
        "model": model,
        "aspect_ratio": aspect_ratio,
        "style": style,
        "images": [
            {
                "name": it["name"],
                "output_path": it["output_path"],
                "ok": Path(it["output_path"]).exists(),
            }
            for it in viewer_items
        ],
    }, indent=2)


@mcp.tool()
def rafiki_list_styles() -> str:
    """List all available Rafiki style presets with their descriptions.

    Returns:
        JSON string mapping style names to descriptions.
    """
    styles = _rafiki.load_styles()
    result = {}
    for name, cfg in styles.items():
        result[name] = {
            "description": cfg.get("description", ""),
            "default": cfg.get("default", False),
        }
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
