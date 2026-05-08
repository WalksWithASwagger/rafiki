from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _workflow(name: str) -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text())


def test_dev_loop_maps_pause_variable_into_runner_env():
    workflow = _workflow("agentic-dev-loop.yml")

    env = workflow["jobs"]["run"]["env"]

    assert env["LOOP_PAUSED"] == "${{ vars.LOOP_PAUSED || 'false' }}"


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
