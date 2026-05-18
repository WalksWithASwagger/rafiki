"""Local provider billing import ledger for Rafiki."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
BILLING_IMPORT_PATH = REPO_ROOT / "data" / "billing-imports.json"

_AMOUNT_FIELDS = ("amount", "cost", "total", "total_cost", "charge", "usd", "spend", "price")
_PROVIDER_FIELDS = ("provider", "vendor", "service", "platform")
_MODEL_FIELDS = ("model", "model_id", "sku", "product")
_CURRENCY_FIELDS = ("currency", "currency_code")
_IMAGE_COUNT_FIELDS = ("image_count", "images", "quantity", "count", "units")
_TIMESTAMP_FIELDS = ("timestamp", "date", "created_at", "started_at", "usage_date")
_NOTE_FIELDS = ("note", "notes", "description", "memo")


def _default_state() -> dict[str, Any]:
    return {"version": 1, "imports": []}


def load_billing_imports(path: Path | None = None) -> dict[str, Any]:
    state_path = Path(path) if path is not None else BILLING_IMPORT_PATH
    if not state_path.exists():
        return _default_state()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return _default_state()
    if not isinstance(data, dict):
        return _default_state()
    imports = data.get("imports")
    if not isinstance(imports, list):
        imports = []
    return {"version": 1, "imports": [item for item in imports if isinstance(item, dict)]}


def save_billing_imports(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".billing-imports.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _normalise_key(key: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(key or "").strip().lower()).strip("_")


def _normalise_row(row: dict[str, Any]) -> dict[str, Any]:
    return {_normalise_key(key): value for key, value in row.items()}


def _first(row: dict[str, Any], names: tuple[str, ...], default: object = "") -> object:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    return default


def _text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _amount(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _text(value)
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = re.sub(r"[^0-9.+-]", "", text)
    if text in ("", ".", "+", "-"):
        return None
    try:
        amount = float(text)
    except ValueError:
        return None
    return -amount if negative else amount


def _int(value: object, default: int = 1) -> int:
    try:
        parsed = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _row_id(entry: dict[str, Any]) -> str:
    payload = json.dumps(
        {key: value for key, value in entry.items() if key not in {"id", "imported_at"}},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def normalise_billing_row(
    row: dict[str, Any],
    *,
    source: str = "",
    provider: str = "",
    label: str = "",
    row_number: int = 0,
) -> dict[str, Any] | None:
    normal = _normalise_row(row)
    amount = _amount(_first(normal, _AMOUNT_FIELDS))
    if amount is None:
        return None
    entry = {
        "provider": provider or _text(_first(normal, _PROVIDER_FIELDS)) or "unknown",
        "model": _text(_first(normal, _MODEL_FIELDS)),
        "amount": round(amount, 6),
        "currency": (_text(_first(normal, _CURRENCY_FIELDS, "USD")) or "USD").upper(),
        "image_count": _int(_first(normal, _IMAGE_COUNT_FIELDS, 1)),
        "timestamp": _text(_first(normal, _TIMESTAMP_FIELDS)),
        "project": _text(normal.get("project", "")),
        "run_id": _text(normal.get("run_id", "")),
        "file": _text(normal.get("file", "")),
        "note": _text(_first(normal, _NOTE_FIELDS)),
        "source": label or source or "manual",
        "source_row": row_number,
        "imported_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    entry["id"] = _row_id(entry)
    return entry


def _rows_from_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _rows_from_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = next(
            (
                data[key]
                for key in ("imports", "entries", "items", "rows", "data")
                if isinstance(data.get(key), list)
            ),
            [data],
        )
    else:
        rows = []
    return [row for row in rows if isinstance(row, dict)]


def _rows_from_file(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _rows_from_csv(path)
    if suffix in {".json", ".jsonl"}:
        if suffix == ".jsonl":
            rows = []
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    value = json.loads(line)
                    if isinstance(value, dict):
                        rows.append(value)
            return rows
        return _rows_from_json(path)
    raise ValueError("billing import source must be .csv, .json, or .jsonl")


def append_billing_entries(
    path: Path | None,
    rows: list[dict[str, Any]],
    *,
    provider: str = "",
    label: str = "",
    source: str = "manual",
) -> dict[str, Any]:
    state_path = Path(path) if path is not None else BILLING_IMPORT_PATH
    state = load_billing_imports(state_path)
    existing_ids = {str(entry.get("id")) for entry in state["imports"]}
    imported = 0
    duplicates = 0
    skipped = 0

    for index, row in enumerate(rows, start=1):
        entry = normalise_billing_row(
            row,
            source=source,
            provider=provider,
            label=label,
            row_number=index,
        )
        if entry is None:
            skipped += 1
            continue
        if entry["id"] in existing_ids:
            duplicates += 1
            continue
        state["imports"].append(entry)
        existing_ids.add(entry["id"])
        imported += 1

    save_billing_imports(state_path, state)
    return {
        "ok": True,
        "path": str(state_path),
        "imported": imported,
        "duplicates": duplicates,
        "skipped": skipped,
        "total_entries": len(state["imports"]),
    }


def import_billing_file(
    source_path: Path,
    *,
    state_path: Path | None = None,
    provider: str = "",
    label: str = "",
) -> dict[str, Any]:
    source = Path(source_path)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"billing import source not found: {source}")
    return append_billing_entries(
        state_path,
        _rows_from_file(source),
        provider=provider,
        label=label,
        source=source.name,
    )


def summarize_billing_imports(path: Path | None = None) -> dict[str, Any]:
    state_path = Path(path) if path is not None else BILLING_IMPORT_PATH
    state = load_billing_imports(state_path)
    entries = state["imports"]
    by_provider: dict[str, dict[str, Any]] = {}
    by_model: dict[str, dict[str, Any]] = {}
    by_currency: dict[str, float] = {}

    for entry in entries:
        amount = _amount(entry.get("amount"))
        if amount is None:
            continue
        currency = _text(entry.get("currency")) or "USD"
        provider = _text(entry.get("provider")) or "unknown"
        model = _text(entry.get("model")) or "unknown"
        by_currency[currency] = by_currency.get(currency, 0.0) + amount
        provider_bucket = by_provider.setdefault(provider, {"provider": provider, "amount": 0.0, "entries": 0})
        provider_bucket["amount"] += amount
        provider_bucket["entries"] += 1
        model_bucket = by_model.setdefault(model, {"model": model, "amount": 0.0, "entries": 0})
        model_bucket["amount"] += amount
        model_bucket["entries"] += 1

    recent = sorted(
        entries,
        key=lambda item: str(item.get("timestamp") or item.get("imported_at") or ""),
        reverse=True,
    )[:8]
    return {
        "path": str(state_path),
        "entries": len(entries),
        "currency": "USD",
        "amount": round(by_currency.get("USD", 0.0), 4),
        "by_currency": [
            {"currency": currency, "amount": round(amount, 4)}
            for currency, amount in sorted(by_currency.items())
        ],
        "by_provider": sorted(
            [
                {**bucket, "amount": round(float(bucket["amount"]), 4)}
                for bucket in by_provider.values()
            ],
            key=lambda bucket: bucket["amount"],
            reverse=True,
        ),
        "by_model": sorted(
            [
                {**bucket, "amount": round(float(bucket["amount"]), 4)}
                for bucket in by_model.values()
            ],
            key=lambda bucket: bucket["amount"],
            reverse=True,
        ),
        "recent": recent,
    }
