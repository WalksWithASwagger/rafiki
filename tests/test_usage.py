"""Tests for lib.usage — local usage log read/write/append."""

from __future__ import annotations

import json
from pathlib import Path

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
