#!/usr/bin/env python3
"""
Rafiki MCP Server — exposes the local Rafiki toolbox as MCP tools.

Tools:
  rafiki_status         Show local setup, env, and client config snippets
  rafiki_generate       Generate a single image
  rafiki_batch          Process an image-prompts.md file
  rafiki_list_styles    List available style presets
  rafiki_usage          Show local generation usage
  rafiki_registry_search Search the asset registry
  rafiki_registry_export Export the asset registry
  rafiki_media_index   Index configured multimedia roots
  rafiki_media_search  Search indexed multimedia assets
  rafiki_subjects      List indexed subject profiles
  rafiki_jobs          List local long-running job records
  rafiki_job_status    Return hardened status fields for a single job
  rafiki_media_warnings Return warnings from the last media registry index run
  rafiki_archive_health Report archive health
  rafiki_viewer_rebuild Rebuild a project viewer
  rafiki_library_rebuild Rebuild the master library viewer
  rafiki_render         Render HTML to PNG through the Node CLI
  rafiki_canva_export   Export a Canva upload bundle
  rafiki_notion_export  Dry-run or export approved images to Notion
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
from typing import Any

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
from lib.models import DEFAULT_IMAGE_MODEL, resolve_model
from lib.usage import load_usage_log

_CLI_SUBCOMMANDS = {
    "archive-health",
    "view",
    "library",
    "link-projects",
    "import",
    "approve",
    "billing",
    "canva-export",
    "clean",
    "deploy",
    "media",
    "notion-export",
    "regen",
    "registry",
    "social-expand",
    "style",
    "subjects",
    "train",
    "video",
    "floyo",
    "keyframes",
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
    "billing",
    "canva-export",
    "clean",
    "deploy",
    "notion-export",
    "regen",
    "social-expand",
    "import",
    "media",
    "subjects",
    "train",
    "video",
    "floyo",
    "keyframes",
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


def _file_url(path: Path) -> str:
    return path.resolve(strict=False).as_uri()


def _path_info(path: Path) -> dict[str, str]:
    resolved = path.resolve(strict=False)
    return {"path": str(resolved), "url": resolved.as_uri()}


def _error_payload(tool: str, error: str, **extra: Any) -> str:
    return _json({
        "success": False,
        "ok": False,
        "tool": tool,
        "error": error,
        **extra,
    })


def _run_command(
    command: list[str],
    timeout_seconds: int,
    *,
    mutating: bool,
    external: bool = False,
) -> dict:
    timeout = max(1, min(int(timeout_seconds), 3600))
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
            "ok": False,
            "timeout": True,
            "timeout_seconds": timeout,
            "command": command,
            "cwd": str(_ROOT),
            "mutating": mutating,
            "external": external,
            "stdout": _trim(e.stdout or ""),
            "stderr": _trim(e.stderr or ""),
        }

    stdout = proc.stdout or ""
    parsed_stdout = None
    try:
        parsed_stdout = json.loads(stdout)
    except json.JSONDecodeError:
        pass

    return {
        "success": proc.returncode == 0,
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "command": command,
        "cwd": str(_ROOT),
        "mutating": mutating,
        "external": external,
        "stdout": _trim(stdout),
        "stderr": _trim(proc.stderr or ""),
        "json": parsed_stdout,
    }


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
        return {"success": False, "ok": False, "error": error, "args": args}

    if args[0] in {"--render", "--render-dir"}:
        return _run_node_rafiki(args, timeout_seconds, mutating=True)

    command = [sys.executable, str(_ROOT / "generate.py"), *args]
    action = args[0]
    mutating = action in _CLI_MUTATING_SUBCOMMANDS
    if action == "billing" and len(args) > 1 and args[1] == "summary":
        mutating = False
    return _run_command(
        command,
        timeout_seconds,
        mutating=mutating,
    )


def _run_node_rafiki(
    args: list[str],
    timeout_seconds: int,
    *,
    mutating: bool,
) -> dict:
    return _run_command(
        ["node", str(_ROOT / "index.js"), *args],
        timeout_seconds,
        mutating=mutating,
    )


def _resolve_project_dir(project: str, output_root: str = "") -> Path:
    project_path = Path(project)
    if project_path.is_absolute() or project_path.exists():
        return project_path.resolve(strict=False)
    root = Path(output_root) if output_root else _ROOT / "output"
    return (root / project).resolve(strict=False)


def _default_output_root(output_root: str = "") -> Path:
    return Path(output_root).resolve(strict=False) if output_root else (_ROOT / "output").resolve(strict=False)


def _library_preview(output_root: str = "") -> dict:
    root = _default_output_root(output_root)
    if not root.is_dir():
        return {
            "success": False,
            "ok": False,
            "error": f"Output root not found: {root}",
            "output_root": str(root),
            "library_path": str(root / "library.html"),
            "library_url": _file_url(root / "library.html"),
        }

    from lib.renderers.library import _records_from_registry

    records = _records_from_registry(root)
    projects = {record.get("project", "") for record in records if record.get("project")}
    present = sum(1 for record in records if record.get("ok"))
    library_path = root / "library.html"
    return {
        "success": True,
        "ok": True,
        "output_root": str(root),
        "library_path": str(library_path),
        "library_url": _file_url(library_path),
        "project_count": len(projects),
        "image_count": len(records),
        "present_image_count": present,
        "missing_image_count": len(records) - present,
    }


def _viewer_preview(
    project: str,
    *,
    all_runs: bool,
    approved: bool,
    output_root: str = "",
) -> dict:
    project_dir = _resolve_project_dir(project, output_root)
    if not project_dir.is_dir():
        return {
            "success": False,
            "error": f"Project not found: {project_dir}",
            "project": project,
            "project_dir": str(project_dir),
        }

    if approved:
        viewer_path = project_dir / "approved" / "viewer.html"
        approved_dir = project_dir / "approved"
        image_count = len(list(approved_dir.glob("*.png"))) if approved_dir.exists() else 0
        return {
            "success": approved_dir.is_dir(),
            "error": "" if approved_dir.is_dir() else f"Approved set not found: {approved_dir}",
            "project": project,
            "project_dir": str(project_dir),
            "viewer_path": str(viewer_path),
            "viewer_url": _file_url(viewer_path),
            "run_count": 0,
            "image_count": image_count,
            "run_viewer_paths": [],
            "run_viewer_urls": [],
        }

    run_dirs = sorted(p for p in project_dir.glob("run-*") if p.is_dir())
    image_count = 0
    for run_dir in run_dirs:
        try:
            data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        image_count += len(data.get("images", []))

    viewer_path = project_dir / "viewer.html"
    run_viewer_paths = [str(run_dir / "viewer.html") for run_dir in run_dirs] if all_runs else []
    run_viewer_urls = [_file_url(run_dir / "viewer.html") for run_dir in run_dirs] if all_runs else []
    return {
        "success": True,
        "project": project,
        "project_dir": str(project_dir),
        "viewer_path": str(viewer_path),
        "viewer_url": _file_url(viewer_path),
        "run_count": len(run_dirs),
        "image_count": image_count,
        "run_viewer_paths": run_viewer_paths,
        "run_viewer_urls": run_viewer_urls,
    }


def _render_targets(html_path: str = "", html_dir: str = "") -> tuple[list[Path], str]:
    if bool(html_path) == bool(html_dir):
        return [], "Pass exactly one of html_path or html_dir"

    if html_path:
        path = Path(html_path)
        if not path.exists():
            return [], f"HTML file not found: {path}"
        return [path.resolve()], ""

    directory = Path(html_dir)
    if not directory.is_dir():
        return [], f"HTML directory not found: {directory}"
    files = sorted(path.resolve() for path in directory.iterdir() if path.suffix == ".html")
    if not files:
        return [], f"No HTML files found in {directory}"
    return files, ""


def _canva_preview(
    project: str,
    *,
    output_dir: str = "",
    no_zip: bool = False,
    output_root: str = "",
) -> dict:
    from lib.exporters import canva

    root = Path(output_root) if output_root else canva.DEFAULT_OUTPUT_ROOT
    project_dir = root / project
    if not project_dir.is_dir():
        return {"success": False, "error": f"Project not found: {project_dir}"}

    try:
        source = canva._resolve_source(project_dir)
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}

    images = sorted(source.glob("*.png"))
    export_dir = Path(output_dir) if output_dir else project_dir / "canva-export"
    result_path = export_dir if no_zip else export_dir.with_suffix(".zip")
    return {
        "success": True,
        "project": project,
        "project_dir": str(project_dir.resolve(strict=False)),
        "source_dir": str(source.resolve(strict=False)),
        "output_dir": str(export_dir.resolve(strict=False)),
        "result_path": str(result_path.resolve(strict=False)),
        "result_url": _file_url(result_path),
        "count": len(images),
        "image_count": len(images),
        "zip": not no_zip,
    }


@mcp.tool()
def rafiki_status() -> str:
    """Report the local Rafiki MCP setup without exposing secret values."""
    python_bin = sys.executable
    server_path = str(_ROOT / "mcp_server.py")
    result = {
        "success": True,
        "ok": True,
        "tool": "rafiki_status",
        "repo_root": str(_ROOT),
        "python": python_bin,
        "mcp_server": server_path,
        "env": {
            "GOOGLE_API_KEY": bool(os.environ.get("GOOGLE_API_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
            "REPLICATE_API_TOKEN": bool(os.environ.get("REPLICATE_API_TOKEN")),
            "NOTION_API_KEY": bool(os.environ.get("NOTION_API_KEY")),
            "NOTION_DATABASE_ID": bool(os.environ.get("NOTION_DATABASE_ID")),
        },
        "common_tools": [
            "rafiki_generate",
            "rafiki_batch",
            "rafiki_list_styles",
            "rafiki_usage",
            "rafiki_registry_search",
            "rafiki_registry_export",
            "rafiki_media_index",
            "rafiki_media_search",
            "rafiki_subjects",
            "rafiki_jobs",
            "rafiki_job_status",
            "rafiki_media_warnings",
            "rafiki_train_lora",
            "rafiki_video_generate",
            "rafiki_floyo_generate",
            "rafiki_keyframes_generate",
            "rafiki_style_anchors",
            "rafiki_archive_health",
            "rafiki_viewer_rebuild",
            "rafiki_library_rebuild",
            "rafiki_render",
            "rafiki_canva_export",
            "rafiki_notion_export",
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
    model: str = DEFAULT_IMAGE_MODEL,
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str = "kk",
    reference_image: str = "",
    global_reference_images: list[str] | None = None,
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
        global_reference_images: Additional reference image paths reused for this generation.
        reference_role: style | brand | mockup.
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
        reference_images=global_reference_images,
        reference_role=reference_role,
        composition_references=composition_references,
        dry_run=dry_run,
    )
    result: dict = {
        "success": success,
        "ok": success,
        "tool": "rafiki_generate",
        "output_path": output_path,
        "output_url": _file_url(Path(output_path)),
        "model": resolved_model,
        "aspect_ratio": resolved_aspect_ratio,
        "resolution": resolution,
        "style": style,
        "reference_image": reference_image,
        "global_reference_images": global_reference_images or [],
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
    model: str = DEFAULT_IMAGE_MODEL,
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str = "kk",
    reference_image: str = "",
    reference_images: list[str] | None = None,
    global_reference_images: list[str] | None = None,
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
        global_reference_images: Additional reference image paths reused for every prompt.
        reference_role: style | brand | mockup.
        composition_references: Extra reference paths for mockup composition.
        workers: Parallel generation workers (1 = sequential, 4 = fast).
        dry_run: Preview without generating any images.
        no_viewer: Skip generating viewer.html gallery.

    Returns:
        JSON string with success, counts, run_dir, viewer_path, and per-image results.
    """
    prompt_path = Path(prompt_file)
    if not prompt_path.exists() and not dry_run:
        return _error_payload(
            "rafiki_batch",
            f"Prompt file not found: {prompt_file}",
            mutating=False,
            external=False,
            dry_run=dry_run,
        )

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
        return _error_payload(
            "rafiki_batch",
            str(e),
            mutating=False,
            external=False,
            dry_run=dry_run,
        )

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
        global_reference_images=global_reference_images,
        reference_role=reference_role,
        composition_references=composition_references,
        workers=workers,
        dry_run=dry_run,
        generate_viewer_html=not no_viewer,
        prompt_file=str(prompt_path),
        invocation_source="mcp",
    )

    return json.dumps({
        "success": result.success,
        "ok": result.success,
        "tool": "rafiki_batch",
        "mode": "batch",
        "dry_run": dry_run,
        "generated": result.success_count,
        "total": result.total,
        "project_dir": str(result.project_dir),
        "run_dir": str(result.run_dir),
        "run_id": result.run_id,
        "viewer_path": result.viewer_path,
        "viewer_url": _file_url(Path(result.viewer_path)) if result.viewer_path else "",
        "model": resolved_model,
        "aspect_ratio": resolved_aspect_ratio,
        "resolution": resolution,
        "style": style,
        "global_reference_images": global_reference_images or [],
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
        "success": True,
        "ok": True,
        "tool": "rafiki_list_styles",
        "count": len(styles),
        "styles": {
            name: {
                "description": cfg.get("description", ""),
                "default": cfg.get("default", False),
            }
            for name, cfg in styles.items()
        },
        "_tip": "Compose styles with '+', e.g. style='kk+bcai'",
    }
    return _json(result)


@mcp.tool()
def rafiki_usage() -> str:
    """Return local Rafiki usage history and recent generations."""
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_usage",
        **load_usage_log(),
    })


