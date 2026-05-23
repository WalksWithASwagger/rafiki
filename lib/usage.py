"""Usage tracking for Rafiki (local log, gitignored)."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.billing import BILLING_IMPORT_PATH, summarize_billing_imports
from lib.pricing import estimate_image_cost, load_pricing_profile, provider_for_model

USAGE_LOG_PATH = Path(__file__).parent.parent / "data" / "usage-log.json"

# Serializes the read-modify-write cycle in log_generation() so concurrent
# workers (ThreadPoolExecutor in lib/batch.py) cannot interleave and corrupt
# the JSON file. Module-level so all threads in the process share it.
_log_lock = threading.Lock()


def load_usage_log() -> dict:
    if USAGE_LOG_PATH.exists():
        try:
            with open(USAGE_LOG_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupted log — back it up and start fresh rather than crashing the batch
            backup = USAGE_LOG_PATH.with_suffix(".json.bak")
            USAGE_LOG_PATH.rename(backup)
    return {"entries": [], "total_images": 0}


def save_usage_log(data: dict) -> None:
    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: serialize to a temp file in the same directory, fsync,
    # then os.replace() onto the target. os.replace is atomic on POSIX and
    # Windows, so a reader can never observe a half-written file.
    fd, tmp_path = tempfile.mkstemp(
        prefix=".usage-log.", suffix=".tmp", dir=str(USAGE_LOG_PATH.parent)
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, USAGE_LOG_PATH)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def log_generation(
    prompt: str,
    model: str,
    output_path: str,
    aspect_ratio: str,
    *,
    style: str = "",
    ok: bool = True,
    error: str = "",
) -> None:
    with _log_lock:
        data = load_usage_log()
        entry: dict = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "aspect_ratio": aspect_ratio,
            "output": str(output_path),
            "prompt": prompt,
            "ok": ok,
        }
        if style:
            entry["style"] = style
        if error:
            entry["error"] = error
        data["entries"].append(entry)
        data["total_images"] = sum(1 for e in data["entries"] if e.get("ok", True))
        save_usage_log(data)


def _numeric_amount(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _cost_amount(cost_estimate: object) -> float | None:
    if not isinstance(cost_estimate, dict):
        return None
    amount = _numeric_amount(cost_estimate.get("amount"))
    if amount is None:
        return None
    return amount


def _is_successful_image(image: dict[str, Any]) -> bool:
    return image.get("ok", True) is not False and image.get("state") != "failed"


def _safe_manifest(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _iter_run_manifests(
    output_root: Path,
    extra_roots: dict[str, Path] | None = None,
) -> list[tuple[str, str, Path, dict[str, Any]]]:
    runs: list[tuple[str, str, Path, dict[str, Any]]] = []
    extra_roots = extra_roots or {}
    extra_projects = set(extra_roots)

    if output_root.exists():
        for project_dir in sorted(output_root.iterdir()):
            if not project_dir.is_dir() or project_dir.name in extra_projects:
                continue
            for manifest_path in sorted(project_dir.glob("run-*/run.json")):
                manifest = _safe_manifest(manifest_path)
                if manifest is not None:
                    runs.append((project_dir.name, manifest_path.parent.name, manifest_path, manifest))

    for project, root in sorted(extra_roots.items()):
        if not root.exists():
            continue
        for manifest_path in sorted(root.glob("run-*/run.json")):
            manifest = _safe_manifest(manifest_path)
            if manifest is not None:
                runs.append((project, manifest_path.parent.name, manifest_path, manifest))

    return runs


def summarize_usage(
    output_root: Path | None = None,
    *,
    extra_roots: dict[str, Path] | None = None,
    billing_import_path: Path | None = None,
) -> dict[str, Any]:
    """Return local usage, pricing-profile, and billing-import summary."""
    data = load_usage_log()
    entries = [entry for entry in data.get("entries", []) if isinstance(entry, dict)]
    successful_entries = [entry for entry in entries if entry.get("ok", True)]
    failed_entries = [entry for entry in entries if not entry.get("ok", True)]

    by_model: Counter[str] = Counter()
    by_provider: Counter[str] = Counter()
    projects: set[str] = set()
    runs_count = 0
    images_count = 0
    failed_images = 0
    unestimated_images = 0
    known_cost = 0.0
    estimated_images = 0
    profile_cost = 0.0
    profile_estimated_images = 0
    profile_unpriced_images = 0
    duration_seconds = 0.0
    recent_runs: list[dict[str, Any]] = []
    pricing_profile = load_pricing_profile()
    billing_summary = summarize_billing_imports(billing_import_path or BILLING_IMPORT_PATH)

    if output_root is not None:
        for project, run_id, manifest_path, manifest in _iter_run_manifests(Path(output_root), extra_roots):
            projects.add(project)
            runs_count += 1
            images = manifest.get("images", [])
            if not isinstance(images, list):
                images = []
            run_duration = _numeric_amount(manifest.get("duration_seconds")) or 0.0
            duration_seconds += run_duration
            run_cost = 0.0
            run_estimated_images = 0
            run_profile_cost = 0.0
            run_profile_estimated_images = 0
            run_failed = 0

            for image in images:
                if not isinstance(image, dict):
                    continue
                images_count += 1
                model = str(image.get("model") or manifest.get("model") or "unknown")
                if model:
                    by_model[model] += 1
                provider = str(image.get("provider") or manifest.get("provider") or "")
                if provider:
                    by_provider[provider] += 1
                if image.get("ok") is False or image.get("state") == "failed":
                    failed_images += 1
                    run_failed += 1
                amount = _cost_amount(image.get("cost_estimate"))
                if amount is None:
                    unestimated_images += 1
                    if _is_successful_image(image):
                        image_model = str(image.get("model") or manifest.get("model") or "unknown")
                        estimate = estimate_image_cost(
                            model=image_model,
                            provider=str(image.get("provider") or manifest.get("provider") or "")
                            or provider_for_model(image_model),
                            resolution=str(image.get("resolution") or manifest.get("resolution") or ""),
                            dry_run=bool(image.get("dry_run") or manifest.get("dry_run")),
                            pricing_profile=pricing_profile,
                        )
                        estimated_amount = _cost_amount(estimate)
                        if estimated_amount is None:
                            profile_unpriced_images += 1
                        else:
                            profile_cost += estimated_amount
                            run_profile_cost += estimated_amount
                            profile_estimated_images += 1
                            run_profile_estimated_images += 1
                else:
                    known_cost += amount
                    run_cost += amount
                    estimated_images += 1
                    run_estimated_images += 1

            recent_runs.append({
                "project": project,
                "run_id": run_id,
                "state": manifest.get("state", ""),
                "timestamp": manifest.get("timestamp", ""),
                "started_at": manifest.get("started_at", ""),
                "finished_at": manifest.get("finished_at", ""),
                "duration_seconds": run_duration,
                "image_count": len(images),
                "failed_images": run_failed,
                "known_cost": round(run_cost, 4),
                "estimated_images": run_estimated_images,
                "profile_estimated_cost": round(run_profile_cost, 4),
                "profile_estimated_images": run_profile_estimated_images,
                "manifest": str(manifest_path),
            })

    recent_runs.sort(
        key=lambda run: str(run.get("finished_at") or run.get("started_at") or run.get("timestamp") or ""),
        reverse=True,
    )

    return {
        "usage_log": {
            "path": str(USAGE_LOG_PATH),
            "entries": len(entries),
            "successful_entries": len(successful_entries),
            "failed_entries": len(failed_entries),
            "total_images": data.get("total_images", len(successful_entries)),
        },
        "archive": {
            "projects": len(projects),
            "runs": runs_count,
            "images": images_count,
            "failed_images": failed_images,
            "duration_seconds": round(duration_seconds, 3),
            "known_cost": {
                "currency": "USD",
                "amount": round(known_cost, 4),
                "estimated_images": estimated_images,
                "unestimated_images": unestimated_images,
                "basis": "local_manifest_amounts",
            },
            "estimated_cost": {
                "currency": "USD",
                "amount": round(known_cost + profile_cost, 4),
                "known_amount": round(known_cost, 4),
                "profile_amount": round(profile_cost, 4),
                "manifest_amount_images": estimated_images,
                "profile_estimated_images": profile_estimated_images,
                "unpriced_images": profile_unpriced_images,
                "basis": "local_manifest_amounts_plus_pricing_profile",
                "pricing_profile": pricing_profile.get("path", ""),
                "pricing_updated_at": pricing_profile.get("updated_at", ""),
            },
            "spend": {
                "currency": "USD",
                "amount": billing_summary["amount"] or round(known_cost + profile_cost, 4),
                "basis": "provider_billing_imports"
                if billing_summary["amount"]
                else "local_manifest_amounts_plus_pricing_profile",
                "provider_billing_amount": billing_summary["amount"],
                "estimated_amount": round(known_cost + profile_cost, 4),
            },
            "by_model": [
                {"model": model, "images": count}
                for model, count in by_model.most_common()
            ],
            "by_provider": [
                {"provider": provider, "images": count}
                for provider, count in by_provider.most_common()
            ],
        },
        "provider_billing": billing_summary,
        "recent_runs": recent_runs[:12],
        "pricing_note": "Provider billing imports are shown when present; otherwise estimated spend combines local manifest amounts with the pricing profile.",
    }
