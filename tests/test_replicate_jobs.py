from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

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


def test_replicate_job_status_captures_failed_provider_response(tmp_path: Path) -> None:
    job = replicate_provider.create_job(
        kind="video-generation",
        model="model/version",
        input={"prompt": "x"},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "run.json",
        execute=True,
        provider_response={"status": "failed", "error": "bad prompt"},
        jobs_dir=tmp_path,
    )

    assert job.status == "failed"
    assert job.error == "bad prompt"
    assert job.polling_status == "failed"
    assert job.output_download_state == "blocked"
    assert job.failure_details["error"] == "bad prompt"
    assert job.last_checked_at


def test_replicate_job_records_provider_url_and_download_state(tmp_path: Path) -> None:
    job = replicate_provider.create_job(
        kind="video-generation",
        model="model/version",
        input={"prompt": "x"},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "run.json",
        execute=True,
        provider_response={
            "status": "succeeded",
            "output": ["https://example.com/out.mp4"],
            "urls": {"get": "https://api.replicate.com/v1/predictions/abc"},
        },
        jobs_dir=tmp_path,
    )

    assert job.provider_url == "https://api.replicate.com/v1/predictions/abc"
    assert job.polling_status == "succeeded"
    assert job.output_download_state == "available"

    updated = replicate_provider.capture_job_output_download(
        job.id,
        {"status": "downloaded", "output_path": str(tmp_path / "out.mp4"), "bytes": 12},
        jobs_dir=tmp_path,
    )

    assert updated["output_download_state"] == "downloaded"
    assert updated["output_download"]["bytes"] == 12


def test_replicate_poll_job_captures_failed_response(tmp_path: Path, monkeypatch) -> None:
    job = replicate_provider.create_job(
        kind="video-generation",
        model="model/version",
        input={"prompt": "x"},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "run.json",
        execute=True,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/abc"},
        },
        jobs_dir=tmp_path,
    )
    calls: list[str] = []

    def fake_get_json(path: str) -> dict:
        calls.append(path)
        return {
            "id": "abc",
            "status": "failed",
            "error": "provider rejected the prompt",
            "urls": {"get": "https://api.replicate.com/v1/predictions/abc"},
        }

    monkeypatch.setattr(replicate_provider, "_get_json", fake_get_json)

    updated = replicate_provider.poll_job(
        job.id,
        jobs_dir=tmp_path,
        execute=True,
        interval_seconds=0,
        max_attempts=1,
    )

    assert calls == ["/predictions/abc"]
    assert updated["status"] == "failed"
    assert updated["failure_details"]["error"] == "provider rejected the prompt"
    saved = json.loads((tmp_path / f"{job.id}.json").read_text(encoding="utf-8"))
    assert saved["polling_status"] == "failed"
    assert saved["output_download_state"] == "blocked"


def test_lora_training_dry_run_writes_manifest_without_network(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(replicate_provider, "save_job", lambda record, **kwargs: tmp_path / f"{record.id}.json")
    monkeypatch.setattr(replicate_provider, "_post_json", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network called")))

    result = plan_lora_training(subject="kris", output_root=tmp_path, input_images_url="https://example.com/data.zip")

    manifest_path = Path(result["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert result["job"]["status"] == "dry-run"
    assert result["job"]["cost_estimate"]["amount"] == 0.0
    assert result["job"]["cost_estimate"]["counts"]["planned_provider_jobs"] == 1
    assert manifest["count_preview"]["steps"] == 1000
    assert manifest["trainer_version"] == "26dce37af90b9d997eeb970d92e47de3064d46c300504ae376c75bef6a9022d2"
    assert manifest["request"]["input_images"] == "https://example.com/data.zip"


def test_video_generation_dry_run_writes_manifest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(replicate_provider, "save_job", lambda record, **kwargs: tmp_path / f"{record.id}.json")
    monkeypatch.setattr(replicate_provider, "_post_json", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network called")))
    storyboard = tmp_path / "storyboard.json"
    storyboard.write_text(json.dumps({"title": "Time Airport", "scenes": [{"id": "s1", "prompt": "terminal"}]}), encoding="utf-8")

    result = plan_video_generation(storyboard_path=storyboard, output_root=tmp_path)

    assert result["job"]["status"] == "dry-run"
    assert result["job"]["cost_estimate"]["counts"]["storyboard_scenes"] == 1
    assert result["manifest"]["count_preview"]["requested_videos"] == 1
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


def test_video_assemble_dry_run_reports_missing_audio_and_duration_mismatch(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    edit = tmp_path / "edit.json"
    edit.write_text(
        json.dumps(
            {
                "project": "demo",
                "audio_path": "missing.wav",
                "clips": [
                    {
                        "path": "clip.mp4",
                        "duration_seconds": 2.0,
                        "expected_duration_seconds": 3.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = assemble_video_edit(edit_path=edit, output_dir=tmp_path / "out")

    assert result["manifest"]["status"] == "blocked"
    errors = result["manifest"]["validation"]["errors"]
    assert {error["type"] for error in errors} == {"missing_audio", "duration_mismatch"}
    assert result["manifest"]["missing_audio"][0].endswith("missing.wav")


def test_video_assemble_execute_renders_tiny_fixture_when_ffmpeg_available(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    _write_tiny_mp4(clip)
    edit = tmp_path / "edit.json"
    edit.write_text(json.dumps({"project": "demo", "clips": [{"path": "clip.mp4"}]}), encoding="utf-8")

    result = assemble_video_edit(edit_path=edit, output_dir=tmp_path / "out", execute=True)

    output_path = Path(result["manifest"]["output_path"])
    assert result["manifest"]["status"] == "rendered"
    assert result["manifest"]["ffmpeg"]["exit_code"] == 0
    assert output_path.exists()


def test_video_assemble_execute_records_ffmpeg_failure_when_ffmpeg_available(tmp_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg unavailable")
    clip = tmp_path / "broken.mp4"
    clip.write_bytes(b"not an mp4")
    edit = tmp_path / "edit.json"
    edit.write_text(json.dumps({"project": "demo", "clips": [{"path": "broken.mp4"}]}), encoding="utf-8")

    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        assemble_video_edit(edit_path=edit, output_dir=tmp_path / "out", execute=True)

    manifest = json.loads((tmp_path / "out" / "edit.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
    assert manifest["ffmpeg"]["exit_code"] != 0


def _write_tiny_mp4(path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("ffmpeg unavailable")
    proc = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=16x16:duration=0.2:rate=1",
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "mpeg4",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.skip(f"ffmpeg fixture generation unavailable: {proc.stderr[-200:]}")
