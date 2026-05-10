"""Tests for lib.providers — OpenAI and Gemini image generation entry points.

The provider classes expose ``generate(...) -> bool`` and write the resulting
PNG to ``output_path``. Network calls are mocked; the real API is never hit.
"""

from __future__ import annotations

import base64
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from lib.providers.openai_provider import OpenAIProvider


# --- helpers --------------------------------------------------------------

# 1x1 transparent PNG, base64-encoded — small valid payload for save tests.
_TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def _fake_openai_response(b64: str | None = _TINY_PNG_B64, url: str | None = None):
    """Build a stand-in for client.images.generate(...) return value."""
    img_data = MagicMock()
    img_data.b64_json = b64
    img_data.url = url
    response = MagicMock()
    response.data = [img_data]
    return response


@pytest.fixture
def fake_openai_module(monkeypatch):
    """Inject a fake ``openai`` module so ``from openai import OpenAI`` works
    without the real package and without making network calls."""
    fake_module = types.ModuleType("openai")
    fake_client = MagicMock()
    fake_module.OpenAI = MagicMock(return_value=fake_client)
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    return fake_client


# --- OpenAI ---------------------------------------------------------------

def test_openai_generate_image_success(tmp_path, fake_openai_module):
    fake_openai_module.images.generate.return_value = _fake_openai_response()
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="a cat",
        output_path=str(out),
        model="gpt-image-1",
        aspect_ratio="1:1",
    )

    assert ok is True
    assert out.exists()
    assert out.read_bytes() == base64.b64decode(_TINY_PNG_B64)
    fake_openai_module.images.generate.assert_called_once()
    call_kwargs = fake_openai_module.images.generate.call_args.kwargs
    assert call_kwargs["model"] == "gpt-image-1"
    assert call_kwargs["size"] == "1024x1024"


def test_openai_generate_image_missing_api_key_returns_false(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="x",
        output_path=str(out),
        model="gpt-image-1",
    )

    assert ok is False
    assert not out.exists()


def test_openai_generate_image_api_error_returns_false(tmp_path, fake_openai_module):
    fake_openai_module.images.generate.side_effect = RuntimeError("rate limited")
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="x",
        output_path=str(out),
        model="gpt-image-1",
    )

    assert ok is False
    assert not out.exists()


def test_openai_generate_image_no_data_returns_false(tmp_path, fake_openai_module):
    fake_openai_module.images.generate.return_value = _fake_openai_response(
        b64=None, url=None
    )
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="x",
        output_path=str(out),
        model="gpt-image-1",
    )

    assert ok is False
    assert not out.exists()


def test_openai_edit_passes_all_reference_images_without_unsupported_fidelity(
    tmp_path, fake_openai_module
):
    fake_openai_module.images.edit.return_value = _fake_openai_response()
    ref_a = tmp_path / "futureproof.png"
    ref_b = tmp_path / "bcai.png"
    ref_a.write_bytes(b"fake-a")
    ref_b.write_bytes(b"fake-b")
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="a logo-aware website hero",
        output_path=str(out),
        model="gpt-image-2",
        aspect_ratio="16:9",
        reference_image=str(ref_a),
        reference_images=[str(ref_b)],
    )

    assert ok is True
    assert out.exists()
    fake_openai_module.images.generate.assert_not_called()
    fake_openai_module.images.edit.assert_called_once()
    call_kwargs = fake_openai_module.images.edit.call_args.kwargs
    assert call_kwargs["model"] == "gpt-image-2"
    assert call_kwargs["size"] == "1536x1024"
    assert "input_fidelity" not in call_kwargs
    assert [Path(img.name).name for img in call_kwargs["image"]] == ["futureproof.png", "bcai.png"]


def test_openai_edit_keeps_high_fidelity_for_gpt_image_1(tmp_path, fake_openai_module):
    fake_openai_module.images.edit.return_value = _fake_openai_response()
    ref = tmp_path / "futureproof.png"
    ref.write_bytes(b"fake")
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="a logo-aware website hero",
        output_path=str(out),
        model="gpt-image-1",
        aspect_ratio="16:9",
        reference_image=str(ref),
    )

    assert ok is True
    call_kwargs = fake_openai_module.images.edit.call_args.kwargs
    assert call_kwargs["model"] == "gpt-image-1"
    assert call_kwargs["input_fidelity"] == "high"


def test_openai_brand_reference_role_adds_logo_preservation_instruction(tmp_path, fake_openai_module):
    fake_openai_module.images.edit.return_value = _fake_openai_response()
    ref = tmp_path / "logo.png"
    ref.write_bytes(b"fake")
    out = tmp_path / "out.png"

    ok = OpenAIProvider().generate(
        prompt="integrated festival poster",
        output_path=str(out),
        model="gpt-image-2",
        reference_image=str(ref),
        reference_role="brand",
    )

    assert ok is True
    call_kwargs = fake_openai_module.images.edit.call_args.kwargs
    assert "preserve their letterforms" in call_kwargs["prompt"]
    assert call_kwargs["prompt"].endswith("integrated festival poster")


# --- Gemini ---------------------------------------------------------------

def test_gemini_style_references_keep_per_prompt_then_global_order(tmp_path, monkeypatch):
    from lib.providers import gemini as gemini_module
    from lib.providers.gemini import GeminiProvider

    refs = [tmp_path / f"ref-{index}.png" for index in range(3)]
    for ref in refs:
        ref.write_bytes(b"fake")

    class FakePILImage:
        @staticmethod
        def open(path):
            return f"opened:{Path(path).name}"

    monkeypatch.setattr(gemini_module, "PILImage", FakePILImage)

    contents = GeminiProvider()._build_contents(
        prompt="actual prompt",
        reference_image=str(refs[0]),
        reference_images=[str(refs[1]), str(refs[2])],
        reference_role="style",
        composition_references=None,
    )

    assert contents[:3] == ["opened:ref-0.png", "opened:ref-1.png", "opened:ref-2.png"]
    assert contents[-1].endswith("actual prompt")


def test_gemini_brand_references_allow_requested_marks(tmp_path, monkeypatch):
    from lib.providers import gemini as gemini_module
    from lib.providers.gemini import GeminiProvider

    ref = tmp_path / "futureproof-logo.png"
    ref.write_bytes(b"fake")

    class FakePILImage:
        @staticmethod
        def open(path):
            return f"opened:{Path(path).name}"

    monkeypatch.setattr(gemini_module, "PILImage", FakePILImage)

    contents = GeminiProvider()._build_contents(
        prompt="make a brand-bearing festival banner",
        reference_image=str(ref),
        reference_images=None,
        reference_role="brand",
        composition_references=None,
    )

    assert contents[0] == "opened:futureproof-logo.png"
    assert "preserve the referenced mark's letterforms" in contents[-1]
    assert "Do not invent alternate Futureproof or BC+AI marks" in contents[-1]
    assert contents[-1].endswith("make a brand-bearing festival banner")


def test_gemini_generate_image_missing_api_key_returns_false(monkeypatch, tmp_path):
    """Smoke test for the Gemini provider's quick-fail path.

    The full success path requires mocking google.genai's nested client,
    types module, and PIL — too much surface area for a baseline test. The
    no-API-key branch exercises the real code without touching the SDK.
    """
    pytest.importorskip(
        "google.genai",
        reason="google-genai not installed in this environment",
    )
    from lib.providers.gemini import GeminiProvider

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    out = tmp_path / "out.png"

    ok = GeminiProvider().generate(
        prompt="x",
        output_path=str(out),
        model="gemini-2.5-flash-image",
    )

    assert ok is False
    assert not out.exists()
