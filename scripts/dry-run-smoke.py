#!/usr/bin/env python3
"""Spend-free smoke for Rafiki's agent-facing dry-run paths."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVIDER_ENV_KEYS = ("GOOGLE_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY")

sys.path.insert(0, str(REPO_ROOT))


def _repo_python() -> Path | None:
    candidates = [
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python3",
        REPO_ROOT / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _maybe_reexec_with_repo_python() -> None:
    python = _repo_python()
    if not python or os.environ.get("RAFIKI_SMOKE_REEXEC") == "1":
        return
    if Path(sys.executable) == python:
        return
    env = os.environ.copy()
    env["RAFIKI_SMOKE_REEXEC"] = "1"
    os.execve(str(python), [str(python), str(Path(__file__).resolve())], env)


def _smoke_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in PROVIDER_ENV_KEYS:
        env[key] = ""
    return env


def _write_prompt_file(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "## 1. Agent Smoke Hero",
                "**Prompt:**",
                "> A local-first creative image archive command center.",
                "",
                "## 2. Agent Smoke Detail",
                "**Prompt:**",
                "> A careful evaluation panel beside generated artwork.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _run(command: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "\n".join(
                [
                    f"{' '.join(command)} failed with {proc.returncode}",
                    proc.stdout,
                    proc.stderr,
                ]
            ).strip()
        )
    return proc


def _load_json_stdout(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"stdout was not JSON: {proc.stdout[:400]}") from e


def _assert_batch_payload(payload: dict[str, Any], output_dir: Path) -> None:
    assert payload["success"] is True
    assert payload["mode"] == "batch"
    assert payload["dry_run"] is True
    assert payload["generated"] == 2
    assert payload["total"] == 2
    assert payload["project_dir"] == str(output_dir)
    assert payload["model"] == "gemini-2.5-flash-image"
    assert payload["aspect_ratio"] == "1:1"
    assert payload["style"] == "none"
    run_dir = Path(payload["run_dir"])
    assert run_dir.exists()
    assert (run_dir / "run.json").exists()
    assert list(run_dir.glob("*.png")) == []


def _node_cli_smoke(prompt_file: Path, output_dir: Path, env: dict[str, str]) -> dict[str, Any]:
    proc = _run(
        [
            "node",
            "index.js",
            str(prompt_file),
            "--output-dir",
            str(output_dir),
            "--model",
            "gemini",
            "--style",
            "none",
            "--aspect-ratio",
            "square",
            "--dry-run",
            "--no-viewer",
            "--json",
        ],
        env=env,
    )
    payload = _load_json_stdout(proc)
    assert "[DRY RUN]" in proc.stderr
    _assert_batch_payload(payload, output_dir)
    return payload


def _mcp_smoke(prompt_file: Path, output_dir: Path, env: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    old_env = {key: os.environ.get(key) for key in PROVIDER_ENV_KEYS}
    for key in PROVIDER_ENV_KEYS:
        os.environ[key] = ""
    try:
        import mcp_server

        status = json.loads(mcp_server.rafiki_status())
        assert status["repo_root"] == str(REPO_ROOT)
        assert "rafiki_run" in status["common_tools"]
        tools = asyncio.run(mcp_server.mcp.list_tools())
        tool_names = {tool.name for tool in tools}
        assert {"rafiki_status", "rafiki_run"}.issubset(tool_names)

        payload = json.loads(
            mcp_server.rafiki_run(
                [
                    "--prompt-file",
                    str(prompt_file),
                    "--output-dir",
                    str(output_dir),
                    "--model",
                    "gemini",
                    "--style",
                    "none",
                    "--aspect-ratio",
                    "square",
                    "--dry-run",
                    "--no-viewer",
                    "--json",
                ],
                timeout_seconds=60,
            )
        )
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    assert payload["success"] is True
    assert payload["exit_code"] == 0
    assert payload["json"] is not None
    assert payload["mutating"] is False
    _assert_batch_payload(payload["json"], output_dir)
    return status, payload


def main() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="rafiki-dry-run-smoke-"))
    keep_tmp = os.environ.get("RAFIKI_SMOKE_KEEP_TMP") == "1"
    env = _smoke_env()

    try:
        prompt_file = tmp_root / "image-prompts.md"
        output_root = tmp_root / "output"
        _write_prompt_file(prompt_file)

        cli_payload = _node_cli_smoke(prompt_file, output_root / "node-cli", env)
        mcp_status, mcp_payload = _mcp_smoke(prompt_file, output_root / "mcp-bridge", env)

        health_proc = _run(
            [
                sys.executable,
                "generate.py",
                "archive-health",
                "--output-dir",
                str(output_root),
                "--json",
            ],
            env=env,
        )
        health = _load_json_stdout(health_proc)
        assert health["summary"]["projects"] == 2
        assert health["summary"]["runs"] == 2
        assert health["summary"]["manifest_images"] == 4
        assert health["summary"]["missing_images"] == 4
        assert health["summary"]["orphaned_evaluations"] == 0

        print(
            json.dumps(
                {
                    "ok": True,
                    "tmp_root": str(tmp_root) if keep_tmp else None,
                    "node_cli": {
                        "generated": cli_payload["generated"],
                        "total": cli_payload["total"],
                        "run_dir": cli_payload["run_dir"],
                    },
                    "mcp": {
                        "tool_count": len(mcp_status["common_tools"]),
                        "bridge_generated": mcp_payload["json"]["generated"],
                        "bridge_total": mcp_payload["json"]["total"],
                    },
                    "archive_health": {
                        "projects": health["summary"]["projects"],
                        "runs": health["summary"]["runs"],
                        "manifest_images": health["summary"]["manifest_images"],
                        "expected_missing_images": health["summary"]["missing_images"],
                    },
                },
                indent=2,
            )
        )
        return 0
    finally:
        if keep_tmp:
            print(f"Kept smoke temp dir: {tmp_root}", file=sys.stderr)
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    _maybe_reexec_with_repo_python()
    raise SystemExit(main())
