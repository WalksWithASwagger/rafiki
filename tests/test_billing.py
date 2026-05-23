from __future__ import annotations

import json
from pathlib import Path

from lib.billing import (
    append_billing_entries,
    import_billing_file,
    load_billing_imports,
    summarize_billing_imports,
)


def test_import_billing_csv_normalizes_and_deduplicates(tmp_path: Path):
    source = tmp_path / "openai.csv"
    source.write_text(
        "Date,Provider,Model,Amount,Currency,Images,Description\n"
        "2026-05-18,OpenAI,gpt-image-2,$12.34,USD,4,May export\n",
        encoding="utf-8",
    )
    state = tmp_path / "billing-imports.json"

    first = import_billing_file(source, state_path=state)
    second = import_billing_file(source, state_path=state)

    assert first["imported"] == 1
    assert second["duplicates"] == 1
    data = load_billing_imports(state)
    assert data["imports"][0]["provider"] == "OpenAI"
    assert data["imports"][0]["amount"] == 12.34
    assert data["imports"][0]["image_count"] == 4


def test_import_billing_json_accepts_items_list(tmp_path: Path):
    source = tmp_path / "gemini.json"
    source.write_text(
        json.dumps({
            "items": [
                {
                    "date": "2026-05-18",
                    "service": "Gemini",
                    "product": "gemini-2.5-flash-image",
                    "total_cost": 1.56,
                    "currency": "USD",
                }
            ]
        }),
        encoding="utf-8",
    )
    state = tmp_path / "billing-imports.json"

    result = import_billing_file(source, state_path=state, label="Gemini May")
    summary = summarize_billing_imports(state)

    assert result["imported"] == 1
    assert summary["entries"] == 1
    assert summary["amount"] == 1.56
    assert summary["by_model"] == [{"model": "gemini-2.5-flash-image", "amount": 1.56, "entries": 1}]


def test_append_billing_entries_skips_rows_without_amount(tmp_path: Path):
    state = tmp_path / "billing-imports.json"

    result = append_billing_entries(
        state,
        [
            {"provider": "OpenAI", "amount": "nope"},
            {"provider": "OpenAI", "amount": "3.21"},
        ],
    )

    assert result["imported"] == 1
    assert result["skipped"] == 1
    assert summarize_billing_imports(state)["amount"] == 3.21
