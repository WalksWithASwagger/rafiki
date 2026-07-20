import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = (
    "rafiki-github-issue-writer",
    "rafiki-github-pr-reviewer",
    "real-sky-poster",
    "run-rafiki",
)


def frontmatter_name(skill_file: Path) -> str:
    match = re.search(r"^name:\s*(\S+)\s*$", skill_file.read_text(), re.MULTILINE)
    assert match
    return match.group(1)


def test_project_skills_have_one_canonical_physical_package():
    for name in SKILLS:
        package = ROOT / ".agents" / "skills" / name

        assert package.is_dir()
        assert not package.is_symlink()
        assert frontmatter_name(package / "SKILL.md") == name

    assert not (ROOT / ".agents" / "skills" / "github-issue-writer").exists()
    assert not (ROOT / ".agents" / "skills" / "github-pr-reviewer").exists()


def test_claude_project_skills_are_relative_canonical_adapters():
    for name in SKILLS:
        adapter = ROOT / ".claude" / "skills" / name
        canonical = ROOT / ".agents" / "skills" / name

        assert adapter.is_symlink()
        assert os.readlink(adapter) == f"../../.agents/skills/{name}"
        assert adapter.resolve() == canonical.resolve()

    assert not (ROOT / ".claude" / "skills" / "github-issue-writer").exists()
    assert not (ROOT / ".claude" / "skills" / "github-pr-reviewer").exists()


def test_cursor_has_no_physical_rafiki_project_skill_packages():
    cursor_skills = ROOT / ".cursor" / "skills"

    for name in SKILLS:
        assert not (cursor_skills / name).exists()