@mcp.tool()
def rafiki_registry_search(query: str, limit: int = 20) -> str:
    """Search the persisted Rafiki asset registry.

    Args:
        query: Case-insensitive substring matched against title, caption, and tags.
        limit: Maximum number of results to return, capped at 100.
    """
    from lib import registry

    safe_limit = max(1, min(int(limit), 100))
    results = [entry.to_dict() for entry in registry.search(query)[:safe_limit]]
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_registry_search",
        "query": query,
        "limit": safe_limit,
        "count": len(results),
        "mutating": False,
        "external": False,
        "results": results,
    })


@mcp.tool()
def rafiki_registry_export(format: str = "csv", dry_run: bool = False) -> str:
    """Export the persisted asset registry to CSV or JSON.

    Args:
        format: csv | json.
        dry_run: Preview the export path and count without writing files.
    """
    from lib import registry

    fmt = format.lower()
    if fmt not in {"csv", "json"}:
        return _error_payload(
            "rafiki_registry_export",
            "format must be 'csv' or 'json'",
            format=format,
            dry_run=dry_run,
            mutating=False,
            external=False,
        )

    entries = registry._load_registry()
    path = registry.REGISTRY_CSV if fmt == "csv" else registry.REGISTRY_JSON
    if dry_run:
        return _json({
            "success": True,
            "ok": True,
            "tool": "rafiki_registry_export",
            "format": fmt,
            "dry_run": True,
            "mutating": False,
            "external": False,
            "count": len(entries),
            **_path_info(path),
        })

    try:
        exported = registry.export(format=fmt)
    except ValueError as e:
        return _error_payload(
            "rafiki_registry_export",
            str(e),
            format=format,
            dry_run=dry_run,
            mutating=False,
            external=False,
        )
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_registry_export",
        "format": fmt,
        "dry_run": False,
        "mutating": True,
        "external": False,
        "count": len(entries),
        **_path_info(exported),
    })


