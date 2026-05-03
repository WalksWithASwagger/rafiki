"""Concurrent-write safety for lib/usage.log_generation.

Reproduces the corruption scenario from issue #17: multiple ThreadPoolExecutor
workers calling log_generation() simultaneously must not interleave their
read-modify-write cycles or leave the JSON file half-written.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import usage  # noqa: E402


THREADS = 4
PER_THREAD = 10
TOTAL = THREADS * PER_THREAD


@pytest.fixture
def isolated_log(tmp_path, monkeypatch):
    log_path = tmp_path / "usage-log.json"
    monkeypatch.setattr(usage, "USAGE_LOG_PATH", log_path)
    return log_path


def _worker(thread_id: int) -> None:
    for i in range(PER_THREAD):
        usage.log_generation(
            prompt=f"thread {thread_id} entry {i}",
            model="test-model",
            output_path=f"/tmp/t{thread_id}-{i}.png",
            aspect_ratio="1:1",
            style="test",
            ok=True,
        )


def test_concurrent_log_generation_preserves_all_entries(isolated_log):
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        futures = [pool.submit(_worker, tid) for tid in range(THREADS)]
        for f in futures:
            f.result()

    assert isolated_log.exists(), "usage log was not written"

    with open(isolated_log) as f:
        data = json.load(f)  # would raise if file is corrupt

    assert data["total_images"] == TOTAL
    assert len(data["entries"]) == TOTAL

    seen = {(e["prompt"], e["output"]) for e in data["entries"]}
    expected = {
        (f"thread {tid} entry {i}", f"/tmp/t{tid}-{i}.png")
        for tid in range(THREADS)
        for i in range(PER_THREAD)
    }
    assert seen == expected, "some entries were lost or duplicated"
