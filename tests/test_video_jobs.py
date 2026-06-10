"""Unit tests for validate_edit_manifest in lib/video_jobs."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.video_jobs import validate_edit_manifest


def _clip_entry(path: Path, **kwargs) -> dict:
    return {"path": str(path), **kwargs}


def _edit(clips: list, **kwargs) -> dict:
    return {"clips": clips, **kwargs}


# ---------------------------------------------------------------------------
# Valid manifest
# ---------------------------------------------------------------------------


def test_valid_manifest_passes(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"")

    result = validate_edit_manifest(_edit([_clip_entry(clip)]), base_path=tmp_path)

    assert result["ok"] is True
    assert result["errors"] == []
    assert len(result["clips"]) == 1


# ---------------------------------------------------------------------------
# Missing clip
# ---------------------------------------------------------------------------


def test_missing_clip_is_reported(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.mp4"  # never created

    result = validate_edit_manifest(_edit([_clip_entry(missing)]), base_path=tmp_path)

    assert result["ok"] is False
    types = [e["type"] for e in result["errors"]]
    assert "missing_clip" in types


def test_missing_clip_error_contains_path(tmp_path: Path) -> None:
    missing = tmp_path / "ghost.mp4"

    result = validate_edit_manifest(_edit([_clip_entry(missing)]), base_path=tmp_path)

    clip_errors = [e for e in result["errors"] if e["type"] == "missing_clip"]
    assert any(str(missing) in e["path"] for e in clip_errors)


# ---------------------------------------------------------------------------
# Missing audio
# ---------------------------------------------------------------------------


def test_missing_audio_is_reported(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"")
    missing_audio = tmp_path / "missing.wav"  # never created

    result = validate_edit_manifest(
        _edit([_clip_entry(clip)], audio_path=str(missing_audio)),
        base_path=tmp_path,
    )

    assert result["ok"] is False
    types = [e["type"] for e in result["errors"]]
    assert "missing_audio" in types


def test_present_audio_does_not_trigger_error(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"")
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"")

    result = validate_edit_manifest(
        _edit([_clip_entry(clip)], audio_path=str(audio)),
        base_path=tmp_path,
    )

    assert result["ok"] is True
    assert result["errors"] == []


# ---------------------------------------------------------------------------
# Duration mismatch
# ---------------------------------------------------------------------------


def test_duration_mismatch_declared_vs_expected(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"")
    # declared=5.0, expected=10.0 — diff is 5.0 >> tolerance of 0.05
    entry = _clip_entry(clip, duration_seconds=5.0, expected_duration_seconds=10.0)

    result = validate_edit_manifest(_edit([entry]), base_path=tmp_path)

    assert result["ok"] is False
    types = [e["type"] for e in result["errors"]]
    assert "duration_mismatch" in types


def test_duration_within_tolerance_does_not_error(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"")
    # diff = 0.01, within DURATION_TOLERANCE_SECONDS = 0.05
    entry = _clip_entry(clip, duration_seconds=5.0, expected_duration_seconds=5.01)

    result = validate_edit_manifest(_edit([entry]), base_path=tmp_path)

    assert result["ok"] is True
    assert result["errors"] == []


def test_duration_mismatch_end_exceeds_source(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"")
    # end_seconds(12) > source_duration_seconds(10) + tolerance(0.05)
    entry = _clip_entry(clip, start_seconds=0.0, end_seconds=12.0, source_duration_seconds=10.0)

    result = validate_edit_manifest(_edit([entry]), base_path=tmp_path)

    assert result["ok"] is False
    types = [e["type"] for e in result["errors"]]
    assert "duration_mismatch" in types


# ---------------------------------------------------------------------------
# Edge: empty or invalid clips raises
# ---------------------------------------------------------------------------


def test_empty_clips_raises() -> None:
    with pytest.raises(ValueError, match="non-empty clips array"):
        validate_edit_manifest({"clips": []}, base_path=Path("/tmp"))


def test_missing_clips_key_raises() -> None:
    with pytest.raises(ValueError, match="non-empty clips array"):
        validate_edit_manifest({}, base_path=Path("/tmp"))
