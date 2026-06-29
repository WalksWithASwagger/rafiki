"""Tests for the keyframe (stills) pipeline — dry-run writes a manifest, no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib import keyframe_jobs
from lib.providers import replicate_provider

_KEYFRAMES = {
    "settings": {
        "model": "walkswithaswagger/alexandra-samuel",
        "version": "462455356f80fd66fc5ba68d277f518f7781bfe77e0197be85015f560098493e",
        "model_type": "dev",
        "aspect_ratio": "21:9",
        "num_inference_steps": 32,
        "guidance_scale": 3.2,
        "lora_scale": 0.95,
        "output_format": "jpg",
    },
    "beats": {
        "situ_01_starman": {"title": "The Starman Arrival", "prompt": "HERO PORTRAIT of KRISKRUG"},
        "situ_02_backstage": {"title": "Backstage", "prompt": "close-up of KRISKRUG androgynous"},
    },
}


def _write_keyframes(tmp_path: Path) -> Path:
    p = tmp_path / "keyframes.json"
    p.write_text(json.dumps(_KEYFRAMES), encoding="utf-8")
    return p


def _no_network(monkeypatch, tmp_path):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    monkeypatch.setattr(replicate_provider, "save_job", lambda record, **kwargs: tmp_path / f"{record.id}.json")
    monkeypatch.setattr(
        replicate_provider, "_post_json",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("network called")),
    )


def test_resolve_beat_by_key_and_number():
    _, beats = _KEYFRAMES["settings"], _KEYFRAMES["beats"]
    assert keyframe_jobs.resolve_beat(beats, "situ_02_backstage")[0] == "situ_02_backstage"
    assert keyframe_jobs.resolve_beat(beats, "02")[0] == "situ_02_backstage"
    assert keyframe_jobs.resolve_beat(beats, "1")[0] == "situ_01_starman"


def test_unknown_beat_raises():
    with pytest.raises(ValueError):
        keyframe_jobs.resolve_beat(_KEYFRAMES["beats"], "99")


def test_build_input_payload_shape():
    payload = keyframe_jobs.build_keyframe_input(
        _KEYFRAMES["settings"], "a prompt", num_outputs=6, seed=42,
    )
    assert payload["num_outputs"] == 4  # clamped to max
    assert payload["aspect_ratio"] == "21:9"
    assert payload["lora_scale"] == 0.95
    assert payload["seed"] == 42


def test_flux2_engine_not_supported(tmp_path):
    kf = _write_keyframes(tmp_path)
    with pytest.raises(ValueError):
        keyframe_jobs.plan_keyframe_generation(keyframes_path=kf, beat="01", engine="flux2-klein")


def test_dry_run_plan_writes_manifest(tmp_path, monkeypatch):
    _no_network(monkeypatch, tmp_path)
    kf = _write_keyframes(tmp_path)
    result = keyframe_jobs.plan_keyframe_generation(
        keyframes_path=kf, beat="02", num_outputs=2, seed=7, output_root=tmp_path, execute=False,
    )
    assert result["job"]["status"] == "dry-run"
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["beat"] == "situ_02_backstage"
    assert manifest["seed"] == 7
    assert "KRISKRUG" in manifest["prompt"]
    assert manifest["cost_estimate"]["amount"] == 0.0
