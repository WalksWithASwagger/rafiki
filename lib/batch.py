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
from lib.pricing import estimate_image_cost, load_pricing_profile, provider_for_model


def _cost_estimate_for_model(
    model: str,
    *,
    resolution: str,
    dry_run: bool,
    pricing_profile: dict,
) -> dict:
    return estimate_image_cost(
        model=model,
        provider=provider_for_model(model),
        resolution=resolution,
        dry_run=dry_run,
        pricing_profile=pricing_profile,
    )


def _iso_now() -> datetime:
    return datetime.now().astimezone()


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
    global_reference_images: list[str] | None = None,
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    dry_run: bool = False,
    workers: int = 1,
    generate_viewer_html: bool = True,
    prompt_file: str = "",
    invocation_source: str = "python-cli",
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
        global_reference_images: Reference images reused for every prompt.
        reference_role: "style", "brand", or "mockup".
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
    pricing_profile = load_pricing_profile()

    run_started = _iso_now()
    run_start_monotonic = time.monotonic()
    run_ts = run_started.strftime("%Y%m%d-%H%M%S")
    run_dir = project_dir / f"run-{run_ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    if ref_paths is None:
        ref_paths = [None] * len(prompts)
    global_reference_images = [ref for ref in (global_reference_images or []) if ref]

    run_reference_images = [
        ref for ref in [*(ref_paths or []), *global_reference_images, *(composition_references or [])] if ref
    ]
    run_reference_images = list(dict.fromkeys(run_reference_images))
    run_meta = {
        "model": model,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "quality": quality,
        "style": style or "none",
        "prompt_file": prompt_file,
        "prompt_source": prompt_file or "inline",
        "invocation": {"surface": invocation_source},
        "timestamp": run_started.strftime("%Y-%m-%d %H:%M"),
        "started_at": run_started.isoformat(timespec="seconds"),
        "run_id": run_ts,
    }
    if run_reference_images:
        run_meta["reference_images"] = run_reference_images
        run_meta["reference_role"] = reference_role

    # Build per-image task dicts, applying per-prompt overrides
    tasks: list[dict] = []
    for i, item in enumerate(prompts):
        safe_name = re.sub(r"[^a-z0-9]+", "-", item["name"].lower()).strip("-")
        output_path = run_dir / f"{i + 1:02d}-{safe_name}.png"
        task_model = item.get("model") or model
        task_style = item.get("style") or style
        tasks.append({
            "index":      i,
            "name":       item["name"],
            "prompt":     item["prompt"],
            "output_path": str(output_path),
            # Per-prompt overrides fall back to batch defaults
            "model":       task_model,
            "aspect_ratio": item.get("aspect_ratio") or aspect_ratio,
            "resolution":  resolution,
            "quality":     item.get("quality") or quality,
            "style":       task_style,
            "provider":    provider_for_model(task_model),
            "reference_image": ref_paths[i] if i < len(ref_paths) else None,
            "reference_images": global_reference_images,
            "reference_role": reference_role,
            "composition_references": composition_references,
            "dry_run":    dry_run,
            "cost_estimate": _cost_estimate_for_model(
                task_model,
                resolution=resolution,
                dry_run=dry_run,
                pricing_profile=pricing_profile,
            ),
        })

    task_providers = sorted({t["provider"] for t in tasks if t.get("provider")})
    if len(task_providers) == 1:
        run_meta["provider"] = task_providers[0]
    elif task_providers:
        run_meta["providers"] = task_providers
    task_models = sorted({t["model"] for t in tasks})
    if len(task_models) > 1:
        run_meta["models"] = task_models
    run_meta["cost_estimate"] = {
        "currency": pricing_profile.get("currency", "USD"),
        "amount": None,
        "estimated": False,
        "basis": "not_estimated",
        "image_count": len(tasks),
        "estimated_images": 0,
        "unestimated_images": len(tasks),
        "pricing_profile": pricing_profile.get("path", ""),
        "pricing_updated_at": pricing_profile.get("updated_at", ""),
        "note": "Provider billing exports remain the source of truth for exact account spend.",
    }

    total = len(tasks)
    results: list[dict | None] = [None] * total

    def _run_one(task: dict) -> dict:
        started_at = _iso_now()
        start = time.monotonic()
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
                reference_images=task["reference_images"],
                reference_role=task["reference_role"],
                composition_references=task["composition_references"],
                dry_run=task["dry_run"],
            )
        except Exception as e:
            print(f"  Error on '{task['name']}': {e}", file=sys.stderr)
            ok = False
            error_msg = str(e)
        if not ok and not error_msg:
            error_msg = "generation failed"
        # Verify the file actually landed on disk — the API can return success
        # without writing anything (e.g. Gemini returning no image parts).
        if not task["dry_run"] and ok and not Path(task["output_path"]).exists():
            ok = False
            error_msg = error_msg or "API returned success but file was not written"
        cost_estimate = dict(task["cost_estimate"])
        if not ok:
            cost_estimate.update({
                "amount": None,
                "estimated": False,
                "basis": "failed_no_output_image_estimate",
                "note": "No output-image estimate is recorded for failed image generation.",
            })
        finished_at = _iso_now()
        duration_seconds = round(time.monotonic() - start, 3)
        return {
            **task,
            "cost_estimate": cost_estimate,
            "ok": ok,
            "state": "succeeded" if ok else "failed",
            "error": error_msg,
            "elapsed": duration_seconds,
            "started_at": started_at.isoformat(timespec="seconds"),
            "finished_at": finished_at.isoformat(timespec="seconds"),
            "duration_seconds": duration_seconds,
        }

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
    failure_count = total - success_count
    run_finished = _iso_now()
    if failure_count == 0:
        run_state = "succeeded"
    elif success_count == 0:
        run_state = "failed"
    else:
        run_state = "partial"
    run_meta.update({
        "finished_at": run_finished.isoformat(timespec="seconds"),
        "duration_seconds": round(time.monotonic() - run_start_monotonic, 3),
        "state": run_state,
    })
    if failure_count:
        noun = "image" if failure_count == 1 else "images"
        run_meta["error"] = f"{failure_count} of {total} {noun} failed"

    # Save run.json manifest
    def _img_record(r: dict) -> dict:
        reference_images = [
            ref for ref in [
                r.get("reference_image"),
                *(r.get("reference_images") or []),
                *(r.get("composition_references") or []),
            ] if ref
        ]
        reference_images = list(dict.fromkeys(reference_images))
        rec: dict = {
            "name":             r["name"],
            "prompt":           r["prompt"],
            "file":             Path(r["output_path"]).name,
            "ok":               r["ok"],
            "state":            r["state"],
            "model":            r["model"],
            "aspect_ratio":     r["aspect_ratio"],
            "resolution":       r["resolution"],
            "quality":          r["quality"],
            "style":            r["style"] or "none",
            "cost_estimate":    r["cost_estimate"],
            "started_at":       r["started_at"],
            "finished_at":      r["finished_at"],
            "duration_seconds": r["duration_seconds"],
            "dry_run":          r["dry_run"],
        }
        if r.get("provider"):
            rec["provider"] = r["provider"]
        if reference_images:
            rec["reference_images"] = reference_images
            rec["reference_role"] = r["reference_role"]
        if r.get("error"):
            rec["error"] = r["error"]
        return rec

    image_records = [_img_record(r) for r in final]
    cost_amounts = [
        rec["cost_estimate"].get("amount")
        for rec in image_records
        if isinstance(rec.get("cost_estimate"), dict)
        and isinstance(rec["cost_estimate"].get("amount"), (int, float))
    ]
    run_meta["cost_estimate"].update({
        "amount": round(sum(float(amount) for amount in cost_amounts), 6) if cost_amounts else None,
        "estimated": bool(cost_amounts),
        "basis": "sum_per_image_estimates" if cost_amounts else "not_estimated",
        "estimated_images": len(cost_amounts),
        "unestimated_images": len(image_records) - len(cost_amounts),
    })

    (run_dir / "run.json").write_text(
        json.dumps(
            {**run_meta, "images": image_records},
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
