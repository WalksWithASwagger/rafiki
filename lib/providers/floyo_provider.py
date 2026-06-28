"""Floyo (flowyo.ai) provider helpers with dry-run-first job records.

Floyo is a hosted ComfyUI service: upload an asset, submit a ComfyUI API-format
workflow to ``/runs``, poll the run, then download the output. Mirrors the shape
of ``replicate_provider`` so the rest of Rafiki treats it the same way.
"""

from __future__ import annotations

import json
import mimetypes
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from time import sleep
from typing import Any

from lib.jobs import new_job_id, now_iso, save_job
from lib.media_types import JobRecord

FLOYO_API_BASE = "https://api.floyo.ai"
FLOYO_UPLOAD_URL = "https://cdn.floyo.ai/upload"
_FAILED_STATUSES = {"failed", "cancelled", "canceled", "error"}
_TERMINAL_STATUSES = {"done", *_FAILED_STATUSES}


class FloyoError(RuntimeError):
    pass


def has_token() -> bool:
    return bool(os.environ.get("FLOYO_KEY"))


def _token() -> str:
    token = os.environ.get("FLOYO_KEY")
    if not token:
        raise FloyoError("FLOYO_KEY is required for --execute")
    return token.strip()


def redact_request(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload))


def upload_asset(path: str | Path, mime: str = "", *, execute: bool = False) -> dict[str, Any]:
    """Upload a local file to the Floyo CDN. Returns at least ``input_path`` and ``id``."""
    src = Path(path).expanduser()
    if not execute:
        return {"status": "dry-run", "input_path": f"#dry-run/{src.name}", "id": ""}
    if not src.is_file():
        raise FloyoError(f"upload source not found: {src}")
    mime = mime or mimetypes.guess_type(src.name)[0] or "application/octet-stream"
    body, content_type = _multipart(
        fields={"path": "/api/uploads", "on_conflict": "rename"},
        file_field="file",
        file_path=src,
        mime=mime,
    )
    req = urllib.request.Request(
        FLOYO_UPLOAD_URL,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": content_type},
    )
    data = _read_json(req, timeout=300)
    if "input_path" not in data:
        raise FloyoError(f"upload response missing input_path: {json.dumps(data)[:500]}")
    return data


def presigned_url(file_id: str, *, execute: bool = False) -> str:
    """Time-limited public URL for an uploaded file (needed by audio_url loaders)."""
    if not execute:
        return f"#dry-run/presigned/{file_id}"
    data = _get_json(f"/files/{file_id}?expand=presigned_url")
    url = data.get("presigned_url")
    if not url:
        raise FloyoError(f"presigned_url missing in response: {json.dumps(data)[:500]}")
    return str(url)


def run_workflow(name: str, workflow: dict[str, Any], *, execute: bool = False) -> dict[str, Any]:
    if not execute:
        return {"status": "dry-run", "workflow_name": name, "workflow": redact_request(workflow)}
    return _post_json("/runs", {"name": name, "workflow": workflow})


def poll_run(
    run_id: str,
    *,
    execute: bool = False,
    interval_seconds: float = 10,
    max_attempts: int = 120,
) -> dict[str, Any]:
    if not execute:
        return {"status": "dry-run", "id": run_id, "polling": False}
    last: dict[str, Any] = {}
    for _ in range(max(1, max_attempts)):
        last = _get_json(f"/runs/{run_id}")
        status = str(last.get("status") or "").lower()
        if status in _TERMINAL_STATUSES:
            return last
        sleep(max(0.1, interval_seconds))
    last["polling_error"] = "max attempts exceeded"
    return last


def find_outputs(run: dict[str, Any]) -> list[dict[str, Any]]:
    """Dig output file dicts out of whatever shape the run object has."""
    found: list[dict[str, Any]] = []
    for key in ("outputs", "output", "results", "files"):
        value = run.get(key)
        if isinstance(value, list):
            found.extend(item for item in value if isinstance(item, dict))
    return found


