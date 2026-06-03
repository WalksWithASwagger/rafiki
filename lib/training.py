"""Subject-aware LoRA training manifests and Replicate dry-run jobs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.jobs import write_manifest
from lib.media_registry import subjects as registry_subjects
from lib.providers import replicate_provider

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TRAINER_MODEL = "ostris/flux-dev-lora-trainer"
DEFAULT_TRAINER_VERSION = "26dce37af90b9d997eeb970d92e47de3064d46c300504ae376c75bef6a9022d2"


def plan_lora_training(
    *,
    subject: str,
    output_root: Path | None = None,
    execute: bool = False,
    trainer_model: str = DEFAULT_TRAINER_MODEL,
    trainer_version: str = DEFAULT_TRAINER_VERSION,
    input_images_url: str = "",
    steps: int = 1000,
    lora_rank: int = 16,
) -> dict[str, Any]:
    output_root = output_root or REPO_ROOT / "output"
    profile = _subject_profile(subject)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    train_dir = output_root / subject / f"train-{stamp}"
    manifest_path = train_dir / "training.json"
    trigger = profile.get("trigger_word") or subject.upper().replace("-", "")
    destination = f"rafiki/{subject}-flux-lora"
    request_input = {
        "input_images": input_images_url,
        "trigger_word": trigger,
        "steps": steps,
        "lora_rank": lora_rank,
    }
    provider_response = replicate_provider.run_training(
        destination,
        trainer_model,
        trainer_version,
        request_input,
        execute=execute,
    )
    job = replicate_provider.create_job(
        kind="lora-training",
        model=trainer_model,
        input=request_input,
        target_output_dir=train_dir,
        manifest_path=manifest_path,
        execute=execute,
        endpoint="trainings",
        provider_response=provider_response,
    )
    manifest = {
        "version": 1,
        "kind": "lora-training",
        "status": "queued" if execute else "dry-run",
        "subject": subject,
        "trigger_word": trigger,
        "trainer_model": trainer_model,
        "trainer_version": trainer_version,
        "destination": destination,
        "request": request_input,
        "job": job.to_dict(),
        "profile": profile,
        "created_at": job.created_at,
    }
    write_manifest(manifest_path, manifest)
    return {"ok": True, "job": job.to_dict(), "manifest": manifest, "manifest_path": str(manifest_path)}


def _subject_profile(subject: str) -> dict[str, Any]:
    for profile in registry_subjects():
        if profile.key == subject:
            return profile.to_dict()
    return {"key": subject, "display_name": subject.replace("-", " ").title(), "trigger_word": ""}
