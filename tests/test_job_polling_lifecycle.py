"""Tests for provider job polling and recoverable local job status (issue #192).

Acceptance criteria:
- Job records include provider URL/status when available.
- Polling updates last_checked_at and status fields.
- Failed provider responses remain visible.
- Dry-run never calls the network.
- Tests mock provider polling success and failure.
"""

from __future__ import annotations

import json
from pathlib import Path

from lib.providers import replicate_provider
from lib.training import plan_lora_training
from lib.video_jobs import plan_video_generation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_job(tmp_path: Path, *, execute: bool = True, provider_response: dict | None = None):
    """Create a minimal job record for testing."""
    return replicate_provider.create_job(
        kind="video-generation",
        model="wan-video/wan2.1-with-lora",
        input={"prompt": "test scene"},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "run.json",
        execute=execute,
        provider_response=provider_response or {},
        jobs_dir=tmp_path,
    )


# ---------------------------------------------------------------------------
# Provider URL and lifecycle fields are present after job creation
# ---------------------------------------------------------------------------


def test_job_record_includes_provider_url_when_available(tmp_path: Path) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/xyz"},
        },
    )

    assert job.provider_url == "https://api.replicate.com/v1/predictions/xyz"
    assert job.polling_status == "starting"
    assert job.last_checked_at


def test_job_record_provider_url_empty_when_not_provided(tmp_path: Path) -> None:
    job = _make_job(tmp_path, provider_response={"status": "queued"})

    assert job.provider_url == ""
    assert job.last_checked_at  # always set at creation


def test_job_record_persisted_to_disk_with_lifecycle_fields(tmp_path: Path) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/abc"},
        },
    )

    saved = json.loads((tmp_path / f"{job.id}.json").read_text(encoding="utf-8"))
    assert saved["provider_url"] == "https://api.replicate.com/v1/predictions/abc"
    assert saved["polling_status"] == "starting"
    assert saved["output_download_state"] == "pending"
    assert saved["last_checked_at"]
    assert saved["failure_details"] == {}


# ---------------------------------------------------------------------------
# Polling updates last_checked_at and status (success path)
# ---------------------------------------------------------------------------


def test_poll_job_success_updates_status_and_last_checked_at(tmp_path: Path, monkeypatch) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/abc"},
        },
    )
    original_checked_at = job.last_checked_at

    def fake_get_json(path: str) -> dict:
        return {
            "id": "abc",
            "status": "succeeded",
            "output": ["https://cdn.replicate.com/out.mp4"],
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

    assert updated["status"] == "succeeded"
    assert updated["polling_status"] == "succeeded"
    assert updated["output_download_state"] == "available"
    assert updated["failure_details"] == {}
    assert updated["last_checked_at"] >= original_checked_at

    # Persisted record matches
    saved = json.loads((tmp_path / f"{job.id}.json").read_text(encoding="utf-8"))
    assert saved["status"] == "succeeded"
    assert saved["polling_status"] == "succeeded"


def test_poll_job_timeout_when_non_terminal_status_after_max_attempts(tmp_path: Path, monkeypatch) -> None:
    """When max_attempts is exhausted without a terminal status, polling_status becomes polling-timeout."""
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/proc"},
        },
    )

    def fake_get_json(path: str) -> dict:
        # Never returns a terminal status — forces timeout after max_attempts=1
        return {
            "status": "processing",
            "urls": {"get": "https://api.replicate.com/v1/predictions/proc"},
        }

    monkeypatch.setattr(replicate_provider, "_get_json", fake_get_json)

    updated = replicate_provider.poll_job(
        job.id,
        jobs_dir=tmp_path,
        execute=True,
        interval_seconds=0,
        max_attempts=1,
    )

    # poll_resource adds polling_error="max attempts exceeded" which maps to polling-timeout
    assert updated["polling_status"] == "polling-timeout"
    assert updated["status"] == "processing"
    assert updated["output_download_state"] == "pending"


