"""Dry-run regressions across Rafiki's agent-facing generation surfaces."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import mcp_server
from lib import server

REPO_ROOT = Path(__file__).resolve().parent.parent


def _prompt_file(tmp_path: Path) -> Path:
    path = tmp_path / "image-prompts.md"
    path.write_text(
        "\n".join(
            [
                "## 1. Hero",
                "**Prompt:**",
                "> A layered community AI workshop poster",
                "",
                "## 2. Detail",
                "**Prompt:**",
                "> A close-up of collaborative field notes and luminous diagrams",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _batch_options(output_dir: Path) -> list[str]:
    return [
        "--output-dir",
        str(output_dir),
        "--model",
        "gpt",
        "--aspect-ratio",
        "instagram",
        "--quality",
        "medium",
        "--style",
        "none",
        "--reference-images",
        "/tmp/ref-a.png,/tmp/ref-b.png",
        "--reference-role",
        "mockup",
        "--composition-references",
        "/tmp/print-art.png",
        "--dry-run",
        "--no-viewer",
        "--json",
    ]


def _single_options(output_path: Path) -> list[str]:
    return [
        "--prompt",
        "A compact studio poster for a local AI image workflow",
        "--output",
        str(output_path),
        "--model",
        "gpt-image-2",
        "--aspect-ratio",
        "4:5",
        "--quality",
        "medium",
        "--no-style",
        "--reference-image",
        "/tmp/ref-single.png",
        "--reference-role",
        "mockup",
        "--composition-references",
        "/tmp/print-single.png",
        "--dry-run",
        "--json",
    ]


def _python_batch_args(prompt_file: Path, output_dir: Path) -> list[str]:
    return ["--prompt-file", str(prompt_file), *_batch_options(output_dir)]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def _assert_batch_json_contract(payload: dict, output_dir: Path) -> None:
    assert payload["success"] is True
    assert payload["mode"] == "batch"
    assert payload["dry_run"] is True
    assert payload["generated"] == 2
    assert payload["total"] == 2
    assert payload["project_dir"] == str(output_dir)
    assert payload["model"] == "gpt-image-2"
    assert payload["aspect_ratio"] == "1:1"
    assert payload["style"] == "none"
    assert len(payload["images"]) == 2
    assert all(image["ok"] is True for image in payload["images"])

    run_dir = Path(payload["run_dir"])
    assert run_dir.exists()
    assert (run_dir / "run.json").exists()
    assert list(run_dir.glob("*.png")) == []


def _assert_single_json_contract(payload: dict, output_path: Path) -> None:
    assert payload["success"] is True
    assert payload["mode"] == "single"
    assert payload["dry_run"] is True
    assert payload["output_path"] == str(output_path)
    assert payload["model"] == "gpt-image-2"
    assert payload["aspect_ratio"] == "4:5"
    assert payload["style"] == "none"
    assert payload["prompt_preview"].startswith("A compact studio poster")
    assert not output_path.exists()


def test_python_cli_single_prompt_dry_run_json_contract(tmp_path: Path) -> None:
    output_path = tmp_path / "single-python.png"

    proc = _run([sys.executable, "generate.py", *_single_options(output_path)])
    payload = json.loads(proc.stdout)

    assert "[DRY RUN]" in proc.stderr
    _assert_single_json_contract(payload, output_path)


def test_node_cli_single_prompt_dry_run_json_stdout_contract(tmp_path: Path) -> None:
    output_path = tmp_path / "single-node.png"

    proc = _run(["node", "index.js", *_single_options(output_path)])
    payload = json.loads(proc.stdout)

    assert "Rafiki" in proc.stderr
    assert "[DRY RUN]" in proc.stderr
    _assert_single_json_contract(payload, output_path)


def test_python_cli_batch_dry_run_json_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_dir = tmp_path / "python-output"

    proc = _run([sys.executable, "generate.py", *_python_batch_args(prompt_file, output_dir)])
    payload = json.loads(proc.stdout)

    assert "[DRY RUN]" in proc.stderr
    _assert_batch_json_contract(payload, output_dir)


def test_node_cli_batch_dry_run_json_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_dir = tmp_path / "node-output"

    proc = _run(["node", "index.js", str(prompt_file), *_batch_options(output_dir)])
    payload = json.loads(proc.stdout)

    assert "Rafiki" in proc.stderr
    assert "[DRY RUN]" in proc.stderr
    _assert_batch_json_contract(payload, output_dir)


def test_mcp_cli_bridge_preserves_dry_run_json_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_dir = tmp_path / "mcp-output"

    payload = json.loads(
        mcp_server.rafiki_run(
            _python_batch_args(prompt_file, output_dir),
            timeout_seconds=30,
        )
    )

    assert payload["success"] is True
    assert payload["exit_code"] == 0
    assert payload["json"] is not None
    assert payload["stdout"].lstrip().startswith("{")
    _assert_batch_json_contract(payload["json"], output_dir)


def test_portal_helper_batch_dry_run_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_root = tmp_path / "portal-output"

    result = server._run_portal_job(
        {
            "mode": "batch",
            "project": "Surface Regression",
            "prompt_file": str(prompt_file),
            "model": "gpt",
            "aspect_ratio": "instagram",
            "quality": "medium",
            "style": "none",
            "reference_images": ["/tmp/ref-a.png", "/tmp/ref-b.png"],
            "reference_role": "mockup",
            "composition_references": ["/tmp/print-art.png"],
            "dry_run": True,
            "workers": 2,
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["all_ok"] is True
    assert result["mode"] == "batch"
    assert result["project"] == "surface-regression"
    assert result["generated"] == 2
    assert result["total"] == 2
    assert result["project_dir"] == str(output_root / "surface-regression")
    assert result["viewer_url"] == "/output/surface-regression/viewer.html"
    assert result["run_viewer_url"].endswith(f"/run-{result['run_id']}/viewer.html")
    assert list(Path(result["run_dir"]).glob("*.png")) == []
