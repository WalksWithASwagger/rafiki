"""Local multimedia root configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
MEDIA_ROOTS_CONFIG = CONFIG_DIR / "media-roots.json"
MEDIA_ROOTS_LOCAL_CONFIG = CONFIG_DIR / "media-roots.local.json"


@dataclass(frozen=True)
class MediaRoot:
    key: str
    path: Path
    importer: str = "generic"
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "path": str(self.path),
            "importer": self.importer,
            "enabled": self.enabled,
            "description": self.description,
        }


def media_roots_config_paths() -> list[Path]:
    return [MEDIA_ROOTS_CONFIG, MEDIA_ROOTS_LOCAL_CONFIG]


def _root_from_mapping(raw: dict[str, Any]) -> MediaRoot | None:
    key = str(raw.get("key") or "").strip()
    path = str(raw.get("path") or "").strip()
    if not key or not path:
        return None
    return MediaRoot(
        key=key,
        path=Path(path).expanduser(),
        importer=str(raw.get("importer") or "generic").strip() or "generic",
        enabled=bool(raw.get("enabled", True)),
        description=str(raw.get("description") or "").strip(),
    )


def _roots_from_file(path: Path) -> dict[str, MediaRoot]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    entries = raw.get("roots") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        return {}

    roots: dict[str, MediaRoot] = {}
    for item in entries:
        if not isinstance(item, dict):
            continue
        root = _root_from_mapping(item)
        if root:
            roots[root.key] = root
    return roots


def load_media_roots(*, include_disabled: bool = False) -> dict[str, MediaRoot]:
    if os.environ.get("RAFIKI_DISABLE_MEDIA_ROOTS") == "1":
        return {}

    roots: dict[str, MediaRoot] = {}
    for path in media_roots_config_paths():
        roots.update(_roots_from_file(path))
    if include_disabled:
        return roots
    return {key: root for key, root in roots.items() if root.enabled}
