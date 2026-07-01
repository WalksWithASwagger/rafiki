"""Mux an audio track over a (silent) video clip via ffmpeg. Dry-run-first.

Ports the useful half of the studio's ``ingest_clips.py``: lay the real song over
clips that came back silent. Local only — no provider, no spend. Never mux over a
lip-sync clip (its vocal is already embedded and drives the lips).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class ClipAudioError(RuntimeError):
    pass


def _probe_duration(path: Path) -> float | None:
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    out = (proc.stdout or "").strip()
    try:
        return float(out) if proc.returncode == 0 and out else None
    except ValueError:
        return None


def mux_clip_audio(
    video_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path | None = None,
    *,
    audio_start_seconds: float = 0.0,
    execute: bool = False,
) -> dict[str, Any]:
    """Lay ``audio_path`` over ``video_path`` (video copied, audio re-encoded to AAC).

    Trims to the clip's duration (`-shortest` + `-t`). Dry-run returns the planned
    ffmpeg command without running it.
    """
    video = Path(video_path).expanduser()
    audio = Path(audio_path).expanduser()
    out = Path(output_path).expanduser() if output_path else video.with_name(f"{video.stem}_scored.mp4")

    duration = _probe_duration(video) if video.is_file() else None
    cmd = ["ffmpeg", "-y", "-i", str(video), "-ss", f"{audio_start_seconds}", "-i", str(audio),
           "-map", "0:v:0", "-map", "1:a:0"]
    if duration:
        cmd += ["-t", f"{duration:.2f}"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-shortest", str(out)]

    if not execute:
        return {
            "status": "dry-run",
            "command": cmd,
            "video": str(video),
            "audio": str(audio),
            "output": str(out),
        }

    if not video.is_file():
        raise ClipAudioError(f"video not found: {video}")
    if not audio.is_file():
        raise ClipAudioError(f"audio not found: {audio}")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except FileNotFoundError as e:
        raise ClipAudioError("ffmpeg not found on PATH") from e
    if proc.returncode != 0:
        raise ClipAudioError(f"ffmpeg failed (exit {proc.returncode}): {proc.stderr[-500:]}")
    return {
        "status": "muxed",
        "output": str(out),
        "bytes": out.stat().st_size if out.exists() else 0,
        "command": cmd,
    }
