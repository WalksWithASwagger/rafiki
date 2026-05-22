#!/usr/bin/env python3
"""Read-only workspace hygiene report for Rafiki maintainers."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

BULK_CANDIDATES = {
    "node_modules": "dependency install",
    ".venv": "Python environment",
    "venv": "Python environment",
    ".pytest_cache": "test cache",
    ".mypy_cache": "type-check cache",
    ".ruff_cache": "lint cache",
    ".next": "web build cache",
    "dist": "build output",
    "build": "build output",
    "coverage": "coverage output",
    "htmlcov": "coverage output",
    "output": "Rafiki generated output",
    "outputs": "generated output",
}


@dataclass(frozen=True)
class WorktreeRecord:
    path: str
    head: str = ""
    branch: str = ""
    detached: bool = False
    bare: bool = False
    locked: bool = False
    lock_reason: str = ""
    prunable: bool = False
    prune_reason: str = ""


@dataclass(frozen=True)
class BranchRecord:
    name: str
    object_name: str = ""
    upstream: str = ""
    tracking: str = ""


@dataclass(frozen=True)
class StatusSummary:
    state: str
    path_count: int = 0
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class BulkHint:
    worktree: str
    path: str
    kind: str
    ignored: bool
    size_bytes: int | None = None


@dataclass(frozen=True)
class WorktreeAudit:
    path: str
    branch: str
    head: str
    status: str
    path_count: int
    risk: str
    notes: tuple[str, ...]
    bulk_hints: tuple[BulkHint, ...]


@dataclass(frozen=True)
class BranchAudit:
    name: str
    upstream: str
    tracking: str
    attached_worktree: str
    risk: str
    notes: tuple[str, ...]


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    except OSError as exc:
        return subprocess.CompletedProcess(command, 1, "", str(exc))


def git_output(repo: Path, args: list[str]) -> str:
    result = run(["git", *args], cwd=repo)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def resolve_repo(path: Path) -> Path:
    return Path(git_output(path, ["rev-parse", "--show-toplevel"]).strip())


def default_branch(repo: Path) -> str:
    result = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=repo)
    if result.returncode == 0:
        ref = result.stdout.strip()
        if ref.startswith("origin/"):
            return ref.removeprefix("origin/")
        if ref:
            return ref
    return "main"


def parse_worktree_porcelain(text: str) -> list[WorktreeRecord]:
    records: list[WorktreeRecord] = []
    current: dict[str, Any] = {}

    def flush() -> None:
        if not current:
            return
        records.append(WorktreeRecord(**current))
        current.clear()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            flush()
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            flush()
            current["path"] = value
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "detached":
            current["detached"] = True
        elif key == "bare":
            current["bare"] = True
        elif key == "locked":
            current["locked"] = True
            current["lock_reason"] = value
        elif key == "prunable":
            current["prunable"] = True
            current["prune_reason"] = value
    flush()
    return records


def parse_branch_records(text: str) -> list[BranchRecord]:
    records: list[BranchRecord] = []
    for line in text.splitlines():
        if not line:
            continue
        name, object_name, upstream, tracking = (line.split("\0") + ["", "", "", ""])[:4]
        records.append(
            BranchRecord(
                name=name,
                object_name=object_name,
                upstream=upstream,
                tracking=tracking,
            )
        )
    return records


def summarize_status(text: str) -> StatusSummary:
    lines = [line for line in text.splitlines() if line]
    if not lines:
        return StatusSummary(state="clean")

    untracked = sum(1 for line in lines if line.startswith("??"))
    staged = sum(1 for line in lines if not line.startswith("??") and line[0] != " ")
    unstaged = sum(1 for line in lines if not line.startswith("??") and len(line) > 1 and line[1] != " ")
    notes: list[str] = [f"{len(lines)} changed path(s)"]
    if staged:
        notes.append(f"{staged} staged")
    if unstaged:
        notes.append(f"{unstaged} unstaged")
    if untracked:
        notes.append(f"{untracked} untracked")
    return StatusSummary(state="dirty", path_count=len(lines), notes=tuple(notes))


def inspect_status(worktree: Path) -> StatusSummary:
    if not worktree.exists():
        return StatusSummary(
            state="missing",
            notes=("worktree path is missing; cleanup remains human-gated",),
        )
    result = run(["git", "status", "--porcelain=v1"], cwd=worktree)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git status failed"
        return StatusSummary(state="unknown", notes=(detail,))
    return summarize_status(result.stdout)


def classify_worktree(record: WorktreeRecord, status: StatusSummary) -> tuple[str, tuple[str, ...]]:
    notes: list[str] = []
    risk = "human-gated"

    if record.locked:
        notes.append(f"locked worktree{': ' + record.lock_reason if record.lock_reason else ''}")
    if record.prunable:
        notes.append(f"git marks prunable{': ' + record.prune_reason if record.prune_reason else ''}")
    if status.state == "dirty":
        notes.extend(status.notes)
    elif status.state not in {"clean", "dirty"}:
        notes.extend(status.notes)
    if record.branch:
        notes.append(f"branch checked out: {record.branch}")
    elif record.detached:
        notes.append("detached HEAD")

    if status.state == "clean" and record.detached and not record.locked:
        risk = "safe-to-review"
        notes.append("clean detached worktree; confirm no active session before any removal")
    elif status.state == "clean":
        notes.append("clean, but still attached to an active checkout")

    return risk, tuple(notes)


def classify_branch(
    record: BranchRecord,
    *,
    attached_worktrees: dict[str, str],
    dirty_branches: set[str],
    merged_branches: set[str],
    default_branch_name: str,
) -> BranchAudit:
    notes: list[str] = []
    risk = "informational"
    attached = attached_worktrees.get(record.name, "")

    if record.name == default_branch_name:
        risk = "preserve"
        notes.append("default branch")
    if attached:
        if record.name != default_branch_name:
            risk = "human-gated"
        notes.append(f"checked out at {attached}")
    if record.name in dirty_branches:
        if record.name != default_branch_name:
            risk = "human-gated"
        notes.append("attached worktree is dirty")
    if "[gone]" in record.tracking:
        risk = "human-gated"
        notes.append("upstream is gone; confirm PR/merge/local commits before cleanup")
    if "[ahead" in record.tracking:
        risk = "human-gated"
        notes.append("branch has local commits ahead of upstream")
    if not record.upstream and record.name != default_branch_name:
        risk = "human-gated"
        notes.append("no upstream configured")

    if risk == "informational" and record.name in merged_branches and record.name != default_branch_name:
        risk = "safe-to-review"
        notes.append(f"merged into origin/{default_branch_name}; deletion still requires approval")
    if not notes:
        notes.append("no cleanup signal")

    return BranchAudit(
        name=record.name,
        upstream=record.upstream,
        tracking=record.tracking,
        attached_worktree=attached,
        risk=risk,
        notes=tuple(notes),
    )


def path_size(path: Path) -> int | None:
    du = shutil.which("du")
    if du:
        result = subprocess.run([du, "-sk", str(path)], text=True, capture_output=True)
        if result.returncode == 0:
            raw = result.stdout.split()[0]
            if raw.isdigit():
                return int(raw) * 1024

    total = 0
    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [name for name in dirs if not Path(root, name).is_symlink()]
            for filename in files:
                candidate = Path(root, filename)
                if not candidate.is_symlink():
                    total += candidate.stat().st_size
    except OSError:
        return None
    return total


def is_ignored(worktree: Path, path: Path) -> bool:
    result = run(["git", "check-ignore", "-q", "--", str(path.relative_to(worktree))], cwd=worktree)
    return result.returncode == 0


def collect_bulk_hints(worktree: Path, *, include_sizes: bool) -> tuple[BulkHint, ...]:
    hints: list[BulkHint] = []
    for name, kind in BULK_CANDIDATES.items():
        candidate = worktree / name
        if not candidate.is_dir():
            continue
        hints.append(
            BulkHint(
                worktree=str(worktree),
                path=str(candidate),
                kind=kind,
                ignored=is_ignored(worktree, candidate),
                size_bytes=path_size(candidate) if include_sizes else None,
            )
        )
    return tuple(hints)


def merged_branch_names(repo: Path, default_branch_name: str) -> set[str]:
    result = run(
        ["git", "branch", "--merged", f"origin/{default_branch_name}", "--format=%(refname:short)"],
        cwd=repo,
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def build_report(repo_path: Path, *, include_sizes: bool = True) -> dict[str, Any]:
    repo = resolve_repo(repo_path)
    default_branch_name = default_branch(repo)
    worktree_records = parse_worktree_porcelain(git_output(repo, ["worktree", "list", "--porcelain"]))
    branch_format = "%(refname:short)%00%(objectname:short)%00%(upstream:short)%00%(upstream:track)"
    branch_records = parse_branch_records(
        git_output(repo, ["for-each-ref", f"--format={branch_format}", "refs/heads"])
    )

    attached_worktrees = {record.branch: record.path for record in worktree_records if record.branch}
    dirty_branches: set[str] = set()
    worktree_audits: list[WorktreeAudit] = []

    for record in worktree_records:
        worktree_path = Path(record.path)
        status = inspect_status(worktree_path)
        if status.state == "dirty" and record.branch:
            dirty_branches.add(record.branch)
        risk, notes = classify_worktree(record, status)
        worktree_audits.append(
            WorktreeAudit(
                path=record.path,
                branch=record.branch,
                head=record.head,
                status=status.state,
                path_count=status.path_count,
                risk=risk,
                notes=notes,
                bulk_hints=collect_bulk_hints(worktree_path, include_sizes=include_sizes),
            )
        )

    merged = merged_branch_names(repo, default_branch_name)
    branch_audits = [
        classify_branch(
            record,
            attached_worktrees=attached_worktrees,
            dirty_branches=dirty_branches,
            merged_branches=merged,
            default_branch_name=default_branch_name,
        )
        for record in branch_records
    ]
    bulk_hints = [hint for audit in worktree_audits for hint in audit.bulk_hints]

    summary = {
        "worktrees": len(worktree_audits),
        "dirty_worktrees": sum(1 for audit in worktree_audits if audit.status == "dirty"),
        "gone_upstreams": sum(1 for audit in branch_audits if "[gone]" in audit.tracking),
        "attached_branches": sum(1 for audit in branch_audits if audit.attached_worktree),
        "bulk_hints": len(bulk_hints),
        "safe_to_review_items": sum(
            1 for audit in [*worktree_audits, *branch_audits] if audit.risk == "safe-to-review"
        ),
        "human_gated_items": sum(
            1 for audit in [*worktree_audits, *branch_audits] if audit.risk == "human-gated"
        ),
    }

    return {
        "repo": str(repo),
        "default_branch": default_branch_name,
        "read_only": True,
        "summary": summary,
        "worktrees": [asdict(audit) for audit in worktree_audits],
        "branches": [asdict(audit) for audit in branch_audits],
        "bulk_hints": [asdict(hint) for hint in bulk_hints],
    }


def format_bytes(size_bytes: int | None) -> str:
    if size_bytes is None:
        return "size not measured"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size_bytes} B"


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "Rafiki Workspace Hygiene Report",
        f"Repo: {payload['repo']}",
        f"Default branch: {payload['default_branch']}",
        "Mode: read-only; no branches, worktrees, stashes, dependencies, or output were deleted.",
        "",
        "Summary",
        f"- Worktrees: {summary['worktrees']} ({summary['dirty_worktrees']} dirty)",
        f"- Branches attached to worktrees: {summary['attached_branches']}",
        f"- Gone upstreams: {summary['gone_upstreams']}",
        f"- Dependency/bulk hints: {summary['bulk_hints']}",
        f"- Safe-to-review items: {summary['safe_to_review_items']}",
        f"- Human-gated items: {summary['human_gated_items']}",
        "",
        "Worktrees",
    ]
    for audit in payload["worktrees"]:
        branch = audit["branch"] or "detached"
        lines.append(f"- {audit['path']} [{branch}] {audit['status']} -> {audit['risk']}")
        for note in audit["notes"]:
            lines.append(f"  - {note}")

    lines.extend(["", "Branches"])
    for audit in payload["branches"]:
        upstream = audit["upstream"] or "no upstream"
        tracking = f" {audit['tracking']}" if audit["tracking"] else ""
        lines.append(f"- {audit['name']} -> {audit['risk']} ({upstream}{tracking})")
        for note in audit["notes"]:
            lines.append(f"  - {note}")

    lines.extend(["", "Dependency/Bulk Hints"])
    if payload["bulk_hints"]:
        for hint in payload["bulk_hints"]:
            ignored = "ignored" if hint["ignored"] else "not ignored"
            lines.append(
                f"- {hint['path']} ({hint['kind']}, {ignored}, {format_bytes(hint['size_bytes'])})"
            )
    else:
        lines.append("- None found in known dependency/cache/output directories.")

    lines.extend(
        [
            "",
            "Cleanup Gate",
            "- Treat safe-to-review as a shortlist for human inspection, not permission to delete.",
            "- Anything dirty, attached to a worktree, ahead of upstream, local-only, locked, or gone-upstream is human-gated.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Any path inside the Rafiki git repository.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--no-size", action="store_true", help="Skip filesystem size measurement.")
    args = parser.parse_args()

    try:
        payload = build_report(Path(args.repo), include_sizes=not args.no_size)
    except RuntimeError as exc:
        print(f"workspace hygiene audit failed: {exc}")
        return 2

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_report(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
