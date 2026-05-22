"""Tests for the Node-based `rafiki doctor` diagnostics."""

from __future__ import annotations

import os
import stat
import subprocess
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_fake_python(tmp_path: Path) -> Path:
    fake_python = tmp_path / "python3"
    fake_python.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("Python 3.12.9")
                raise SystemExit(0)

            code = args[1] if len(args) >= 2 and args[0] == "-c" else ""
            if "checks = [" in code:
                missing = [item for item in os.environ.get("FAKE_MISSING_DEPS", "").split(",") if item]
                print(json.dumps({"missing": missing}))
                raise SystemExit(0)

            if "server_compiles" in code:
                ready = os.environ.get("FAKE_MCP_READY", "1") == "1"
                print(json.dumps({
                    "server_exists": True,
                    "server_compiles": ready,
                    "sdk_imports": ready,
                    "error": "" if ready else "No module named mcp",
                }))
                raise SystemExit(0)

            raise SystemExit(1)
            """
        )
    )
    fake_python.chmod(fake_python.stat().st_mode | stat.S_IXUSR)
    return fake_python


def _run_doctor(
    tmp_path: Path,
    *,
    google_key: str = "test-google-key",
    openai_key: str = "test-openai-key",
    missing_deps: str = "",
    mcp_ready: bool = True,
    script_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    fake_python = _write_fake_python(tmp_path)
    fake_browser = tmp_path / "chrome"
    fake_browser.write_text("")
    script = script_path or REPO_ROOT / "index.js"

    env = os.environ.copy()
    if script_path is not None:
        env.pop("NODE_PATH", None)
    env.update(
        {
            "NO_COLOR": "1",
            "RAFIKI_DOCTOR_PYTHON": str(fake_python),
            "PUPPETEER_EXECUTABLE_PATH": str(fake_browser),
            "GOOGLE_API_KEY": google_key,
            "OPENAI_API_KEY": openai_key,
            "FAKE_MISSING_DEPS": missing_deps,
            "FAKE_MCP_READY": "1" if mcp_ready else "0",
        }
    )

    return subprocess.run(
        ["node", str(script), "--doctor"],
        cwd=script.parent,
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
    )


def test_doctor_reports_expanded_ready_status(tmp_path: Path) -> None:
    result = _run_doctor(tmp_path)

    assert result.returncode == 0
    assert "[ok] Node deps: core CLI dependencies installed" in result.stdout
    assert "[ok] Python deps: core requirements installed" in result.stdout
    assert "[ok] Provider keys: GOOGLE_API_KEY set; OPENAI_API_KEY set" in result.stdout
    assert "[ok] MCP availability: mcp_server.py compiles and FastMCP imports" in result.stdout
    assert "[ok] Browser rendering: puppeteer and sharp installed; Chrome/Chromium at" in result.stdout
    assert "Doctor found 0 critical issue(s)" in result.stdout
    assert "test-google-key" not in result.stdout
    assert "test-openai-key" not in result.stdout


def test_doctor_warns_without_failing_when_provider_keys_are_missing(tmp_path: Path) -> None:
    result = _run_doctor(tmp_path, google_key="", openai_key="")

    assert result.returncode == 0
    assert "[warn] Provider keys: GOOGLE_API_KEY not set; OPENAI_API_KEY not set" in result.stdout
    assert "Add `GOOGLE_API_KEY` for Gemini or `OPENAI_API_KEY` for OpenAI image generation; dry-run, render, and review workflows can still run without provider keys." in result.stdout
    assert "Doctor found 0 critical issue(s)" in result.stdout


def test_doctor_fails_for_missing_core_python_dependency(tmp_path: Path) -> None:
    result = _run_doctor(tmp_path, missing_deps="openai")

    assert result.returncode == 1
    assert "[fail] Python deps: missing openai" in result.stdout
    assert "Required next steps:" in result.stdout
    assert "python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt" in result.stdout
    assert "Doctor found 1 critical issue(s)" in result.stdout


def test_doctor_reports_missing_node_deps_without_crashing(tmp_path: Path) -> None:
    isolated_script = tmp_path / "index.js"
    isolated_script.write_text((REPO_ROOT / "index.js").read_text(encoding="utf-8"), encoding="utf-8")

    result = _run_doctor(tmp_path, script_path=isolated_script)

    assert result.returncode == 1
    assert "[fail] Node deps: missing commander, dotenv, chalk" in result.stdout
    assert "[warn] Browser rendering: missing puppeteer, sharp" in result.stdout
    assert "Install Node dependencies from the repo root: `npm install`, then re-run `npm run doctor`." in result.stdout
    assert "Doctor found 1 critical issue(s)" in result.stdout
