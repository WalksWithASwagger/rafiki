"""Slingsby proposal runner gates (status, dotenv, consent, LoRA plan)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "slingsby-proposal-generate.sh"


def _run(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    # Isolate secrets so the test asserts the runner's own detection.
    merged.pop("GOOGLE_API_KEY", None)
    merged.pop("GEMINI_API_KEY", None)
    merged.pop("OPENAI_API_KEY", None)
    merged.pop("REPLICATE_API_TOKEN", None)
    merged.pop("SLINGSBY_LIKENESS_CONSENT", None)
    merged.setdefault("SLINGSBY_SKIP_VARLOCK", "1")
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
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
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


def test_runner_prefers_private_likeness_pack(tmp_path: Path) -> None:
    from PIL import Image

    private = tmp_path / "proposal.md"
    private.write_text(
        "## 1. Hero\n"
        "**For:** cover\n"
        "**Aspect Ratio:** 4:5\n"
        "**Style:** slingsby\n"
        "**Prompt:**\n"
        "> The woman in the attached authorized reference photographs, exact likeness.\n"
    )
    likeness = tmp_path / "likeness"
    likeness.mkdir()
    Image.new("RGB", (64, 64), (30, 30, 30)).save(likeness / "face.jpg", "JPEG")
    result = _run(
        ["--likeness-only"],
        env={
            "SLINGSBY_LIKENESS_PACK": str(private),
            "SLINGSBY_LIKENESS_DIR": str(likeness),
            "SLINGSBY_OUTPUT_DIR": str(tmp_path / "out"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert str(private) in result.stdout
    assert "examples/slingsby-advisors-likeness-jobs.md" not in result.stdout


def test_status_reports_overridden_likeness_pack(tmp_path: Path) -> None:
    private = tmp_path / "local-proposal.md"
    private.write_text("# local\n")
    result = _run(
        ["--status"],
        env={
            "SLINGSBY_LIKENESS_PACK": str(private),
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr
    assert str(private) in result.stdout


def test_execute_reexecs_through_varlock(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake = fake_bin / "varlock"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        "echo varlock-wrapped\n"
        "while [[ $# -gt 0 && \"$1\" != -- ]]; do shift; done\n"
        "shift || true\n"
        "export GOOGLE_API_KEY=should-never-be-printed-varlock\n"
        'exec "$@"\n'
    )
    fake.chmod(0o755)
    result = _run(
        ["--status"],
        env={
            "PATH": f"{fake_bin}:{os.environ.get('PATH', '')}",
            "SLINGSBY_SKIP_VARLOCK": "",
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "varlock-wrapped" in result.stdout
    assert "GOOGLE_API_KEY: set" in result.stdout
    assert "should-never-be-printed-varlock" not in result.stdout
    assert "should-never-be-printed-varlock" not in result.stderr


def test_status_accepts_gemini_api_key_alias(tmp_path: Path) -> None:
    result = _run(
        ["--status"],
        env={
            "GEMINI_API_KEY": "should-never-be-printed-alias",
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr
    assert "GOOGLE_API_KEY: set" in result.stdout
    assert "should-never-be-printed-alias" not in result.stdout
    assert "should-never-be-printed-alias" not in result.stderr


def test_likeness_ref_cap_prefers_full_face_plates(tmp_path: Path) -> None:
    likeness = tmp_path / "likeness"
    likeness.mkdir()
    for name in (
        "014-front-smile-crop.jpg",
        "070-front-white-blouse-down.jpg",
        "045-threequarter-stage-black.jpg",
        "075-threequarter-white-blouse.jpg",
        "024-profile-stage-black.jpg",
        "146-front-smile-blue-coat-crop.jpg",
        "086-threequarter-white-mic.jpg",
        "133-threequarter-tanya-slingsby-tag.jpg",
    ):
        (likeness / name).write_bytes(b"x")
    result = _run(
        ["--likeness-only"],
        env={
            "SLINGSBY_LIKENESS_DIR": str(likeness),
            "SLINGSBY_OUTPUT_DIR": str(tmp_path / "out"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "consent.md"),
            "SLINGSBY_MAX_LIKENESS_REFS": "6",
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    cmd = result.stdout
    assert "014-front-smile-crop.jpg" in cmd
    assert "146-front-smile-blue-coat-crop.jpg" in cmd
    assert "086-threequarter-white-mic.jpg" not in cmd
    assert "133-threequarter-tanya-slingsby-tag.jpg" not in cmd


def test_smoke_runs_first_style_job_only(tmp_path: Path) -> None:
    result = _run(
        ["--style-only", "--smoke"],
        env={
            "SLINGSBY_OUTPUT_DIR": str(tmp_path / "out"),
            "SLINGSBY_SMOKE_DIR": str(tmp_path / "smoke"),
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "Smoke: first job only" in result.stdout
    assert "Generated 1/1 images" in result.stdout


def test_status_accepts_openai_as_stills_fallback(tmp_path: Path) -> None:
    result = _run(
        ["--status"],
        env={
            "OPENAI_API_KEY": "should-never-be-printed-openai",
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr
    assert "OPENAI_API_KEY: set" in result.stdout
    assert "model:          gpt" in result.stdout
    assert "style plates:   ready" in result.stdout
    assert "should-never-be-printed-openai" not in result.stdout
    assert "Floyo:" in result.stdout
    assert "video only" in result.stdout


def test_openai_dry_run_passes_gpt_model(tmp_path: Path) -> None:
    result = _run(
        ["--style-only"],
        env={
            "OPENAI_API_KEY": "dummy-not-used-xxxxxx",
            "SLINGSBY_OUTPUT_DIR": str(tmp_path / "out"),
            "SLINGSBY_STYLE_DIR": str(tmp_path / "empty-style"),
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "--model gpt" in result.stdout
    assert "Provider: OpenAI" in result.stdout


def test_status_treats_redacted_stub_as_unset(tmp_path: Path) -> None:
    result = _run(
        ["--status"],
        env={
            "GOOGLE_API_KEY": "x" + ("\u2592" * 5),
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr
    assert "GOOGLE_API_KEY: unset" in result.stdout
    assert "style plates:   blocked" in result.stdout
    assert "\u2592" not in result.stdout


def test_execute_without_key_exits_2() -> None:
    result = _run(["--execute", "--style-only"])
    assert result.returncode == 2
    assert "GOOGLE_API_KEY" in result.stderr
    assert "OPENAI_API_KEY" in result.stderr


def test_likeness_execute_without_consent_exits_3(tmp_path: Path) -> None:
    portrait = tmp_path / "face.jpg"
    portrait.write_bytes(b"fake-portrait")
    result = _run(
        ["--execute", "--likeness-only"],
        env={
            "GOOGLE_API_KEY": "dummy-not-used-xxxxxx",
            "SLINGSBY_ASSETS_ROOT": str(tmp_path / "empty-assets"),
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
            "GOOGLE_API_KEY": "dummy-not-used-xxxxxx",
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty"),
        },
    )
    assert result.returncode == 0
    assert "no photos" in result.stdout


def test_prep_refs_writes_face_free_and_likeness_clean(tmp_path: Path) -> None:
    from PIL import Image

    likeness = tmp_path / "likeness"
    tiles = tmp_path / "tiles"
    likeness.mkdir()
    tiles.mkdir()
    Image.new("RGB", (200, 300), (40, 40, 40)).save(likeness / "014-front-smile-crop.jpg", "JPEG")
    Image.new("RGB", (400, 300), (80, 80, 90)).save(tiles / "tile-039.jpg", "JPEG")
    Image.new("RGB", (400, 500), (20, 20, 20)).save(tiles / "tile-040.jpg", "JPEG")
    clean = tmp_path / "likeness-clean"
    face_free = tmp_path / "face-free"
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "slingsby-proposal-prep-refs.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "SLINGSBY_LIKENESS_DIR": str(likeness),
            "SLINGSBY_LIKENESS_CLEAN_DIR": str(clean),
            "SLINGSBY_STYLE_TILES_DIR": str(tiles),
            "SLINGSBY_FACE_FREE_DIR": str(face_free),
        },
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (clean / "014-front-smile-crop.jpg").exists()
    assert (face_free / "glass-geometry.jpg").exists()
    assert (face_free / "urban-canyon.jpg").exists()
    cropped = Image.open(clean / "014-front-smile-crop.jpg")
    assert cropped.size[1] < 300


def test_runner_prefers_face_free_and_likeness_clean(tmp_path: Path) -> None:
    from PIL import Image

    assets = tmp_path / "slingsby"
    face_free = assets / "style-refs" / "moodboard" / "face-free"
    selected = assets / "style-refs" / "moodboard" / "selected"
    clean = assets / "likeness-clean"
    raw = assets / "likeness"
    for folder in (face_free, selected, clean, raw):
        folder.mkdir(parents=True)
    Image.new("RGB", (80, 80), (10, 10, 10)).save(face_free / "glass-geometry.jpg", "JPEG")
    Image.new("RGB", (80, 80), (200, 10, 10)).save(selected / "page-1.jpg", "JPEG")
    Image.new("RGB", (80, 80), (10, 200, 10)).save(clean / "014-front-smile-crop.jpg", "JPEG")
    Image.new("RGB", (80, 80), (10, 10, 200)).save(raw / "tagged.jpg", "JPEG")
    result = _run(
        ["--status"],
        env={
            "SLINGSBY_ASSETS_ROOT": str(assets),
            "SLINGSBY_CONSENT_FILE": str(tmp_path / "missing-consent.md"),
        },
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "glass-geometry.jpg" in out or "face-free" in out
    assert str(face_free) in out
    assert str(clean) in out
    assert str(selected) not in out
    assert "tagged.jpg" not in out


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
    result = _run(
        ["--review"],
        env={
            "SLINGSBY_OUTPUT_DIR": str(out),
            "SLINGSBY_LIKENESS_DIR": str(tmp_path / "empty-likeness"),
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (out / "viewer.html").exists() or "viewer" in result.stdout.lower()
    assert (out / "taste-gate.html").is_file()
    assert "should-never-be-printed" not in result.stdout
    assert "should-never-be-printed" not in (out / "taste-gate.html").read_text()


def test_train_lora_plan_is_dry_run() -> None:
    result = _run(["--train-lora-plan"])
    assert result.returncode == 0, result.stderr + result.stdout
    assert "dry-run" in result.stdout.lower() or "LoRA training dry-run" in result.stdout
    assert "no spend" in result.stdout.lower() or "Execute later" in result.stdout
