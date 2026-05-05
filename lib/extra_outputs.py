"""Helpers for loading external project output directories.

Tracked shared mappings may live in ``config/extra-outputs.json``.
Machine-specific mappings should live in ``config/extra-outputs.local.json``.
Local mappings override shared ones when the same project key appears in both.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
EXTRA_OUTPUTS_CONFIG = CONFIG_DIR / "extra-outputs.json"
EXTRA_OUTPUTS_LOCAL_CONFIG = CONFIG_DIR / "extra-outputs.local.json"


def extra_outputs_config_paths() -> list[Path]:
    return [EXTRA_OUTPUTS_CONFIG, EXTRA_OUTPUTS_LOCAL_CONFIG]


def load_extra_outputs() -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for config_path in extra_outputs_config_paths():
        if not config_path.exists():
            continue
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, dict):
            continue
        for name, path in raw.items():
            if isinstance(name, str) and isinstance(path, str) and path.strip():
                mappings[name] = Path(path)
    return mappings
