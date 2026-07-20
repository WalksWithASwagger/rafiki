import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "agentic"))

from pr_traceability import check_traceability  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = json.loads((ROOT / "agentic" / "contract.json").read_text(encoding="utf-8"))


def test_traceability_accepts_matching_closes_link():
    result = check_traceability(
        contract=CONTRACT,
        pr_body="## Related Issues\n\nCloses #77\n",
        head_ref="codex/issue-77-harden-traceability",
    )

    assert result["ok"]
    assert result["linked_issue"] == "77"
    assert result["branch_issue"] == "77"


def test_traceability_accepts_matching_refs_link():
    result = check_traceability(
        contract=CONTRACT,
        pr_body="## Related Issues\n\nRefs #49\n",
        head_ref="codex/issue-49-tighten-release-docs",
    )

    assert result["ok"]
    assert result["linked_issue_verb"] == "Refs"


def test_traceability_flags_mismatched_issue_numbers():
    result = check_traceability(
        contract=CONTRACT,
        pr_body="## Related Issues\n\nCloses #77\n",
        head_ref="codex/issue-76-harden-traceability",
    )

    assert not result["ok"]
    assert "must match linked issue `#77`" in result["comment"]


def test_traceability_flags_missing_issue_link():
    result = check_traceability(
        contract=CONTRACT,
        pr_body="## Related Issues\n",
        head_ref="codex/issue-77-harden-traceability",
    )

    assert not result["ok"]
    assert "Add `Closes #<issue>` or `Refs #<issue>`" in result["comment"]


def test_traceability_flags_noncanonical_branch():
    result = check_traceability(
        contract=CONTRACT,
        pr_body="## Related Issues\n\nRefs #77\n",
        head_ref="feature/harden-traceability",
    )

    assert not result["ok"]
    assert "Use `codex/issue-<number>-<slug>`" in result["comment"]