# ---------------------------------------------------------------------------
# Failed provider responses remain visible after polling
# ---------------------------------------------------------------------------


def test_failed_response_at_creation_persists_failure_details(tmp_path: Path) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "failed",
            "error": "NSFW content detected",
        },
    )

    assert job.status == "failed"
    assert job.failure_details["error"] == "NSFW content detected"
    assert job.output_download_state == "blocked"

    saved = json.loads((tmp_path / f"{job.id}.json").read_text(encoding="utf-8"))
    assert saved["failure_details"]["error"] == "NSFW content detected"
    assert saved["output_download_state"] == "blocked"


def test_poll_failure_updates_failure_details_in_record(tmp_path: Path, monkeypatch) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/fail-test"},
        },
    )

    def fake_get_json(path: str) -> dict:
        return {
            "id": "fail-test",
            "status": "failed",
            "error": "GPU quota exceeded",
            "urls": {"get": "https://api.replicate.com/v1/predictions/fail-test"},
        }

    monkeypatch.setattr(replicate_provider, "_get_json", fake_get_json)

    updated = replicate_provider.poll_job(
        job.id,
        jobs_dir=tmp_path,
        execute=True,
        interval_seconds=0,
        max_attempts=1,
    )

    assert updated["status"] == "failed"
    assert updated["failure_details"]["error"] == "GPU quota exceeded"
    assert updated["output_download_state"] == "blocked"

    # Failure is durable — persisted to disk
    saved = json.loads((tmp_path / f"{job.id}.json").read_text(encoding="utf-8"))
    assert saved["failure_details"]["error"] == "GPU quota exceeded"


def test_cancelled_provider_status_maps_to_failed(tmp_path: Path, monkeypatch) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/cancel-test"},
        },
    )

    def fake_get_json(path: str) -> dict:
        return {"status": "canceled", "error": "user requested cancellation"}

    monkeypatch.setattr(replicate_provider, "_get_json", fake_get_json)

    updated = replicate_provider.poll_job(
        job.id,
        jobs_dir=tmp_path,
        execute=True,
        interval_seconds=0,
        max_attempts=1,
    )

    assert updated["status"] == "failed"
    assert updated["polling_status"] == "canceled"
    assert updated["output_download_state"] == "blocked"


# ---------------------------------------------------------------------------
# Dry-run never calls the network
# ---------------------------------------------------------------------------


def test_dry_run_job_has_not_started_polling_status(tmp_path: Path) -> None:
    job = _make_job(tmp_path, execute=False)

    assert job.status == "dry-run"
    assert job.polling_status == "not-started"
    assert job.output_download_state == "not-started"
    assert job.failure_details == {}


def test_dry_run_poll_resource_never_calls_network(monkeypatch) -> None:
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    network_called = []

    def trap(*args, **kwargs):
        network_called.append(args)
        raise AssertionError("network called during dry-run")

    monkeypatch.setattr(replicate_provider, "_get_json", trap)

    result = replicate_provider.poll_resource(
        "https://api.replicate.com/v1/predictions/xyz",
        execute=False,
    )

    assert network_called == []
    assert result["status"] == "dry-run"
    assert result["polling"] is False


