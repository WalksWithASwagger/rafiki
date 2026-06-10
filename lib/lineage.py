"""Read-only archive lineage helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lib.registry import AssetEntry


COMPARISON_FIELDS = (
    ("title", "Title"),
    ("prompt", "Prompt"),
    ("model", "Model"),
    ("style", "Style"),
    ("aspect_ratio", "Aspect"),
    ("run_id", "Run"),
    ("metadata_states", "Archive State"),
)


def _display_value(record: dict[str, Any], field: str) -> str:
    if field == "title":
        return str(record.get("title") or record.get("name") or "").strip()
    if field == "prompt":
        return str(record.get("source_prompt") or record.get("prompt") or record.get("caption") or "").strip()
    value = record.get(field)
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def _comparison_changes(source: dict[str, Any], target: dict[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for field, label in COMPARISON_FIELDS:
        before = _display_value(source, field)
        after = _display_value(target, field)
        if not before and not after:
            continue
        changes.append({
            "field": field,
            "label": label,
            "before": before,
            "after": after,
            "changed": before != after,
        })
    return changes


def annotate_lineage_comparisons(records: list[dict[str, Any]]) -> None:
    by_file = {str(record.get("file") or ""): record for record in records if record.get("file")}
    by_index = {str(record.get("file") or ""): index for index, record in enumerate(records) if record.get("file")}

    for record in records:
        target_key = str(record.get("superseded_by") or "").strip()
        if not target_key:
            continue

        comparison: dict[str, Any] = {
            "source_key": str(record.get("file") or ""),
            "target_key": target_key,
            "status": "missing-target",
            "message": "Comparison target is not in the current local archive.",
        }

        target = by_file.get(target_key)
        if target:
            comparison.update({
                "status": "linked",
                "target_index": by_index.get(target_key),
                "target_title": _display_value(target, "title"),
                "target_run_id": _display_value(target, "run_id"),
                "target_project": _display_value(target, "project"),
                "changes": _comparison_changes(record, target),
            })

        record["lineage_comparison"] = comparison


# ── lineage suggestion heuristics ────────────────────────────────────────────

# Version/variant suffixes that mark a file as a derivative of another.
_VERSION_SUFFIX_RE = re.compile(
    r"[-_](?:v\d+|r\d+|alt\d*|retry\d*|take\d*|\d+)$",
    re.IGNORECASE,
)


def _slug_base(slug: str) -> str:
    """Strip trailing version/variant suffixes to get a canonical base slug.

    Iterates so that chained suffixes like ``hero-v2-alt`` reduce to ``hero``.
    """
    result = slug.lower()
    while True:
        trimmed = _VERSION_SUFFIX_RE.sub("", result)
        if trimmed == result:
            break
        result = trimmed
    return result.strip("-_")


def _title_words(title: str) -> frozenset[str]:
    """Return a frozenset of lowercase alphabetic words from a title (length >= 3)."""
    return frozenset(w for w in re.findall(r"[a-z]{3,}", title.lower()))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _path_stem(entry: "AssetEntry") -> str:
    """Return the filename stem (no extension) for an AssetEntry path."""
    return Path(entry.path).stem if entry.path else entry.id


def suggest_lineage_candidates(
    entries: "list[AssetEntry]",
    *,
    title_jaccard_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    """Return read-only lineage suggestions for entries without an explicit link.

    Pairs two entries in the same project when they share a slug base (after
    stripping version suffixes) OR when their titles have significant word
    overlap.  Pairs already connected by an explicit ``superseded_by`` link are
    excluded.

    Each suggestion is a dict::

        {
            "source_id": str,
            "candidate_id": str,
            "source_path": str,
            "candidate_path": str,
            "project": str,
            "reasons": list[str],   # human-readable explanation
        }

    The list is ordered: (source, candidate) with source_id < candidate_id so
    each unique pair appears exactly once.
    """
    # Collect ids referenced by explicit superseded_by links to suppress them.
    explicitly_linked: set[tuple[str, str]] = set()
    for entry in entries:
        if entry.superseded_by:
            a, b = entry.id, entry.superseded_by
            explicitly_linked.add((a, b) if a < b else (b, a))

    # Group by project for O(project-size^2) pairwise comparison.
    by_project: dict[str, list["AssetEntry"]] = {}
    for entry in entries:
        by_project.setdefault(entry.project, []).append(entry)

    suggestions: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for project, group in by_project.items():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                pair = (a.id, b.id) if a.id < b.id else (b.id, a.id)
                if pair in seen_pairs or pair in explicitly_linked:
                    continue

                reasons: list[str] = []

                # Heuristic 1: slug base match.
                a_stem = _slug_base(re.sub(r"[^a-z0-9-]", "-", _path_stem(a)))
                b_stem = _slug_base(re.sub(r"[^a-z0-9-]", "-", _path_stem(b)))
                if a_stem and b_stem and a_stem == b_stem and a_stem != project.lower():
                    reasons.append(f"slug base match: {a_stem!r}")

                # Heuristic 2: title word overlap.
                a_words = _title_words(a.title)
                b_words = _title_words(b.title)
                j = _jaccard(a_words, b_words)
                if j >= title_jaccard_threshold:
                    reasons.append(f"title overlap: {j:.0%} ({', '.join(sorted(a_words & b_words))})")

                if not reasons:
                    continue

                seen_pairs.add(pair)
                suggestions.append({
                    "source_id": pair[0],
                    "candidate_id": pair[1],
                    "source_path": a.path if a.id == pair[0] else b.path,
                    "candidate_path": b.path if a.id == pair[0] else a.path,
                    "project": project,
                    "reasons": reasons,
                })

    return suggestions
