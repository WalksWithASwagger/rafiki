"""Style-anchor extraction and import helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.media_types import StyleProfile


def style_profile_from_source(source: Path, *, name: str = "") -> StyleProfile:
    source = Path(source).expanduser().resolve()
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"could not read style source {source}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("style source must be a JSON object")

    suffix = data.get("style_suffix") or data.get("suffix") or ""
    negative = data.get("negative_suffix") or data.get("negative_prompt") or ""
    if not suffix and not negative:
        suffix = _derive_suffix(data)
    style_name = name or str(data.get("version") or data.get("name") or source.stem)
    return StyleProfile(
        name=style_name,
        suffix=str(suffix),
        negative_suffix=str(negative),
        source=str(source),
        media_types=["image", "video"],
        metadata={key: value for key, value in data.items() if key not in {"style_suffix", "suffix", "negative_suffix", "negative_prompt"}},
    )


def _derive_suffix(data: dict[str, Any]) -> str:
    prompts = data.get("prompts") or data.get("items") or []
    if not isinstance(prompts, list):
        return ""
    snippets = []
    for item in prompts[:12]:
        if isinstance(item, dict):
            text = item.get("prompt") or item.get("raw_prompt") or item.get("text")
            if isinstance(text, str) and text.strip():
                snippets.append(text.strip())
        elif isinstance(item, str):
            snippets.append(item.strip())
    if not snippets:
        return ""
    return "Style cues derived from reviewed references: " + " ".join(snippets)[:1200]
