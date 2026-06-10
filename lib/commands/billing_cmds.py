"""Billing subcommands extracted from generate.py — behavior unchanged."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cmd_billing(argv: list[str]) -> None:
    """Import or summarize local provider billing exports."""
    p = argparse.ArgumentParser(
        prog="generate.py billing",
        description="Import provider billing CSV/JSON into local gitignored spend ledger.",
    )
    sub = p.add_subparsers(dest="action", required=True)

    sp_import = sub.add_parser("import", help="Import .csv, .json, or .jsonl billing rows")
    sp_import.add_argument("source", help="Billing export file")
    sp_import.add_argument("--provider", default="", help="Provider override, e.g. OpenAI or Gemini")
    sp_import.add_argument("--label", default="", help="Friendly source label stored with each row")
    sp_import.add_argument("--state", default=None, help="Override billing ledger path")
    sp_import.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON result")

    sp_summary = sub.add_parser("summary", help="Summarize imported billing ledger")
    sp_summary.add_argument("--state", default=None, help="Override billing ledger path")
    sp_summary.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON result")

    args = p.parse_args(argv)

    from lib.billing import import_billing_file, summarize_billing_imports

    state_path = Path(args.state) if getattr(args, "state", None) else None
    if args.action == "import":
        try:
            result = import_billing_file(
                Path(args.source),
                state_path=state_path,
                provider=args.provider,
                label=args.label,
            )
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if args.json_output:
            print(json.dumps(result, indent=2))
            return
        print(
            f"Billing import: {result['imported']} imported, "
            f"{result['duplicates']} duplicate(s), {result['skipped']} skipped"
        )
        print(f"Ledger: {result['path']}")
        return

    summary = summarize_billing_imports(state_path)
    if args.json_output:
        print(json.dumps(summary, indent=2))
        return
    print(f"Billing ledger: {summary['path']}")
    print(f"Imported: {summary['entries']} row(s)")
    print(f"USD total: ${summary['amount']:.2f}")
    for provider in summary["by_provider"]:
        print(f"  {provider['provider']}: ${provider['amount']:.2f} ({provider['entries']} row(s))")
