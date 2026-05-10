#!/usr/bin/env python3
"""Synchronize Linear issue status from GitHub issue and PR events."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    extract_linear_keys,
    load_contract,
    read_text_arg,
    repo_root,
    write_json,
)


class LinearClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            "https://api.linear.app/graphql",
            data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
            headers={
                "Authorization": self.token,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(body or f"Linear API request failed: HTTP {exc.code}") from exc
        if payload.get("errors"):
            raise RuntimeError(json.dumps(payload["errors"], indent=2))
        return payload["data"]

    def get_issue(self, identifier: str) -> dict[str, Any]:
        data = self.graphql(
            """
            query IssueSync($id: String!) {
              issue(id: $id) {
                id
                identifier
                title
                state {
                  id
                  name
                  type
                }
                project {
                  id
                  name
                }
                team {
                  id
                  key
                  states(first: 100) {
                    nodes {
                      id
                      name
                      type
                    }
                  }
                }
                attachments(first: 100) {
                  nodes {
                    id
                    url
                    title
                  }
                }
                comments(first: 100) {
                  nodes {
                    id
                    body
                  }
                }
              }
            }
            """,
            {"id": identifier},
        )
        issue = data.get("issue")
        if not issue:
            raise RuntimeError(f"Linear issue {identifier} was not found.")
        return issue

    def update_issue_state(self, identifier: str, state_id: str) -> dict[str, Any]:
        data = self.graphql(
            """
            mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
              issueUpdate(id: $id, input: $input) {
                success
                issue {
                  id
                  identifier
                  state {
                    id
                    name
                    type
                  }
                }
              }
            }
            """,
            {"id": identifier, "input": {"stateId": state_id}},
        )
        return data["issueUpdate"]

    def create_comment(self, issue_id: str, body: str) -> dict[str, Any]:
        data = self.graphql(
            """
            mutation CommentCreate($input: CommentCreateInput!) {
              commentCreate(input: $input) {
                success
                comment {
                  id
                }
              }
            }
            """,
            {"input": {"issueId": issue_id, "body": body}},
        )
        return data["commentCreate"]


def resolve_linear_keys(
    contract: dict[str, Any],
    issue_title: str,
    issue_body: str,
    pr_title: str,
    pr_body: str,
    head_ref: str,
) -> list[str]:
    issue_prefix = contract["pr_requirements"]["github_only_issue_prefix"].rstrip("-").upper() + "-"
    return [
        key
        for key in extract_linear_keys(issue_title, issue_body, pr_title, pr_body, head_ref)
        if not key.startswith(issue_prefix)
    ]


def desired_state_name(contract: dict[str, Any], event: str) -> str | None:
    return contract["linear_sync"]["status_mapping"].get(event)


def find_state_id(issue: dict[str, Any], desired_state: str) -> str | None:
    states = issue.get("team", {}).get("states", {}).get("nodes", [])
    for state in states:
        if state["name"].lower() == desired_state.lower():
            return state["id"]
    return None


def issue_in_active_project(contract: dict[str, Any], issue: dict[str, Any]) -> bool:
    policy = contract["linear_sync"]["active_project_policy"]
    if policy != "active_delivery_only":
        return True
    project = issue.get("project")
    return bool(project and project.get("name") == contract["repo"]["linear_project"])


def comment_already_present(issue: dict[str, Any], pr_url: str) -> bool:
    if not pr_url:
        return True
    attachments = issue.get("attachments", {}).get("nodes", [])
    if any(node.get("url") == pr_url for node in attachments):
        return True
    comments = issue.get("comments", {}).get("nodes", [])
    return any(pr_url in (node.get("body") or "") for node in comments)


def backfill_comment(pr_url: str) -> str:
    return (
        "Agentic pipeline note: GitHub PR did not auto-attach in Linear, so this comment "
        f"preserves the breadcrumb: {pr_url}"
    )


def handoff_comment(keys: list[str]) -> str:
    if len(keys) > 1:
        return (
            "Linear sync skipped because the GitHub metadata resolves to multiple Linear keys. "
            "Keep exactly one BC key across the branch, title, body, and linked issue."
        )
    return (
        "Linear sync skipped because no Linear key could be resolved from the GitHub metadata. "
        "Add a `Linear: BC-###` line or use the GitHub-only branch format outside the active delivery lane."
    )


def sync_linear_issue(
    *,
    contract: dict[str, Any],
    event: str,
    issue_title: str = "",
    issue_body: str = "",
    pr_title: str = "",
    pr_body: str = "",
    head_ref: str = "",
    pr_url: str = "",
    client: LinearClient | None = None,
) -> dict[str, Any]:
    sync_config = contract["linear_sync"]
    payload: dict[str, Any] = {
        "ok": True,
        "event": event,
        "linear_key": None,
        "linear_keys": resolve_linear_keys(contract, issue_title, issue_body, pr_title, pr_body, head_ref),
        "status": "noop",
        "comment": "",
        "state_changed": False,
        "comment_backfilled": False,
    }
    if not sync_config["enabled"]:
        payload["status"] = "disabled"
        return payload
    if len(payload["linear_keys"]) != 1:
        payload.update(
            {
                "ok": False,
                "status": "needs-human",
                "comment": handoff_comment(payload["linear_keys"]),
            }
        )
        return payload

    payload["linear_key"] = payload["linear_keys"][0]
    desired_state = desired_state_name(contract, event)
    if not client:
        raise RuntimeError("A Linear client is required for live synchronization.")

    issue = client.get_issue(payload["linear_key"])
    payload["issue_identifier"] = issue["identifier"]
    payload["project_name"] = (issue.get("project") or {}).get("name")
    payload["current_state"] = issue.get("state", {}).get("name")

    if not issue_in_active_project(contract, issue):
        payload.update(
            {
                "ok": False,
                "status": "outside-active-project",
                "comment": (
                    "Linear sync skipped because the issue is outside the active delivery project. "
                    f"Expected `{contract['repo']['linear_project']}`."
                ),
            }
        )
        return payload

    if desired_state:
        target_state_id = find_state_id(issue, desired_state)
        if not target_state_id:
            payload.update(
                {
                    "ok": False,
                    "status": "missing-state",
                    "comment": f"Linear sync could not find the `{desired_state}` state in the team workflow.",
                }
            )
            return payload
        if issue.get("state", {}).get("name", "").lower() != desired_state.lower():
            client.update_issue_state(payload["linear_key"], target_state_id)
            payload["state_changed"] = True
            payload["status"] = "updated"
            payload["current_state"] = desired_state

    if pr_url and sync_config["comment_backfill"] and not comment_already_present(issue, pr_url):
        client.create_comment(issue["id"], backfill_comment(pr_url))
        payload["comment_backfilled"] = True
        if payload["status"] == "noop":
            payload["status"] = "commented"

    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--issue-title", default="")
    parser.add_argument("--issue-file", default=None)
    parser.add_argument("--pr-title", default="")
    parser.add_argument("--pr-body-file", default=None)
    parser.add_argument("--head-ref", default="")
    parser.add_argument("--pr-url", default="")
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    root = repo_root()
    contract = load_contract(root)
    token_env = contract["linear_sync"]["api_token_env"]
    token = os.environ.get(token_env, "")
    if token:
        client: LinearClient | None = LinearClient(token)
    else:
        client = None
    if client is None and contract["linear_sync"]["enabled"]:
        payload = {
            "ok": True,
            "event": args.event,
            "status": "missing-token",
            "comment": "",
            "linear_key": None,
            "linear_keys": resolve_linear_keys(
                contract,
                args.issue_title,
                read_text_arg(args.issue_file),
                args.pr_title,
                read_text_arg(args.pr_body_file),
                args.head_ref,
            ),
            "state_changed": False,
            "comment_backfilled": False,
        }
    else:
        payload = sync_linear_issue(
            contract=contract,
            event=args.event,
            issue_title=args.issue_title,
            issue_body=read_text_arg(args.issue_file),
            pr_title=args.pr_title,
            pr_body=read_text_arg(args.pr_body_file),
            head_ref=args.head_ref,
            pr_url=args.pr_url,
            client=client,
        )
    write_json(Path(args.json_output), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