@mcp.tool()
def rafiki_media_index(
    root: str = "",
    key: str = "alex-samuel",
    importer: str = "alex-samuel",
    dry_run: bool = True,
) -> str:
    """Index configured multimedia roots or one explicit local root."""
    from lib import media_registry
    from lib.media_roots import MediaRoot

    if importer not in {"alex-samuel", "generic"}:
        return _error_payload("rafiki_media_index", "importer must be alex-samuel or generic")
    roots = None
    if root:
        roots = {key: MediaRoot(key=key, path=Path(root).expanduser(), importer=importer)}
    payload = media_registry.index(roots=roots, write=not dry_run)
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_media_index",
        "dry_run": dry_run,
        "mutating": not dry_run,
        "external": False,
        "registry_path": str(media_registry.MEDIA_REGISTRY_JSON),
        "registry_url": _file_url(media_registry.MEDIA_REGISTRY_JSON),
        **payload,
    })


@mcp.tool()
def rafiki_media_search(query: str = "", kind: str = "", collection: str = "", limit: int = 50) -> str:
    """Search the multimedia registry for images, videos, audio, styles, and manifests."""
    from lib import media_registry

    safe_limit = max(1, min(int(limit), 200))
    results = [entry.to_dict() for entry in media_registry.search(query, kind=kind, collection=collection)[:safe_limit]]
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_media_search",
        "query": query,
        "kind": kind,
        "collection": collection,
        "limit": safe_limit,
        "count": len(results),
        "mutating": False,
        "external": False,
        "results": results,
    })


