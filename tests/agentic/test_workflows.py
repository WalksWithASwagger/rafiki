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
    assert env["LINEAR_API_KEY"] == "${{ secrets.LINEAR_API_KEY }}"


def test_issue_quality_skips_in_progress_label_event():
    workflow = _workflow("agentic-issue-quality.yml")

    gate = workflow["jobs"]["gate"]

    assert "github.event.label.name != 'in-progress'" in gate["if"]


def test_ci_runs_documented_contract_commands():
    workflow = _workflow("ci.yml")
    steps = workflow["jobs"]["test"]["steps"]
    commands = [step.get("run") for step in steps if "run" in step]

    assert "npm test" in commands
    assert "npm run pack:check" in commands
    assert "npm run doctor" in commands


def test_traceability_workflow_listens_for_pr_and_in_progress_events():
    workflow = _workflow("agentic-traceability-sync.yml")

    pr_types = workflow["on"]["pull_request"]["types"]
    issue_types = workflow["on"]["issues"]["types"]

    assert "closed" in pr_types
    assert "converted_to_draft" in pr_types
    assert "labeled" in issue_types
