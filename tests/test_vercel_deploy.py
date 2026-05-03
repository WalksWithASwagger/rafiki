"""Tests for lib.deploy.vercel — mocks subprocess and shutil.which."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.deploy import vercel as vercel_mod
from lib.deploy.vercel import (
    VercelNotInstalledError,
    ViewerNotFoundError,
    deploy,
)


@pytest.fixture
def viewer_dir(tmp_path: Path) -> Path:
    d = tmp_path / "viewer"
    d.mkdir()
    (d / "viewer.html").write_text("<html></html>", encoding="utf-8")
    return d


def _fake_run(stdout: str = "https://rafiki-abc123.vercel.app\n", stderr: str = "") -> MagicMock:
    completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr=stderr)
    return MagicMock(return_value=completed)


def test_deploy_constructs_correct_command_default(viewer_dir: Path):
    fake = _fake_run()
    with patch.object(vercel_mod.shutil, "which", return_value="/usr/local/bin/vercel"), \
         patch.object(vercel_mod.subprocess, "run", fake):
        deploy("rap-all-weeks", viewer_dir=viewer_dir)
    args, _ = fake.call_args
    assert args[0] == ["vercel", "deploy", str(viewer_dir), "--yes"]


def test_deploy_prod_flag(viewer_dir: Path):
    fake = _fake_run()
    with patch.object(vercel_mod.shutil, "which", return_value="/usr/local/bin/vercel"), \
         patch.object(vercel_mod.subprocess, "run", fake):
        deploy("rap-all-weeks", viewer_dir=viewer_dir, prod=True)
    args, _ = fake.call_args
    assert args[0] == ["vercel", "deploy", str(viewer_dir), "--yes", "--prod"]


def test_deploy_dry_run_skips_subprocess(viewer_dir: Path, capsys):
    fake = MagicMock()
    with patch.object(vercel_mod.shutil, "which", return_value="/usr/local/bin/vercel"), \
         patch.object(vercel_mod.subprocess, "run", fake):
        result = deploy("rap-all-weeks", viewer_dir=viewer_dir, dry_run=True)
    assert result == ""
    fake.assert_not_called()
    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert "vercel deploy" in out


def test_deploy_creates_vercel_json_if_missing(viewer_dir: Path):
    assert not (viewer_dir / "vercel.json").exists()
    fake = _fake_run()
    with patch.object(vercel_mod.shutil, "which", return_value="/usr/local/bin/vercel"), \
         patch.object(vercel_mod.subprocess, "run", fake):
        deploy("rap-all-weeks", viewer_dir=viewer_dir)
    vj = viewer_dir / "vercel.json"
    assert vj.exists()
    assert "version" in vj.read_text()


def test_deploy_does_not_overwrite_existing_vercel_json(viewer_dir: Path):
    custom = '{"version": 2, "routes": []}'
    (viewer_dir / "vercel.json").write_text(custom, encoding="utf-8")
    fake = _fake_run()
    with patch.object(vercel_mod.shutil, "which", return_value="/usr/local/bin/vercel"), \
         patch.object(vercel_mod.subprocess, "run", fake):
        deploy("rap-all-weeks", viewer_dir=viewer_dir)
    assert (viewer_dir / "vercel.json").read_text() == custom


def test_deploy_parses_url_from_output(viewer_dir: Path):
    out = (
        "Vercel CLI 32.0.0\n"
        "Deploying ~/output/rap-all-weeks\n"
        "Inspect: https://vercel.com/kk/rafiki/abc123 [2s]\n"
        "Production: https://rafiki-xyz.vercel.app [copied to clipboard]\n"
    )
    fake = _fake_run(stdout=out)
    with patch.object(vercel_mod.shutil, "which", return_value="/usr/local/bin/vercel"), \
         patch.object(vercel_mod.subprocess, "run", fake):
        url = deploy("rap-all-weeks", viewer_dir=viewer_dir)
    assert url == "https://rafiki-xyz.vercel.app"


def test_deploy_raises_if_vercel_not_on_path(viewer_dir: Path):
    with patch.object(vercel_mod.shutil, "which", return_value=None):
        with pytest.raises(VercelNotInstalledError) as exc:
            deploy("rap-all-weeks", viewer_dir=viewer_dir)
    assert "npm install -g vercel" in str(exc.value)


def test_deploy_raises_if_viewer_html_missing(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ViewerNotFoundError):
        deploy("rap-all-weeks", viewer_dir=empty)
