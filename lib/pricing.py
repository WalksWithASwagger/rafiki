"""Local pricing-profile helpers for Rafiki cost estimates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PRICING_PATH = REPO_ROOT / "config" / "pricing.json"


def load_pricing_profile(path: Path | None = None) -> dict[str, Any]:
    pricing_path = Path(path) if path is not None else DEFAULT_PRICING_PATH
    try:
        data = json.loads(pricing_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": 0,
            "currency": "USD",
            "models": {},
            "path": str(pricing_path),
            "loaded": False,
        }
    if not isinstance(data, dict):
        data = {}
    data.setdefault("currency", "USD")
    data.setdefault("models", {})
    data["path"] = str(pricing_path)
    data["loaded"] = True
    return data


def provider_for_model(model: str) -> str | None:
    if model.startswith("gemini"):
        return "Gemini"
    if model.startswith(("gpt-image", "dall-e")):
        return "OpenAI"
    return None


def _amount(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def estimate_image_cost(
    *,
    model: str,
    provider: str | None = None,
    resolution: str | None = None,
    service_tier: str | None = None,
    usage_tokens: int | float | None = None,
    dry_run: bool = False,
    pricing_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a cost estimate record suitable for run manifests.

    `amount` is only non-null when Rafiki has enough local evidence to estimate
    the generated image output. Provider billing exports are still the exact
    source of truth.
    """
    profile = pricing_profile if pricing_profile is not None else load_pricing_profile()
    models = profile.get("models", {}) if isinstance(profile.get("models"), dict) else {}
    entry = models.get(model, {}) if isinstance(models.get(model), dict) else {}
    currency = _string(profile.get("currency")) or "USD"
    provider_name = _string(provider) or _string(entry.get("provider")) or provider_for_model(model)
    tier = (service_tier or _string(entry.get("default_tier")) or "standard").lower()
    resolution_key = (resolution or _string(entry.get("default_resolution")) or "").upper()

    amount: float | None = None
    basis = _string(entry.get("basis")) or "not_estimated"
    note = _string(entry.get("source_detail")) or "No pricing profile entry matched this image."

    per_image = entry.get("per_image_usd")
    if isinstance(per_image, dict):
        amount = _amount(per_image.get(tier)) or _amount(per_image.get("standard"))

    per_resolution = entry.get("per_image_usd_by_resolution")
    if amount is None and isinstance(per_resolution, dict):
        amount = _amount(per_resolution.get(resolution_key))
        if amount is None:
            default_resolution = _string(entry.get("default_resolution")).upper()
            amount = _amount(per_resolution.get(default_resolution))

    token_rate = _amount(entry.get("output_usd_per_1m_tokens"))
    if amount is None and token_rate is not None and usage_tokens is not None:
        token_count = _amount(usage_tokens)
        if token_count is not None:
            amount = token_count * token_rate / 1_000_000
            basis = "manifest_output_tokens"
            note = "Estimated from manifest output tokens and pricing profile token rate."

    potential_amount = amount
    if dry_run and amount is not None:
        amount = 0.0
        basis = "dry_run_no_provider_spend"
        note = "Dry run did not call a provider; potential image output cost is included separately."

    estimated = amount is not None
    result: dict[str, Any] = {
        "currency": currency,
        "amount": round(amount, 6) if amount is not None else None,
        "estimated": estimated,
        "basis": basis if estimated else "not_estimated",
        "provider": provider_name,
        "model": model,
        "pricing_profile": profile.get("path", str(DEFAULT_PRICING_PATH)),
        "pricing_updated_at": profile.get("updated_at", ""),
        "note": note,
    }
    if potential_amount is not None and dry_run:
        result["potential_amount"] = round(potential_amount, 6)
    if entry.get("source_url"):
        result["source_url"] = entry["source_url"]
    if not estimated and token_rate is not None:
        result["note"] = "Token-priced model needs manifest token usage or provider billing export for a local estimate."
    return result
