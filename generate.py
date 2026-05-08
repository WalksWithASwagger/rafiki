#!/usr/bin/env python3
"""
Rafiki — multi-provider image generator

Providers:
  Gemini (Google)  — gemini-2.5-flash-image, gemini-3-pro-image-preview
  OpenAI           — gpt-image-2, gpt-image-1, dall-e-3, dall-e-2

Model aliases: flash, nano, pro (Gemini) · gpt, gpt1, dalle3, dalle2 (OpenAI)
Style composition: --style kk+bcai stacks both style suffixes

Usage:
    python generate.py --prompt "A creative professional..." --output image.png
    python generate.py --prompt "..." -m gpt --quality high
    python generate.py -f image-prompts.md -d ./images/ --workers 4
    python generate.py --list-styles

    # Rebuild viewer from actual files on disk (no re-generation):
    python generate.py view <project>
    python generate.py view <project> --all-runs
    python generate.py view <project> --approved

    # Curate approved set + clean old runs (see docs/ARCHIVE.md):
    python generate.py approve <project> [--run <run-id>]
    python generate.py clean <project> [--keep-approved] [--older-than 30d] [--dry-run]

    # Start the generative portal with persistent ratings + search:
    python generate.py serve [--port 7433] [--open]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Auto-load .env from repo root so API keys work without `source .env`
def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    import os
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

_load_dotenv(Path(__file__).parent / ".env")

from lib.core import generate_image
from lib.models import resolve_model, ALIASES
from lib.prompts import parse_image_prompts_md, ASPECT_RATIOS
from lib.styles import load_styles, get_default_style
from lib.usage import load_usage_log
from lib.batch import run_batch

# Re-export for MCP server and other importers that do `import generate`
__all__ = [
    "generate_image",
    "parse_image_prompts_md",
    "load_styles",
    "get_default_style",
]


def _cmd_library(argv: list[str]) -> None:
    """Build (or rebuild) the master library.html from all runs in output/."""
    p = argparse.ArgumentParser(
        prog="generate.py library",
        description="Build output/library.html — all Rafiki images in one page.",
    )
    p.add_argument(
        "--output-dir", "-d", default=None,
        help="Root output directory (default: output/ next to generate.py)",
    )
    p.add_argument("--open", action="store_true", help="Open in browser after building")
    args = p.parse_args(argv)

    output_root = Path(args.output_dir) if args.output_dir else Path(__file__).parent / "output"
    if not output_root.exists():
        print(f"Error: output dir not found: {output_root}")
        sys.exit(1)

    from lib.renderers.library import generate_library_viewer, load_extra_outputs, _scan_root
    lp = generate_library_viewer(output_root, open_browser=args.open)

    # Count across output_root + extra_roots (mirrors library generator logic)
    seen: set[str] = set()
    all_records: list[dict] = []
    extra_roots = load_extra_outputs()
    for project_name, extra_root in extra_roots.items():
        if extra_root.exists():
            for rec in _scan_root(extra_root, project_name, project_name):
                seen.add(rec["file"])
                all_records.append(rec)
    for proj_dir in sorted(output_root.iterdir()):
        if not proj_dir.is_dir():
            continue
        for rec in _scan_root(proj_dir, proj_dir.name, proj_dir.name):
            if rec["file"] not in seen:
                seen.add(rec["file"])
                all_records.append(rec)

    total = len(all_records)
    ok = sum(1 for r in all_records if r["ok"])
    projects = {r["project"] for r in all_records}
    print(f"Library: {lp}")
    print(f"Images:  {ok}/{total} present  ({len(projects)} projects)")


def _cmd_view(argv: list[str]) -> None:
    """Rebuild viewer HTML for a project from actual files on disk."""
    p = argparse.ArgumentParser(
        prog="generate.py view",
        description=(
            "Rebuild viewer.html from actual files on disk — no re-generation.\n"
            "Re-verifies which images exist and updates ok/error state."
        ),
    )
    p.add_argument("project", help="Project dir path, or name under output/")
    p.add_argument(
        "--all-runs", action="store_true",
        help="Also rebuild each run's individual viewer.html",
    )
    p.add_argument(
        "--approved", action="store_true",
        help="Build viewer from output/<project>/approved/ instead of run-*/",
    )
    args = p.parse_args(argv)

    if args.approved:
        from lib.archive import build_approved_viewer
        vp = build_approved_viewer(args.project)
        print(f"Approved viewer: {vp}")
        return

    project_dir = Path(args.project)
    if not project_dir.exists():
        candidate = Path(__file__).parent / "output" / args.project
        if candidate.exists():
            project_dir = candidate
        else:
            print(f"Error: project not found: {args.project!r}")
            print(f"  Tried: {project_dir}")
            print(f"  Tried: {candidate}")
            sys.exit(1)

    from lib.renderers.viewer import generate_comparison_viewer, generate_viewer

    if args.all_runs:
        for run_dir in sorted(project_dir.glob("run-*/")):
            run_json = run_dir / "run.json"
            if not run_json.exists():
                continue
            try:
                data = json.loads(run_json.read_text(encoding="utf-8"))
                items = [
                    {
                        "name": img["name"],
                        "prompt": img.get("prompt", ""),
                        "output_path": str(run_dir / img["file"]),
                        "error": img.get("error", ""),
                    }
                    for img in data.get("images", [])
                ]
                title = (
                    Path(data["prompt_file"]).stem.replace("-", " ").replace("_", " ").title()
                    if data.get("prompt_file")
                    else project_dir.name.replace("-", " ").title()
                )
                generate_viewer(output_dir=run_dir, items=items, title=title, run_meta=data)
                print(f"  Rebuilt {run_dir.name}/viewer.html")
            except Exception as e:
                print(f"  Error rebuilding {run_dir.name}: {e}", file=sys.stderr)

    vp = generate_comparison_viewer(project_dir)
    print(f"Viewer:  {vp}")

    # Print a quick on-disk summary
    run_json_paths = sorted(project_dir.glob("run-*/run.json"))
    total_images = present_images = 0
    for rjp in run_json_paths:
        try:
            data = json.loads(rjp.read_text(encoding="utf-8"))
            for img in data.get("images", []):
                total_images += 1
                if (rjp.parent / img["file"]).exists():
                    present_images += 1
        except Exception:
            pass
    print(
        f"Summary: {len(run_json_paths)} run(s), "
        f"{present_images}/{total_images} images on disk"
    )


def _cmd_link_projects(argv: list[str]) -> None:
    """Recreate output/ symlinks from configured extra outputs (for file:// mode)."""
    p = argparse.ArgumentParser(
        prog="generate.py link-projects",
        description=(
            "Create/refresh output/ symlinks for each project in "
            "config/extra-outputs.json or config/extra-outputs.local.json so "
            "the viewer works when opened as a file."
        ),
    )
    p.add_argument("--output-dir", "-d", default=None,
                   help="Root output directory (default: output/)")
    args = p.parse_args(argv)

    from lib.extra_outputs import extra_outputs_config_paths, load_extra_outputs

    output_root = Path(args.output_dir) if args.output_dir else Path(__file__).parent / "output"
    extra_roots = load_extra_outputs()
    if not extra_roots:
        config_names = ", ".join(path.name for path in extra_outputs_config_paths())
        print(f"No extra output mappings found in {config_names} — nothing to link.")
        return

    output_root.mkdir(parents=True, exist_ok=True)
    for name, real in extra_roots.items():
        link = output_root / name
        if not real.exists():
            print(f"  skip {name}: source not found ({real})")
            continue
        if link.is_symlink():
            if link.resolve() == real.resolve():
                print(f"  ok   {name} (already linked)")
                continue
            link.unlink()
        elif link.exists():
            print(f"  skip {name}: {link} exists as real dir — remove it manually to re-link")
            continue
        link.symlink_to(real)
        print(f"  link {name} → {real}")


def _cmd_canva_export(argv: list[str]) -> None:
    """Export approved/latest-run images + assets.csv for Canva bulk upload."""
    p = argparse.ArgumentParser(
        prog="generate.py canva-export",
        description=(
            "Bundle a project's images and a metadata CSV for Canva.\n"
            "Source: output/<project>/approved/ if present, else latest run-*/."
        ),
    )
    p.add_argument("project", help="Project name under output/ (e.g. rap-all-weeks)")
    p.add_argument("--output", "-o", default=None,
                   help="Export dir (default: output/<project>/canva-export/)")
    p.add_argument("--no-zip", action="store_true",
                   help="Skip zipping the bundle (return the dir instead)")
    args = p.parse_args(argv)

    from lib.exporters.canva import export

    out = Path(args.output) if args.output else None
    result = export(project=args.project, output_dir=out, zip=not args.no_zip)
    print(f"Canva export: {result}")


def _cmd_regen(argv: list[str]) -> None:
    """Run scheduled regeneration jobs from config/scheduled-regen.json."""
    p = argparse.ArgumentParser(
        prog="generate.py regen",
        description=(
            "Run scheduled regeneration jobs from config/scheduled-regen.json. "
            "Without flags, runs any job whose latest run-*/ is older than its interval_days."
        ),
    )
    p.add_argument("--dry-run", action="store_true",
                   help="List jobs and last-run ages; don't run anything")
    p.add_argument("--name", default=None,
                   help="Run a specific job by name regardless of schedule")
    p.add_argument("--yes", "-y", action="store_true",
                   help="Skip the confirmation prompt before running due jobs")
    p.add_argument("--config", default=None,
                   help="Override config path (default: config/scheduled-regen.json)")
    args = p.parse_args(argv)

    repo_root = Path(__file__).parent
    config_path = Path(args.config) if args.config else repo_root / "config" / "scheduled-regen.json"

    from lib.regen import load_config, due_jobs, latest_run_age_days, run_job

    try:
        jobs = load_config(config_path)
    except FileNotFoundError:
        print(f"No config at {config_path}.")
        print("Copy config/scheduled-regen.json.example to get started.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    if args.dry_run:
        due = {j.name for j in due_jobs(jobs, repo_root=repo_root)}
        print(f"Scheduled regen jobs ({len(jobs)} configured):")
        for job in jobs:
            age = latest_run_age_days((repo_root / job.output_dir).resolve())
            age_str = f"{age}d ago" if age is not None else "never run"
            mark = "DUE" if job.name in due else "ok "
            print(f"  [{mark}] {job.name:40s} interval={job.interval_days}d  last={age_str}")
        return

    if args.name:
        targets = [j for j in jobs if j.name == args.name]
        if not targets:
            print(f"Error: no job named {args.name!r}")
            sys.exit(1)
    else:
        targets = due_jobs(jobs, repo_root=repo_root)
        if not targets:
            print("No jobs are due.")
            return
        print(f"{len(targets)} job(s) due:")
        for j in targets:
            print(f"  - {j.name}")
        if not args.yes:
            try:
                resp = input("Run them? [y/N] ").strip().lower()
            except EOFError:
                resp = ""
            if resp != "y":
                print("Aborted.")
                return

    for job in targets:
        print(f"\n=== Regenerating: {job.name} ===")
        summary = run_job(job, repo_root=repo_root)
        print(f"  status: {summary['status']}")
        if job.notify:
            print(f"  [notify] {job.name} → {summary['status']} (output: {job.output_dir})")


def _cmd_registry(argv: list[str]) -> None:
    """Asset registry — index, search, export across all projects."""
    p = argparse.ArgumentParser(
        prog="generate.py registry",
        description="Cross-project image asset registry (index/search/export).",
    )
    sub = p.add_subparsers(dest="action", required=True)

    sub.add_parser("index", help="Rebuild data/asset-registry.json from output/")

    sp_search = sub.add_parser("search", help="Search registry by title/caption/tags")
    sp_search.add_argument("query", help="Substring to match (case-insensitive)")
    sp_search.add_argument("--json", action="store_true", dest="json_output",
                           help="Emit results as JSON")

    sp_export = sub.add_parser("export", help="Export registry to CSV or JSON")
    sp_export.add_argument("--format", choices=["csv", "json"], default="csv")

    args = p.parse_args(argv)

    from lib.registry import index as registry_index, search as registry_search, export as registry_export

    if args.action == "index":
        entries = registry_index()
        projects = sorted({e.project for e in entries})
        print(f"Indexed {len(entries)} assets across {len(projects)} project(s).")
        return

    if args.action == "search":
        results = registry_search(args.query)
        if args.json_output:
            print(json.dumps([e.to_dict() for e in results], indent=2))
            return
        if not results:
            print(f"No matches for {args.query!r}.")
            return
        print(f"{len(results)} match(es) for {args.query!r}:")
        for e in results:
            print(f"  [{e.project}] {e.title}")
            print(f"    id={e.id}  style={e.style}  model={e.model}")
            print(f"    {e.path}")
        return

    if args.action == "export":
        path = registry_export(format=args.format)
        print(f"Exported registry: {path}")
        return


def _cmd_deploy(argv: list[str]) -> None:
    """Deploy a project's viewer directory to Vercel as a static site."""
    p = argparse.ArgumentParser(
        prog="generate.py deploy",
        description=(
            "Deploy <project>'s viewer to Vercel.\n"
            "Requires the `vercel` CLI on PATH (npm i -g vercel) and a prior `vercel login`."
        ),
    )
    p.add_argument("project", help="Project name under output/, or use --viewer-dir")
    p.add_argument("--prod", action="store_true", help="Deploy to production (default: preview)")
    p.add_argument("--viewer-dir", default=None, help="Explicit path to dir containing viewer.html")
    p.add_argument("--dry-run", action="store_true", help="Print the command without running it")
    args = p.parse_args(argv)

    from lib.deploy.vercel import deploy, VercelNotInstalledError, ViewerNotFoundError

    viewer_dir = Path(args.viewer_dir) if args.viewer_dir else None
    try:
        url = deploy(args.project, viewer_dir=viewer_dir, prod=args.prod, dry_run=args.dry_run)
    except (VercelNotInstalledError, ViewerNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        return
    print(f"Deployed: {url}")


def _cmd_social_expand(argv: list[str]) -> None:
    """Generate platform-specific social posts for a project's latest run."""
    p = argparse.ArgumentParser(
        prog="generate.py social-expand",
        description=(
            "LLM second pass: expand each generated image's title + caption "
            "into platform-specific social posts (LinkedIn, X, Instagram). "
            "Writes <latest-run>/social-posts.json."
        ),
    )
    p.add_argument("project", help="Project dir path, or name under output/")
    p.add_argument(
        "--platform", nargs="+", default=None,
        choices=["linkedin", "x", "instagram"],
        help="Subset of platforms to generate (default: all three)",
    )
    p.add_argument("--model", default="gpt-4o-mini",
                   help="OpenAI chat model (default: gpt-4o-mini)")
    p.add_argument("--dry-run", action="store_true",
                   help="Skip API calls; write a placeholder showing what would run")
    args = p.parse_args(argv)

    from lib.social import expand
    expand(
        args.project,
        platforms=args.platform,
        model=args.model,
        dry_run=args.dry_run,
    )


def _cmd_notion_export(argv: list[str]) -> None:
    """Push approved images for a project to a Notion database."""
    p = argparse.ArgumentParser(
        prog="generate.py notion-export",
        description=(
            "Push approved Rafiki images to a Notion gallery database. "
            "Reads NOTION_API_KEY (and NOTION_DATABASE_ID, if --database is "
            "omitted) from the environment. See docs/NOTION-EXPORT.md."
        ),
    )
    p.add_argument("project", help="Project name under output/, or absolute path")
    p.add_argument("--database", default=None,
                   help="Notion database id (default: $NOTION_DATABASE_ID)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be uploaded; make no API calls")
    p.add_argument("--force", action="store_true",
                   help="Re-export images already in .notion-exported.json")
    p.add_argument("--output-dir", "-d", default=None,
                   help="Root output directory (default: output/)")
    args = p.parse_args(argv)

    from lib.exporters.notion import export, NotionExportError

    output_root = Path(args.output_dir) if args.output_dir else Path(__file__).parent / "output"
    try:
        result = export(
            args.project,
            database_id=args.database,
            output_root=output_root,
            dry_run=args.dry_run,
            force=args.force,
        )
    except NotionExportError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"\nNotion export: {result['exported']} exported, "
        f"{result['skipped']} skipped, {len(result['errors'])} error(s) "
        f"(source: {result['source']})"
    )
    sys.exit(0 if not result["errors"] else 1)


def _cmd_serve(argv: list[str]) -> None:
    """Run the Rafiki generative portal — persistent ratings, search, regen."""
    p = argparse.ArgumentParser(
        prog="generate.py serve",
        description="Start the Rafiki portal at http://localhost:7433/",
    )
    p.add_argument("--port", type=int, default=7433, help="Port (default: 7433)")
    p.add_argument(
        "--output-dir", "-d", default=None,
        help="Root output directory (default: output/ next to generate.py)",
    )
    p.add_argument("--open", action="store_true", help="Open browser on start")
    p.add_argument(
        "--public", action="store_true",
        help="Bind to 0.0.0.0 (all interfaces) instead of 127.0.0.1. "
             "Set PORTAL_USERNAME and PORTAL_PASSWORD to enable Basic auth.",
    )
    args = p.parse_args(argv)

    output_root = Path(args.output_dir) if args.output_dir else Path(__file__).parent / "output"
    if not output_root.exists():
        print(f"Error: output dir not found: {output_root}")
        sys.exit(1)

    from lib.server import serve
    serve(output_root=output_root, port=args.port, open_browser=args.open, public=args.public)


def _cmd_approve(argv: list[str]) -> None:
    """Copy starred images from a run into output/<project>/approved/."""
    p = argparse.ArgumentParser(
        prog="generate.py approve",
        description="Promote starred images into the project's approved/ set.",
    )
    p.add_argument("project", help="Project name under output/ (or absolute path)")
    p.add_argument("--run", default=None,
                   help="Run id to approve from (default: latest run)")
    args = p.parse_args(argv)

    from lib.archive import approve as _approve
    n = _approve(args.project, run=args.run)
    print(f"Approved {n} image(s) → output/{args.project}/approved/")


def _parse_days(spec: str) -> int:
    """Parse '30d' / '7' into an int day count."""
    s = spec.strip().lower()
    if s.endswith("d"):
        s = s[:-1]
    try:
        return int(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"--older-than expects N or Nd (e.g. 30 or 30d), got {spec!r}"
        ) from e


def _cmd_clean(argv: list[str]) -> None:
    """Delete old run-* dirs, optionally keeping runs with approved images."""
    p = argparse.ArgumentParser(
        prog="generate.py clean",
        description="Remove run-*/ dirs from a project. approved/ is never touched.",
    )
    p.add_argument("project", help="Project name under output/ (or absolute path)")
    p.add_argument("--keep-approved", action="store_true",
                   help="Only delete runs whose images are all in approved/")
    p.add_argument("--older-than", default=None, metavar="DAYS",
                   help="Only delete runs older than N days (e.g. 30 or 30d)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be deleted without removing anything")
    args = p.parse_args(argv)

    older = _parse_days(args.older_than) if args.older_than else None
    from lib.archive import clean as _clean
    deleted = _clean(
        args.project,
        keep_approved=args.keep_approved,
        older_than_days=older,
        dry_run=args.dry_run,
    )
    verb = "Would delete" if args.dry_run else "Deleted"
    print(f"{verb} {len(deleted)} run dir(s):")
    for d in deleted:
        print(f"  {d}")


def main() -> None:
    # Dispatch subcommands before main arg parsing
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        _cmd_view(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "library":
        _cmd_library(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        _cmd_serve(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "link-projects":
        _cmd_link_projects(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "approve":
        _cmd_approve(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "canva-export":
        _cmd_canva_export(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        _cmd_clean(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        _cmd_deploy(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "notion-export":
        _cmd_notion_export(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "regen":
        _cmd_regen(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "registry":
        _cmd_registry(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "social-expand":
        _cmd_social_expand(sys.argv[2:])
        return

    parser = argparse.ArgumentParser(
        description="Rafiki — AI image generator (Gemini + OpenAI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Model aliases: " + ", ".join(f"{k}→{v}" for k, v in ALIASES.items()),
            "Style composition: --style kk+bcai stacks both style suffixes",
        ]),
    )

    parser.add_argument("--prompt", "-p", help="Text prompt for image generation")
    parser.add_argument("--prompt-file", "-f", help="Path to image-prompts.md file")
    parser.add_argument("--output", "-o", default="output.png",
                        help="Output file path (default: output.png)")
    parser.add_argument("--output-dir", "-d",
                        help="Output directory for batch runs")
    parser.add_argument(
        "--model", "-m", default="gemini-2.5-flash-image",
        help=(
            "Model ID or alias (default: gemini-2.5-flash-image). "
            "Aliases: flash/nano/pro (Gemini), gpt/gpt1/dalle3 (OpenAI). "
            "Full IDs: gpt-image-2, dall-e-3, gemini-3-pro-image-preview."
        ),
    )
    parser.add_argument("--quality", "-q", default="high",
                        choices=["low", "medium", "high"],
                        help="Quality for OpenAI models (default: high). Ignored by Gemini.")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        help="Aspect ratio (default: 16:9). Presets: linkedin, instagram, twitter, story, square")
    parser.add_argument("--resolution", "-r", default="1K",
                        choices=["1K", "2K", "4K"],
                        help="Resolution (default: 1K). 2K/4K: Gemini Pro only.")
    parser.add_argument(
        "--style", "-s", default=None,
        help=(
            "Style preset or composed spec (e.g. kk, bcai, kk+bcai). "
            "Use 'none' for no style. Default: kk. Run --list-styles to see all."
        ),
    )
    parser.add_argument("--no-style", action="store_true",
                        help="No style suffix (same as --style none)")
    parser.add_argument("--list-styles", action="store_true",
                        help="Show available styles and exit")
    parser.add_argument("--reference-image", "--ref",
                        help="Path to reference image for style/composition guidance")
    parser.add_argument(
        "--reference-images", metavar="PATHS",
        help=(
            "Comma-separated reference image paths for batch mode. "
            "One path per prompt (in order), or a single path to reuse for all."
        ),
    )
    parser.add_argument("--reference-role", choices=["style", "mockup"], default="style",
                        help="'style' (look-and-feel) or 'mockup' (preserve garment + add print)")
    parser.add_argument("--composition-references", metavar="PATHS",
                        help="Extra comma-separated ref images for mockup mode")
    parser.add_argument("--workers", "-w", type=int, default=1, metavar="N",
                        help="Parallel generation workers for batch mode (default: 1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without calling any API")
    parser.add_argument("--no-viewer", action="store_true",
                        help="Skip generating viewer.html after a batch run")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Emit structured JSON to stdout; progress to stderr")
    parser.add_argument("--usage", action="store_true",
                        help="Show usage statistics")

    args = parser.parse_args()

    # JSON mode: all print() → stderr so stdout carries only the result JSON
    _real_stdout = sys.stdout
    if args.json_output:
        sys.stdout = sys.stderr

    # Resolve model alias early
    args.model = resolve_model(args.model)

    # Resolve aspect ratio preset
    if args.aspect_ratio in ASPECT_RATIOS:
        args.aspect_ratio = ASPECT_RATIOS[args.aspect_ratio]

    composition_refs: list[str] | None = None
    if args.composition_references:
        composition_refs = [p.strip() for p in args.composition_references.split(",") if p.strip()]
        if not composition_refs:
            print("Error: --composition-references has no paths")
            sys.exit(1)

    # ── Informational flags ──────────────────────────────────────────────────

    if args.list_styles:
        styles = load_styles()
        print("Available styles:")
        for name, cfg in styles.items():
            marker = " (default)" if cfg.get("default") else ""
            print(f"  {name}{marker}: {cfg.get('description', '')}")
        print("\nTip: compose styles with '+', e.g.  --style kk+bcai")
        return

    if args.usage:
        data = load_usage_log()
        print(f"Total images generated: {data['total_images']}")
        if data["entries"]:
            print("\nRecent generations:")
            for entry in data["entries"][-5:]:
                print(f"  {entry['timestamp']}: {entry['model']} → {entry['output']}")
        return

    # ── Style resolution ─────────────────────────────────────────────────────

    style = "none" if args.no_style else args.style

    # ── Reference image helpers ───────────────────────────────────────────────

    def _resolve_ref_list(n: int) -> list[str | None]:
        if args.reference_images and args.reference_image:
            print("Error: use --reference-image OR --reference-images, not both")
            sys.exit(1)
        if args.reference_images:
            parts = [p.strip() for p in args.reference_images.split(",") if p.strip()]
            if not parts:
                print("Error: --reference-images has no paths")
                sys.exit(1)
            if len(parts) == 1:
                return parts * n
            if len(parts) != n:
                print(
                    f"Error: --reference-images has {len(parts)} paths "
                    f"but {n} prompts"
                )
                sys.exit(1)
            return parts
        single = args.reference_image
        return [single] * n if single else [None] * n

    # ── Single prompt ────────────────────────────────────────────────────────

    if args.prompt:
        if args.reference_images:
            print("Error: --reference-images is for batch mode (--prompt-file)")
            sys.exit(1)
        success = generate_image(
            prompt=args.prompt,
            output_path=args.output,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            quality=args.quality,
            style=style,
            reference_image=args.reference_image,
            reference_role=args.reference_role,
            composition_references=composition_refs,
            dry_run=args.dry_run,
        )
        if args.json_output:
            _real_stdout.write(json.dumps({
                "success": success,
                "mode": "single",
                "dry_run": args.dry_run,
                "output_path": args.output,
                "model": args.model,
                "aspect_ratio": args.aspect_ratio,
                "style": style or "none",
                "prompt_preview": args.prompt[:120],
            }, indent=2) + "\n")
        sys.exit(0 if success else 1)

    # ── Batch from prompt file ────────────────────────────────────────────────

    if args.prompt_file:
        prompts = parse_image_prompts_md(args.prompt_file)
        print(f"Found {len(prompts)} prompts in {args.prompt_file}")

        project_dir = Path(args.output_dir or Path(args.prompt_file).parent / "images")
        ref_paths = _resolve_ref_list(len(prompts))

        result = run_batch(
            prompts=prompts,
            project_dir=project_dir,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            quality=args.quality,
            style=style,
            ref_paths=ref_paths,
            reference_role=args.reference_role,
            composition_references=composition_refs,
            dry_run=args.dry_run,
            workers=args.workers,
            generate_viewer_html=not args.no_viewer,
            prompt_file=args.prompt_file,
            invocation_source="python-cli",
        )

        if args.json_output:
            _real_stdout.write(json.dumps({
                "success": result.success,
                "mode": "batch",
                "dry_run": args.dry_run,
                "generated": result.success_count,
                "total": result.total,
                "project_dir": str(result.project_dir),
                "run_dir": str(result.run_dir),
                "run_id": result.run_id,
                "viewer_path": result.viewer_path,
                "model": args.model,
                "aspect_ratio": args.aspect_ratio,
                "style": style or "none",
                "images": result.images,
            }, indent=2) + "\n")

        sys.exit(0 if result.success else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