@mcp.tool()
def rafiki_subjects(subject: str = "") -> str:
    """List indexed subject profiles, or return one subject when subject is passed."""
    from lib import media_registry

    profiles = [profile.to_dict() for profile in media_registry.subjects()]
    if subject:
        profiles = [profile for profile in profiles if profile.get("key") == subject]
    return _json({
        "success": bool(profiles) or not subject,
        "ok": bool(profiles) or not subject,
        "tool": "rafiki_subjects",
        "subject": subject,
        "count": len(profiles),
        "mutating": False,
        "external": False,
        "subjects": profiles,
    })


@mcp.tool()
def rafiki_jobs() -> str:
    """List local dry-run/executed job records stored under data/jobs."""
    from lib.jobs import list_jobs

    jobs = list_jobs()
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_jobs",
        "count": len(jobs),
        "mutating": False,
        "external": False,
        "jobs": jobs,
    })


@mcp.tool()
def rafiki_train_lora(
    subject: str,
    input_images_url: str = "",
    execute: bool = False,
    output_root: str = "",
) -> str:
    """Plan or launch a Replicate FLUX LoRA training job. Defaults to dry-run."""
    from lib.training import plan_lora_training

    result = plan_lora_training(
        subject=subject,
        input_images_url=input_images_url,
        execute=execute,
        output_root=Path(output_root) if output_root else None,
    )
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_train_lora",
        "mutating": True,
        "external": execute,
        **result,
    })


