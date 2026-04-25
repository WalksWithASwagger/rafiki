"""Style loading and composition for Rafiki."""

from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

STYLES_CONFIG_PATH = Path(__file__).parent.parent / "styles" / "styles.yaml"


def load_styles() -> dict:
    """Load style definitions from styles/styles.yaml."""
    if yaml is None:
        raise ImportError("PyYAML not installed. Run: pip install pyyaml")
    if STYLES_CONFIG_PATH.exists():
        with open(STYLES_CONFIG_PATH) as f:
            config = yaml.safe_load(f)
            return config.get("styles", {})
    return {}


def get_default_style() -> str:
    """Return the name of the style marked default: true in config."""
    styles = load_styles()
    for name, cfg in styles.items():
        if cfg.get("default", False):
            return name
    return "kk"


def resolve_style_suffix(style_spec: str | None, styles: dict | None = None) -> str:
    """Return the prompt suffix for a style spec.

    Supports:
    - None or "none"  → empty string (no style)
    - "kk"            → single style suffix
    - "kk+bcai"       → stacked suffixes, joined by double newline
    """
    if not style_spec or style_spec == "none":
        return ""
    if styles is None:
        styles = load_styles()
    parts = [s.strip() for s in style_spec.split("+") if s.strip()]
    suffixes = []
    for part in parts:
        if part in styles:
            s = styles[part].get("suffix", "")
            if s:
                suffixes.append(s.strip())
        else:
            import sys
            print(f"Warning: Unknown style '{part}' — skipping", file=sys.stderr)
    return "\n\n".join(suffixes)
