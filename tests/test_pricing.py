from __future__ import annotations

from lib.pricing import estimate_image_cost, load_pricing_profile


def test_pricing_profile_estimates_gemini_flash_image():
    profile = load_pricing_profile()

    estimate = estimate_image_cost(
        model="gemini-2.5-flash-image",
        provider="Gemini",
        resolution="1K",
        pricing_profile=profile,
    )

    assert estimate["amount"] == 0.039
    assert estimate["estimated"] is True
    assert estimate["basis"] == "official_output_image_price"
    assert estimate["source_url"] == "https://ai.google.dev/gemini-api/docs/pricing"


def test_pricing_profile_keeps_token_priced_openai_unestimated_without_usage_tokens():
    estimate = estimate_image_cost(model="gpt-image-2", provider="OpenAI")

    assert estimate["amount"] is None
    assert estimate["estimated"] is False
    assert "Token-priced model" in estimate["note"]


def test_pricing_profile_can_estimate_openai_when_manifest_tokens_exist():
    estimate = estimate_image_cost(
        model="gpt-image-2",
        provider="OpenAI",
        usage_tokens=1200,
    )

    assert estimate["amount"] == 0.036
    assert estimate["estimated"] is True
    assert estimate["basis"] == "manifest_output_tokens"
