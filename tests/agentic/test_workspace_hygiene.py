from __future__ import annotations

from scripts import workspace_hygiene as hygiene


def test_parse_worktree_porcelain_handles_attached_and_detached_records() -> None:
    records = hygiene.parse_worktree_porcelain(
        """worktree /repo
HEAD abc123
branch refs/heads/main

worktree /tmp/old
HEAD def456
detached
locked still running
"""
    )

    assert records[0].path == "/repo"
    assert records[0].branch == "main"
    assert records[1].detached is True
    assert records[1].locked is True
    assert records[1].lock_reason == "still running"


def test_summarize_status_counts_staged_unstaged_and_untracked_paths() -> None:
    summary = hygiene.summarize_status(" M docs/ROADMAP.md\nA  script.py\n?? scratch.txt\n")

    assert summary.state == "dirty"
    assert summary.path_count == 3
    assert "1 staged" in summary.notes
    assert "1 unstaged" in summary.notes
    assert "1 untracked" in summary.notes


def test_classify_branch_marks_attached_dirty_gone_upstream_as_human_gated() -> None:
    audit = hygiene.classify_branch(
        hygiene.BranchRecord(
            name="codex/stale",
            upstream="origin/codex/stale",
            tracking="[gone]",
        ),
        attached_worktrees={"codex/stale": "/repo"},
        dirty_branches={"codex/stale"},
        merged_branches=set(),
        default_branch_name="main",
    )

    assert audit.risk == "human-gated"
    assert audit.attached_worktree == "/repo"
    assert "attached worktree is dirty" in audit.notes
    assert "upstream is gone; confirm PR/merge/local commits before cleanup" in audit.notes


def test_classify_branch_shortlists_only_unattached_merged_branches() -> None:
    audit = hygiene.classify_branch(
        hygiene.BranchRecord(
            name="codex/merged",
            upstream="origin/codex/merged",
            tracking="",
        ),
        attached_worktrees={},
        dirty_branches=set(),
        merged_branches={"codex/merged"},
        default_branch_name="main",
    )

    assert audit.risk == "safe-to-review"
    assert audit.notes == ("merged into origin/main; deletion still requires approval",)


def test_worktree_classification_shortlists_clean_detached_only() -> None:
    record = hygiene.WorktreeRecord(path="/tmp/wt", head="abc123", detached=True)
    risk, notes = hygiene.classify_worktree(record, hygiene.StatusSummary(state="clean"))

    assert risk == "safe-to-review"
    assert "clean detached worktree; confirm no active session before any removal" in notes


def test_worktree_classification_keeps_missing_prunable_entries_human_gated() -> None:
    record = hygiene.WorktreeRecord(path="/tmp/missing", prunable=True, prune_reason="not found")
    risk, notes = hygiene.classify_worktree(
        record,
        hygiene.StatusSummary(
            state="missing",
            notes=("worktree path is missing; cleanup remains human-gated",),
        ),
    )

    assert risk == "human-gated"
    assert "git marks prunable: not found" in notes
    assert "worktree path is missing; cleanup remains human-gated" in notes


def test_render_report_keeps_cleanup_gate_explicit() -> None:
    payload = {
        "repo": "/repo",
        "default_branch": "main",
        "summary": {
            "worktrees": 0,
            "dirty_worktrees": 0,
            "attached_branches": 0,
            "gone_upstreams": 0,
            "bulk_hints": 0,
            "safe_to_review_items": 0,
            "human_gated_items": 0,
        },
        "worktrees": [],
        "branches": [],
        "bulk_hints": [],
    }

    report = hygiene.render_report(payload)

    assert "Mode: read-only" in report
    assert "not permission to delete" in report
