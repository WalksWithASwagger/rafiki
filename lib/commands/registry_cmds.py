"""Registry subcommands extracted from generate.py — behavior unchanged."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _cmd_registry(argv: list[str]) -> None:
    """Asset registry — index, search, export across all projects."""
    p = argparse.ArgumentParser(
        prog="generate.py registry",
        description="Cross-project image asset registry (index/search/export).",
    )
    sub = p.add_subparsers(dest="action", required=True)

    sp_index = sub.add_parser("index", help="Rebuild data/asset-registry.json from output/")
    sp_index.add_argument(
        "--all-runs",
        action="store_true",
        help="Index every run-* image instead of the curated approved/latest-run scope",
    )

    sp_search = sub.add_parser("search", help="Search registry by title/caption/tags")
    sp_search.add_argument("query", help="Substring to match (case-insensitive)")
    sp_search.add_argument("--json", action="store_true", dest="json_output",
                           help="Emit results as JSON")

    sp_export = sub.add_parser("export", help="Export registry to CSV or JSON")
    sp_export.add_argument("--format", choices=["csv", "json"], default="csv")

    sp_suggest = sub.add_parser(
        "suggest-lineage",
        help="Show lineage candidates not yet linked by superseded_by",
    )
    sp_suggest.add_argument("--json", action="store_true", dest="json_output",
                            help="Emit results as JSON")
    sp_suggest.add_argument(
        "--all-runs",
        action="store_true",
        help="Include all runs (not just curated) when loading the registry",
    )

    args = p.parse_args(argv)

    from lib.registry import index as registry_index, search as registry_search, export as registry_export

    if args.action == "index":
        entries = registry_index(scope="all-runs" if args.all_runs else "curated")
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

    if args.action == "suggest-lineage":
        from lib.lineage import suggest_lineage_candidates
        scope = "all-runs" if args.all_runs else "curated"
        entries = registry_index(scope=scope)
        suggestions = suggest_lineage_candidates(entries)
        if args.json_output:
            print(json.dumps(suggestions, indent=2))
            return
        if not suggestions:
            print("No unlinked lineage candidates found.")
            return
        print(f"{len(suggestions)} lineage suggestion(s):")
        for s in suggestions:
            print(f"  [{s['project']}] {s['source_id']}  <->  {s['candidate_id']}")
            for reason in s["reasons"]:
                print(f"    reason: {reason}")
        return


def _refresh_registry_after_mutation(output_root: Path, *, reason: str) -> dict[str, object]:
    from lib import registry

    return registry.refresh_cache(output_root=output_root, reason=reason)