def output_url(output: dict[str, Any]) -> str:
    for key in ("presigned_url", "url", "download_url"):
        value = output.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def download_output(url: str, output_path: Path, *, execute: bool = False) -> dict[str, Any]:
    output_path = Path(output_path).expanduser()
    if not execute:
        return {"status": "dry-run", "url": url, "output_path": str(output_path)}
    req = urllib.request.Request(url, headers={"Accept": "application/octet-stream"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise FloyoError(f"download HTTP {e.code}: {detail[:1000]}") from e
    except urllib.error.URLError as e:
        raise FloyoError(f"download failed: {e}") from e
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(body)
    return {"status": "downloaded", "url": url, "output_path": str(output_path), "bytes": len(body)}


def create_job(
    *,
    kind: str,
    workflow_name: str,
    input: dict[str, Any],
    target_output_dir: Path,
    manifest_path: Path,
    execute: bool = False,
    provider_response: dict[str, Any] | None = None,
    cost_estimate: dict[str, Any] | None = None,
    jobs_dir: Path | None = None,
) -> JobRecord:
    created_at = now_iso()
    response = provider_response or {}
    run_id = str(response.get("id") or "")
    record = JobRecord(
        id=new_job_id(kind),
        kind=kind,
        provider="Floyo",
        status=_job_status(response, execute=execute),
        target_output_dir=str(target_output_dir.resolve(strict=False)),
        cost_estimate=cost_estimate or {
            "basis": "provider_billing_required",
            "currency": "USD",
            "amount": None,
            "estimated": False,
            "provider": "Floyo",
            "model": workflow_name,
            "note": "Floyo FloTime billing remains the source of truth for paid job spend.",
        },
        created_at=created_at,
        updated_at=created_at,
        manifest_path=str(manifest_path.resolve(strict=False)),
        provider_url=f"{FLOYO_API_BASE}/runs/{run_id}" if run_id else "",
        polling_status=_polling_status(response, execute=execute),
        last_checked_at=created_at,
        request={
            "workflow": workflow_name,
            "input": redact_request(input),
            "execute": execute,
        },
        error=_job_error(response),
        provider_response=response,
    )
    save_job(record, jobs_dir=jobs_dir)
    return record


def _job_status(response: dict[str, Any], *, execute: bool) -> str:
    if not execute:
        return "dry-run"
    status = str(response.get("status") or "").lower()
    if status in _FAILED_STATUSES:
        return "failed"
    if status == "done":
        return "succeeded"
    return status or "queued"


def _polling_status(response: dict[str, Any], *, execute: bool) -> str:
    if not execute:
        return "not-started"
    if response.get("polling_error"):
        return "polling-timeout"
    status = str(response.get("status") or "").lower()
    if status in _TERMINAL_STATUSES:
        return "succeeded" if status == "done" else status
    return status or "queued"


def _job_error(response: dict[str, Any]) -> str:
    status = str(response.get("status") or "").lower()
    if status not in _FAILED_STATUSES and not response.get("error"):
        return ""
    return str(response.get("error") or response.get("logs") or "")[:2000]


def _multipart(
    *,
    fields: dict[str, str],
    file_field: str,
    file_path: Path,
    mime: str,
) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    crlf = b"\r\n"
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(f"--{boundary}".encode())
        parts.append(f'Content-Disposition: form-data; name="{key}"'.encode())
        parts.append(b"")
        parts.append(value.encode())
    parts.append(f"--{boundary}".encode())
    parts.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"'.encode()
    )
    parts.append(f"Content-Type: {mime}".encode())
    parts.append(b"")
    parts.append(file_path.read_bytes())
    parts.append(f"--{boundary}--".encode())
    parts.append(b"")
    return crlf.join(parts), f"multipart/form-data; boundary={boundary}"


def _post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{FLOYO_API_BASE}{path}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    return _read_json(req, timeout=60)


def _get_json(path: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{FLOYO_API_BASE}{path}",
        headers={"Authorization": f"Bearer {_token()}", "Accept": "application/json"},
    )
    return _read_json(req, timeout=60)


def _read_json(req: urllib.request.Request, *, timeout: int) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise FloyoError(f"Floyo HTTP {e.code}: {detail[:1000]}") from e
    except urllib.error.URLError as e:
        raise FloyoError(f"Floyo request failed: {e}") from e
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"response": data}
