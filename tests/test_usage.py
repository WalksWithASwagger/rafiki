"""Tests for lib.usage — local usage log read/write/append."""

from __future__ import annotations

import json

import pytest

from lib import usage


@pytest.fixture
def isolated_log(tmp_path, monkeypatch):
    """Redirect USAGE_LOG_PATH to a tmp file so tests never touch real data/."""
    log_path = tmp_path / "usage-log.json"
    monkeypatch.setattr(usage, "USAGE_LOG_PATH", log_path)
    return log_path


def test_load_empty_returns_default(isolated_log):
    assert not isolated_log.exists()
    assert usage.load_usage_log() == {"entries": [], "total_images": 0}


def test_load_corrupted_backs_up_and_resets(isolated_log):
    isolated_log.write_text("{not valid json", encoding="utf-8")

    result = usage.load_usage_log()

    assert result == {"entries": [], "total_images": 0}
    backup = isolated_log.with_suffix(".json.bak")
    assert backup.exists(), "corrupted log should be moved aside as .json.bak"
    assert not isolated_log.exists(), "original corrupted log should be renamed"


def test_log_generation_appends_entry(isolated_log):
    usage.log_generation(
        prompt="a cat",
        model="gemini-2.5-flash-image",
        output_path="/tmp/out.png",
        aspect_ratio="1:1",
        style="punk",
    )

    data = json.loads(isolated_log.read_text(encoding="utf-8"))
    assert len(data["entries"]) == 1
    assert data["total_images"] == 1
    entry = data["entries"][0]
    assert entry["prompt"] == "a cat"
    assert entry["model"] == "gemini-2.5-flash-image"
    assert entry["aspect_ratio"] == "1:1"
    assert entry["style"] == "punk"
    assert entry["ok"] is True


def test_log_generation_failed_does_not_increment_total(isolated_log):
    usage.log_generation(
        prompt="a cat",
        model="gemini-2.5-flash-image",
        output_path="/tmp/out.png",
        aspect_ratio="1:1",
        ok=False,
        error="boom",
    )

    data = json.loads(isolated_log.read_text(encoding="utf-8"))
    assert len(data["entries"]) == 1
    assert data["total_images"] == 0
    assert data["entries"][0]["error"] == "boom"
    assert data["entries"][0]["ok"] is False


def test_save_creates_parent_directory(tmp_path, monkeypatch):
    nested = tmp_path / "deep" / "nested" / "usage-log.json"
    monkeypatch.setattr(usage, "USAGE_LOG_PATH", nested)

    usage.save_usage_log({"entries": [], "total_images": 0})

    assert nested.exists()
    assert json.loads(nested.read_text(encoding="utf-8")) == {
        "entries": [],
        "total_images": 0,
    }


def test_summarize_usage_combines_log_and_run_manifests(isolated_log, tmp_path):
    usage.save_usage_log({
        "entries": [
            {"ok": True, "model": "gpt-image-2"},
            {"ok": False, "model": "gpt-image-2"},
        ],
        "total_images": 1,
    })
    run_dir = tmp_path / "output" / "demo" / "run-20260518-101010"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({
            "model": "gpt-image-2",
            "provider": "OpenAI",
            "timestamp": "2026-05-18 10:10",
            "duration_seconds": 12.5,
            "state": "partial",
            "images": [
                {
                    "file": "01-hero.png",
                    "ok": True,
                    "model": "gpt-image-2",
                    "provider": "OpenAI",
                    "cost_estimate": {"amount": 0.04, "currency": "USD", "estimated": True},
                },
                {
                    "file": "02-miss.png",
                    "ok": False,
                    "model": "gpt-image-2",
                    "provider": "OpenAI",
                    "cost_estimate": {"amount": None, "currency": "USD", "estimated": False},
                },
            ],
        }),
        encoding="utf-8",
    )

    summary = usage.summarize_usage(tmp_path / "output")

    assert summary["usage_log"]["entries"] == 2
    assert summary["usage_log"]["successful_entries"] == 1
    assert summary["archive"]["projects"] == 1
    assert summary["archive"]["runs"] == 1
    assert summary["archive"]["images"] == 2
    assert summary["archive"]["failed_images"] == 1
    assert summary["archive"]["known_cost"]["amount"] == 0.04
    assert summary["archive"]["known_cost"]["estimated_images"] == 1
    assert summary["archive"]["known_cost"]["unestimated_images"] == 1
    assert summary["archive"]["estimated_cost"]["amount"] == 0.04
    assert summary["archive"]["estimated_cost"]["manifest_amount_images"] == 1
    assert summary["archive"]["by_model"] == [{"model": "gpt-image-2", "images": 2}]
    assert summary["recent_runs"][0]["project"] == "demo"


def test_summarize_usage_applies_pricing_profile_to_successful_images(isolated_log, tmp_path):
    usage.save_usage_log({"entries": [], "total_images": 0})
    run_dir = tmp_path / "output" / "demo" / "run-20260518-111111"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({
            "model": "gemini-2.5-flash-image",
            "provider": "Gemini",
            "resolution": "1K",
            "duration_seconds": 2.0,
            "state": "succeeded",
            "images": [
                {
                    "file": "01-hero.png",
                    "ok": True,
                    "model": "gemini-2.5-flash-image",
                    "provider": "Gemini",
                    "cost_estimate": {"amount": None, "currency": "USD", "estimated": False},
                }
            ],
        }),
        encoding="utf-8",
    )

    summary = usage.summarize_usage(tmp_path / "output")

    assert summary["archive"]["known_cost"]["amount"] == 0
    assert summary["archive"]["estimated_cost"]["amount"] == 0.039
    assert summary["archive"]["estimated_cost"]["profile_estimated_images"] == 1
    assert summary["archive"]["estimated_cost"]["unpriced_images"] == 0


def test_summarize_usage_prefers_imported_billing_for_spend(isolated_log, tmp_path):
    usage.save_usage_log({"entries": [], "total_images": 0})
    billing_path = tmp_path / "billing-imports.json"
    billing_path.write_text(
        json.dumps({
            "version": 1,
            "imports": [
                {
                    "id": "one",
                    "provider": "OpenAI",
                    "model": "gpt-image-2",
                    "amount": 22.0,
                    "currency": "USD",
                }
            ],
        }),
        encoding="utf-8",
    )

    summary = usage.summarize_usage(tmp_path / "output", billing_import_path=billing_path)

    assert summary["provider_billing"]["amount"] == 22.0
    assert summary["archive"]["spend"]["amount"] == 22.0
    assert summary["archive"]["spend"]["basis"] == "provider_billing_imports"
