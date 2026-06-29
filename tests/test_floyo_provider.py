"""Tests for the Floyo provider — dry-run never touches the network."""

from __future__ import annotations

import pytest

from lib.providers import floyo_provider


def test_has_token_reads_env(monkeypatch):
    monkeypatch.delenv("FLOYO_KEY", raising=False)
    assert floyo_provider.has_token() is False
    monkeypatch.setenv("FLOYO_KEY", "secret")
    assert floyo_provider.has_token() is True


def test_run_workflow_dry_run_never_requires_token(monkeypatch):
    monkeypatch.delenv("FLOYO_KEY", raising=False)
    result = floyo_provider.run_workflow("wan22_endframe", {"67": {"inputs": {}}}, execute=False)
    assert result["status"] == "dry-run"
    assert result["workflow_name"] == "wan22_endframe"


def test_upload_asset_dry_run_no_network(monkeypatch):
    monkeypatch.delenv("FLOYO_KEY", raising=False)
    result = floyo_provider.upload_asset("/tmp/plate.jpg", execute=False)
    assert result["status"] == "dry-run"
    assert result["input_path"].startswith("#dry-run/")


def test_poll_run_dry_run(monkeypatch):
    monkeypatch.delenv("FLOYO_KEY", raising=False)
    result = floyo_provider.poll_run("run-123", execute=False)
    assert result["status"] == "dry-run"
    assert result["polling"] is False


def test_execute_without_token_raises(monkeypatch):
    monkeypatch.delenv("FLOYO_KEY", raising=False)
    with pytest.raises(floyo_provider.FloyoError):
        floyo_provider.run_workflow("wan22_endframe", {}, execute=True)


def test_find_outputs_and_url():
    run = {"outputs": [{"presigned_url": "https://x/clip.mp4", "file_name": "clip.mp4"}, "skip"]}
    outs = floyo_provider.find_outputs(run)
    assert len(outs) == 1
    assert floyo_provider.output_url(outs[0]) == "https://x/clip.mp4"


def test_job_status_mapping():
    assert floyo_provider._job_status({}, execute=False) == "dry-run"
    assert floyo_provider._job_status({"status": "done"}, execute=True) == "succeeded"
    assert floyo_provider._job_status({"status": "error"}, execute=True) == "failed"
    assert floyo_provider._job_status({"status": "processing"}, execute=True) == "processing"


def test_done_with_error_is_failed():
    # Floyo can return status=done alongside a system error dict.
    resp = {"status": "done", "error": {"type": "system", "code": "system_error", "message": "boom"}}
    assert floyo_provider._job_status(resp, execute=True) == "failed"
    assert floyo_provider._job_error(resp) == "boom"
