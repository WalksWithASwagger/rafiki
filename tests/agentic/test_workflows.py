import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _workflow(name: str) -> dict:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text())
    if True in workflow and "on" not in workflow:
        workflow["on"] = workflow[True]
    return workflow


def test_dev_loop_maps_pause_variable_into_runner_env():
    workflow = _workflow("agentic-dev-loop.yml")

    env = workflow["jobs"]["run"]["env"]

    assert env["LOOP_PAUSED"] == "${{ vars.LOOP_PAUSED || 'false' }}"


def test_active_workflows_do_not_invoke_linear_sync():
    secret_name = "_".join(("LINEAR", "API", "KEY"))
    client_name = "_".join(("linear", "sync")) + ".py"

    for name in ("agentic-dev-loop.yml", "agentic-traceability.yml"):
        text = (ROOT / ".github" / "workflows" / name).read_text()

        assert secret_name not in text
        assert client_name not in text


def test_contract_uses_github_issue_traceability():
    contract = json.loads((ROOT / "agentic" / "contract.json").read_text())
    retired_team_field = "_".join(("linear", "team"))
    retired_project_field = "_".join(("linear", "project"))

    assert contract["branch_template"] == "codex/issue-{issue_number}-{slug}"
    assert contract["pr_requirements"] == {
        "require_issue_link": True,
        "issue_link_verbs": ["Closes", "Refs"],
        "branch_prefix": "codex/",
        "issue_prefix": "issue-",
    }
    assert retired_team_field not in contract["repo"]
    assert retired_project_field not in contract["repo"]


def test_retired_external_sync_remains_disabled():
    contract = json.loads((ROOT / "agentic" / "contract.json").read_text())
    retired_sync_field = "_".join(("linear", "sync"))

    assert contract[retired_sync_field] == {"enabled": False}


def test_issue_quality_only_accepts_ready_label_events():
    workflow = _workflow("agentic-issue-quality.yml")

    assert workflow["on"]["issues"]["types"] == ["labeled"]
    gate = workflow["jobs"]["gate"]
    assert "agent:ready" in gate["if"]
    assert "auto-implement" in gate["if"]
    assert "autonomous" in gate["if"]


def test_issue_quality_claims_ready_before_dispatching_dev_loop():
    workflow = _workflow("agentic-issue-quality.yml")
    steps = workflow["jobs"]["gate"]["steps"]
    names = [step.get("name") for step in steps]

    assert workflow["permissions"]["actions"] == "write"
    assert names.index("Claim approved ready transition") < names.index(
        "Dispatch approved dev loop"
    )
    dispatch = next(step for step in steps if step.get("name") == "Dispatch approved dev loop")
    assert "quality_labels" in dispatch["run"]
    assert "provider=noop" in dispatch["run"]
    assert "AGENTIC_PROVIDER" not in dispatch.get("env", {})


def test_dev_loop_starts_only_from_dispatch_and_validates_before_progress():
    workflow = _workflow("agentic-dev-loop.yml")

    assert "issues" not in workflow["on"]
    assert "quality_labels" in workflow["on"]["workflow_dispatch"]["inputs"]
    steps = workflow["jobs"]["run"]["steps"]
    names = [step.get("name") for step in steps]
    assert names.index("Validate approved intake") < names.index("Create work branch")
    assert names.index("Validate approved intake") < names.index("Mark issue in progress")


def test_dev_loop_branch_uses_only_the_github_issue_number():
    workflow = _workflow("agentic-dev-loop.yml")
    steps = workflow["jobs"]["run"]["steps"]
    branch_step = next(step for step in steps if step.get("name") == "Create work branch")

    assert 'ref = f"issue-{os.environ[\'ISSUE_NUMBER\']}"' in branch_step["run"]


def test_intake_workflows_serialize_duplicate_deliveries_without_cancellation():
    for name in ("agentic-issue-quality.yml", "agentic-dev-loop.yml"):
        workflow = _workflow(name)

        assert workflow["concurrency"]["cancel-in-progress"] is False


def test_ci_runs_documented_contract_commands():
    workflow = _workflow("ci.yml")
    steps = workflow["jobs"]["test"]["steps"]
    commands = [step.get("run") for step in steps if "run" in step]

    assert "npm test" in commands
    assert "npm run pack:check" in commands
    assert "npm run doctor" in commands


def test_traceability_workflow_listens_for_pr_events_only():
    workflow = _workflow("agentic-traceability.yml")

    pr_types = workflow["on"]["pull_request"]["types"]

    assert "closed" in pr_types
    assert "converted_to_draft" in pr_types
    assert "issues" not in workflow["on"]
