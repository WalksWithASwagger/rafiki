# dontsurveil.me — Bill C-22 Prompts

Image candidates for the four placeholder slots on
[c22.html](https://opencivics-labs.github.io/dontsurveil.me/c22.html), the
opposition page for Canada's proposed Bill C-22 encryption-backdoor
legislation.

## Pack

- `image-prompts.md` — two `zine`-style variations for each of the four
  placeholder slots (paradigm shift, why this is about you, time is running
  out, if this passes). Eight prompts total, all 16:9.

## Aesthetic

The page is minimal black-on-white with red urgency accents. The `zine`
style (black/white/blood-red xerox-grain collage) is the closest direct
match in `styles/styles.yaml`.

## Example Command

```bash
npx rafiki prompts/dontsurveil-c22/image-prompts.md \
  --style zine \
  --output-dir output/dontsurveil-c22
```

Review the contact sheet in the local portal and pick one variation per
slot before exporting.
