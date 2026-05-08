import json
import os
import subprocess
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "agentic"))

from provider_adapter import run_provider  # noqa: E402

from test_dev_loop import copy_contract_repo  # noqa: E402


def test_command_provider_redacts_stdout_and_stderr(tmp_path):
    repo = copy_contract_repo(tmp_path)
    issue_file = tmp_path / "issue.md"
    issue_file.write_text("secret issue context\n", encoding="utf-8")
    env = os.environ.copy()
    env["AGENTIC_PROVIDER_COMMAND"] = (
        f"{sys.executable} -c "
        + json.dumps(
            "import sys; print('SECRET_STDOUT_TOKEN'); print('SECRET_STDERR_TOKEN', file=sys.stderr)"
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; "
                f"sys.path.insert(0, {str(Path(__file__).resolve().parents[2] / 'scripts' / 'agentic')!r}); "
                "from pathlib import Path; "
                "from provider_adapter import run_provider; "
                f"print(json.dumps(run_provider('command', Path({str(issue_file)!r}), Path({str(repo)!r}))))"
            ),
        ],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    serialized = json.dumps(payload)

    assert payload["ok"] is True
    assert payload["output_redacted"] is True
    assert payload["stdout_bytes"] > 0
    assert payload["stderr_bytes"] > 0
    assert "SECRET_STDOUT_TOKEN" not in serialized
    assert "SECRET_STDERR_TOKEN" not in serialized
    assert "stdout" not in payload
    assert "stderr" not in payload
