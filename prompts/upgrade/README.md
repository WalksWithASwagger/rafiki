# The Upgrade — Prompt Library

Prompt library for **The Upgrade** — KK's newsletter and podcast covering AI & society — and the related **The Upgrade AI** training program. Both surfaces share the same `upgrade` visual style: bold transformation, deep purple + bright orange + light blue, human-centered AI as partner.

## What is The Upgrade?

**The Upgrade (Newsletter + Podcast):** independent editorial covering how AI is reshaping work, governance, communities, and everyday life. Practical, human-centered, written for professionals who want to think clearly about AI without hype or doom.

**The Upgrade AI (Training):** the companion training program that teaches an "AI mindset" — using AI as a collaborator and force multiplier.

Both share a single visual identity so issues, episodes, and course materials feel like one connected world.

## Visual System

- **Style flag:** `upgrade`
- **Palette:** Deep Purple (wisdom, transformation), Bright Orange (energy, action), Light Blue (technology, trust), White (clarity)
- **Tone:** Bold and energetic yet welcoming, tech-forward but human-centered
- **Avoid:** robotic AI clichés, dystopian tech, anything cold or alienating

See the full [Upgrade Style Guide](../../styles/upgrade.md) for complete brand guidelines.

## Run the whole folder

```bash
python generate.py -f prompts/upgrade/newsletter-heroes.md   -d output/upgrade-newsletter --style upgrade -m gpt-image-2 -w 2
python generate.py -f prompts/upgrade/social-tiles.md        -d output/upgrade-social    --style upgrade -m gpt-image-2 -w 2
python generate.py -f prompts/upgrade/podcast-thumbnails.md  -d output/upgrade-podcast   --style upgrade -m gpt-image-2 -w 2
python generate.py -f prompts/upgrade/training-marketing.md  -d output/upgrade-training  --style upgrade -m gpt-image-2 -w 2
```

## Image Index

| File | Surface | Aspect | Count | Best for |
|------|---------|--------|-------|----------|
| [`newsletter-heroes.md`](./newsletter-heroes.md) | Newsletter | 16:9 | 8 | Weekly issue cover art, themed by editorial beat |
| [`social-tiles.md`](./social-tiles.md) | Social | 1:1 | 6 | Instagram, LinkedIn, X — quote cards, summaries, announcements |
| [`podcast-thumbnails.md`](./podcast-thumbnails.md) | Podcast | 1:1 | 4 | Episode art for guest, solo, series-opener, live formats |
| [`training-marketing.md`](./training-marketing.md) | Training | varies | — | Course headers, skill diagrams, program marketing |

**Total reusable prompts: 18 (newsletter + social + podcast)** plus the existing training-marketing library.

## Best-for use cases

- **Newsletter heroes** — top-of-issue art that signals the editorial beat (policy, tools, human stories, etc.) without tying art to a specific article. Reusable across issues sharing a theme.
- **Social tiles** — square assets for promoting issues, episodes, quotes, and guests on Instagram/LinkedIn/X. Some are designed as backdrops for overlaid text.
- **Podcast thumbnails** — square art for episode covers in podcast apps. Differentiated by format (guest interview, solo, series-opener, live).
- **Training marketing** — course landing pages, module headers, program promo (existing library).

## Writing more Upgrade prompts

The `upgrade` style suffix handles palette, energy, and tone automatically. Prompts should describe:

- **What to show** — the metaphor, the people, the focal object
- **Composition** — focal point, layered depth, where text could overlay
- **Mood** — empowering, curious, urgent, contemplative — but never cold or dystopian

Trust the style for color and typography energy. Write for the editorial beat, not for one specific article — these are reusable assets.

## Comparison with other styles

- **vs. `kk`** — Upgrade is energetic and transformation-focused; kk is polished editorial dark-mode.
- **vs. `bcai`** — Upgrade centers individual transformation; bcai centers community/ecosystem networks.
- **vs. `hopecode`** — Upgrade is bold and accessible; hopecode is anti-corporate and radical.

---

**Remember:** The Upgrade isn't selling hype — it's offering clear-eyed transformation. Every visual should make a reader lean in and say "tell me more."
