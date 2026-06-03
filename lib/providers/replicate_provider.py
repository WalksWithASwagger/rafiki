"""Replicate provider helpers with dry-run-first job records."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from time import sleep
from typing import Any

from lib.jobs import new_job_id, now_iso, save_job
from lib.media_types import JobRecord

REPLICATE_API_BASE = "https://api.replicate.com/v1"


class ReplicateError(RuntimeError):
    pass


def has_token() -> bool:
    return bool(os.environ.get("REPLICATE_API_TOKEN"))


def redact_request(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload))


def create_job(
    *,
    kind: str,
    model: str,
    input: dict[str, Any],
    target_output_dir: Path,
    manifest_path: Path,
    execute: bool = False,
    endpoint: str = "predictions",
    provider_response: dict[str, Any] | None = None,
) -> JobRecord:
    created_at = now_iso()
    response = provider_response or {}
    record = JobRecord(
        id=new_job_id(kind),
        kind=kind,
        provider="replicate",
        status=_job_status(response, execute=execute),
        target_output_dir=str(target_output_dir.resolve(strict=False)),
        cost_estimate={"basis": "provider", "currency": "USD", "amount": None},
        created_at=created_at,
        updated_at=created_at,
        manifest_path=str(manifest_path.resolve(strict=False)),
        request={
            "model": model,
            "input": redact_request(input),
            "endpoint": endpoint,
            "execute": execute,
        },
        error=_job_error(response),
        provider_response=response,
    )
    save_job(record)
    return record


def run_prediction(model: str, input: dict[str, Any], *, execute: bool = False) -> dict[str, Any]:
    if not execute:
        return {"status": "dry-run", "model": model, "input": redact_request(input)}
    return _post_json("/predictions", {"version": model, "input": input})


def run_training(
    destination: str,
    trainer_model: str,
    trainer_version: str,
    input: dict[str, Any],
    *,
    execute: bool = False,
) -> dict[str, Any]:
    if not execute:
        return {
            "status": "dry-run",
            "destination": destination,
            "trainer_model": trainer_model,
            "trainer_version": trainer_version,
            "input": redact_request(input),
        }
    owner, name = trainer_model.split("/", 1)
    path = f"/models/{owner}/{name}/versions/{trainer_version}/trainings"
    return _post_json(path, {"destination": destination, "input": input})


def get_resource(path_or_url: str, *, execute: bool = False) -> dict[str, Any]:
    if not execute:
        return {"status": "dry-run", "url": path_or_url}
    return _get_json(_api_path(path_or_url))


def poll_resource(
    path_or_url: str,
    *,
    execute: bool = False,
    interval_seconds: float = 2,
    max_attempts: int = 120,
) -> dict[str, Any]:
    if not execute:
        return {"status": "dry-run", "url": path_or_url, "polling": False}
    path = _api_path(path_or_url)
    last: dict[str, Any] = {}
    for _ in range(max(1, max_attempts)):
        last = _get_json(path)
        status = str(last.get("status") or "").lower()
        if status in {"succeeded", "failed", "canceled", "cancelled"}:
            return last
        sleep(max(0.1, interval_seconds))
    last["polling_error"] = "max attempts exceeded"
    return last


def download_output(url: str, output_path: Path, *, execute: bool = False) -> dict[str, Any]:
    output_path = Path(output_path).expanduser()
    if not execute:
        return {"status": "dry-run", "url": url, "output_path": str(output_path)}
    req = urllib.request.Request(url, headers={"Accept": "application/octet-stream"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise ReplicateError(f"download HTTP {e.code}: {detail[:1000]}") from e
    except urllib.error.URLError as e:
        raise ReplicateError(f"download failed: {e}") from e
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(body)
    return {"status": "downloaded", "url": url, "output_path": str(output_path), "bytes": len(body)}


def _post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise ReplicateError("REPLICATE_API_TOKEN is required for --execute")
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{REPLICATE_API_BASE}{path}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise ReplicateError(f"Replicate HTTP {e.code}: {detail[:1000]}") from e
    except urllib.error.URLError as e:
        raise ReplicateError(f"Replicate request failed: {e}") from e
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"response": data}


def _get_json(path: str) -> dict[str, Any]:
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise ReplicateError("REPLICATE_API_TOKEN is required for --execute")
    req = urllib.request.Request(
        f"{REPLICATE_API_BASE}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise ReplicateError(f"Replicate HTTP {e.code}: {detail[:1000]}") from e
    except urllib.error.URLError as e:
        raise ReplicateError(f"Replicate request failed: {e}") from e
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"response": data}


def _api_path(path_or_url: str) -> str:
    if path_or_url.startswith(REPLICATE_API_BASE):
        return path_or_url.removeprefix(REPLICATE_API_BASE)
    if path_or_url.startswith("/"):
        return path_or_url
    return f"/{path_or_url}"


def _job_status(provider_response: dict[str, Any], *, execute: bool) -> str:
    if not execute:
        return "dry-run"
    status = str(provider_response.get("status") or "").lower()
    if status in {"failed", "canceled", "cancelled"}:
        return "failed"
    if status == "succeeded":
        return "succeeded"
    return status or "queued"


def _job_error(provider_response: dict[str, Any]) -> str:
    if str(provider_response.get("status") or "").lower() != "failed":
        return ""
    return str(provider_response.get("error") or provider_response.get("logs") or "")[:2000]