def test_dry_run_video_generation_never_calls_network(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    monkeypatch.setattr(
        replicate_provider,
        "_post_json",
        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network called")),
    )
    monkeypatch.setattr(
        replicate_provider,
        "save_job",
        lambda record, **kwargs: tmp_path / f"{record.id}.json",
    )

    storyboard = tmp_path / "storyboard.json"
    storyboard.write_text(
        '{"title": "Test Film", "scenes": [{"id": "s1", "prompt": "a room"}]}',
        encoding="utf-8",
    )

    result = plan_video_generation(storyboard_path=storyboard, output_root=tmp_path)

    assert result["job"]["status"] == "dry-run"
    assert result["job"]["polling_status"] == "not-started"
    assert result["job"]["output_download_state"] == "not-started"


def test_dry_run_lora_training_never_calls_network(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    monkeypatch.setattr(
        replicate_provider,
        "_post_json",
        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network called")),
    )
    monkeypatch.setattr(
        replicate_provider,
        "save_job",
        lambda record, **kwargs: tmp_path / f"{record.id}.json",
    )

    result = plan_lora_training(
        subject="kris",
        output_root=tmp_path,
        input_images_url="https://example.com/data.zip",
    )

    assert result["job"]["status"] == "dry-run"
    assert result["job"]["polling_status"] == "not-started"
    assert result["job"]["output_download_state"] == "not-started"


# ---------------------------------------------------------------------------
# Training job lifecycle mirrors video job lifecycle
# ---------------------------------------------------------------------------


def test_training_job_record_has_all_lifecycle_fields(tmp_path: Path) -> None:
    job = replicate_provider.create_job(
        kind="lora-training",
        model="ostris/flux-dev-lora-trainer",
        input={"input_images": "https://example.com/data.zip", "steps": 1000},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "training.json",
        execute=True,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/trainings/abc"},
        },
        jobs_dir=tmp_path,
    )

    assert job.kind == "lora-training"
    assert job.provider == "replicate"
    assert job.provider_url == "https://api.replicate.com/v1/trainings/abc"
    assert job.polling_status == "starting"
    assert job.output_download_state == "pending"
    assert job.last_checked_at
    assert job.created_at
    assert job.updated_at


def test_training_job_poll_success_updates_record(tmp_path: Path, monkeypatch) -> None:
    job = replicate_provider.create_job(
        kind="lora-training",
        model="ostris/flux-dev-lora-trainer",
        input={"input_images": "https://example.com/data.zip", "steps": 500},
        target_output_dir=tmp_path,
        manifest_path=tmp_path / "training.json",
        execute=True,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/trainings/train-abc"},
        },
        jobs_dir=tmp_path,
    )

    def fake_get_json(path: str) -> dict:
        return {
            "id": "train-abc",
            "status": "succeeded",
            "output": {"version": "lora-model-version-hash"},
            "urls": {"get": "https://api.replicate.com/v1/trainings/train-abc"},
        }

    monkeypatch.setattr(replicate_provider, "_get_json", fake_get_json)

    updated = replicate_provider.poll_job(
        job.id,
        jobs_dir=tmp_path,
        execute=True,
        interval_seconds=0,
        max_attempts=1,
    )

    assert updated["status"] == "succeeded"
    assert updated["polling_status"] == "succeeded"
    assert updated["output_download_state"] == "available"


# ---------------------------------------------------------------------------
# capture_job_provider_response can be called standalone (testable update path)
# ---------------------------------------------------------------------------


def test_capture_job_provider_response_updates_lifecycle(tmp_path: Path) -> None:
    """The update path is callable with a mocked response dict — no network needed."""
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/standalone"},
        },
    )

    mock_response = {
        "id": "standalone",
        "status": "succeeded",
        "output": ["https://cdn.replicate.com/result.mp4"],
        "urls": {"get": "https://api.replicate.com/v1/predictions/standalone"},
    }

    updated = replicate_provider.capture_job_provider_response(
        job.id, mock_response, jobs_dir=tmp_path
    )

    assert updated["status"] == "succeeded"
    assert updated["polling_status"] == "succeeded"
    assert updated["output_download_state"] == "available"
    assert updated["last_checked_at"] >= job.last_checked_at
    assert updated["failure_details"] == {}


def test_capture_job_provider_response_failure_path(tmp_path: Path) -> None:
    job = _make_job(
        tmp_path,
        provider_response={
            "status": "processing",
            "urls": {"get": "https://api.replicate.com/v1/predictions/fail-path"},
        },
    )

    mock_failure = {
        "status": "failed",
        "error": "out of memory",
    }

    updated = replicate_provider.capture_job_provider_response(
        job.id, mock_failure, jobs_dir=tmp_path
    )

    assert updated["status"] == "failed"
    assert updated["failure_details"]["error"] == "out of memory"
    assert updated["output_download_state"] == "blocked"
