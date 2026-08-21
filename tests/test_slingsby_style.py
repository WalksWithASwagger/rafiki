"""Slingsby style pack and public style-plate prompt fixture."""

from pathlib import Path

from lib.core import generate_image, likeness_requires_references
from lib.prompts import parse_image_prompts_md
from lib.styles import load_styles, resolve_style_suffix

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLE_PLATES = REPO_ROOT / "examples" / "slingsby-advisors-style-plates.md"
LIKENESS_JOBS = REPO_ROOT / "examples" / "slingsby-advisors-likeness-jobs.md"


def test_slingsby_style_is_registered() -> None:
    styles = load_styles()
    assert "slingsby" in styles
    suffix = resolve_style_suffix("slingsby", styles)
    assert "Haute Peinture" in suffix
    assert "Meridians" in suffix
    assert "HARD BANS" in suffix


def test_slingsby_style_plates_parse_without_likeness() -> None:
    prompts = parse_image_prompts_md(STYLE_PLATES)
    assert len(prompts) == 8
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


def test_slingsby_likeness_jobs_require_attached_refs_and_do_not_invent_appearance() -> None:
    prompts = parse_image_prompts_md(LIKENESS_JOBS)
    assert len(prompts) == 6
    invented = ("blonde", "brunette", "glasses", "bob", "red hair", "blue eyes")
    for item in prompts:
        assert item["style"] == "slingsby"
        lowered = item["prompt"].lower()
        assert "attached authorized reference" in lowered
        assert "do not invent" in lowered
        for token in invented:
            assert token not in lowered, f"{item['name']} invents {token!r}"


def test_likeness_role_requires_authorized_references(tmp_path) -> None:
    assert likeness_requires_references("style") is None
    assert (
        likeness_requires_references("likeness", reference_image=str(tmp_path / "a.jpg"))
        is None
    )
    assert likeness_requires_references("likeness") is not None
    ok = generate_image(
        prompt="exact likeness",
        output_path=str(tmp_path / "out.png"),
        reference_role="likeness",
        dry_run=False,
    )
    assert ok is False
    ok_dry = generate_image(
        prompt="exact likeness",
        output_path=str(tmp_path / "out.png"),
        reference_role="likeness",
        dry_run=True,
    )
    assert ok_dry is True