@mcp.tool()
def rafiki_video_generate(
    storyboard: str,
    model: str = "wan-video/wan2.1-with-lora",
    execute: bool = False,
    output_root: str = "",
) -> str:
    """Plan or launch a storyboard video generation job. Defaults to dry-run."""
    from lib.video_jobs import plan_video_generation

    result = plan_video_generation(
        storyboard_path=Path(storyboard),
        model=model,
        execute=execute,
        output_root=Path(output_root) if output_root else None,
    )
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_video_generate",
        "mutating": True,
        "external": execute,
        **result,
    })


@mcp.tool()
def rafiki_floyo_generate(
    workflow: str = "wan22_endframe",
    start_image: str = "",
    end_image: str = "",
    prompt: str = "",
    project: str = "floyo",
    execute: bool = False,
    output_root: str = "",
) -> str:
    """Plan or launch a Floyo (flowyo.ai) video workflow. Defaults to dry-run.

    The default workflow `wan22_endframe` morphs start_image -> end_image into a
    short silent clip. On execute, this submits only (does not block-poll); use
    the CLI `generate.py floyo generate --execute` to also wait and download.
    """
    from lib.floyo_jobs import plan_floyo_generation

    inputs = {
        k: v
        for k, v in (("start_image", start_image), ("end_image", end_image), ("prompt", prompt))
        if v
    }
    result = plan_floyo_generation(
        workflow=workflow,
        inputs=inputs,
        project=project,
        execute=execute,
        wait=False,
        output_root=Path(output_root) if output_root else None,
    )
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_floyo_generate",
        "mutating": True,
        "external": execute,
        **result,
    })


@mcp.tool()
def rafiki_keyframes_generate(
    keyframes: str = "keyframes.json",
    beat: str = "",
    engine: str = "flux1-lora",
    num_outputs: int = 4,
    execute: bool = False,
    output_root: str = "",
) -> str:
    """Generate keyframe stills from a keyframes.json beat. Defaults to dry-run.

    Uses Replicate (FLUX + the trained character image LoRA); FloTime can't load
    FLUX image LoRAs, so stills run on Replicate while Floyo handles video. On
    execute this submits only (does not block-poll); use the CLI to wait + download.
    """
    from lib.keyframe_jobs import plan_keyframe_generation

    result = plan_keyframe_generation(
        keyframes_path=Path(keyframes),
        beat=beat,
        engine=engine,
        num_outputs=num_outputs,
        execute=execute,
        wait=False,
        output_root=Path(output_root) if output_root else None,
    )
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_keyframes_generate",
        "mutating": True,
        "external": execute,
        **result,
    })


@mcp.tool()
def rafiki_style_anchors(source: str, name: str = "") -> str:
    """Read or derive a normalized style profile from a style-anchor JSON file."""
    from lib.style_anchors import style_profile_from_source

    profile = style_profile_from_source(Path(source), name=name)
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_style_anchors",
        "mutating": False,
        "external": False,
        "style": profile.to_dict(),
    })


