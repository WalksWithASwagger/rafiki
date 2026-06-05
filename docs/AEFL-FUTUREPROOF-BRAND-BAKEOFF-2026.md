# AEFL Futureproof Brand Bakeoff 2026

Purpose: style exploration for AI Ethical Futures Lab Luma and WordPress covers using the Futureproof + BC+AI poster system. This is a review setup only; do not update Luma until a direction is approved.

## Prompt Packs

- `prompts/bcai/aefl-futureproof-brand-bakeoff-2026.md`
- `prompts/bcai/aefl-futureproof-brand-bakeoff-2026-clean-pass.md`

Both packs use:

- `--style futureproof-mythic+bcai-ecosystem`
- `--reference-role brand`
- 1:1 square output
- the supplied Futureproof AEFL screenshots
- the official BC+AI logo reference assets

## Local Output

Generated images and review pages are under ignored `output/` paths:

- Project: `output/aefl-futureproof-brand-bakeoff-2026/`
- Combined review page: `output/aefl-futureproof-brand-bakeoff-2026/comparison-review.html`
- Local review URL: `http://127.0.0.1:7433/output/aefl-futureproof-brand-bakeoff-2026/comparison-review.html`

## Runs

Round 1, original Futureproof mythic pass:

- `run-20260604-142858` - `gpt-image-2`, 10 images
- `run-20260604-143957` - `gemini-3-pro-image-preview`, 10 images

Round 2, cleaner pass:

- `run-20260604-153832` - `gpt-image-2`, 10 images
- `run-20260604-155516` - `gemini-3-pro-image-preview`, 10 images

## Review Criteria

Reject candidates with:

- malformed `AI ETHICAL FUTURES LAB` text
- malformed `BC+AI ecosystem` logo text
- fake sponsor marks, venue claims, URLs, or extra readable words
- generic AI stock styling
- circuit-board traces or PCB motifs
- over-busy dot-and-line networks

## Verification

Last verified on 2026-06-05:

- Rafiki all-runs viewer rebuilt with 4 runs and 40/40 images on disk.
- Combined review page returned `200 text/html`.
- Rafiki rating API returned `200 application/json`.
- In-app browser loaded 40 cards, 40 images, 20 Round 1 refs, and 20 Round 2 refs with no failed image refs.
