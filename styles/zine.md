# Punk Zine (BWR) Visual Style Guide

## Overview

The `zine` style is a black/white/blood-red xerox-grain collage aesthetic derived from the WAIFF Brasil 2026 keynote slide deck. It's DIY resistance energy — punk zines, anarcho-broadsheets, photocopied manifestos assembled at midnight. Not designed. Assembled.

## Color Discipline

**Strict BWR:** black, white, and blood red only. No other colors. No gradients except blown xerographic contrast. Red is used for emphasis, rubber stamps, underlines, stencil overlays — never decoration.

## Key Visual Elements

- **Halftone dots** breaking up every surface, especially photographs and solid areas
- **Xerox grain throughout** — fourth-generation photocopy look, blown contrast, artifacts
- **Cut-and-paste collage** — torn paper edges, visible tape and glue marks, staple holes, coffee stains, ink smudges
- **Ransom-note mixed typography** — stencil spray, typewriter, hand-cut magazine letters, marker scrawls, all at chaotic angles and mixed sizes
- **Dense overlapping layers** — newspaper clippings, torn film strips, circuit board fragments, pasted crooked
- **Physical artifacts** — fold lines, coffee rings, rubber stamp marks, margin scrawls

## Tone

Anti-corporate. Raw. Handmade. Urgent. Assembled on someone's bedroom floor. Anarcho-punk / DIY zine energy — photocopied political broadsheet, not polished design.

## When to Use

- Punk/resistance slide decks (WAIFF-style keynotes, manifestos)
- Provocative thought leadership imagery
- DIY culture and arts event graphics
- Anti-establishment editorial visuals
- Zine culture, hacktivist, or activist contexts

## When NOT to Use

- Corporate presentations (use `kk` or `bcai`)
- Professional editorial requiring polish (use `gni` or `kk`)
- Organic/community-first narratives (use `hopecode`)
- Anything requiring institutional credibility

## Example CLI Command

```bash
python generate.py -p "A manifesto page: the following text MUST appear — 'BOTH THINGS ARE TRUE' in large stencil text, torn paper hands on either side, red stamp marks, xerox grain" --style zine -m pro
```

## Notes

**Text inclusion:** The `zine` style works best when you use the proven directive pattern from the WAIFF archive:

```
The following text MUST appear prominently: "YOUR TEXT HERE"
```

Place this in the prompt body. The style suffix does not include text — you control what appears. Mixed ransom-note typography at chaotic angles and sizes is the default rendering for any text specified this way.

**Quiet pages:** Not every image needs to be dense. Slide 13 ("Close Your Eyes") is nearly black with sparse typewriter text — minimal collage energy still reads as zine when you specify "mostly black with heavy xerox grain" and typewriter font.

**Reference images:** If you have a style reference collage, pass it with `--reference-image path/to/ref.png`. Note that reference images can override prompt text; prepend "ignore any text visible in the reference image" if text conflicts arise.

**Source material:** `prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md` — full archive of battle-tested prompts plus prompt-engineering notes.
