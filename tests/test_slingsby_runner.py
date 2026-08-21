"""Slingsby proposal runner gates (status, dotenv, consent, LoRA plan)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "slingsby-proposal-generate.sh"


def _run(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    # Isolate secrets so the test asserts the runner's own detection.
    merged.pop("GOOGLE_API_KEY", None)
    merged.pop("GEMINI_API_KEY", None)
    merged.pop("REPLICATE_API_TOKEN", None)
    merged.pop("SLINGSBY_LIKENESS_CONSENT", None)
    if env:
        merged.update(env)
    return subprocess.run(
        ["bash", str(RUNNER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )


def test_status_reports_blocked_gates_without_leaking_values(tmp_path: Path) -> None:
    env_file = tmp_path / "dotenv"
    env_file.write_text("GOOGLE_API_KEY=should-never-be-printed-xyz\n")
    result = _run(
        ["--status"],
        env={
            "SLINGSBY_ENV_FILE": str(env_file),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "GOOGLE_API_KEY: set" in out
    assert "should-never-be-printed-xyz" not in out
    assert "should-never-be-printed-xyz" not in result.stderr
    assert "likeness consent: missing" in out
    assert "style plates:   ready" in out
    assert "likeness jobs:  blocked" in out


def test_execute_without_key_exits_2() -> None:
    result = _run(["--execute", "--style-only"])
    assert result.returncode == 2
    assert "GOOGLE_API_KEY" in result.stderr


def test_likeness_execute_without_consent_exits_3(tmp_path: Path) -> None:
    portrait = tmp_path / "face.jpg"
    portrait.write_bytes(b"fake-portrait")
    result = _run(
        ["--execute", "--likeness-only"],
        env={
            "GOOGLE_API_KEY": "dummy-not-used",
            "SLINGSBY_LIKENESS_DIR": str(tmp_path),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 3
    assert "written consent" in result.stderr


def test_likeness_only_without_photos_skips(tmp_path: Path) -> None:
    result = _run(
        ["--execute", "--likeness-only"],
        env={
            "GOOGLE_API_KEY": "dummy-not-used",
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty"),
        },
    )
    assert result.returncode == 0
    assert "no photos" in result.stdout


def test_style_ref_cap_prefers_moodboard_pages(tmp_path: Path) -> None:
    style_dir = tmp_path / "moodboard"
    (style_dir / "pages").mkdir(parents=True)
    (style_dir / "tiles").mkdir()
    (style_dir / "pages" / "page-1.jpg").write_bytes(b"p" * 50)
    (style_dir / "pages" / "page-2.jpg").write_bytes(b"p" * 50)
    (style_dir / "tiles" / "tile-huge.jpg").write_bytes(b"y" * 400)
    result = _run(
        ["--style-only"],
        env={
            "SLINGSBY_STYLE_DIR": str(style_dir),
            "SLINGSBY_MAX_STYLE_REFS": "2",
            "SLINGSBY_OUTPUT_DIR": str(tmp_path / "out"),
        },
    )
    assert result.returncode == 0, result.stderr
    cmd = result.stdout.splitlines()[0]
    assert "page-1.jpg" in cmd
    assert "page-2.jpg" in cmd
    assert "tile-huge.jpg" not in cmd


def test_style_ref_cap_keeps_one_plate_per_locked_series(tmp_path: Path) -> None:
    style_dir = tmp_path / "style-refs"
    style_dir.mkdir()
    # Tiny files for most series; one huge "other" that would win a size-only cap.
    for name in (
        "meridians2012_01.jpg",
        "mutual2017_05.jpg",
        "shoru2011_01.jpg",
        "arcana_01.jpg",
        "artInSitu01.jpg",
    ):
        (style_dir / name).write_bytes(b"x")
    (style_dir / "noise-a.jpg").write_bytes(b"y" * 200)
    (style_dir / "noise-b.jpg").write_bytes(b"y" * 200)
    (style_dir / "noise-c.jpg").write_bytes(b"y" * 200)
    result = _run(
        ["--style-only"],
        env={
            "SLINGSBY_STYLE_DIR": str(style_dir),
            "SLINGSBY_MAX_STYLE_REFS": "5",
            "SLINGSBY_OUTPUT_DIR": str(tmp_path / "out"),
        },
    )
    assert result.returncode == 0, result.stderr
    cmd = result.stdout.splitlines()[0]
    assert "shoru2011_01.jpg" in cmd
    assert "meridians2012_01.jpg" in cmd
    assert "mutual2017_05.jpg" in cmd
    assert "arcana_01.jpg" in cmd
    assert "artInSitu01.jpg" in cmd


def test_ingest_likeness_from_folder(tmp_path: Path) -> None:
    from PIL import Image

    src = tmp_path / "drop"
    src.mkdir()
    Image.new("RGB", (400, 400), (20, 20, 20)).save(src / "tanya-front.jpg", "JPEG")
    dest = tmp_path / "likeness"
    ingest = REPO_ROOT / "scripts" / "slingsby-proposal-ingest.sh"
    result = subprocess.run(
        ["bash", str(ingest), "--likeness", str(src)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "SLINGSBY_LIKENESS_DIR": str(dest)},
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (dest / "tanya-front.jpg").exists()


def test_review_builds_viewer_from_existing_output(tmp_path: Path) -> None:
    out = tmp_path / "slingsby-advisors"
    run = out / "run-20260821-review"
    run.mkdir(parents=True)
    (run / "run.json").write_text('{"prompts": []}\n')
    result = _run(["--review"], env={"SLINGSBY_OUTPUT_DIR": str(out)})
    assert result.returncode == 0, result.stderr + result.stdout
    assert (out / "viewer.html").exists() or "viewer" in result.stdout.lower()


def test_train_lora_plan_is_dry_run() -> None:
    result = _run(["--train-lora-plan"])
    assert result.returncode == 0, result.stderr + result.stdout
    assert "dry-run" in result.stdout.lower() or "LoRA training dry-run" in result.stdout
    assert "no spend" in result.stdout.lower() or "Execute later" in result.stdout
