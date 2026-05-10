# Futureproof Prompt Packs

Production-oriented prompt packs and reference images for Futureproof Festival visuals.

## Packs

- `production-candidates-2026-05-09.md` — gpt-image-2 hero and section-image candidates for the website.
- `production-candidates-gemini-2026-05-09.md` — Gemini-oriented companion pack for the same website-image directions.
- `logo-variations-2026-05-09.md` — logo and co-brand lockup experiments using the reference board.

## Reference Images

- `reference/futureproof-dot-matrix-style.png` — dot-matrix Futureproof typography style reference.
- `reference/bcai-logo-light-official.png` — official BC+AI ecosystem light lockup reference.
- `reference/futureproof-bcai-logo-reference-board.png` — combined board for logo and co-brand experiments.

## Example Commands

```bash
python3 generate.py \
  -f prompts/futureproof/production-candidates-2026-05-09.md \
  -d output/futureproof/production-gpt \
  --global-reference-images prompts/futureproof/reference/futureproof-dot-matrix-style.png \
  --reference-role style \
  --workers 3
```

```bash
python3 generate.py \
  -f prompts/futureproof/production-candidates-gemini-2026-05-09.md \
  -d output/futureproof/production-gemini \
  -m pro \
  --global-reference-images prompts/futureproof/reference/futureproof-dot-matrix-style.png \
  --reference-role style \
  --workers 3
```

```bash
python3 generate.py \
  -f prompts/futureproof/logo-variations-2026-05-09.md \
  -d output/futureproof/logo-variations \
  -m gpt \
  --style futureproof-mythic \
  --global-reference-images prompts/futureproof/reference/futureproof-bcai-logo-reference-board.png \
  --reference-role brand \
  --workers 2
```

Use `brand` when the reference image contains marks or lockups that the prompt explicitly asks the model to preserve. Use `style` when the reference should only inform texture, palette, composition, or atmosphere.
