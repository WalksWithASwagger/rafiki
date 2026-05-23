import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "agentic"))

from linear_sync import sync_linear_issue  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = json.loads((ROOT / "agentic" / "contract.json").read_text(encoding="utf-8"))


class FakeLinearClient:
    def __init__(self, issue):
        self.issue = issue
        self.updated_states = []
        self.comments = []

    def get_issue(self, identifier):
        assert identifier == self.issue["identifier"]
        return self.issue

    def update_issue_state(self, identifier, state_id):
        assert identifier == self.issue["identifier"]
        self.updated_states.append(state_id)
        for state in self.issue["team"]["states"]["nodes"]:
            if state["id"] == state_id:
                self.issue["state"] = state
                break
        return {"success": True, "issue": self.issue}

    def create_comment(self, issue_id, body):
        assert issue_id == self.issue["id"]
        self.comments.append(body)
        self.issue["comments"]["nodes"].append({"id": f"comment-{len(self.comments)}", "body": body})
        return {"success": True, "comment": {"id": f"comment-{len(self.comments)}"}}


def issue_fixture(state_name="Todo", project_name=None):
    project_name = project_name or CONTRACT["repo"]["linear_project"]
    states = [
        {"id": "todo", "name": "Todo", "type": "unstarted"},
        {"id": "progress", "name": "In Progress", "type": "started"},
        {"id": "review", "name": "In Review", "type": "started"},
        {"id": "done", "name": "Done", "type": "completed"},
    ]
    return {
        "id": "issue-id",
        "identifier": "BC-77",
        "title": "Harden traceability",
        "state": next(state for state in states if state["name"] == state_name),
        "project": {"id": "project-id", "name": project_name},
        "team": {"id": "team-id", "key": "BC", "states": {"nodes": states}},
        "attachments": {"nodes": []},
        "comments": {"nodes": []},
    }


def test_linear_sync_moves_issue_to_in_progress():
    client = FakeLinearClient(issue_fixture())

    result = sync_linear_issue(
        contract=CONTRACT,
        event="issue-in-progress",
        issue_title="Harden traceability",
        issue_body="Mirror BC-77.\n",
        client=client,
    )

    assert result["ok"]
    assert result["state_changed"] is True
    assert client.issue["state"]["name"] == "In Progress"


def test_linear_sync_backfills_pr_comment_when_attachment_is_missing():
    client = FakeLinearClient(issue_fixture(state_name="In Progress"))

    result = sync_linear_issue(
        contract=CONTRACT,
        event="pr-open",
        pr_title="BC-77: Harden traceability",
        pr_body="Closes #77\nLinear: BC-77\n",
        head_ref="codex/BC-77-harden-traceability",
        pr_url="https://github.com/WalksWithASwagger/rafiki/pull/77",
        client=client,
    )

    assert result["ok"]
    assert result["comment_backfilled"] is True
    assert client.issue["state"]["name"] == "In Review"
    assert client.comments


def test_linear_sync_treats_no_linear_key_as_github_only():
    client = FakeLinearClient(issue_fixture())

    result = sync_linear_issue(
        contract=CONTRACT,
        event="pr-open",
        pr_title="Refresh roadmap truth",
        pr_body="Refs #141\n",
        head_ref="codex/issue-141-roadmap-truth",
        issue_body="Relevant files: docs/WORKPLAN-2026-05-21.md\n",
        pr_url="https://github.com/WalksWithASwagger/rafiki/pull/149",
        client=client,
    )

    assert result["ok"]
    assert result["status"] == "github-only"
    assert result["linear_keys"] == []
    assert client.updated_states == []
    assert client.comments == []


def test_linear_sync_returns_handoff_when_linear_key_is_ambiguous():
    client = FakeLinearClient(issue_fixture())

    result = sync_linear_issue(
        contract=CONTRACT,
        event="pr-open",
        pr_title="BC-77: Harden traceability",
        pr_body="Closes #77\nLinear: BC-70\n",
        head_ref="codex/BC-77-harden-traceability",
        client=client,
    )

    assert not result["ok"]
    assert result["status"] == "needs-human"
    assert "multiple Linear keys" in result["comment"]
    assert client.updated_states == []


def test_linear_sync_skips_issue_outside_active_project():
    client = FakeLinearClient(issue_fixture(project_name="Some Other Project"))

    result = sync_linear_issue(
        contract=CONTRACT,
        event="issue-in-progress",
        issue_body="Mirror BC-77.\n",
        client=client,
    )

    assert not result["ok"]
    assert result["status"] == "outside-active-project"
    assert client.updated_states == []
