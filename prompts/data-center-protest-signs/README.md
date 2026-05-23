# Data Center Protest Signs

DIY-to-designed protest-sign artwork for a Vancouver data-center protest. The whole set runs on
one idea: **both hands full** — signs that refuse to pick a side, holding love for the technology
and clear-eyed critique of its cost in the same breath. Same boat, same storm.

Companion blog post: `notion-local/kk-ai-ecosystem/content/articles/kris-krug-thought-leadership/25-data-center-protest-signs/`

## The arc

We iterated through several directions before the look locked in:

1. **Handwritten cardboard** (`image-prompts.md`) — photos of marker-on-cardboard signs.
2. **Flat punk** (`image-prompts-flat-punk*.md`) — full-bleed xerox-grain bootleg-flyer artwork.
3. **Future punk** (`image-prompts-future-punk*.md`, `round2/3/4`) — blocky, colorful, glitchy posters; this is where the energy was.
4. **Round 5 constructivist** — a wrong turn (art-history pastiche); retired.
5. **Signature styles** (`image-prompts-signature*.md`) — the keeper direction, codified (below).

Voice evolved too: the strongest copy is weird/witty/deadpan and *tender toward the monster*
("Who's a thirsty little data center?", "Unplug it gently", "Give the GPUs a nap") — never preachy
hope-manifesto, never doom.

## The fix: codified signature styles

The recurring failure was **style drift** — re-describing the aesthetic every round and wandering
off. The fix: KK's emergent looks are now **named presets** in `../../styles/styles.yaml`. Rafiki
appends a preset's `suffix` to every prompt verbatim, so the look is deterministic and reusable —
prompts can stay minimal (exact text only) and the preset carries palette/type/texture/layout.

| Preset | Look |
|---|---|
| `kk-blocks` | Megacolor block-stack — neon color-panel rows, each word its own clashing color, halftone + chromatic glitch |
| `kk-cmyk` | CMYK slab-glitch — process Y/C/M + black, fat condensed slab caps, halftone + RGB offset |
| `kk-glitch` | Datamosh hard-glitch — pixel-sort, RGB split, scanlines, cyan/magenta/black/white |
| `kk-acid` | Acid-riso distress — hot orange/red/yellow tritone, gritty riso grain, sun-faded gig-poster |

Invoke with `style="kk-glitch"` (etc.) on `rafiki_generate` / `rafiki_batch`, or `--style kk-glitch` on the CLI.

## Signature-style image set

10 strongest lines + the other 12 favorite lines, each run through all 4 presets.

| Folder | Lines | Model | Count |
|---|---|---|---|
| `images-sig-blocks-gpt` / `-cmyk-` / `-glitch-` / `-acid-gpt` | first 10 | GPT-image | 10 each |
| `images-sig-blocks-rest-pro` / `-cmyk-` / `-glitch-` / `-acid-rest-pro` | other 12 | Gemini Pro | 12 each |

**Why two models:** OpenAI hit a `billing_hard_limit_reached` cap partway through, so the first 10
lines are GPT-image and the remaining 12 are Gemini Pro (the `kk-*` presets are model-agnostic). To
make the set uniform once the cap is raised, re-run the rest on GPT:

```
rafiki_batch(
  prompt_file="image-prompts-signature-rest.md",
  output_dir="images-sig-glitch-rest-gpt",   # one per style
  model="gpt", aspect_ratio="9:16", style="kk-glitch", workers=4)
```

(Earlier rounds — flat-punk, future-punk, round2–5 — remain in their own `images-*` folders.)

## Browse everything

Open **`ALL-SIGNS-viewer.html`** — a single gallery of all renders with click-to-zoom lightbox,
arrow-key nav, and filter chips (★ Signature → Block-Stack / CMYK / Glitch / Acid; plus earlier
rounds). Regenerate it with `/tmp/build_viewer.py` after new runs.

## Master archive + registry

This project is wired into Rafiki's global archive. The 8 signature-style folders are registered as
external projects in `../../config/extra-outputs.local.json`, so they flow into:

- **Asset registry** (`data/asset-registry.json` / `.csv`) — searchable index with full metadata
  (title, caption, `kk-*` style, model, run id, path). Rebuild: `rafiki_run(["registry","index"])`;
  search: `rafiki_registry_search("thirsty")`; export: `rafiki_registry_export(format="csv")`.
- **Master library** (`output/library.html`) — every Rafiki image across all projects on one page.
  Rebuild: `rafiki_run(["library"])`. (Currently 764 images / 68 projects, ours included.)

**Important:** external projects live outside `output/`, so the master library can't display their
images until they're symlinked in. After editing `extra-outputs.local.json`, run
`rafiki_run(["link-projects"])` once (creates `output/dc-signs-* → prompts/...` symlinks), or the
thumbnails show as broken placeholders. Then `registry index` and `library` to refresh both.

## Favorites

KK's hand-picked finals live in `/Users/kk/Pictures/protest/`.

## Notes / next steps

- GPT re-run of the rest-12 once the OpenAI billing cap is raised (command above).
- Optional: publish the companion blog post to KrisKrug.co (needs images uploaded to media first).
- Direction + voice are recorded in the project memory (`kk-protest-poster-styles`).
