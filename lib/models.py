"""Model aliases and resolution for Rafiki providers."""

from __future__ import annotations

ALIASES: dict[str, str] = {
    "flash":  "gemini-2.5-flash-image",
    "nano":   "gemini-2.5-flash-image",
    "gemini": "gemini-2.5-flash-image",
    "pro":    "gemini-3-pro-image-preview",
    "gpt":    "gpt-image-2",
    "gpt2":   "gpt-image-2",
    "gpt1":   "gpt-image-1",
    "dalle3": "dall-e-3",
    "dalle2": "dall-e-2",
}


def resolve_model(model: str) -> str:
    """Expand a friendly alias to the full model ID; pass through unknowns."""
    return ALIASES.get(model.lower(), model)
