"""Usage tracking for Rafiki (local log, gitignored)."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from datetime import datetime
from pathlib import Path

USAGE_LOG_PATH = Path(__file__).parent.parent / "data" / "usage-log.json"

# Serializes the read-modify-write cycle in log_generation() so concurrent
# workers (ThreadPoolExecutor in lib/batch.py) cannot interleave and corrupt
# the JSON file. Module-level so all threads in the process share it.
_log_lock = threading.Lock()


def load_usage_log() -> dict:
    if USAGE_LOG_PATH.exists():
        try:
            with open(USAGE_LOG_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupted log — back it up and start fresh rather than crashing the batch
            backup = USAGE_LOG_PATH.with_suffix(".json.bak")
            USAGE_LOG_PATH.rename(backup)
    return {"entries": [], "total_images": 0}


def save_usage_log(data: dict) -> None:
    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: serialize to a temp file in the same directory, fsync,
    # then os.replace() onto the target. os.replace is atomic on POSIX and
    # Windows, so a reader can never observe a half-written file.
    fd, tmp_path = tempfile.mkstemp(
        prefix=".usage-log.", suffix=".tmp", dir=str(USAGE_LOG_PATH.parent)
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, USAGE_LOG_PATH)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def log_generation(
    prompt: str,
    model: str,
    output_path: str,
    aspect_ratio: str,
    *,
    style: str = "",
    ok: bool = True,
    error: str = "",
) -> None:
    with _log_lock:
        data = load_usage_log()
        entry: dict = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "aspect_ratio": aspect_ratio,
            "output": str(output_path),
            "prompt": prompt,
            "ok": ok,
        }
        if style:
            entry["style"] = style
        if error:
            entry["error"] = error
        data["entries"].append(entry)
        data["total_images"] = sum(1 for e in data["entries"] if e.get("ok", True))
        save_usage_log(data)
