from __future__ import annotations


def get_provider(model: str):
    """Route to the correct provider based on model name prefix."""
    if model.startswith("gemini"):
        from .gemini import GeminiProvider
        return GeminiProvider()
    if model.startswith(("gpt-image", "dall-e")):
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
    raise ValueError(
        f"Unknown model '{model}'. "
        "Supported prefixes: gemini-* (e.g. gemini-2.5-flash-image), "
        "gpt-image-* (e.g. gpt-image-2), dall-e-* (e.g. dall-e-3)."
    )
