"""Prompt file parsing for Rafiki batch generation."""

from __future__ import annotations

import re
from pathlib import Path

# Aspect ratio presets (also used for CLI argparse help)
ASPECT_RATIOS: dict[str, str] = {
    "linkedin":  "16:9",
    "instagram": "1:1",
    "twitter":   "16:9",
    "story":     "9:16",
    "square":    "1:1",
}

# Normalise **Key:** field names to internal attribute names
_FIELD_MAP: dict[str, str] = {
    "for":          "usage",
    "aspect":       "aspect_ratio",
    "aspect ratio": "aspect_ratio",
    "model":        "model",
    "style":        "style",
    "quality":      "quality",
}


def parse_image_prompts_md(file_path: str | Path) -> list[dict]:
    """Parse an image-prompts.md file into a list of prompt dicts.

    Each dict contains:
        name          Section title (str)
        usage         **For:** field value, or ""
        prompt        Multi-line blockquote text
        aspect_ratio  **Aspect Ratio:** override, or None
        model         **Model:** override, or None
        style         **Style:** override, or None
        quality       **Quality:** override, or None

    Fields set to None mean "use the batch-level CLI default".
    """
    content = Path(file_path).read_text(encoding="utf-8")
    prompts = []

    sections = re.split(r"^## \d+\.", content, flags=re.MULTILINE)[1:]

    for section in sections:
        lines = section.strip().split("\n")
        name = lines[0].strip() if lines else "Untitled"

        # Collect all **Key:** Value pairs (colon is inside the bold markers)
        fields: dict[str, str] = {}
        for raw_key, value in re.findall(r"\*\*([^*:]+):\*\*\s*(.+)", section):
            normalised = _FIELD_MAP.get(raw_key.strip().lower())
            if normalised:
                fields[normalised] = value.strip()

        # Multi-line blockquote prompt
        prompt_text = ""
        prompt_block = re.search(
            r"\*\*Prompt:\*\*\s*\n((?:>[^\n]*(?:\n|$))+)",
            section,
            re.MULTILINE,
        )
        if prompt_block:
            raw = prompt_block.group(1)
            out_lines: list[str] = []
            for line in raw.splitlines():
                if line.startswith(">"):
                    out_lines.append(line[1:].lstrip())
                elif line.strip() == "":
                    out_lines.append("")
                elif out_lines:
                    out_lines[-1] = f"{out_lines[-1]} {line.strip()}".strip()
            prompt_text = "\n".join(out_lines).strip()

        if not prompt_text:
            continue

        # Normalise aspect ratio preset names
        ar = fields.get("aspect_ratio")
        if ar and ar in ASPECT_RATIOS:
            ar = ASPECT_RATIOS[ar]

        prompts.append({
            "name": name,
            "usage": fields.get("usage", ""),
            "prompt": prompt_text,
            "aspect_ratio": ar,
            "model": fields.get("model"),
            "style": fields.get("style"),
            "quality": fields.get("quality"),
        })

    return prompts
