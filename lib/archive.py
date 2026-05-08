"""Approved-image archive management for Rafiki.

The viewer/server records star ratings in ``output/ratings.json`` keyed by
``"{project}/{run_id}/{filename}"`` with value ``"star"`` or ``"reject"``.

This module promotes starred images into a curated, stable set under
``output/<project>/approved/``, tracks provenance in
``output/<project>/approved/index.json``, and provides a safe ``clean``
operation that can drop ``run-*/`` dirs while preserving the approved set.

Design choices (see PR #23 discussion):
- Single rating source of truth: ``output/ratings.json`` (no parallel
  starring mechanism in run.json).
- Approved filenames keep their original ``run.json`` ``file`` name.
  Collisions are resolved by prefixing with the short run-id, so two
  distinct runs that both produced ``01-foo.png`` end up as
  ``01-foo.png`` and ``20260502-202936__01-foo.png``.
- ``approve`` is idempotent: re-running merges into the existing
  ``index.json`` keyed by ``(source_run, original_file)``.
- The CLI parses ``--older-than 30d``; ``clean(older_than_days=int)``
  takes a plain int — no unit parsing inside the library.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from lib import extra_outputs


def _project_ref(output_root: Path, project: str) -> tuple[Path, str]:
    candidate = Path(project)
    if candidate.is_absolute():
        return candidate, candidate.name

    extra_roots = extra_outputs.load_extra_outputs()
    if project in extra_roots:
        return extra_roots[project], project

    return output_root / project, project


def _load_ratings(output_root: Path) -> dict[str, str]:
    ratings_file = output_root / "ratings.json"
    if not ratings_file.exists():
        return {}
    try:
        return json.loads(ratings_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _load_index(approved_dir: Path) -> dict:
    index_file = approved_dir / "index.json"
    if not index_file.exists():
        return {"images": []}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
        if "images" not in data:
            data["images"] = []
        return data
    except (json.JSONDecodeError, OSError):
        return {"images": []}


def _write_index(approved_dir: Path, index: dict) -> None:
    index_file = approved_dir / "index.json"
    index_file.write_text(json.dumps(index, indent=2), encoding="utf-8")


def _list_run_dirs(project_dir: Path) -> list[Path]:
    if not project_dir.exists():
        return []
    return sorted(d for d in project_dir.glob("run-*") if d.is_dir())


def _latest_run(project_dir: Path) -> Path | None:
    runs = _list_run_dirs(project_dir)
    return runs[-1] if runs else None


def _read_run_json(run_dir: Path) -> dict | None:
    rj = run_dir / "run.json"
    if not rj.exists():
        return None
    try:
        return json.loads(rj.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def approve(
    project: str,
    run: str | None = None,
    *,
    output_root: Path | None = None,
) -> int:
    """Copy starred images from ``run`` (or latest run) into ``approved/``.

    Updates ``output/<project>/approved/index.json`` with provenance
    ``{slug, source_run, original_file, prompt, timestamp}`` per image.

    Returns the number of images newly copied (re-approving an already-
    approved image is a no-op).
    """
    output_root = (output_root or _default_output_root()).resolve()
    project_dir, project_name = _project_ref(output_root, project)
    if not project_dir.exists():
        raise FileNotFoundError(f"project not found: {project_dir}")

    if run:
        run_dir = project_dir / run if not run.startswith("run-") else project_dir / run
        if not run_dir.exists():
            # Allow callers to pass either "20260502-202936" or "run-20260502-202936"
            alt = project_dir / f"run-{run}"
            if alt.exists():
                run_dir = alt
            else:
                raise FileNotFoundError(f"run not found: {run_dir}")
    else:
        latest = _latest_run(project_dir)
        if latest is None:
            raise FileNotFoundError(f"no runs found under {project_dir}")
        run_dir = latest

    run_data = _read_run_json(run_dir)
    if run_data is None:
        raise FileNotFoundError(f"run.json missing for {run_dir}")

    run_id = run_dir.name
    ratings = _load_ratings(output_root)

    approved_dir = project_dir / "approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    index = _load_index(approved_dir)
    existing_keys = {(e["source_run"], e["original_file"]) for e in index["images"]}
    existing_slugs = {e["slug"] for e in index["images"]}

    copied = 0
    for img in run_data.get("images", []):
        original_file = img.get("file")
        if not original_file:
            continue
        rating_key = f"{project_name}/{run_id}/{original_file}"
        if ratings.get(rating_key) != "star":
            continue

        src = run_dir / original_file
        if not src.exists():
            continue

        idem_key = (run_id, original_file)
        if idem_key in existing_keys:
            continue

        slug = original_file
        if slug in existing_slugs:
            stem = Path(original_file).stem
            suffix = Path(original_file).suffix
            slug = f"{run_id.removeprefix('run-')}__{stem}{suffix}"

        dest = approved_dir / slug
        shutil.copy2(src, dest)
        index["images"].append({
            "slug": slug,
            "source_run": run_id,
            "original_file": original_file,
            "name": img.get("name", ""),
            "prompt": img.get("prompt", ""),
            "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": run_data.get("model", ""),
            "aspect_ratio": run_data.get("aspect_ratio", ""),
            "style": run_data.get("style", ""),
        })
        existing_keys.add(idem_key)
        existing_slugs.add(slug)
        copied += 1

    _write_index(approved_dir, index)
    return copied


def clean(
    project: str,
    *,
    keep_approved: bool = False,
    older_than_days: int | None = None,
    dry_run: bool = False,
    output_root: Path | None = None,
) -> list[Path]:
    """Return ``run-*`` dirs deleted (or that would be deleted in dry-run).

    Selection rules:
    - With ``keep_approved=True``: only delete a run if every image listed
      in its ``run.json`` is already in ``approved/index.json`` for that
      same ``source_run``.
    - With ``older_than_days=N``: only delete runs whose mtime is older
      than ``N`` days.
    - When both are set, both conditions must hold.
    - When neither is set, all runs are eligible (caller is responsible
      for confirming with the user).

    The ``approved/`` directory is never touched.
    """
    output_root = (output_root or _default_output_root()).resolve()
    project_dir, _project_name = _project_ref(output_root, project)
    if not project_dir.exists():
        raise FileNotFoundError(f"project not found: {project_dir}")

    approved_dir = project_dir / "approved"
    index = _load_index(approved_dir)
    approved_pairs = {(e["source_run"], e["original_file"]) for e in index["images"]}

    cutoff = (
        datetime.now() - timedelta(days=older_than_days)
        if older_than_days is not None
        else None
    )

    to_delete: list[Path] = []
    for run_dir in _list_run_dirs(project_dir):
        if cutoff is not None:
            mtime = datetime.fromtimestamp(run_dir.stat().st_mtime)
            if mtime > cutoff:
                continue

        if keep_approved:
            run_data = _read_run_json(run_dir)
            if run_data is None:
                # No run.json — can't verify approval state; skip to be safe.
                continue
            run_id = run_dir.name
            run_files = [img["file"] for img in run_data.get("images", []) if img.get("file")]
            if not run_files:
                continue
            if not all((run_id, f) in approved_pairs for f in run_files):
                continue

        to_delete.append(run_dir)

    if not dry_run:
        for run_dir in to_delete:
            shutil.rmtree(run_dir)

    return to_delete


def build_approved_viewer(
    project: str,
    *,
    output_root: Path | None = None,
) -> Path:
    """Generate ``output/<project>/approved/viewer.html`` from the approved set.

    Reuses :func:`lib.renderers.viewer.generate_viewer` by synthesising a
    pseudo-run from ``approved/index.json``.
    """
    from lib.renderers.viewer import generate_viewer

    output_root = (output_root or _default_output_root()).resolve()
    project_dir, _project_name = _project_ref(output_root, project)
    approved_dir = project_dir / "approved"
    if not approved_dir.exists():
        raise FileNotFoundError(f"no approved set: {approved_dir}")

    index = _load_index(approved_dir)
    items = [
        {
            "name": entry.get("name") or entry["slug"],
            "prompt": entry.get("prompt", ""),
            "output_path": str(approved_dir / entry["slug"]),
            "aspect_ratio": entry.get("aspect_ratio", ""),
            "error": "",
        }
        for entry in index["images"]
    ]

    title = f"{project_dir.name.replace('-', ' ').title()} — Approved"
    run_meta = {
        "model": "approved-set",
        "aspect_ratio": "16:9",
        "style": "—",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prompt_file": "",
    }
    return generate_viewer(
        output_dir=approved_dir,
        items=items,
        title=title,
        run_meta=run_meta,
    )


def _default_output_root() -> Path:
    return Path(__file__).resolve().parent.parent / "output"
