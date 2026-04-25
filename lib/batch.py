"""Canonical batch runner for Rafiki — parallel generation with run isolation."""

from __future__ import annotations

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.core import generate_image


@dataclass
class BatchResult:
    success_count: int
    total: int
    run_dir: Path
    project_dir: Path
    viewer_path: str
    run_id: str
    images: list[dict] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.success_count == self.total


def run_batch(
    prompts: list[dict],
    project_dir: Path,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str | None = None,
    ref_paths: list[str | None] | None = None,
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    dry_run: bool = False,
    workers: int = 1,
    generate_viewer_html: bool = True,
    prompt_file: str = "",
) -> BatchResult:
    """Generate a batch of images with run isolation and an HTML viewer.

    Each call creates a timestamped run-YYYYMMDD-HHMMSS/ subdirectory so
    previous runs are never overwritten. A `latest` symlink always points to
    the newest run.

    Per-prompt metadata (aspect_ratio, model, style, quality) in each prompt
    dict overrides the batch-level defaults when not None.

    Args:
        prompts: List of prompt dicts from parse_image_prompts_md().
        project_dir: Root output directory for this project.
        model: Default model for the batch.
        aspect_ratio: Default aspect ratio.
        resolution: Default resolution (Gemini Pro only).
        quality: Default quality (OpenAI only).
        style: Default style preset or composed spec (e.g. "kk+bcai").
        ref_paths: Per-prompt reference image paths (aligned with prompts).
        reference_role: "style" or "mockup".
        composition_references: Extra ref paths for mockup mode.
        dry_run: Preview without calling any API.
        workers: Parallel generation workers (1 = sequential).
        generate_viewer_html: Generate viewer.html after the run.
        prompt_file: Source prompt file path (stored in run.json).

    Returns:
        BatchResult with counts, paths, and per-image metadata.
    """
    project_dir = Path(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    run_ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = project_dir / f"run-{run_ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    if ref_paths is None:
        ref_paths = [None] * len(prompts)

    run_meta = {
        "model": model,
        "aspect_ratio": aspect_ratio,
        "style": style or "none",
        "prompt_file": prompt_file,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "run_id": run_ts,
    }

    # Build per-image task dicts, applying per-prompt overrides
    tasks: list[dict] = []
    for i, item in enumerate(prompts):
        safe_name = re.sub(r"[^a-z0-9]+", "-", item["name"].lower()).strip("-")
        output_path = run_dir / f"{i + 1:02d}-{safe_name}.png"
        tasks.append({
            "index":      i,
            "name":       item["name"],
            "prompt":     item["prompt"],
            "output_path": str(output_path),
            # Per-prompt overrides fall back to batch defaults
            "model":       item.get("model") or model,
            "aspect_ratio": item.get("aspect_ratio") or aspect_ratio,
            "resolution":  resolution,
            "quality":     item.get("quality") or quality,
            "style":       item.get("style") or style,
            "reference_image": ref_paths[i] if i < len(ref_paths) else None,
            "reference_role": reference_role,
            "composition_references": composition_references,
            "dry_run":    dry_run,
        })

    total = len(tasks)
    results: list[dict | None] = [None] * total

    def _run_one(task: dict) -> dict:
        start = time.time()
        error_msg = ""
        try:
            ok = generate_image(
                prompt=task["prompt"],
                output_path=task["output_path"],
                model=task["model"],
                aspect_ratio=task["aspect_ratio"],
                resolution=task["resolution"],
                quality=task["quality"],
                style=task["style"],
                reference_image=task["reference_image"],
                reference_role=task["reference_role"],
                composition_references=task["composition_references"],
                dry_run=task["dry_run"],
            )
        except Exception as e:
            print(f"  Error on '{task['name']}': {e}", file=sys.stderr)
            ok = False
            error_msg = str(e)
        # Verify the file actually landed on disk — the API can return success
        # without writing anything (e.g. Gemini returning no image parts).
        if not task["dry_run"] and ok and not Path(task["output_path"]).exists():
            ok = False
            error_msg = error_msg or "API returned success but file was not written"
        return {**task, "ok": ok, "error": error_msg, "elapsed": time.time() - start}

    mode_label = f"parallel, {workers} workers" if workers > 1 else "sequential"
    print(f"\nRunning {total} prompt{'s' if total != 1 else ''} ({mode_label})")

    if workers <= 1:
        for task in tasks:
            print(f"\n[{task['index'] + 1}/{total}] {task['name']}")
            result = _run_one(task)
            results[task["index"]] = result
    else:
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_one, t): t for t in tasks}
            for fut in as_completed(futures):
                result = fut.result()
                results[result["index"]] = result
                done += 1
                status = "✓" if result["ok"] else "✗"
                elapsed = f"{result.get('elapsed', 0):.1f}s"
                print(f"[{done}/{total}] {result['name']} {status} ({elapsed})")

    # Flatten (no Nones should remain, but be safe)
    final: list[dict] = [r for r in results if r is not None]
    success_count = sum(1 for r in final if r["ok"])

    # Save run.json manifest
    def _img_record(r: dict) -> dict:
        rec: dict = {
            "name":   r["name"],
            "prompt": r["prompt"],
            "file":   Path(r["output_path"]).name,
            "ok":     r["ok"],
        }
        if r.get("error"):
            rec["error"] = r["error"]
        return rec

    (run_dir / "run.json").write_text(
        json.dumps(
            {**run_meta, "images": [_img_record(r) for r in final]},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # latest symlink
    latest_link = project_dir / "latest"
    if latest_link.is_symlink() or latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(run_dir.name)

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Generated {success_count}/{total} images")
    print(f"{prefix}Run dir:  {run_dir}")

    viewer_path_str = ""
    if generate_viewer_html:
        from lib.renderers.viewer import generate_viewer, generate_comparison_viewer

        title = (
            Path(prompt_file).stem.replace("-", " ").replace("_", " ").title()
            if prompt_file
            else project_dir.name.replace("-", " ").title()
        )
        generate_viewer(
            output_dir=run_dir,
            items=[{
                "name": r["name"],
                "prompt": r["prompt"],
                "output_path": r["output_path"],
                "error": r.get("error", ""),
            } for r in final],
            title=title,
            run_meta=run_meta,
        )
        vp = generate_comparison_viewer(project_dir)
        viewer_path_str = str(vp)
        print(f"{prefix}Viewer:   {viewer_path_str}")

    return BatchResult(
        success_count=success_count,
        total=total,
        run_dir=run_dir,
        project_dir=project_dir,
        viewer_path=viewer_path_str,
        run_id=run_ts,
        images=[
            {"name": r["name"], "output_path": r["output_path"], "ok": r["ok"]}
            for r in final
        ],
    )
