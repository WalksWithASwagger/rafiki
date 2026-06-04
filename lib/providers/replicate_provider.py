"""Replicate provider helpers with dry-run-first job records."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from time import sleep
from typing import Any

from lib.jobs import load_job, new_job_id, now_iso, save_job, update_job
from lib.media_types import JobRecord

REPLICATE_API_BASE = "https://api.replicate.com/v1"
_FAILED_STATUSES = {"failed", "canceled", "cancelled"}
_TERMINAL_STATUSES = {"succeeded", *_FAILED_STATUSES}


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
    cost_estimate: dict[str, Any] | None = None,
    jobs_dir: Path | None = None,
) -> JobRecord:
    created_at = now_iso()
    response = provider_response or {}
    lifecycle = _job_lifecycle(response, execute=execute, checked_at=created_at)
    record = JobRecord(
        id=new_job_id(kind),
        kind=kind,
        provider="replicate",
        status=_job_status(response, execute=execute),
        target_output_dir=str(target_output_dir.resolve(strict=False)),
        cost_estimate=cost_estimate or {
            "basis": "provider_billing_required",
            "currency": "USD",
            "amount": None,
            "estimated": False,
            "provider": "Replicate",
            "model": model,
            "note": "Replicate billing remains the source of truth for paid job spend.",
        },
        created_at=created_at,
        updated_at=created_at,
        manifest_path=str(manifest_path.resolve(strict=False)),
        provider_url=lifecycle["provider_url"],
        polling_status=lifecycle["polling_status"],
        output_download_state=lifecycle["output_download_state"],
        failure_details=lifecycle["failure_details"],
        last_checked_at=lifecycle["last_checked_at"],
        request={
            "model": model,
            "input": redact_request(input),
            "endpoint": endpoint,
            "execute": execute,
        },
        error=_job_error(response),
        provider_response=response,
    )
    save_job(record, jobs_dir=jobs_dir)
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


def poll_job(
    job_id: str,
    *,
    jobs_dir: Path | None = None,
    execute: bool = False,
    interval_seconds: float = 2,
    max_attempts: int = 120,
) -> dict[str, Any]:
    record = load_job(job_id, jobs_dir=jobs_dir)
    if record is None:
        raise ValueError(f"job not found: {job_id}")
    provider_url = str(record.get("provider_url") or _provider_url(record.get("provider_response")))
    if not provider_url:
        raise ValueError(f"job has no provider URL: {job_id}")
    provider_response = poll_resource(
        provider_url,
        execute=execute,
        interval_seconds=interval_seconds,
        max_attempts=max_attempts,
    )
    return capture_job_provider_response(job_id, provider_response, jobs_dir=jobs_dir)


def capture_job_provider_response(
    job_id: str,
    provider_response: dict[str, Any],
    *,
    jobs_dir: Path | None = None,
    output_download_state: str = "",
) -> dict[str, Any]:
    record = load_job(job_id, jobs_dir=jobs_dir)
    if record is None:
        raise ValueError(f"job not found: {job_id}")
    request = record.get("request") if isinstance(record.get("request"), dict) else {}
    execute = bool(request.get("execute"))
    checked_at = now_iso()
    lifecycle = _job_lifecycle(provider_response, execute=execute, checked_at=checked_at)
    if output_download_state:
        lifecycle["output_download_state"] = output_download_state
    return update_job(
        job_id,
        {
            **lifecycle,
            "status": _job_status(provider_response, execute=execute),
            "error": _job_error(provider_response),
            "provider_response": provider_response,
        },
        jobs_dir=jobs_dir,
    )


def capture_job_output_download(
    job_id: str,
    download_result: dict[str, Any],
    *,
    jobs_dir: Path | None = None,
) -> dict[str, Any]:
    status = str(download_result.get("status") or "").lower()
    if status == "downloaded":
        state = "downloaded"
    elif status == "dry-run":
        state = "dry-run"
    else:
        state = "failed" if download_result.get("error") else "pending"
    updates: dict[str, Any] = {
        "output_download_state": state,
        "last_checked_at": now_iso(),
        "output_download": download_result,
    }
    if download_result.get("error"):
        updates["failure_details"] = {"download_error": str(download_result.get("error"))[:2000]}
    return update_job(job_id, updates, jobs_dir=jobs_dir)


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
    if status in _FAILED_STATUSES:
        return "failed"
    if status == "succeeded":
        return "succeeded"
    return status or "queued"


def _job_error(provider_response: dict[str, Any]) -> str:
    status = str(provider_response.get("status") or "").lower()
    if status not in _FAILED_STATUSES and not provider_response.get("error"):
        return ""
    return str(provider_response.get("error") or provider_response.get("logs") or "")[:2000]


def _job_lifecycle(provider_response: dict[str, Any], *, execute: bool, checked_at: str) -> dict[str, Any]:
    return {
        "provider_url": _provider_url(provider_response),
        "polling_status": _polling_status(provider_response, execute=execute),
        "output_download_state": _output_download_state(provider_response, execute=execute),
        "failure_details": _failure_details(provider_response),
        "last_checked_at": checked_at,
    }


def _provider_url(provider_response: object) -> str:
    if not isinstance(provider_response, dict):
        return ""
    urls = provider_response.get("urls")
    if isinstance(urls, dict):
        for key in ("get", "web", "stream"):
            value = urls.get(key)
            if isinstance(value, str) and value:
                return value
    for key in ("url", "prediction_url", "training_url"):
        value = provider_response.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _polling_status(provider_response: dict[str, Any], *, execute: bool) -> str:
    if not execute:
        return "not-started"
    status = str(provider_response.get("status") or "").lower()
    if provider_response.get("polling_error"):
        return "polling-timeout"
    if status in _TERMINAL_STATUSES:
        return status
    return status or "queued"


def _output_download_state(provider_response: dict[str, Any], *, execute: bool) -> str:
    if not execute:
        return "not-started"
    status = str(provider_response.get("status") or "").lower()
    if status in _FAILED_STATUSES:
        return "blocked"
    output = provider_response.get("output")
    if status == "succeeded":
        return "available" if output else "none"
    return "pending"


def _failure_details(provider_response: dict[str, Any]) -> dict[str, Any]:
    status = str(provider_response.get("status") or "").lower()
    if status not in _FAILED_STATUSES and not provider_response.get("error") and not provider_response.get("polling_error"):
        return {}
    details: dict[str, Any] = {}
    if status:
        details["status"] = status
    for key in ("error", "logs", "polling_error"):
        value = provider_response.get(key)
        if value:
            details[key] = str(value)[:2000]
    return details
