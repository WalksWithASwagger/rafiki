import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_python_ci_lock_is_hashed_and_reproducible() -> None:
    lock = (ROOT / "requirements-ci.txt").read_text(encoding="utf-8")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    package_lines = [
        index
        for index, line in enumerate(lock.splitlines())
        if re.match(r"^[a-z0-9][a-z0-9_.-]*==", line)
    ]

    assert "--only-binary :all:" in lock
    assert package_lines
    assert "--allow-unsafe" in package["scripts"]["lock:python-ci"]
    assert "--python-version 3.11" in package["scripts"]["lock:python-ci"]
    assert "manylinux_2_17_x86_64" in package["scripts"]["lock:python-ci"]

    lines = lock.splitlines()
    for position, start in enumerate(package_lines):
        stop = package_lines[position + 1] if position + 1 < len(package_lines) else len(lines)
        block = "\n".join(lines[start:stop])
        assert "--hash=sha256:" in block, lines[start]
