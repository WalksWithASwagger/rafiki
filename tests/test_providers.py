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


# --- Gemini ---------------------------------------------------------------

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