@mcp.tool()
def rafiki_archive_health(
    output_root: str = "",
    cleanup_report: bool = False,
) -> str:
    """Report output archive health without mutating generated files.

    Args:
        output_root: Optional output root; defaults to repo output/.
        cleanup_report: Include the full conservative cleanup report.
    """
    from lib.archive_health import archive_health_report

    root = _default_output_root(output_root)
    report = archive_health_report(root)
    summary = report.get("summary", {})
    payload = {
        "success": bool(report.get("ok", False)),
        "ok": bool(report.get("ok", False)),
        "tool": "rafiki_archive_health",
        "dry_run": True,
        "mutating": False,
        "external": False,
        "output_root": str(root),
        "project_count": summary.get("projects", 0),
        "run_count": summary.get("runs", 0),
        "manifest_image_count": summary.get("manifest_images", 0),
        "present_image_count": summary.get("present_images", 0),
        "missing_image_count": summary.get("missing_images", 0),
        "malformed_run_count": len(report.get("malformed_runs", [])),
        "duplicate_filename_group_count": summary.get("duplicate_filename_groups", 0),
        "orphaned_sidecar_count": (
            summary.get("orphaned_ratings", 0)
            + summary.get("orphaned_feedback", 0)
            + summary.get("orphaned_evaluations", 0)
            + summary.get("orphaned_metadata", 0)
        ),
        "summary": summary,
        "errors": {
            "missing_images": report.get("missing_images", []),
            "malformed_runs": report.get("malformed_runs", []),
        },
        "recommendations": report.get("recommendations", []),
    }
    if cleanup_report:
        payload["cleanup_report"] = report.get("cleanup_report", {})
    return _json(payload)


@mcp.tool()
def rafiki_viewer_rebuild(
    project: str,
    all_runs: bool = False,
    approved: bool = False,
    output_root: str = "",
    dry_run: bool = False,
    timeout_seconds: int = 300,
) -> str:
    """Rebuild viewer.html for a project without regenerating images.

    Args:
        project: Project path, or project name under output_root/output/.
        all_runs: Also rebuild each run-*/viewer.html.
        approved: Build output/<project>/approved/viewer.html instead.
        output_root: Optional root for project names. Absolute project paths ignore this.
        dry_run: Preview paths and counts without writing viewer files.
        timeout_seconds: Seconds before the CLI subprocess is stopped.
    """
    preview = _viewer_preview(
        project,
        all_runs=all_runs,
        approved=approved,
        output_root=output_root,
    )
    base = {
        "tool": "rafiki_viewer_rebuild",
        "dry_run": dry_run,
        "mutating": not dry_run,
        "external": False,
        **preview,
    }
    base["ok"] = bool(base.get("success"))
    if dry_run or not preview.get("success"):
        return _json(base)

    args = ["view", str(preview["project_dir"])]
    if all_runs:
        args.append("--all-runs")
    if approved:
        args.append("--approved")
    run = _run_generate_py(args, timeout_seconds)
    return _json({
        **base,
        **run,
        "tool": "rafiki_viewer_rebuild",
        "mutating": True,
        "external": False,
        "ok": bool(run.get("success")),
    })


@mcp.tool()
def rafiki_render(
    html_path: str = "",
    html_dir: str = "",
    dry_run: bool = False,
    timeout_seconds: int = 900,
) -> str:
    """Render one HTML file or a directory of HTML files to PNG.

    Args:
        html_path: Single HTML file to render.
        html_dir: Directory whose top-level .html files should be rendered.
        dry_run: Preview output PNG paths without launching Chrome.
        timeout_seconds: Seconds before the Node subprocess is stopped.
    """
    targets, error = _render_targets(html_path, html_dir)
    if error:
        return _error_payload(
            "rafiki_render",
            error,
            html_path=html_path,
            html_dir=html_dir,
            dry_run=dry_run,
            mutating=False,
            external=False,
        )

    output_paths = [target.with_suffix(".png") for target in targets]
    args = ["--render", str(targets[0])] if html_path else ["--render-dir", html_dir]
    base = {
        "success": True,
        "ok": True,
        "tool": "rafiki_render",
        "dry_run": dry_run,
        "mutating": not dry_run,
        "external": False,
        "count": len(targets),
        "html_paths": [str(path) for path in targets],
        "output_paths": [str(path.resolve(strict=False)) for path in output_paths],
        "output_urls": [_file_url(path) for path in output_paths],
        "command": ["node", str(_ROOT / "index.js"), *args],
    }
    if dry_run:
        return _json(base)

    run = _run_node_rafiki(args, timeout_seconds, mutating=True)
    return _json({**base, **run, "tool": "rafiki_render", "ok": bool(run.get("success"))})


