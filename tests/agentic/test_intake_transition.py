import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "agentic"))

from common import load_contract  # noqa: E402
from intake_transition import evaluate_intake  # noqa: E402

from test_issue_lint import complete_issue


ROOT = Path(__file__).resolve().parents[2]


def transition(*, event_label: str, labels: list[str], body: str | None = None):
    return evaluate_intake(
        event_name="issues",
        event_action="labeled",
        event_label=event_label,
        issue_body=body or complete_issue(),
        labels=labels,
        contract=load_contract(ROOT),
    )


def test_ready_event_dispatches_once_with_approved_label_snapshot():
    result = transition(event_label="agent:ready", labels=["bug", "agent:ready"])

    assert result["action"] == "dispatch"
    assert result["approved_labels"] == ["bug", "agent:ready"]
    assert result["ready_labels"] == ["agent:ready"]


def test_unrelated_label_event_does_not_relint_running_ready_issue():
    result = transition(
        event_label="documentation",
        labels=["agent:ready", "in-progress", "documentation"],
    )

    assert result["action"] == "ignore"
    assert result["reason"] == "unrelated-event"


def test_in_progress_label_event_does_not_relint_owning_intake():
    result = transition(
        event_label="in-progress",
        labels=["agent:ready", "in-progress"],
    )

    assert result["action"] == "ignore"
    assert result["reason"] == "unrelated-event"


def test_duplicate_ready_delivery_is_ignored_after_transition_is_claimed():
    result = transition(event_label="agent:ready", labels=["bug"])

    assert result["action"] == "ignore"
    assert result["reason"] == "ready-no-longer-present"


def test_independent_ready_attempt_during_in_progress_still_escalates():
    result = transition(
        event_label="agent:ready",
        labels=["agent:ready", "in-progress"],
    )

    assert result["action"] == "escalate"
    assert result["lint"]["stop_labels"] == ["in-progress"]


def test_invalid_ready_issue_escalates_with_all_ready_aliases_claimed():
    body = complete_issue().replace(
        "## Tests/Evals\n\n- Add a regression test.\n\n",
        "",
    )

    result = transition(
        event_label="autonomous",
        labels=["auto-implement", "autonomous"],
        body=body,
    )

    assert result["action"] == "escalate"
    assert result["ready_labels"] == ["auto-implement", "autonomous"]
    assert "Tests/Evals" in result["lint"]["missing_sections"]
