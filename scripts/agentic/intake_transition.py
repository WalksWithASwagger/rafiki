#!/usr/bin/env python3
"""Evaluate one agent-ready intake event without mutating GitHub state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import load_contract, read_text_arg, repo_root, write_json  # noqa: E402
from issue_lint import lint_issue, parse_labels  # noqa: E402


def evaluate_intake(
    *,
    event_name: str,
    event_action: str,
    event_label: str,
    issue_body: str,
    labels: list[str],
    contract: dict[str, Any],
) -> dict[str, Any]:
    label_config = contract["labels"]
    ready_names = [label_config["ready"], *label_config.get("ready_aliases", [])]
    normalized_labels = list(dict.fromkeys(labels))
    label_set = set(normalized_labels)
    ready_labels = [label for label in ready_names if label in label_set]
    relevant_event = event_name == "workflow_dispatch" or (
        event_name == "issues" and event_action == "labeled" and event_label in ready_names
    )

    if not relevant_event:
        return {
            "ok": True,
            "action": "ignore",
            "reason": "unrelated-event",
            "ready_labels": [],
            "approved_labels": [],
            "lint": None,
        }
    if not ready_labels:
        return {
            "ok": True,
            "action": "ignore",
            "reason": "ready-no-longer-present",
            "ready_labels": [],
            "approved_labels": [],
            "lint": None,
        }

    lint = lint_issue(issue_body, normalized_labels, contract)
    return {
        "ok": lint["ok"],
        "action": "dispatch" if lint["ok"] else "escalate",
        "reason": "quality-passed" if lint["ok"] else "quality-failed",
        "ready_labels": ready_labels,
        "approved_labels": normalized_labels if lint["ok"] else [],
        "lint": lint,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--event-action", default="")
    parser.add_argument("--event-label", default="")
    parser.add_argument("--issue-file", required=True)
    parser.add_argument("--labels", default="")
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    result = evaluate_intake(
        event_name=args.event_name,
        event_action=args.event_action,
        event_label=args.event_label,
        issue_body=read_text_arg(args.issue_file),
        labels=parse_labels(args.labels),
        contract=load_contract(repo_root()),
    )
    write_json(Path(args.json_output), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
