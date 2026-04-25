# KK Prompt Library

Prompt files for Kris Krüg's personal brand, writing, and editorial work.

Default style for this library: `kk` (dark editorial, teal/purple). Override per-prompt with `**Style:**` or pass `--style hopecode` for the organic/mycelial look.

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
