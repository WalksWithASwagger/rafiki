"""Tests for clip audio muxing — dry-run builds the ffmpeg command, never runs it."""

from __future__ import annotations

import pytest

from lib import clip_audio


def test_mux_dry_run_builds_command_without_running():
    result = clip_audio.mux_clip_audio("/tmp/clip.mp4", "/tmp/song.mp3", execute=False)
    assert result["status"] == "dry-run"
    cmd = result["command"]
    assert cmd[0] == "ffmpeg"
    assert "/tmp/clip.mp4" in cmd and "/tmp/song.mp3" in cmd
    assert "0:v:0" in cmd and "1:a:0" in cmd
    assert "copy" in cmd  # video stream copied


def test_mux_default_output_name():
    result = clip_audio.mux_clip_audio("/tmp/shot_07.mp4", "/tmp/song.mp3", execute=False)
    assert result["output"].endswith("shot_07_scored.mp4")


def test_mux_audio_start_offset_in_command():
    result = clip_audio.mux_clip_audio(
        "/tmp/clip.mp4", "/tmp/song.mp3", audio_start_seconds=5.0, execute=False
    )
    cmd = result["command"]
    assert "-ss" in cmd and "5.0" in cmd


def test_mux_execute_missing_video_raises():
    with pytest.raises(clip_audio.ClipAudioError):
        clip_audio.mux_clip_audio("/tmp/does-not-exist.mp4", "/tmp/song.mp3", execute=True)
