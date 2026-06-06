# Comox Valley AI Seasonal Crest v2 Handoff

Date: 2026-06-05

## Context

The first Comox Valley seasonal Luma batch was generated natively, but the prompt language invited poster-style typography: large `CV + AI` blocks, lower-third event text, and detached maker marks. That made the results feel like layover graphics even though Rafiki did not composite anything after generation.

The v2 retry corrects the direction by making each output a complete native crest, badge, patch, or heraldic sticker. The crest is the whole artifact. Dates are allowed only as small integrated crest ribbons.

## Prompt Pack

- Prompt file: `/Users/kk/Code/rafiki/prompts/bcai/comox-valley-luma-seasonal-2026-crest-v2.md`
- Prompt count: 12
- Aspect ratio: `1:1`
- Style: `none`
- Reference role: `brand`
- Reference strategy: crest/badge references only, plus the official BC+AI mark for tiny integrated maker-mark treatment.

## Outputs

- OpenAI `gpt-image-2`
  - Viewer: `/Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-openai/viewer.html`
  - Run: `/Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-openai/run-20260605-182549`
  - Contact sheet: `/Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-openai/contact-sheet.jpg`
  - Result: 12/12 succeeded, 1024x1024

- Gemini Pro `gemini-3-pro-image-preview`
  - Viewer: `/Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-google-pro/viewer.html`
  - Run: `/Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-google-pro/run-20260605-184544`
  - Contact sheet: `/Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-google-pro/contact-sheet.jpg`
  - Result: 12/12 succeeded, 1024x1024

## Review Notes

- v2 is much closer to the requested direction: no lower thirds, no large poster typography, and no detached corner logo boxes in the contact-sheet review.
- OpenAI preserved the detailed old-growth punk-sticker crest feel strongly and produced richer texture.
- Gemini Pro produced simpler, cleaner crest silhouettes with more varied patch/heraldic shapes.
- Native text still needs full-size human review before publishing. Some crest lettering and tiny maker marks may need reruns because model-native text remains the fragile part.

## Next Round

Start from the v2 prompt pack, not the v1 native-branding pack. If tighter publish candidates are needed, rerun only selected months with stricter wording:

- `COMOX VALLEY` on the rim and `AI` only as the central monogram.
- Date ribbon exactly as shown for the month.
- Omit `BC+AI ecosystem` if the model cannot integrate it cleanly.
- No text anywhere outside the crest.
