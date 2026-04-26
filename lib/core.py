"""Core single-image generation function for Rafiki."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure rafiki root is importable when this module is loaded directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.models import resolve_model
from lib.styles import resolve_style_suffix, get_default_style
from lib.usage import log_generation
from lib.providers import get_provider


def generate_image(
    prompt: str,
    output_path: str,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str | None = None,
    reference_image: str | None = None,
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    dry_run: bool = False,
) -> bool:
    """Generate a single image via the appropriate provider.

    Args:
        prompt: Text prompt describing the image.
        output_path: Destination file path.
        model: Full model ID or alias (see lib.models.ALIASES).
        aspect_ratio: Ratio string or preset (linkedin, instagram, story, square).
        resolution: 1K/2K/4K — Gemini Pro only.
        quality: low/medium/high — OpenAI only.
        style: Style preset name, composed spec (e.g. "kk+bcai"), "none", or None.
        reference_image: Path to a reference image.
        reference_role: "style" (look-and-feel) or "mockup" (preserve garment).
        composition_references: Extra ref image paths (mockup mode).
        dry_run: Log intent without calling any API.

    Returns:
        True on success, False on failure.
    """
    model = resolve_model(model)

    if style is None:
        style = get_default_style()

    if dry_run:
        provider_name = "OpenAI" if model.startswith(("gpt-image", "dall-e")) else "Gemini"
        print("[DRY RUN] Would generate image:")
        print(f"  Provider: {provider_name}")
        print(f"  Model:    {model}")
        print(f"  Ratio:    {aspect_ratio}  Resolution: {resolution}  Quality: {quality}")
        print(f"  Style:    {style}")
        print(f"  Output:   {output_path}")
        print(f"  Prompt:   {prompt[:200]}...")
        return True

    full_prompt = prompt
    if style and style != "none":
        suffix = resolve_style_suffix(style)
        if suffix:
            full_prompt = f"{prompt}\n\n{suffix}"
        else:
            print(f"Warning: No suffix found for style '{style}' — sending prompt unstyled")

    print(f"Generating image with {model}...")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Prompt: {prompt[:100]}...")

    try:
        provider = get_provider(model)
    except ValueError as e:
        print(f"Error: {e}")
        return False

    success = provider.generate(
        prompt=full_prompt,
        output_path=output_path,
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        quality=quality,
        reference_image=reference_image,
        reference_role=reference_role,
        composition_references=composition_references,
    )

    log_generation(
        prompt, model, output_path, aspect_ratio,
        style=style or "",
        ok=success,
    )

    return success
