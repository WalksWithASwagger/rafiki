"""Tests for lib.social — LLM social-post expansion.

All OpenAI calls are mocked. No live API requests.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from lib import social


def _make_run(tmp_path: Path, n_items: int = 3) -> Path:
    """Create a minimal output/<project>/run-*/run.json layout for tests."""
    project_dir = tmp_path / "fake-project"
    run_dir = project_dir / "run-20260101-000000"
    run_dir.mkdir(parents=True)

    images = [
        {
            "name": f"Item {i}",
            "prompt": f"A test prompt for item {i}",
            "file": f"{i:02d}-item-{i}.png",
            "ok": True,
        }
        for i in range(1, n_items + 1)
    ]
    (run_dir / "run.json").write_text(
        json.dumps({"images": images, "model": "test", "timestamp": "2026-01-01"}),
        encoding="utf-8",
    )
    return project_dir


def _mock_openai_response(payload: dict) -> SimpleNamespace:
    """Build a fake chat.completions.create() response."""
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )


def _patch_openai(monkeypatch, response_payload: dict | list[dict]) -> MagicMock:
    """Patch lib.social.OpenAI to return a mock client.

    response_payload may be a dict (same response for every call) or a list
    of dicts (one per sequential call).
    """
    if isinstance(response_payload, dict):
        side_effect = lambda **kw: _mock_openai_response(response_payload)  # noqa: E731
    else:
        responses = [_mock_openai_response(p) for p in response_payload]
        side_effect = responses

    create = MagicMock(side_effect=side_effect)
    client = MagicMock()
    client.chat.completions.create = create

    fake_openai_cls = MagicMock(return_value=client)
    monkeypatch.setattr("lib.social.OpenAI", fake_openai_cls, raising=False)
    # Ensure the lazy `from openai import OpenAI` inside expand() picks up the patch.
    import openai
    monkeypatch.setattr(openai, "OpenAI", fake_openai_cls)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    return create


# ──────────────────────────────────────────────────────────────────────────────


def test_expand_calls_openai_per_item(tmp_path, monkeypatch):
    project_dir = _make_run(tmp_path, n_items=3)
    payload = {"linkedin": "li", "x": "xx", "instagram": "ig"}
    create = _patch_openai(monkeypatch, payload)

    social.expand(str(project_dir))

    assert create.call_count == 3


def test_expand_writes_social_posts_json(tmp_path, monkeypatch):
    project_dir = _make_run(tmp_path, n_items=2)
    payload = {"linkedin": "LI body", "x": "X body", "instagram": "IG body"}
    _patch_openai(monkeypatch, payload)

    result = social.expand(str(project_dir))

    out_path = project_dir / "run-20260101-000000" / "social-posts.json"
    assert out_path.exists()
    on_disk = json.loads(out_path.read_text(encoding="utf-8"))
    assert on_disk == result
    assert set(on_disk.keys()) == {"01-item-1", "02-item-2"}
    first = on_disk["01-item-1"]
    assert first["title"] == "Item 1"
    assert first["caption"] == "A test prompt for item 1"
    assert first["platforms"] == payload


def test_expand_respects_platform_filter(tmp_path, monkeypatch):
    project_dir = _make_run(tmp_path, n_items=1)
    payload = {"linkedin": "li", "x": "xx", "instagram": "ig"}
    _patch_openai(monkeypatch, payload)

    result = social.expand(str(project_dir), platforms=["linkedin", "x"])

    item = next(iter(result.values()))
    assert set(item["platforms"].keys()) == {"linkedin", "x"}
    assert "instagram" not in item["platforms"]


def test_dry_run_does_not_call_openai(tmp_path, monkeypatch):
    project_dir = _make_run(tmp_path, n_items=2)
    create = _patch_openai(monkeypatch, {"linkedin": "x"})

    result = social.expand(str(project_dir), dry_run=True)

    assert create.call_count == 0
    out_path = project_dir / "run-20260101-000000" / "social-posts.json"
    assert out_path.exists()
    assert len(result) == 2
    for entry in result.values():
        assert "dry-run" in entry["platforms"]["linkedin"]


def test_missing_api_key_raises_clear_error(tmp_path, monkeypatch):
    project_dir = _make_run(tmp_path, n_items=1)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        social.expand(str(project_dir))


def test_invalid_json_response_logged_and_skipped(tmp_path, monkeypatch, capsys):
    project_dir = _make_run(tmp_path, n_items=2)

    # First item: malformed JSON. Second item: valid.
    bad = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="not json{"))]
    )
    good = _mock_openai_response({"linkedin": "ok", "x": "ok", "instagram": "ok"})
    create = MagicMock(side_effect=[bad, good])
    client = MagicMock()
    client.chat.completions.create = create
    fake_cls = MagicMock(return_value=client)
    monkeypatch.setattr("lib.social.OpenAI", fake_cls, raising=False)
    import openai
    monkeypatch.setattr(openai, "OpenAI", fake_cls)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    result = social.expand(str(project_dir))

    captured = capsys.readouterr()
    assert "skip 01-item-1" in captured.err
    assert "01-item-1" not in result  # bad item omitted
    assert "02-item-2" in result      # good item kept
    assert create.call_count == 2     # batch did not crash mid-loop
