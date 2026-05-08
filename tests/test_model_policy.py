"""Regression checks for the public default-model policy."""

from __future__ import annotations

import inspect

import mcp_server
from lib import server
from lib.models import DEFAULT_IMAGE_MODEL, resolve_model


def test_default_image_model_policy_is_gemini_flash() -> None:
    assert DEFAULT_IMAGE_MODEL == "gemini-2.5-flash-image"
    assert server.DEFAULT_MODEL == DEFAULT_IMAGE_MODEL
    assert resolve_model("flash") == DEFAULT_IMAGE_MODEL
    assert resolve_model("gemini") == DEFAULT_IMAGE_MODEL


def test_mcp_generation_defaults_match_policy() -> None:
    assert inspect.signature(mcp_server.rafiki_generate).parameters["model"].default == DEFAULT_IMAGE_MODEL
    assert inspect.signature(mcp_server.rafiki_batch).parameters["model"].default == DEFAULT_IMAGE_MODEL