@mcp.tool()
def rafiki_library_rebuild(
    output_root: str = "",
    dry_run: bool = False,
    timeout_seconds: int = 300,
) -> str:
    """Rebuild output/library.html without regenerating images.

    Args:
        output_root: Optional output root; defaults to repo output/.
        dry_run: Preview path and counts without writing library.html.
        timeout_seconds: Seconds before the CLI subprocess is stopped.
    """
    preview = _library_preview(output_root)
    base = {
        "tool": "rafiki_library_rebuild",
        "dry_run": dry_run,
        "mutating": not dry_run,
        "external": False,
        **preview,
    }
    if dry_run or not preview.get("success"):
        return _json(base)

    args = ["library", "--output-dir", preview["output_root"]]
    run = _run_generate_py(args, timeout_seconds)
    return _json({
        **base,
        **run,
        "tool": "rafiki_library_rebuild",
        "mutating": True,
        "external": False,
        "ok": bool(run.get("success")),
    })


@mcp.tool()
def rafiki_canva_export(
    project: str,
    output_dir: str = "",
    no_zip: bool = False,
    output_root: str = "",
    dry_run: bool = False,
) -> str:
    """Export approved/latest-run images and assets.csv for Canva bulk upload.

    Args:
        project: Project name under output_root/output/.
        output_dir: Optional export directory.
        no_zip: Return the export directory instead of a .zip bundle.
        output_root: Optional output root for tests or alternate workspaces.
        dry_run: Preview source/output paths and image count without writing files.
    """
    preview = _canva_preview(
        project,
        output_dir=output_dir,
        no_zip=no_zip,
        output_root=output_root,
    )
    base = {
        "tool": "rafiki_canva_export",
        "dry_run": dry_run,
        "mutating": not dry_run,
        "external": False,
        **preview,
    }
    base["ok"] = bool(base.get("success"))
    if dry_run or not preview.get("success"):
        return _json(base)

    from lib.exporters import canva

    root = Path(output_root) if output_root else canva.DEFAULT_OUTPUT_ROOT
    try:
        result = _capture(
            canva.export,
            project,
            output_dir=Path(output_dir) if output_dir else None,
            zip=not no_zip,
            output_root=root,
        )
    except FileNotFoundError as e:
        return _error_payload(
            "rafiki_canva_export",
            str(e),
            project=project,
            dry_run=dry_run,
            mutating=False,
            external=False,
        )

    return _json({
        **base,
        "success": True,
        "ok": True,
        "result_path": str(result.resolve(strict=False)),
        "result_url": _file_url(result),
    })


@mcp.tool()
def rafiki_notion_export(
    project: str,
    database_id: str = "",
    output_root: str = "",
    dry_run: bool = True,
    force: bool = False,
) -> str:
    """Dry-run or export approved/latest-run images to a Notion database.

    Args:
        project: Project name under output_root/output/, or an absolute path.
        database_id: Optional Notion database id; falls back to env for real exports.
        output_root: Optional output root for project names.
        dry_run: Skip Notion API calls and local export-log writes.
        force: Re-export images already recorded in the local export log.
    """
    from lib.exporters import notion

    try:
        result = _capture(
            notion.export,
            project,
            database_id=database_id or None,
            output_root=Path(output_root) if output_root else None,
            dry_run=dry_run,
            force=force,
        )
    except notion.NotionExportError as e:
        return _error_payload(
            "rafiki_notion_export",
            str(e),
            project=project,
            dry_run=dry_run,
            force=force,
            mutating=False,
            external=True,
        )

    return _json({
        "success": not result["errors"],
        "ok": not result["errors"],
        "tool": "rafiki_notion_export",
        "project": project,
        "database_id": database_id or "",
        "dry_run": dry_run,
        "force": force,
        "mutating": not dry_run,
        "external": True,
        **result,
    })


