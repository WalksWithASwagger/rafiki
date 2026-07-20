import json
import subprocess
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


def test_active_delivery_instructions_are_github_only():
    active_paths = (
        "docs/DELIVERY-PIPELINE.md",
        "docs/INDEX.md",
        "docs/ROADMAP.md",
        "docs/FOLDER-LAYOUT.md",
        "meta/routines/SETUP.md",
        "meta/routines/dev-loop-runner.prompt.md",
        "meta/routines/auto-merge-gate.prompt.md",
        ".github/ISSUE_TEMPLATE/agentic-task.md",
        ".agents/skills/rafiki-github-issue-writer/SKILL.md",
        ".agents/skills/rafiki-github-pr-reviewer/SKILL.md",
        ".claude/commands/agentic-intake.md",
        ".company-os/project.yaml",
    )
    retired_secret = "_".join(("linear", "api", "key"))

    for relative_path in active_paths:
        text = (ROOT / relative_path).read_text().lower()
        if relative_path == "docs/DELIVERY-PIPELINE.md":
            assert text.count(retired_secret) == 1
            text = text.replace(retired_secret, "")

        assert "linear" not in text, relative_path


def test_agentic_issue_template_matches_required_sections():
    contract = json.loads((ROOT / "agentic" / "contract.json").read_text())
    template = (ROOT / ".github/ISSUE_TEMPLATE/agentic-task.md").read_text()

    for section in contract["issue_quality"]["required_sections"]:
        assert f"## {section}" in template


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


def test_ci_runs_canonical_deterministic_verification():
    workflow = _workflow("ci.yml")
    steps = workflow["jobs"]["test"]["steps"]
    commands = [step.get("run") for step in steps if "run" in step]

    assert "npm run verify" in commands


def test_ci_installs_and_checks_hashed_python_lock():
    workflow = _workflow("ci.yml")
    steps = workflow["jobs"]["test"]["steps"]
    commands = [step.get("run") for step in steps if "run" in step]

    assert "python -m pip install --require-hashes -r requirements-ci.txt" in commands
    assert any(
        "npm run lock:python-ci" in command
        and "git diff --exit-code -- requirements-ci.txt" in command
        for command in commands
    )
    assert "python -m pip_audit -r requirements-ci.txt" in commands


def test_verify_script_covers_every_deterministic_ci_gate():
    package = json.loads((ROOT / "package.json").read_text())
    package_lock = json.loads((ROOT / "package-lock.json").read_text())
    frontend_package = json.loads((ROOT / "frontend" / "package.json").read_text())
    frontend_lock = json.loads(
        (ROOT / "frontend" / "package-lock.json").read_text()
    )
    workflow = _workflow("ci.yml")
    setup_node = next(
        step
        for step in workflow["jobs"]["test"]["steps"]
        if step.get("name") == "Set up Node.js"
    )

    assert package["engines"]["node"] == ">=22.12.0"
    assert package_lock["packages"][""]["engines"]["node"] == ">=22.12.0"
    assert frontend_package["engines"]["node"] == ">=22.12.0"
    assert frontend_lock["packages"][""]["engines"]["node"] == ">=22.12.0"
    assert setup_node["with"]["node-version"] == "22.12"
    assert package["scripts"]["verify"].split(" && ") == [
        "npm run lint",
        "npm test",
        "npm run frontend:verify",
        "npm run e2e:portal",
        "npm run docs:check",
        "npm run public:check",
        "npm run smoke:dry-run",
        "npm run pack:check",
        "npm run doctor",
    ]


def test_policy_workflow_covers_pr_lifecycle_and_label_changes():
    workflow = _workflow("agentic-traceability.yml")

    pr_types = set(workflow["on"]["pull_request"]["types"])

    assert {
        "opened",
        "edited",
        "synchronize",
        "reopened",
        "ready_for_review",
        "converted_to_draft",
        "closed",
        "labeled",
        "unlabeled",
    } <= pr_types
    assert "issues" not in workflow["on"]
    policy = workflow["jobs"]["policy"]
    assert policy["name"] == "policy"
    assert workflow["permissions"] == {
        "contents": "read",
        "issues": "write",
        "pull-requests": "read",
    }
    names = [step.get("name") for step in policy["steps"]]
    assert names.index("Comment traceability drift") < names.index("Enforce policy")


def test_automation_never_removes_stop_labels():
    workflows = (ROOT / ".github" / "workflows").glob("agentic-*.yml")

    for workflow in workflows:
        text = workflow.read_text()
        assert '--remove-label "needs-human"' not in text, workflow.name
        assert '--remove-label "blocked"' not in text, workflow.name


def test_policy_workflow_shell_steps_parse():
    workflow = _workflow("agentic-traceability.yml")

    for step in workflow["jobs"]["policy"]["steps"]:
        if "run" not in step:
            continue
        result = subprocess.run(
            ["bash", "-n"],
            input=step["run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"{step['name']}: {result.stderr}"
