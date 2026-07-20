#!/usr/bin/env python3
"""Validate GitHub issue traceability requirements for a pull request."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    extract_issue_reference,
    load_contract,
    read_text_arg,
    repo_root,
    write_json,
)


def extract_branch_issue(branch: str, branch_prefix: str, issue_prefix: str) -> str | None:
    pattern = (
        rf"^{re.escape(branch_prefix)}{re.escape(issue_prefix)}"
        rf"(\d+)-[a-z0-9][a-z0-9-]*$"
    )
    match = re.match(pattern, branch, flags=re.IGNORECASE)
    return match.group(1) if match else None


def build_comment(payload: dict[str, Any]) -> str:
    lines = [
        "## Agentic Traceability",
        "",
        f"Verdict: {'traceable' if payload['ok'] else 'needs-human'}",
        "",
        "Checks:",
        f"- Linked GitHub issue present: {'yes' if payload['checks']['has_issue_link'] else 'no'}",
        f"- Branch naming matches contract: {'yes' if payload['checks']['branch_ok'] else 'no'}",
        f"- Branch and linked issue match: {'yes' if payload['checks']['issue_number_matches'] else 'no'}",
    ]
    if payload["errors"]:
        lines.extend(["", "Next actions:"])
        lines.extend(f"- {item}" for item in payload["errors"])
    else:
        lines.extend(["", "Traceability contract is satisfied."])
    return "\n".join(lines)


def check_traceability(
    *,
    contract: dict[str, Any],
    pr_body: str,
    head_ref: str,
) -> dict[str, Any]:
    rules = contract["pr_requirements"]
    issue_ref = extract_issue_reference(pr_body, verbs=tuple(rules["issue_link_verbs"]))
    branch_issue = extract_branch_issue(
        head_ref,
        rules["branch_prefix"],
        rules["issue_prefix"],
    )
    linked_issue = issue_ref["issue_number"] if issue_ref else None
    issue_number_matches = branch_issue is not None and branch_issue == linked_issue
    errors: list[str] = []

    if rules["require_issue_link"] and issue_ref is None:
        errors.append(
            "Add `Closes #<issue>` or `Refs #<issue>` to the PR body so GitHub remains the execution truth."
        )
    if branch_issue is None:
        errors.append("Use `codex/issue-<number>-<slug>` for the pull-request branch.")
    elif linked_issue is not None and branch_issue != linked_issue:
        errors.append(
            f"Branch issue `#{branch_issue}` must match linked issue `#{linked_issue}`."
        )

    payload = {
        "ok": not errors,
        "verdict": "traceable" if not errors else "needs-human",
        "linked_issue": linked_issue,
        "linked_issue_verb": issue_ref["verb"] if issue_ref else None,
        "branch_issue": branch_issue,
        "head_ref": head_ref,
        "checks": {
            "has_issue_link": issue_ref is not None,
            "branch_ok": branch_issue is not None,
            "issue_number_matches": issue_number_matches,
        },
        "errors": errors,
    }
    payload["comment"] = build_comment(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-body-file", required=True)
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    root = repo_root()
    payload = check_traceability(
        contract=load_contract(root),
        pr_body=read_text_arg(args.pr_body_file),
        head_ref=args.head_ref,
    )
    write_json(Path(args.json_output), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
