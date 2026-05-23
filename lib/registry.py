"""Cross-project image asset registry — index, search, export.

Walks every project under output/ and any roots configured in
config/extra-outputs.json plus config/extra-outputs.local.json. The default
curated scope prefers an approved/ subdir and falls back to the latest run-*
dir. The all-runs scope indexes every run-* dir so the master library can act
as a complete local archive. Pulls metadata from run.json (canonical) and
merges optional title/caption/tags from a sibling viewer-data.json when
present.

The on-disk registry is a local cache (gitignored). Successful generation and
curation workflows refresh the curated cache automatically; rebuild manually
with `generate.py registry index --all-runs` when you need every run.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from lib.archive_metadata import archive_metadata_path, load_archive_metadata, metadata_for_key
from lib import extra_outputs

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "output"
REGISTRY_JSON = DATA_DIR / "asset-registry.json"
REGISTRY_CSV = DATA_DIR / "asset-registry.csv"

CSV_COLUMNS = [
    "id",
    "project",
    "title",
    "caption",
    "tags",
    "approval_status",
    "metadata_states",
    "export_status",
    "publish_status",
    "superseded_by",
    "source_prompt",
    "style",
    "model",
    "aspect_ratio",
    "source",
    "source_run",
    "indexed_at",
    "path",
]


@dataclass
class AssetEntry:
    id: str
    project: str
    title: str
    caption: str
    tags: list[str] = field(default_factory=list)
    approval_status: str = ""
    metadata_states: list[str] = field(default_factory=list)
    export_status: str = ""
    publish_status: str = ""
    superseded_by: str = ""
    source_prompt: str = ""
    style: str = ""
    model: str = ""
    aspect_ratio: str = ""
    source: str = ""
    source_run: str = ""
    indexed_at: str = ""
    path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_csv_row(self) -> dict[str, str]:
        d = self.to_dict()
        d["tags"] = ",".join(self.tags)
        d["metadata_states"] = ",".join(self.metadata_states)
        return d


def _load_extra_roots() -> dict[str, Path]:
    return extra_outputs.load_extra_outputs()


def _latest_run_dir(project_dir: Path) -> Path | None:
    runs = sorted(project_dir.glob("run-*"))
    return runs[-1] if runs else None


def _load_viewer_data(directory: Path) -> dict[str, dict]:
    """Optional sibling viewer-data.json — keyed by image filename."""
    vd = directory / "viewer-data.json"
    if not vd.exists():
        return {}
    try:
        data = json.loads(vd.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Malformed viewer-data.json at %s: %s", vd, e)
        return {}

    if isinstance(data, dict) and "images" in data:
        items = data["images"]
    elif isinstance(data, list):
        items = data
    else:
        return {}

    out: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = item.get("file") or item.get("filename") or item.get("name")
        if key:
            out[str(key)] = item
    return out


def _load_run_meta(directory: Path) -> tuple[dict, dict[str, dict]]:
    """Return (run-level meta, per-file image meta) from run.json (or empty)."""
    rj = directory / "run.json"
    if not rj.exists():
        return {}, {}
    try:
        data = json.loads(rj.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Malformed run.json at %s: %s", rj, e)
        return {}, {}

    per_file: dict[str, dict] = {}
    for img in data.get("images", []) or []:
        if isinstance(img, dict) and img.get("file"):
            per_file[img["file"]] = img
    return data, per_file


def _load_approved_index(directory: Path) -> dict[str, dict]:
    index_file = directory / "index.json"
    if not index_file.exists():
        return {}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Malformed approved index at %s: %s", index_file, e)
        return {}

    entries = data.get("images", []) if isinstance(data, dict) else []
    out: dict[str, dict] = {}
    for item in entries:
        if not isinstance(item, dict):
            continue
        key = item.get("slug") or item.get("file") or item.get("original_file")
        if key:
            out[str(key)] = item
    return out


def _slugify(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in "-_ ":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _entries_from_dir(
    project: str,
    directory: Path,
    indexed_at: str,
    source: str = "",
    *,
    approved_by_source: dict[tuple[str, str], dict] | None = None,
    include_run_id_in_id: bool = False,
) -> list[AssetEntry]:
    """Build AssetEntry list from PNGs in directory + adjacent metadata."""
    if not directory.exists():
        return []

    run_meta, per_file = _load_run_meta(directory)
    viewer_meta = _load_viewer_data(directory)
    approved_meta = _load_approved_index(directory) if source == "approved" else {}
    approved_by_source = approved_by_source or {}

    style = run_meta.get("style", "") or ""
    model = run_meta.get("model", "") or ""
    aspect_ratio = run_meta.get("aspect_ratio", "") or ""
    run_id = directory.name if directory.name.startswith("run-") else ""

    entries: list[AssetEntry] = []
    image_paths = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    for image_path in image_paths:
        fname = image_path.name
        approved = approved_meta.get(fname, {})
        img_meta = per_file.get(fname, {})
        view = viewer_meta.get(fname, {})
        source_approval = approved_by_source.get((run_id, fname), {}) if run_id else {}
        if source_approval:
            approved = {**approved, **source_approval}
        source_prompt = approved.get("prompt") or img_meta.get("prompt") or view.get("caption") or ""

        title = (
            view.get("title")
            or approved.get("name")
            or img_meta.get("name")
            or image_path.stem.replace("-", " ").replace("_", " ").title()
        )
        caption = view.get("caption") or source_prompt or ""

        tags: list[str] = []
        for src in (view.get("tags"), img_meta.get("tags")):
            if isinstance(src, list):
                tags.extend(str(t) for t in src)
        if aspect_ratio and aspect_ratio not in tags:
            tags.append(aspect_ratio)

        image_style = approved.get("style") or img_meta.get("style") or style
        image_model = approved.get("model") or img_meta.get("model") or model
        image_aspect_ratio = approved.get("aspect_ratio") or img_meta.get("aspect_ratio") or aspect_ratio
        image_source_run = approved.get("source_run") or run_id
        approval_status = "approved" if source == "approved" or source_approval else "unapproved"

        try:
            rel_path = image_path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel_path = image_path.resolve().as_posix()

        id_parts = [project]
        if include_run_id_in_id and image_source_run:
            id_parts.append(str(image_source_run).removeprefix("run-"))
        id_parts.append(image_path.stem)

        entries.append(
            AssetEntry(
                id="-".join(id_parts),
                project=project,
                title=str(title),
                caption=str(caption),
                tags=tags,
                approval_status=approval_status,
                source_prompt=str(source_prompt),
                style=str(image_style),
                model=str(image_model),
                aspect_ratio=str(image_aspect_ratio),
                source=source,
                source_run=str(image_source_run),
                indexed_at=indexed_at,
                path=rel_path,
            )
        )
    return entries


def _approved_by_source(project_dir: Path) -> dict[tuple[str, str], dict]:
    approved_dir = project_dir / "approved"
    if not approved_dir.is_dir():
        return {}

    out: dict[tuple[str, str], dict] = {}
    for item in _load_approved_index(approved_dir).values():
        source_run = item.get("source_run")
        original_file = item.get("original_file")
        if source_run and original_file:
            out[(str(source_run), str(original_file))] = item
    return out


def _project_roots(output_root: Path | None = None) -> dict[str, Path]:
    """Map project name -> project dir, merging output/ and extra-output config."""
    output_root = Path(output_root) if output_root else DEFAULT_OUTPUT_ROOT
    roots: dict[str, Path] = {}

    if output_root.exists():
        for child in sorted(output_root.iterdir()):
            if child.is_dir():
                roots[child.name] = child

    for name, path in _load_extra_roots().items():
        if path.exists():
            roots[name] = path  # extras win — canonical source
        else:
            logger.warning("extra-outputs project %s missing on disk: %s", name, path)

    return roots


def _archive_metadata_key(entry: AssetEntry, output_root: Path) -> str:
    path = Path(entry.path)
    resolved = path if path.is_absolute() else REPO_ROOT / path

    try:
        return resolved.resolve().relative_to(output_root.resolve()).as_posix()
    except ValueError:
        pass

    if not path.is_absolute() and path.parts and path.parts[0] == output_root.name:
        return Path(*path.parts[1:]).as_posix()

    if entry.source == "approved":
        return f"{entry.project}/approved/{path.name}"
    if entry.source_run:
        return f"{entry.project}/{entry.source_run}/{path.name}"
    return path.as_posix()


def _status_from_states(states: list[str], choices: set[str]) -> str:
    return ",".join(state for state in states if state in choices)


def _apply_archive_metadata(entries: list[AssetEntry], output_root: Path) -> None:
    metadata = load_archive_metadata(archive_metadata_path(output_root))
    for entry in entries:
        item = metadata_for_key(metadata, _archive_metadata_key(entry, output_root))
        states = item.get("states", [])
        if not isinstance(states, list):
            states = []
        entry.metadata_states = [str(state).strip() for state in states if str(state).strip()]
        entry.export_status = _status_from_states(entry.metadata_states, {"canva", "notion"})
        entry.publish_status = _status_from_states(entry.metadata_states, {"deployed", "published"})
        entry.superseded_by = str(item.get("superseded_by") or "").strip()


def collect(output_root: Path | None = None, *, scope: str = "curated") -> list[AssetEntry]:
    """Walk projects and build registry entries without writing the local cache."""
    if scope not in {"curated", "all-runs"}:
        raise ValueError("scope must be 'curated' or 'all-runs'")

    output_root = Path(output_root) if output_root else DEFAULT_OUTPUT_ROOT
    indexed_at = datetime.now().isoformat(timespec="seconds")
    roots = _project_roots(output_root)

    all_entries: list[AssetEntry] = []
    for project, project_dir in roots.items():
        try:
            approved = project_dir / "approved"
            if scope == "all-runs":
                approved_lookup = _approved_by_source(project_dir)
                run_dirs = sorted(project_dir.glob("run-*"))
                seen_sources: set[tuple[str, str]] = set()
                for run_dir in run_dirs:
                    if not run_dir.is_dir():
                        continue
                    entries = _entries_from_dir(
                        project,
                        run_dir,
                        indexed_at,
                        source="run",
                        approved_by_source=approved_lookup,
                        include_run_id_in_id=True,
                    )
                    for entry in entries:
                        seen_sources.add((entry.source_run, Path(entry.path).name))
                    all_entries.extend(entries)
                if approved.is_dir():
                    approved_index = _load_approved_index(approved)
                    for entry in _entries_from_dir(
                        project,
                        approved,
                        indexed_at,
                        source="approved",
                        include_run_id_in_id=True,
                    ):
                        approved_meta = approved_index.get(Path(entry.path).name, {})
                        original = approved_meta.get("original_file")
                        source_run = approved_meta.get("source_run") or entry.source_run
                        if original and source_run and (str(source_run), str(original)) in seen_sources:
                            continue
                        all_entries.append(entry)
            elif approved.is_dir():
                entries = _entries_from_dir(project, approved, indexed_at, source="approved")
                all_entries.extend(entries)
            else:
                latest = _latest_run_dir(project_dir)
                if latest is None:
                    logger.info("No approved/ or run-* in %s — skipping", project_dir)
                    continue
                entries = _entries_from_dir(project, latest, indexed_at, source="latest-run")
                all_entries.extend(entries)
        except Exception as e:
            logger.warning("Skipping project %s due to error: %s", project, e)
            continue

    _apply_archive_metadata(all_entries, output_root)
    return all_entries


def index(output_root: Path | None = None, *, scope: str = "curated") -> list[AssetEntry]:
    """Walk projects, build registry entries, persist to data/asset-registry.json."""
    all_entries = collect(output_root, scope=scope)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_JSON.write_text(
        json.dumps([e.to_dict() for e in all_entries], indent=2) + "\n",
        encoding="utf-8",
    )
    return all_entries


def refresh_cache(
    output_root: Path | None = None,
    *,
    scope: str = "curated",
    reason: str = "",
) -> dict[str, object]:
    entries = index(output_root=output_root, scope=scope)
    return {
        "registry_refreshed": True,
        "registry_count": len(entries),
        "registry_scope": scope,
        "registry_reason": reason,
        "registry_path": str(REGISTRY_JSON.resolve(strict=False)),
    }


def _load_registry() -> list[AssetEntry]:
    if not REGISTRY_JSON.exists():
        return []
    try:
        raw = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Failed to read %s: %s", REGISTRY_JSON, e)
        return []
    return [AssetEntry(**item) for item in raw if isinstance(item, dict)]


def search(query: str) -> list[AssetEntry]:
    """Case-insensitive substring search across title, caption, tags."""
    needle = (query or "").lower().strip()
    if not needle:
        return []
    out: list[AssetEntry] = []
    for entry in _load_registry():
        haystack = " ".join([
            entry.title.lower(),
            entry.caption.lower(),
            " ".join(t.lower() for t in entry.tags),
        ])
        if needle in haystack:
            out.append(entry)
    return out


def export(format: str = "csv") -> Path:
    """Export the persisted registry as CSV or JSON. Returns the file path."""
    fmt = format.lower()
    entries = _load_registry()
    _apply_archive_metadata(entries, DEFAULT_OUTPUT_ROOT)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        with REGISTRY_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry.to_csv_row())
        return REGISTRY_CSV

    if fmt == "json":
        REGISTRY_JSON.write_text(
            json.dumps([e.to_dict() for e in entries], indent=2) + "\n",
            encoding="utf-8",
        )
        return REGISTRY_JSON

    raise ValueError(f"Unsupported export format: {format!r} (use 'csv' or 'json')")
