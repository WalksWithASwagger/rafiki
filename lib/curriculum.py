"""Curriculum Atlas helpers for connecting archive assets to teaching maps."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ATLAS_PATH = REPO_ROOT / "config" / "curriculum-atlas.json"


def load_curriculum_atlas(path: Path | None = None) -> dict:
    atlas_path = Path(path) if path else DEFAULT_ATLAS_PATH
    if not atlas_path.exists():
        return {"version": 1, "programs": []}

    data = json.loads(atlas_path.read_text(encoding="utf-8"))
    programs = data.get("programs") if isinstance(data, dict) else []
    if not isinstance(programs, list):
        programs = []

    return {"version": data.get("version", 1), "programs": [p for p in programs if isinstance(p, dict)]}


def build_curriculum_atlas(
    records: list[dict],
    config: dict | None = None,
    evaluations: dict | None = None,
) -> dict:
    atlas_config = config or load_curriculum_atlas()
    evaluation_items = _evaluation_items(evaluations)
    programs = []
    matched_indices: set[int] = set()

    for program in atlas_config.get("programs", []):
        modules = []
        program_indices: set[int] = set()
        program_patterns = _patterns_for(program, "project_patterns", "asset_query")

        for module in program.get("modules", []) or []:
            if not isinstance(module, dict):
                continue
            module_patterns = _patterns_for(module, "asset_query")
            asset_indices = [
                idx for idx, record in enumerate(records)
                if _record_matches(record, program_patterns, module_patterns)
            ]
            program_indices.update(asset_indices)
            matched_indices.update(asset_indices)
            modules.append({
                "id": str(module.get("id") or ""),
                "title": str(module.get("title") or "Untitled module"),
                "objective": str(module.get("objective") or ""),
                "level": str(module.get("level") or ""),
                "competencies": _clean_list(module.get("competencies")),
                "asset_query": _clean_list(module.get("asset_query")),
                "facilitator_notes": _clean_list(module.get("facilitator_notes")),
                "discussion_prompts": _clean_list(module.get("discussion_prompts")),
                "critique_criteria": _clean_criteria(module.get("critique_criteria")),
                "concept_links": _clean_concept_links(module.get("concept_links")),
                "asset_indices": asset_indices,
                "asset_count": len(asset_indices),
                "evaluation_summary": _evaluation_summary(asset_indices, records, evaluation_items),
            })

        programs.append({
            "id": str(program.get("id") or ""),
            "title": str(program.get("title") or "Untitled program"),
            "summary": str(program.get("summary") or ""),
            "competencies": _clean_list(program.get("competencies")),
            "modules": modules,
            "story_steps": _story_steps_for(program, modules),
            "asset_indices": sorted(program_indices),
            "asset_count": len(program_indices),
            "evaluation_summary": _evaluation_summary(sorted(program_indices), records, evaluation_items),
        })

    unmapped_indices = [idx for idx in range(len(records)) if idx not in matched_indices]
    module_count = sum(len(program["modules"]) for program in programs)
    linked_assets = len(matched_indices)
    return {
        "version": atlas_config.get("version", 1),
        "summary": {
            "programs": len(programs),
            "modules": module_count,
            "linked_assets": linked_assets,
            "unmapped_assets": len(unmapped_indices),
        },
        "programs": programs,
        "unmapped_asset_indices": unmapped_indices,
    }


def _clean_list(value: object) -> list[str]:
    if isinstance(value, list):
        values = value
    elif isinstance(value, str):
        values = value.split(",")
    else:
        return []
    out = []
    seen = set()
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _evaluation_items(evaluations: dict | None) -> dict:
    if not isinstance(evaluations, dict):
        return {}
    items = evaluations.get("items") if isinstance(evaluations.get("items"), dict) else evaluations
    return items if isinstance(items, dict) else {}


def _evaluation_summary(asset_indices: list[int], records: list[dict], evaluations: dict) -> dict:
    counts = {"approve": 0, "revise": 0, "reject": 0, "reference": 0}
    scores: list[int] = []
    evaluated = 0

    for idx in asset_indices:
        if idx < 0 or idx >= len(records):
            continue
        key = str(records[idx].get("file") or "")
        entry = evaluations.get(key) if key else None
        if not isinstance(entry, dict):
            continue
        decision = str(entry.get("decision") or "").strip().lower()
        score = entry.get("score")
        has_evaluation = bool(
            decision
            or score
            or str(entry.get("use_case") or "").strip()
            or str(entry.get("rationale") or "").strip()
            or str(entry.get("next_step") or "").strip()
        )
        if not has_evaluation:
            continue
        evaluated += 1
        if decision in counts:
            counts[decision] += 1
        try:
            numeric_score = int(score)
        except (TypeError, ValueError):
            continue
        if 1 <= numeric_score <= 5:
            scores.append(numeric_score)

    average_score = round(sum(scores) / len(scores), 1) if scores else None
    return {
        "asset_count": len(asset_indices),
        "evaluated_count": evaluated,
        "unreviewed_count": max(0, len(asset_indices) - evaluated),
        "decision_counts": counts,
        "average_score": average_score,
    }


def _story_steps_for(program: dict, modules: list[dict]) -> list[dict]:
    program_id = str(program.get("id") or "")
    steps = []
    for index, module in enumerate(modules, start=1):
        module_id = str(module.get("id") or "")
        asset_indices = list(module.get("asset_indices") or [])
        evaluation = module.get("evaluation_summary")
        steps.append({
            "sequence": index,
            "program_id": program_id,
            "module_id": module_id,
            "title": str(module.get("title") or "Untitled module"),
            "objective": str(module.get("objective") or ""),
            "facilitator_notes": list(module.get("facilitator_notes") or []),
            "discussion_prompts": list(module.get("discussion_prompts") or []),
            "asset_indices": asset_indices,
            "asset_count": len(asset_indices),
            "evaluation_summary": dict(evaluation) if isinstance(evaluation, dict) else {},
            "review_action": {
                "type": "focusAtlasModule",
                "program_id": program_id,
                "module_id": module_id,
                "enabled": bool(asset_indices),
            },
        })
    return steps


def _clean_criteria(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("id") or "").strip()
        prompt = str(item.get("prompt") or "").strip()
        if not label and not prompt:
            continue
        out.append({
            "id": str(item.get("id") or _slugify(label or prompt)).strip(),
            "label": label or prompt,
            "prompt": prompt,
            "scale": str(item.get("scale") or "").strip(),
        })
    return out


def _clean_concept_links(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if not isinstance(item, dict):
            continue
        concept = str(item.get("concept") or "").strip()
        target = str(item.get("target") or "").strip()
        relation = str(item.get("relation") or "related").strip()
        if not concept and not target:
            continue
        out.append({
            "concept": concept or target,
            "relation": relation or "related",
            "target": target or concept,
        })
    return out


def _slugify(value: str) -> str:
    out = []
    for ch in value.casefold():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_/":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _patterns_for(source: dict, *keys: str) -> list[str]:
    patterns: list[str] = []
    for key in keys:
        patterns.extend(_clean_list(source.get(key)))
    return [pattern.casefold() for pattern in patterns if pattern]


def _record_matches(record: dict, program_patterns: list[str], module_patterns: list[str]) -> bool:
    text = _record_search_text(record)
    program_match = not program_patterns or any(pattern in text for pattern in program_patterns)
    module_match = not module_patterns or any(pattern in text for pattern in module_patterns)
    return program_match and module_match


def _record_search_text(record: dict) -> str:
    tags = record.get("tags") if isinstance(record.get("tags"), list) else []
    parts = [
        record.get("project"),
        record.get("title"),
        record.get("name"),
        record.get("caption"),
        record.get("source_prompt"),
        record.get("prompt"),
        record.get("style"),
        record.get("model"),
        " ".join(str(tag) for tag in tags),
    ]
    return " ".join(str(part or "") for part in parts).casefold()
