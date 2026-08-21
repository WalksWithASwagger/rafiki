"""Slingsby style pack and public style-plate prompt fixture."""

from pathlib import Path

from lib.prompts import parse_image_prompts_md
from lib.styles import load_styles, resolve_style_suffix

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLE_PLATES = REPO_ROOT / "examples" / "slingsby-advisors-style-plates.md"


def test_slingsby_style_is_registered() -> None:
    styles = load_styles()
    assert "slingsby" in styles
    suffix = resolve_style_suffix("slingsby", styles)
    assert "Haute Peinture" in suffix
    assert "jewel" in suffix.lower()
    assert "HARD BANS" in suffix


def test_slingsby_style_plates_parse_without_likeness() -> None:
    prompts = parse_image_prompts_md(STYLE_PLATES)
    assert len(prompts) == 6
    banned = ("tanya", "slingsby", "portrait of", "headshot", "likeness")
    for item in prompts:
        assert item["style"] == "slingsby"
        assert item["prompt"]
        lowered = item["prompt"].lower()
        for token in banned:
            assert token not in lowered, f"{item['name']} mentions {token!r}"
        assert any(
            marker in lowered
            for marker in ("no people", "no faces", "no figure", "no figures")
        )
