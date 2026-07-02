"""Archive curation subcommands extracted from generate.py — behavior unchanged."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib.commands.registry_cmds import _refresh_registry_after_mutation

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _approval_output_root(project: str, output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()
    project_path = Path(project).expanduser()
    if project_path.is_absolute():
        return project_path.parent.resolve()
    return (REPO_ROOT / "output").resolve()


def _approval_project_dir(project: str, output_root: Path) -> Path:
    project_path = Path(project).expanduser()
    if project_path.is_absolute():
        return project_path.resolve()
    return output_root / project


def _cmd_archive_health(argv: list[str]) -> None:
    """Report archive health without mutating generated outputs."""
    p = argparse.ArgumentParser(
        prog="generate.py archive-health",
        description="Read-only report for missing images, malformed runs, sidecar orphans, duplicates, and disk usage.",
    )
    p.add_argument(
        "--output-dir", "-d", default=None,
        help="Root output directory (default: output/ next to generate.py)",
    )
    p.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON result")
    p.add_argument(
        "--cleanup-report",
        action="store_true",
        help="Print the conservative cleanup report grouped by project and run",
    )
    args = p.parse_args(argv)

    output_root = Path(args.output_dir) if args.output_dir else REPO_ROOT / "output"
    from lib.archive_health import archive_health_report

    report = archive_health_report(output_root)
    if args.json_output:
        print(json.dumps(report, indent=2))
        return
    if args.cleanup_report:
        _print_archive_cleanup_report(report)
        return

    summary = report["summary"]
    print(f"Archive health: {output_root}")
    print(
        f"Runs: {summary['runs']}  Images: {summary['present_images']}/"
        f"{summary['manifest_images']} present  Disk: {summary['disk_bytes']} bytes"
    )
    print(
        f"Missing: {summary['missing_images']}  Malformed runs: {len(report['malformed_runs'])}  "
        f"Duplicate filename groups: {summary['duplicate_filename_groups']}"
    )
    print(
        f"Orphans: ratings={summary['orphaned_ratings']} "
        f"feedback={summary['orphaned_feedback']} "
        f"evaluations={summary['orphaned_evaluations']} "
        f"metadata={summary['orphaned_metadata']}"
    )
    cleanup = report["cleanup_report"]["summary"]
    print(
        f"Cleanup candidates: {cleanup['candidate_runs']} run(s), "
        f"{cleanup['candidate_bytes']} bytes; risky runs: {cleanup['risky_runs']}"
    )
    cache = report["thumbnail_cache"]
    print(f"Thumbnail cache: {cache['files']} file(s), {cache['disk_bytes']} bytes at {cache['path']}")
    for rec in report["recommendations"]:
        print(f"- {rec}")


def _cmd_archive_thumbnails(argv: list[str]) -> None:
    """Build optional local thumbnails without changing originals or viewers."""
    p = argparse.ArgumentParser(
        prog="generate.py archive-thumbnails",
        description="Build local preview thumbnails under output/.rafiki-cache/ for large archives.",
    )
    p.add_argument(
        "--output-dir", "-d", default=None,
        help="Root output directory (default: output/ next to generate.py)",
    )
    p.add_argument("--width", type=int, default=480, help="Thumbnail max width in pixels")
    p.add_argument("--force", action="store_true", help="Regenerate thumbnails even if cached")
    p.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON result")
    args = p.parse_args(argv)

    output_root = Path(args.output_dir) if args.output_dir else REPO_ROOT / "output"
    if not output_root.exists():
        print(f"Error: output dir not found: {output_root}")
        sys.exit(1)

    from lib.renderers.library import _records_from_registry
    from lib.thumbnail_cache import build_thumbnail_cache

    records = _records_from_registry(output_root)
    summary = build_thumbnail_cache(output_root, records, width=args.width, force=args.force)
    if args.json_output:
        print(json.dumps(summary, indent=2))
        return

    print(f"Thumbnail cache: {summary['path']}")
    print(
        f"Images: {summary['checked']} checked  "
        f"created={summary['created']} reused={summary['reused']} failed={summary['failed']}"
    )
    if summary["failed"]:
        print("Errors:")
        for error in summary["errors"]:
            print(f"- {error['file']}: {error['error']}")


def _cmd_archive_repair(argv: list[str]) -> None:
    """Repair missing records, duplicates, and sidecars with backups."""
    p = argparse.ArgumentParser(
        prog="generate.py archive-repair",
        description="Reversibly repair missing archive records, exact duplicates, malformed runs, and orphaned sidecars.",
    )
    p.add_argument(
        "--output-dir", "-d", default=None,
        help="Root output directory (default: output/ next to generate.py)",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Apply the repair plan. Without this flag, archive-repair is a dry-run.",
    )
    p.add_argument(
        "--backup-dir",
        default=None,
        help="Backup/quarantine directory (default: output/.rafiki-cleanup/<timestamp>)",
    )
    p.add_argument(
        "--no-registry",
        action="store_true",
        help="Skip rebuilding data/asset-registry.json after applying repairs.",
    )
    p.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON result")
    args = p.parse_args(argv)

    output_root = Path(args.output_dir) if args.output_dir else REPO_ROOT / "output"
    backup_dir = Path(args.backup_dir).expanduser() if args.backup_dir else None
    from lib.archive_repair import repair_archive

    result = repair_archive(
        output_root,
        apply=args.apply,
        backup_dir=backup_dir,
        rebuild_registry=not args.no_registry,
    )
    if args.json_output:
        print(json.dumps(result, indent=2))
        return

    mode = "Applied" if args.apply else "Dry-run"
    counts = result["counts"]
    missing_count = counts.get("missing_records", counts.get("missing_records_removed", 0))
    print(f"{mode} archive repair: {Path(result['output_root'])}")
    print(f"Backup/quarantine: {result['backup_dir']}")
    print(
        "Planned/applied: "
        f"missing_records={missing_count} "
        f"exact_duplicates={counts.get('exact_duplicate_files', counts.get('duplicate_files_quarantined', 0))} "
        f"rewrites={counts.get('run_json_rewrites', 0)} "
        f"quarantined_runs={counts.get('runs_quarantined', 0)} "
        f"synthesized_runs={counts.get('malformed_runs_synthesized', 0)} "
        f"sidecar_orphans={counts.get('sidecar_orphans', counts.get('sidecar_orphans_removed', 0))}"
    )
    if not args.apply:
        print("No files changed. Re-run with --apply to write backups and repair the archive.")
    elif result.get("registry", {}).get("registry_refreshed"):
        print(
            f"Registry rebuilt ({result['registry']['registry_scope']}): "
            f"{result['registry']['registry_count']} entries"
        )


def _print_archive_cleanup_report(report: dict) -> None:
    cleanup = report["cleanup_report"]
    summary = cleanup["summary"]
    print(f"Archive cleanup report: {report['output_root']}")
    print(f"Policy: {cleanup['policy']}")
    print(
        f"Candidates: {summary['candidate_runs']} run(s), "
        f"{summary['candidate_images']} image(s), {summary['candidate_bytes']} bytes"
    )
    print(
        f"Review before cleanup: {summary['risky_runs']} run(s), "
        f"{summary['sidecar_orphan_groups']} sidecar orphan group(s), "
        f"{summary['duplicate_filename_groups']} duplicate filename group(s)"
    )

    for project in cleanup["projects"]:
        project_summary = project["summary"]
        print(
            f"\n{project['project']}: {project_summary['candidate_runs']} candidate / "
            f"{project_summary['risky_runs']} review"
        )
        for run in project["runs"]:
            print(
                f"  [{run['action']}:{run['risk_level']}] {run['run']} "
                f"{run['approved_images']}/{run['image_count']} approved, "
                f"{run['disk_bytes']} bytes"
            )
            print(f"    {run['reason']}")
        for command in project["suggested_commands"]:
            print(f"    next: {command}")

    if cleanup["sidecar_orphans"]:
        print("\nSidecar orphans:")
        for orphan in cleanup["sidecar_orphans"]:
            print(f"  {orphan['collection']}: {orphan['count']} key(s)")


def _cmd_approve(argv: list[str]) -> None:
    """Copy starred images from a run into output/<project>/approved/."""
    p = argparse.ArgumentParser(
        prog="generate.py approve",
        description="Promote starred images into the project's approved/ set.",
    )
    p.add_argument("project", help="Project name under output/ (or absolute path)")
    p.add_argument("--run", default=None,
                   help="Run id to approve from (default: latest run)")
    p.add_argument(
        "--output-dir",
        default=None,
        help="Root output directory for relative projects (default: output/ next to generate.py)",
    )
    args = p.parse_args(argv)

    from lib.archive import approve as _approve
    output_root = _approval_output_root(args.project, args.output_dir)
    n = _approve(args.project, run=args.run, output_root=output_root)
    approved_dir = _approval_project_dir(args.project, output_root) / "approved"
    print(f"Approved {n} image(s) → {approved_dir}/")
    if n > 0:
        refresh = _refresh_registry_after_mutation(output_root, reason="approve")
        print(f"Registry refreshed: {refresh['registry_path']} ({refresh['registry_count']} assets)")


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
