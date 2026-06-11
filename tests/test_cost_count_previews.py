"""Tests for cost/count preview payloads for training and video generation.

Covers:
- build_training_preview / build_video_preview return correct count/provider/model/pricing-note.
- Graceful degradation when Replicate pricing is unknown (no pricing.json entry).
- No network calls during preview.
- Server preview endpoints return expected structure.
- Execute confirmation is still required after a preview.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.training import build_training_preview
from lib.video_jobs import build_video_preview
from tests.server_harness import http_post_json


# ---------------------------------------------------------------------------
# Training preview — unit
# ---------------------------------------------------------------------------


def test_training_preview_dry_run_returns_correct_counts():
    result = build_training_preview(subject="kris")

    assert result["kind"] == "lora-training"
    assert result["subject"] == "kris"
    assert result["provider"] == "Replicate"
    assert result["dry_run"] is True
    assert result["execute"] is False
    counts = result["count_preview"]
    assert counts["planned_provider_jobs"] == 1
    assert counts["network_calls"] == 0
    assert counts["training_runs"] == 1
    assert counts["steps"] == 1000
    assert counts["lora_rank"] == 16
    assert counts["dataset_urls"] == 0


def test_training_preview_execute_sets_network_calls():
    result = build_training_preview(subject="kris", execute=True)

    assert result["execute"] is True
    assert result["dry_run"] is False
    assert result["count_preview"]["network_calls"] == 1


def test_training_preview_with_dataset_url_counts_one():
    result = build_training_preview(subject="kris", input_images_url="https://example.com/data.zip")

    assert result["count_preview"]["dataset_urls"] == 1


def test_training_preview_includes_provider_and_model():
    result = build_training_preview(subject="kris")

    assert result["provider"] == "Replicate"
    assert "ostris/flux-dev-lora-trainer" in result["model"]


def test_training_preview_includes_pricing_note():
    result = build_training_preview(subject="kris")

    note = result["pricing_note"]
    assert isinstance(note, str)
    assert len(note) > 0
    # note must be explicit about unpriced state — not a silent zero
    assert "provider billing" in note.lower() or "not estimated" in note.lower()


def test_training_preview_cost_estimate_dry_run_amount_is_zero():
    result = build_training_preview(subject="kris")

    # dry_run=True means no provider spend; local amount is 0.0
    assert result["cost_estimate"]["amount"] == 0.0


def test_training_preview_cost_estimate_execute_amount_is_none():
    # execute=True but Replicate training cost is not in pricing.json
    result = build_training_preview(subject="kris", execute=True)

    assert result["cost_estimate"]["amount"] is None


def test_training_preview_makes_no_network_calls(monkeypatch):
    """Preview must not touch the network even when execute=True."""
    import lib.providers.replicate_provider as rp

    def boom(*args, **kwargs):
        raise AssertionError("network call made during preview")

    monkeypatch.setattr(rp, "_post_json", boom, raising=False)

    result = build_training_preview(subject="kris", execute=True)
    assert result["kind"] == "lora-training"


# ---------------------------------------------------------------------------
# Video preview — unit
# ---------------------------------------------------------------------------


def test_video_preview_dry_run_counts_scenes(tmp_path: Path):
    storyboard = tmp_path / "storyboard.json"
    storyboard.write_text(
        json.dumps({"title": "Test Film", "scenes": [
            {"id": "s1", "prompt": "a street"},
            {"id": "s2", "prompt": "a park"},
            {"id": "s3"},
        ]}),
        encoding="utf-8",
    )

    result = build_video_preview(storyboard_path=storyboard)

    assert result["kind"] == "video-generation"
    assert result["dry_run"] is True
    assert result["execute"] is False
    counts = result["count_preview"]
    assert counts["storyboard_scenes"] == 3
    assert counts["prompted_scenes"] == 2
    assert counts["planned_provider_jobs"] == 1
    assert counts["network_calls"] == 0
    assert counts["requested_videos"] == 1


def test_video_preview_execute_sets_network_calls(tmp_path: Path):
    storyboard = tmp_path / "sb.json"
    storyboard.write_text(
        json.dumps({"title": "clip", "scenes": [{"id": "s1", "prompt": "x"}]}),
        encoding="utf-8",
    )

    result = build_video_preview(storyboard_path=storyboard, execute=True)

    assert result["execute"] is True
    assert result["count_preview"]["network_calls"] == 1


def test_video_preview_includes_provider_and_model(tmp_path: Path):
    storyboard = tmp_path / "sb.json"
    storyboard.write_text(json.dumps({"title": "clip", "scenes": []}), encoding="utf-8")

    result = build_video_preview(storyboard_path=storyboard)

    assert result["provider"] == "Replicate"
    assert result["model"] == "wan-video/wan2.1-with-lora"


def test_video_preview_includes_pricing_note(tmp_path: Path):
    storyboard = tmp_path / "sb.json"
    storyboard.write_text(json.dumps({"title": "clip", "scenes": []}), encoding="utf-8")

    result = build_video_preview(storyboard_path=storyboard)

    note = result["pricing_note"]
    assert isinstance(note, str)
    assert len(note) > 0
    assert "provider billing" in note.lower() or "not estimated" in note.lower()


def test_video_preview_execute_cost_is_none(tmp_path: Path):
    storyboard = tmp_path / "sb.json"
    storyboard.write_text(
        json.dumps({"title": "clip", "scenes": [{"id": "s1", "prompt": "x"}]}),
        encoding="utf-8",
    )

    result = build_video_preview(storyboard_path=storyboard, execute=True)

    assert result["cost_estimate"]["amount"] is None


def test_video_preview_makes_no_network_calls(tmp_path: Path, monkeypatch):
    """Preview reads only the storyboard file; no provider calls."""
    import lib.providers.replicate_provider as rp

    def boom(*args, **kwargs):
        raise AssertionError("network call made during preview")

    monkeypatch.setattr(rp, "_post_json", boom, raising=False)

    storyboard = tmp_path / "sb.json"
    storyboard.write_text(
        json.dumps({"title": "clip", "scenes": [{"id": "s1", "prompt": "x"}]}),
        encoding="utf-8",
    )

    result = build_video_preview(storyboard_path=storyboard, execute=True)
    assert result["kind"] == "video-generation"


def test_video_preview_missing_storyboard_raises(tmp_path: Path):
    missing = tmp_path / "nonexistent.json"

    with pytest.raises(FileNotFoundError):
        build_video_preview(storyboard_path=missing)


# ---------------------------------------------------------------------------
# Graceful degradation: Replicate not in pricing.json
# ---------------------------------------------------------------------------


def test_training_preview_gracefully_omits_amount_for_replicate():
    """Replicate is not in pricing.json; amount must be None for execute mode."""
    result = build_training_preview(subject="test-subject", execute=True)

    assert result["cost_estimate"]["amount"] is None
    # pricing_note must be present and non-empty
    assert result["pricing_note"]


def test_video_preview_gracefully_omits_amount_for_replicate(tmp_path: Path):
    storyboard = tmp_path / "sb.json"
    storyboard.write_text(json.dumps({"title": "clip", "scenes": [{"id": "s1"}]}), encoding="utf-8")

    result = build_video_preview(storyboard_path=storyboard, execute=True)

    assert result["cost_estimate"]["amount"] is None
    assert result["pricing_note"]


# ---------------------------------------------------------------------------
# Server preview endpoints
# ---------------------------------------------------------------------------


def test_server_train_lora_preview_returns_preview(server):
    resp = http_post_json(f"{server}/api/jobs/train-lora/preview", {"subject": "kris"})

    assert resp.status == 200
    data = json.loads(resp.read())
    assert data["kind"] == "lora-training"
    assert data["provider"] == "Replicate"
    assert data["dry_run"] is True
    assert data["count_preview"]["planned_provider_jobs"] == 1
    assert data["pricing_note"]


def test_server_train_lora_preview_requires_subject(server):
    resp = http_post_json(f"{server}/api/jobs/train-lora/preview", {})

    assert resp.status == 400
    body = json.loads(resp.read())
    assert "subject" in body["error"].lower()


def test_server_video_generate_preview_returns_preview(server, tmp_path):
    storyboard = tmp_path / "output" / "sb.json"
    storyboard.parent.mkdir(parents=True, exist_ok=True)
    storyboard.write_text(
        json.dumps({"title": "Clip", "scenes": [{"id": "s1", "prompt": "a shot"}]}),
        encoding="utf-8",
    )

    resp = http_post_json(f"{server}/api/jobs/video-generate/preview", {"storyboard": str(storyboard)})

    assert resp.status == 200
    data = json.loads(resp.read())
    assert data["kind"] == "video-generation"
    assert data["provider"] == "Replicate"
    assert data["count_preview"]["storyboard_scenes"] == 1
    assert data["pricing_note"]


def test_server_video_generate_preview_requires_storyboard(server):
    resp = http_post_json(f"{server}/api/jobs/video-generate/preview", {})

    assert resp.status == 400
    body = json.loads(resp.read())
    assert "storyboard" in body["error"].lower()


def test_execute_still_requires_confirm_after_preview(server, monkeypatch):
    """Calling preview must not bypass the execute confirmation guard on the execute endpoint."""
    import lib.providers.replicate_provider as rp

    monkeypatch.setattr(
        rp,
        "_post_json",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("network called")),
        raising=False,
    )

    resp = http_post_json(f"{server}/api/jobs/train-lora", {
        "subject": "kris",
        "execute": True,
        # confirm_execute intentionally omitted
    })

    assert resp.status == 400
    body = json.loads(resp.read())
    assert "confirm_execute" in body["error"]