@mcp.tool()
def rafiki_media_warnings(registry_path: str = "") -> str:
    """Return warnings collected during the last multimedia registry index run.

    Reads the persisted media-registry.json without triggering a re-index.
    Returns an empty warnings list if the registry has not been built yet.

    Args:
        registry_path: Optional absolute path to a media-registry.json file.
            Defaults to data/media-registry.json in the repo root.

    Returns:
        JSON with ok, warning_count, warnings (list of strings), indexed_at,
        and registry_path. Always mutating: false, external: false.
    """
    from lib import media_registry

    reg_path = Path(registry_path).expanduser() if registry_path else media_registry.MEDIA_REGISTRY_JSON
    data = media_registry.load_registry(reg_path, rebuild_if_missing=False)
    warnings_list = [str(w) for w in (data.get("warnings") or []) if w]
    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_media_warnings",
        "mutating": False,
        "external": False,
        "registry_path": str(reg_path),
        "registry_url": _file_url(reg_path),
        "indexed_at": data.get("indexed_at", ""),
        "count": len(warnings_list),
        "warning_count": len(warnings_list),
        "warnings": warnings_list,
    })


@mcp.tool()
def rafiki_job_status(job_id: str) -> str:
    """Return hardened status fields for a single local job record.

    Reads the job file under data/jobs/ and returns stable typed fields
    including status, polling_status, provider, kind, cost_estimate, and
    explicit safety flags. Never calls any provider or mutates local state.

    Args:
        job_id: Job ID as returned by rafiki_jobs, rafiki_train_lora, or
            rafiki_video_generate.

    Returns:
        JSON with ok, job_id, status, polling_status, error, provider, kind,
        created_at, updated_at, cost_estimate, mutating: false, external: false,
        and the full raw job dict under 'job'.
    """
    from lib.jobs import load_job

    if not job_id or not job_id.strip():
        return _error_payload(
            "rafiki_job_status",
            "job_id is required",
            mutating=False,
            external=False,
        )

    record = load_job(job_id.strip())
    if record is None:
        return _error_payload(
            "rafiki_job_status",
            f"job not found: {job_id}",
            job_id=job_id,
            mutating=False,
            external=False,
        )

    return _json({
        "success": True,
        "ok": True,
        "tool": "rafiki_job_status",
        "mutating": False,
        "external": False,
        "job_id": str(record.get("id") or job_id),
        "status": str(record.get("status") or ""),
        "polling_status": str(record.get("polling_status") or ""),
        "error": str(record.get("error") or ""),
        "provider": str(record.get("provider") or ""),
        "kind": str(record.get("kind") or ""),
        "created_at": str(record.get("created_at") or ""),
        "updated_at": str(record.get("updated_at") or ""),
        "cost_estimate": record.get("cost_estimate") or {},
        "job": record,
    })


@mcp.tool()
def rafiki_run(args: list[str], timeout_seconds: int = 900) -> str:
    """Run a supported Rafiki CLI workflow through generate.py.

    Use this for workflows not covered by the direct tools, such as:
    ['library'], ['archive-health', '--json'], ['approve', 'project'],
    ['billing', 'summary', '--json'], ['clean', 'project', '--dry-run'],
    ['social-expand', 'project', '--dry-run'], or ['regen', '--dry-run'].
    Prefer the typed wrappers for registry, viewer rebuild, render, Canva export,
    and Notion export workflows.

    The server never invokes a shell. Python workflows run:
    <this python> <repo>/generate.py <args...>
    Render-only bridge calls run:
    node <repo>/index.js <args...>

    Args:
        args: generate.py arguments only; do not include python, rafiki, or generate.py.
        timeout_seconds: Seconds before the subprocess is stopped, max 3600.
    """
    result = _run_generate_py(args, timeout_seconds)
    success = bool(result.get("success", False))
    normalized = {
        "success": success,
        "ok": bool(result.get("ok", success)),
        "tool": "rafiki_run",
        "exit_code": result.get("exit_code"),
        "timeout": bool(result.get("timeout", False)),
        "error": result.get("error"),
        "mutating": bool(result.get("mutating", False)),
        "external": bool(result.get("external", False)),
        "command": result.get("command", []),
        "cwd": result.get("cwd", str(_ROOT)),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "json": result.get("json"),
        "args": result.get("args", args),
    }
    return _json(normalized)


if __name__ == "__main__":
    mcp.run()
