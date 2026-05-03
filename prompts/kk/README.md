# KK Prompt Library

Prompt files for Kris Krüg's personal brand, writing, and editorial work.

Default style for this library: `kk` (dark editorial, teal/purple). Override per-prompt with `**Style:**` or pass `--style hopecode` for the organic/mycelial look.

## Visual system

**Mixed styles per file** — most prompts declare `**Style:**` inline:

- `kk` (default) — dark editorial, deep dark background `#0f0f1a`, teal `#00c8b4`, purple `#9333ea`, cinematic depth of field. Style guide: [`../../styles/kk.md`](../../styles/kk.md).
- `hopecode` — solarpunk / mycelial, anti-corporate, photocopy grain, bioluminescent glow on key terms (used by `name-the-bias-hopecode.md`). Style guide: [`../../styles/hopecode.md`](../../styles/hopecode.md).
- `none` — for files where prompts carry their own art direction end-to-end (used by `philadelphia-aurora.md` — aurora ribbons, no style suffix).

No single shared reference image; per-file art direction supplies palette and motif.

## Files

| File | Description |
|------|-------------|
| `name-the-bias-hopecode.md` | 6 solarpunk mycelial images for the article "Stop Saying 'Bias.' Name What You're Seeing." |
| `name-the-bias-social-variants.md` | Square + vertical social variants for the Name the Bias series |
| `2026-01-24-what-would-chat-do.md` | Images for the "What Would Chat Do?" article |

## Usage

```bash
# Batch — uses per-prompt aspect ratios automatically
python generate.py -f prompts/kk/name-the-bias-hopecode.md \
  -d output/name-the-bias --style hopecode

# Single alias
python generate.py -p "Your prompt" -m flash --style kk
```

## Prompt format

```markdown
## 1. Image Title

**For:** Article header
**Aspect Ratio:** 16:9
**Style:** hopecode

**Prompt:**
> Multi-line prompt text here.
> Keep going on the next line.
```

Fields `**Aspect Ratio:**`, `**Model:**`, `**Style:**`, and `**Quality:**` are all optional per-prompt overrides of the CLI defaults.
