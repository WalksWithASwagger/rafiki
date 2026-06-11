"""Optional integration tests for ffmpeg-backed video assembly.

These tests are skipped automatically when ffmpeg is absent so CI stays
green in environments that lack ffmpeg.  When ffmpeg is present they
exercise the real render path end-to-end with tiny synthetic fixtures.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from lib.video_jobs import assemble_video_edit

# ---------------------------------------------------------------------------
# Skip guard — shared by every test in this module
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None,
    reason="ffmpeg not available — skipping real render tests",
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_tiny_mp4(path: Path) -> None:
    """Generate a 0.2-second 16×16 pixel video using ffmpeg lavfi."""
    ffmpeg = shutil.which("ffmpeg")
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
        pytest.skip(f"ffmpeg fixture generation failed: {proc.stderr[-200:]}")


# ---------------------------------------------------------------------------
# Success case: real render with a valid clip
# ---------------------------------------------------------------------------


def test_assemble_real_render_succeeds(tmp_path: Path) -> None:
    """A single valid clip assembles to an output file with exit_code 0."""
    clip = tmp_path / "clip.mp4"
    _make_tiny_mp4(clip)
    edit = tmp_path / "edit.json"
    edit.write_text(
        json.dumps({"project": "test-project", "clips": [{"path": "clip.mp4"}]}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    result = assemble_video_edit(edit_path=edit, output_dir=out_dir, execute=True)

    assert result["manifest"]["status"] == "rendered"
    assert result["manifest"]["ffmpeg"]["exit_code"] == 0
    output_path = Path(result["manifest"]["output_path"])
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_assemble_real_render_two_clips_concatenates(tmp_path: Path) -> None:
    """Two valid clips are concatenated into a single output file."""
    clip_a = tmp_path / "clip_a.mp4"
    clip_b = tmp_path / "clip_b.mp4"
    _make_tiny_mp4(clip_a)
    _make_tiny_mp4(clip_b)
    edit = tmp_path / "edit.json"
    edit.write_text(
        json.dumps({
            "project": "two-clip-test",
            "clips": [{"path": "clip_a.mp4"}, {"path": "clip_b.mp4"}],
        }),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    result = assemble_video_edit(edit_path=edit, output_dir=out_dir, execute=True)

    assert result["manifest"]["status"] == "rendered"
    assert result["manifest"]["ffmpeg"]["exit_code"] == 0
    assert Path(result["manifest"]["output_path"]).exists()


# ---------------------------------------------------------------------------
# Failure case: corrupt/invalid clip is reported clearly
# ---------------------------------------------------------------------------


def test_assemble_corrupt_clip_raises_runtime_error(tmp_path: Path) -> None:
    """A corrupt clip causes ffmpeg to fail; RuntimeError is raised with a clear message."""
    bad_clip = tmp_path / "broken.mp4"
    bad_clip.write_bytes(b"this is not a valid mp4 container")
    edit = tmp_path / "edit.json"
    edit.write_text(
        json.dumps({"project": "test-project", "clips": [{"path": "broken.mp4"}]}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        assemble_video_edit(edit_path=edit, output_dir=out_dir, execute=True)

    manifest = json.loads((out_dir / "edit.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
    assert manifest["ffmpeg"]["exit_code"] != 0


def test_assemble_missing_clip_raises_file_not_found_before_ffmpeg(tmp_path: Path) -> None:
    """A missing clip path raises FileNotFoundError — no ffmpeg call is made."""
    edit = tmp_path / "edit.json"
    edit.write_text(
        json.dumps({"project": "test-project", "clips": [{"path": "nonexistent.mp4"}]}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    with pytest.raises(FileNotFoundError, match="missing"):
        assemble_video_edit(edit_path=edit, output_dir=out_dir, execute=True)

    manifest = json.loads((out_dir / "edit.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "blocked"
    assert manifest["missing"] != []
