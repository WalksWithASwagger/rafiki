#!/usr/bin/env python3
"""Validate non-blocking PR traceability requirements."""

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
    contract_linear_prefixes,
    extract_issue_reference,
    extract_linear_keys,
    load_contract,
    read_text_arg,
    repo_root,
    write_json,
)


def branch_matches_linear(branch: str, branch_prefix: str, linear_key: str) -> bool:
    pattern = rf"^{re.escape(branch_prefix)}{re.escape(linear_key)}-[a-z0-9][a-z0-9-]*$"
    return bool(re.match(pattern, branch, flags=re.IGNORECASE))


def branch_matches_issue(branch: str, branch_prefix: str, issue_prefix: str) -> bool:
    pattern = rf"^{re.escape(branch_prefix)}{re.escape(issue_prefix)}\d+(?:-[a-z0-9][a-z0-9-]*)?$"
    return bool(re.match(pattern, branch, flags=re.IGNORECASE))


def body_has_linear_line(body: str, linear_key: str, body_prefix: str) -> bool:
    pattern = rf"^{re.escape(body_prefix)}\s*{re.escape(linear_key)}\s*$"
    return bool(re.search(pattern, body, flags=re.IGNORECASE | re.MULTILINE))


def title_has_linear_prefix(title: str, linear_key: str) -> bool:
    return title.startswith(f"{linear_key}:")


def build_comment(payload: dict[str, Any]) -> str:
    lines = [
        "## Agentic Traceability",
        "",
        f"Verdict: {'traceable' if payload['ok'] else 'needs-human'}",
        "",
        "Checks:",
        f"- Linked GitHub issue present: {'yes' if payload['checks']['has_issue_link'] else 'no'}",
        f"- Branch naming matches contract: {'yes' if payload['checks']['branch_ok'] else 'no'}",
        f"- PR title prefix matches contract: {'yes' if payload['checks']['title_ok'] else 'no'}",
        f"- PR body includes Linear line when required: {'yes' if payload['checks']['body_ok'] else 'no'}",
    ]
    if payload["linear_keys"]:
        lines.append(f"- Linear keys found: {', '.join(payload['linear_keys'])}")
    else:
        lines.append("- Linear keys found: none")
    if payload["errors"]:
        lines.extend(["", "Next actions:"])
        lines.extend(f"- {item}" for item in payload["errors"])
    else:
        lines.extend(["", "Traceability contract is satisfied."])
    return "\n".join(lines)


def check_traceability(
    *,
    contract: dict[str, Any],
    pr_title: str,
    pr_body: str,
    head_ref: str,
    issue_body: str,
) -> dict[str, Any]:
    rules = contract["pr_requirements"]
    issue_ref = extract_issue_reference(pr_body, verbs=tuple(rules["issue_link_verbs"]))
    branch_prefix = rules["branch_prefix"]
    issue_prefix = rules["github_only_issue_prefix"]
    linear_keys = [
        key
        for key in extract_linear_keys(
            pr_title,
            pr_body,
            head_ref,
            issue_body,
            prefixes=contract_linear_prefixes(contract),
        )
        if not key.startswith(f"{issue_prefix.rstrip('-').upper()}-")
    ]
    linear_key = linear_keys[0] if len(linear_keys) == 1 else None
    requires_linear = bool(linear_keys) and rules["require_linear_key_when_present"]

    branch_ok = False
    title_ok = not requires_linear
    body_ok = not requires_linear
    errors: list[str] = []

    if rules["require_issue_link"] and issue_ref is None:
        errors.append(
            "Add `Closes #<issue>` or `Refs #<issue>` to the PR body so GitHub remains the execution truth."
        )

    if len(linear_keys) > 1:
        errors.append(
            "Use exactly one Linear key across the branch, title, body, and linked issue. Multiple BC keys were detected."
        )
    elif linear_key:
        branch_ok = branch_matches_linear(head_ref, branch_prefix, linear_key)
        title_ok = title_has_linear_prefix(pr_title, linear_key)
        body_ok = body_has_linear_line(pr_body, linear_key, rules["body_linear_prefix"])
        if not branch_ok:
            errors.append(
                f"Rename the branch to `{branch_prefix}{linear_key}-<slug>` so the Linear key is visible in the ref."
            )
        if not title_ok:
            errors.append(f"Prefix the PR title with `{linear_key}:`.")
        if not body_ok:
            errors.append(f"Add `{rules['body_linear_prefix']} {linear_key}` to the PR body.")
    else:
        branch_ok = branch_matches_issue(head_ref, branch_prefix, issue_prefix)
        if not branch_ok:
            errors.append(
                f"Use `{branch_prefix}{issue_prefix}<number>-<slug>` for GitHub-only work outside the active Linear delivery lane."
            )

    payload = {
        "ok": not errors,
        "verdict": "traceable" if not errors else "needs-human",
        "linked_issue": issue_ref["issue_number"] if issue_ref else None,
        "linked_issue_verb": issue_ref["verb"] if issue_ref else None,
        "linear_key": linear_key,
        "linear_keys": linear_keys,
        "head_ref": head_ref,
        "checks": {
            "has_issue_link": issue_ref is not None,
            "branch_ok": branch_ok,
            "title_ok": title_ok,
            "body_ok": body_ok,
        },
        "errors": errors,
    }
    payload["comment"] = build_comment(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-title", required=True)
    parser.add_argument("--pr-body-file", required=True)
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--issue-file", default=None)
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    root = repo_root()
    payload = check_traceability(
        contract=load_contract(root),
        pr_title=args.pr_title,
        pr_body=read_text_arg(args.pr_body_file),
        head_ref=args.head_ref,
        issue_body=read_text_arg(args.issue_file),
    )
    write_json(Path(args.json_output), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
