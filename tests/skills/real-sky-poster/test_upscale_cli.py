from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[3]
    / ".agents/skills/real-sky-poster/scripts/upscale.py"
)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-S", str(SCRIPT), *args],
        capture_output=True,
        check=False,
        text=True,
    )


def test_help_does_not_require_imaging_dependencies() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "--model" in result.stdout


def test_missing_input_fails_before_imaging_dependencies(tmp_path: Path) -> None:
    model = tmp_path / "model.pth"
    model.touch()

    result = run_cli("missing.png", "output.png", "--model", str(model))

    assert result.returncode == 2
    assert "input file not found: missing.png" in result.stderr
    assert "Traceback" not in result.stderr


def test_missing_model_fails_before_imaging_dependencies(tmp_path: Path) -> None:
    source = tmp_path / "plate.png"
    source.touch()

    result = run_cli(str(source), "output.png", "--model", "missing.pth")

    assert result.returncode == 2
    assert "model file not found: missing.pth" in result.stderr
    assert "Traceback" not in result.stderr
