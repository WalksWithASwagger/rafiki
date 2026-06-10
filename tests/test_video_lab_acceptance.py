from __future__ import annotations

import json
import subprocess
import sys


def test_video_lab_acceptance_command_passes() -> None:
    proc = subprocess.run(
        [sys.executable, "scripts/video-lab-acceptance.py"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["portal"]["range_status"] == 206
    assert payload["dry_run_job"]["status"] == "dry-run"
    assert payload["private_media"]["copied_alex_media"] is False
    assert payload["registry"]["clean_warnings"] == []
    assert payload["validation"]["good_ok"] is True
    assert payload["validation"]["bad_detects_missing_clip"] is True
    assert payload["warnings"]["missing_root_warned"] is True
