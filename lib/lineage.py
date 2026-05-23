"""Read-only archive lineage helpers."""

from __future__ import annotations

from typing import Any


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
