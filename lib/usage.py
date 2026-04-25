"""Usage tracking for Rafiki (local log, gitignored)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

USAGE_LOG_PATH = Path(__file__).parent.parent / "data" / "usage-log.json"


def load_usage_log() -> dict:
    if USAGE_LOG_PATH.exists():
        with open(USAGE_LOG_PATH) as f:
            return json.load(f)
    return {"entries": [], "total_images": 0}


def save_usage_log(data: dict) -> None:
    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USAGE_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def log_generation(prompt: str, model: str, output_path: str, aspect_ratio: str) -> None:
    data = load_usage_log()
    data["entries"].append({
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "aspect_ratio": aspect_ratio,
        "output": str(output_path),
        "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
    })
    data["total_images"] = len(data["entries"])
    save_usage_log(data)
