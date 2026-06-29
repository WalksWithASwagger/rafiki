"""Keyframe generation: a beat from keyframes.json -> Replicate stills.

Reads a project's ``keyframes.json`` (settings + beats) and generates the
keyframe stills that feed the Floyo video workflows. Uses the existing
``replicate_provider`` (the trained character LoRA lives on Replicate).
Dry-run-first; ``--execute`` is the only path that spends.
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.jobs import provider_cost_preview, write_manifest
from lib.providers import replicate_provider

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENGINE = "flux1-lora"
_MAX_OUTPUTS = 4


def load_keyframes(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    settings = data.get("settings") or {}
    beats = data.get("beats") or {}
    if not beats:
        raise ValueError(f"no beats found in {path}")
    return settings, beats


def resolve_beat(beats: dict[str, Any], selector: str) -> tuple[str, dict[str, Any]]:
    """Match a beat by exact key, or by number (e.g. '02' -> situ_02_*)."""
    if selector in beats:
        return selector, beats[selector]
    sel = selector.strip().lstrip("0") or "0"
    for key, beat in beats.items():
        parts = key.replace("-", "_").split("_")
        if any(p.lstrip("0").lower() == sel.lower() or p.lower() == selector.lower() for p in parts):
            return key, beat
    raise ValueError(f"beat {selector!r} not found; available: {list(beats)[:8]}…")


def build_keyframe_input(
    settings: dict[str, Any], prompt: str, *, num_outputs: int, seed: int
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        "model": settings.get("model_type", "dev"),
        "aspect_ratio": settings.get("aspect_ratio", "1:1"),
        "num_inference_steps": settings.get("num_inference_steps", 32),
        "guidance_scale": settings.get("guidance_scale", 3.2),
        "lora_scale": settings.get("lora_scale", 0.95),
        "num_outputs": max(1, min(num_outputs, _MAX_OUTPUTS)),
        "output_format": settings.get("output_format", "jpg"),
        "seed": seed,
    }


def build_keyframe_preview(
    *, keyframes_path: Path, beat: str, engine: str = DEFAULT_ENGINE, num_outputs: int = 4,
    execute: bool = False,
) -> dict[str, Any]:
    settings, beats = load_keyframes(Path(keyframes_path))
    key, _ = resolve_beat(beats, beat)
    counts = {"planned_provider_jobs": 1, "network_calls": 1 if execute else 0,
              "requested_images": max(1, min(num_outputs, _MAX_OUTPUTS)), "beat": key}
    cost = provider_cost_preview(
        provider="Replicate", model=f"{engine}:{settings.get('version','')[:12]}",
        counts=counts, dry_run=not execute,
        note="Replicate image spend is not estimated locally; use provider billing for exact charges.",
    )
    return {"kind": "keyframe-generation", "provider": "Replicate", "engine": engine,
            "beat": key, "execute": execute, "dry_run": not execute,
            "count_preview": counts, "cost_estimate": cost, "pricing_note": cost["note"]}


def plan_keyframe_generation(
    *,
    keyframes_path: Path,
    beat: str,
    engine: str = DEFAULT_ENGINE,
    num_outputs: int = 4,
    seed: int | None = None,
    project: str = "keyframes",
    output_root: Path | None = None,
    execute: bool = False,
    wait: bool = True,
) -> dict[str, Any]:
    if engine != "flux1-lora":
        # flux2-klein needs reference-image uploads; deferred to a follow-up.
        raise ValueError(f"engine {engine!r} not supported yet; use 'flux1-lora'")
    settings, beats = load_keyframes(Path(keyframes_path))
    version = settings.get("version")
    if not version:
        raise ValueError("keyframes.json settings has no 'version' (the trained LoRA model version)")
    key, beat_obj = resolve_beat(beats, beat)
    prompt = beat_obj.get("prompt") if isinstance(beat_obj, dict) else str(beat_obj)
    if not prompt:
        raise ValueError(f"beat {key!r} has no prompt")

    seed = seed if seed is not None else random.randint(1, 2**31 - 1)
    request_input = build_keyframe_input(settings, prompt, num_outputs=num_outputs, seed=seed)

    output_root = output_root or REPO_ROOT / "output"
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    run_dir = output_root / project / key / f"keyframe-run-{stamp}"
    manifest_path = run_dir / "run.json"

    counts = {"planned_provider_jobs": 1, "network_calls": 1 if execute else 0,
              "requested_images": request_input["num_outputs"], "beat": key}
    cost = provider_cost_preview(
        provider="Replicate", model=f"{engine}:{version[:12]}", counts=counts,
        dry_run=not execute,
        note="Replicate image spend is not estimated locally; use provider billing for exact charges.",
    )
    provider_response = replicate_provider.run_prediction(version, request_input, execute=execute)
    job = replicate_provider.create_job(
        kind="keyframe-generation", model=version, input=request_input,
        target_output_dir=run_dir, manifest_path=manifest_path, execute=execute,
        endpoint="predictions", provider_response=provider_response, cost_estimate=cost,
    )

    outputs: list[dict[str, Any]] = []
    final_status = job.status
    if execute and wait and job.provider_url:
        final = replicate_provider.poll_resource(job.provider_url, execute=True)
        final_status = replicate_provider._job_status(final, execute=True)
        urls = final.get("output") or []
        urls = urls if isinstance(urls, list) else [urls]
        for i, url in enumerate(urls, 1):
            if not isinstance(url, str) or not url:
                continue
            dest = run_dir / f"{key}_{seed}_{i}.{settings.get('output_format','jpg')}"
            try:
                outputs.append(replicate_provider.download_output(url, dest, execute=True))
            except Exception as e:  # noqa: BLE001 - record, don't crash the run
                outputs.append({"status": "failed", "url": url, "error": str(e)[:300]})

    manifest = {
        "version": 1, "kind": "keyframe-generation", "status": final_status if execute else "dry-run",
        "provider": "Replicate", "engine": engine, "beat": key, "prompt": prompt,
        "seed": seed, "count_preview": counts, "cost_estimate": cost,
        "job": job.to_dict(), "outputs": outputs, "created_at": job.created_at,
    }
    write_manifest(manifest_path, manifest)
    return {"ok": True, "job": job.to_dict(), "manifest": manifest,
            "manifest_path": str(manifest_path), "outputs": outputs}
