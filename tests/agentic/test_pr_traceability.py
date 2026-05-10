import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "agentic"))

from pr_traceability import check_traceability  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = json.loads((ROOT / "agentic" / "contract.json").read_text(encoding="utf-8"))


def test_traceability_accepts_linear_pr_metadata():
    result = check_traceability(
        contract=CONTRACT,
        pr_title="BC-77: Harden traceability",
        pr_body="## Related Issues\n\nCloses #77\nLinear: BC-77\n",
        head_ref="codex/BC-77-harden-traceability",
        issue_body="Context for BC-77.\n",
    )

    assert result["ok"]
    assert result["linear_key"] == "BC-77"


def test_traceability_accepts_github_only_branch_contract():
    result = check_traceability(
        contract=CONTRACT,
        pr_title="Tighten release docs",
        pr_body="## Related Issues\n\nRefs #49\n",
        head_ref="codex/issue-49-tighten-release-docs",
        issue_body="GitHub-only follow-up.\n",
    )

    assert result["ok"]
    assert result["linear_key"] is None


def test_traceability_flags_missing_linear_pr_fields():
    result = check_traceability(
        contract=CONTRACT,
        pr_title="Harden traceability",
        pr_body="## Related Issues\n\nCloses #77\n",
        head_ref="codex/BC-77-harden-traceability",
        issue_body="Linear mirror BC-77.\n",
    )

    assert not result["ok"]
    assert "Prefix the PR title" in result["comment"]
    assert "Add `Linear: BC-77`" in result["comment"]


def test_traceability_flags_missing_issue_link():
    result = check_traceability(
        contract=CONTRACT,
        pr_title="BC-77: Harden traceability",
        pr_body="## Related Issues\n\nLinear: BC-77\n",
        head_ref="codex/BC-77-harden-traceability",
        issue_body="Linear mirror BC-77.\n",
    )

    assert not result["ok"]
    assert "Add `Closes #<issue>` or `Refs #<issue>`" in result["comment"]
