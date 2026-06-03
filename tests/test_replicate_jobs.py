from __future__ import annotations

import json
from pathlib import Path

from lib.providers import replicate_provider
from lib.training import plan_lora_training
from lib.video_jobs import assemble_video_edit, plan_video_generation


def test_replicate_prediction_dry_run_never_requires_token(monkeypatch) -> None:
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)

    result = replicate_provider.run_prediction("model/version", {"prompt": "hello"}, execute=False)

    assert result["status"] == "dry-run"
    assert result["input"]["prompt"] == "hello"


def test_replicate_poll_and_download_dry_runs_never_require_token(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)

    poll = replicate_provider.poll_resource("/predictions/abc", execute=False)
    download = replicate_provider.download_output("https://example.com/out.mp4", tmp_path / "out.mp4", execute=False)

    assert poll["status"] == "dry-run"
    assert poll["polling"] is False
    assert download["status"] == "dry-run"
    assert not (tmp_path / "out.mp4").exists()


def test_replicate_job_status_captures_failed_provider_response(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(replicate_provider, "save_job", lambda record: tmp_path / f"{record.id}.json")

    job = replicate_provider.create_job(
        kind="video-generation",
        model="model/version",
        input={"prompt": "x"},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "run.json",
        execute=True,
        provider_response={"status": "failed", "error": "bad prompt"},
    )

    assert job.status == "failed"
    assert job.error == "bad prompt"


def test_lora_training_dry_run_writes_manifest_without_network(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(replicate_provider, "save_job", lambda record: tmp_path / f"{record.id}.json")

    result = plan_lora_training(subject="kris", output_root=tmp_path, input_images_url="https://example.com/data.zip")

    manifest_path = Path(result["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert result["job"]["status"] == "dry-run"
    assert manifest["trainer_version"] == "26dce37af90b9d997eeb970d92e47de3064d46c300504ae376c75bef6a9022d2"
    assert manifest["request"]["input_images"] == "https://example.com/data.zip"


def test_video_generation_dry_run_writes_manifest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(replicate_provider, "save_job", lambda record: tmp_path / f"{record.id}.json")
    storyboard = tmp_path / "storyboard.json"
    storyboard.write_text(json.dumps({"title": "Time Airport", "scenes": [{"id": "s1", "prompt": "terminal"}]}), encoding="utf-8")

    result = plan_video_generation(storyboard_path=storyboard, output_root=tmp_path)

    assert result["job"]["status"] == "dry-run"
    assert result["manifest"]["project"] == "time-airport"
    assert Path(result["manifest_path"]).exists()


def test_video_assemble_dry_run_validates_clip_paths(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    edit = tmp_path / "edit.json"
    edit.write_text(json.dumps({"project": "demo", "clips": [{"path": "clip.mp4"}]}), encoding="utf-8")

    result = assemble_video_edit(edit_path=edit, output_dir=tmp_path / "out")

    assert result["manifest"]["status"] == "dry-run"
    assert result["manifest"]["missing"] == []
    assert Path(result["manifest_path"]).exists()
