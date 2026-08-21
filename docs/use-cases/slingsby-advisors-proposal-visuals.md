# Slingsby Advisors Proposal Visuals

Prep packet for generating Tanya Slingsby into a family-office proposal in
her visual language. This document is the public-safe work plan. Source
photos, the unpublished proposal, likeness datasets, and the working prompt
pack stay local and gitignored.

Related:

- [Keynote visual workflow](keynote-visual-workflow.md) — the same artifact
  chain: notes → reference kit → prompt pack → review gate → export
- [Prompt and media release policy](../PROMPT-MEDIA-POLICY.md)
- [Personal media suite](../PERSONAL-MEDIA-SUITE.md) — subjects, LoRA jobs,
  private studio roots
- [Model policy](../MODEL-POLICY.md)
- [Floyo / FLUX LoRA stills](../FLOYO.md)

## Status

**Blocked on source materials.** Pipeline research and the prompting system
are ready. No likeness dataset, mood board, or proposal shot list is in this
checkout. Do not scrape public photos. Do not train. Do not generate.

## Goal

Produce a reviewed set of proposal-ready images of Tanya that look like her,
in a locked visual register that matches her practice and the family-office
document, not a generic wealth-management stock look.

The operator asked for:

1. a likeness LoRA (or equivalent) of Tanya
2. a style LoRA or style reference for "her style"
3. a prompting system that can take the proposal and generate the needed shots
4. the generations themselves once materials arrive

## Why this is two problems, not one LoRA

"Photos of her, not just of her, but in her style" splits into three
independent controls. Mixing them into one training set is how likeness
collapses into costume, or style collapses into a single pose.

| Control | What it locks | Rafiki primitive |
|---|---|---|
| Likeness | Face, hair, age, body, presence | Subject LoRA **or** Gemini reference images |
| Style language | Palette, surface, geometry, atmosphere | Style pack + style refs; style LoRA only if needed |
| Shot job | What the image must do in the proposal | Markdown prompt pack |

Train likeness and style separately. Compose them at generation time.

## Public research (no private archive)

Public sources only. Used to hypothesize style and naming, not to build a
training set.

| Source | What it establishes |
|---|---|
| [tanyaslingsby.com](https://www.tanyaslingsby.com/) | Artist site. Commission process called **Haute Peinture** ("The Completion of Space"). Studio at 1000 Parker Street, Vancouver. Eastside Culture Crawl. |
| [Artist statement](https://tanyaslingsby.com/artist.html) | Abstract painter. Colour, form, line, surface. Arcs, ellipses, iconic forms. Chromatic purity. Pigment-emulsion / resin / hand-sanded titanium-white layers. Meridians series: bold lines, flat jewel tones. Titles from Sanskrit, Latin, Arabic. "Colour as Form." Light as colour. |
| CreativeMornings | Lists her as CEO of **Slingsby Legacy Advisors Inc.**, Vancouver. |
| LinkedIn / HFF | Senior Advisor (formerly COO in older copy) at the Herrendorf Family Foundation. Philanthropy, family-office governance, legacy, wealth + social impact. MA Aesthetics / Art History (Sussex); BA Fine Art / Art History (UVic). Salt Spring Island upbringing. |
| User brief | Friend of Tanya. She runs **Slingsby Advisors**, described as her family fund transition office, and is assembling a large proposal that needs photos of her in her style. |

**Naming to confirm:** public legal name appears to be Slingsby Legacy
Advisors Inc. The operator said Slingsby Advisors / family fund transition
office. Do not bake a wordmark into generated images until the proposal
letterhead is confirmed.

**Do not use public web photos as training data.** Those images are not an
authorized likeness set, often have bad crops and watermarks, and would
violate the media policy. Tanya (via Kris) supplies the set.

## What Rafiki already has

No new product work is required to start. The job uses existing primitives.

### Fast generation (no train)

- Default model: `gemini-2.5-flash-image` ([MODEL-POLICY.md](../MODEL-POLICY.md))
- `--reference-image` / `--reference-images` / `--global-reference-images` for
  likeness and style plates
- `--style` suffix from `styles/styles.yaml`, stackable (`a+b`)
- Batch Markdown prompt packs (`lib/prompts.py`)
- Isolated `output/<project>/run-*` + review portal / viewer
- Canva export of approved assets

This is the right first lane. If Gemini plus a tight reference kit can put
Tanya in the required shots, skip training.

### Likeness LoRA (when the fast lane fails)

- `python generate.py train lora --subject <key>` → Replicate
  `ostris/flux-dev-lora-trainer`
- Trigger word from the subject profile, else `SUBJECTKEY`
- Destination `rafiki/<subject>-flux-lora`
- Dataset is a **provider-accessible zip URL**, not a local folder
- Dry-run by default; `--execute` spends
- FLUX-image-LoRA stills then run on Replicate, not Floyo
  ([FLOYO.md](../FLOYO.md): Floyo cannot load FLUX image LoRAs)

### Style without a second LoRA

- Style pack in `styles/styles.yaml` + optional `styles/<name>.md`
- Style-anchor JSON import: `python generate.py style anchors --source ...`
- Painting / mood-board plates as `--global-reference-images`

A style LoRA is a fallback if the pack + refs cannot hold the register across
a large shot list.

### Privacy boundary (non-negotiable)

Rafiki is a public tool repo. Faces, proposals, and working prompt libraries
do not get committed here.

- Local prompt pack: `prompts/` (gitignored)
- Local refs: `assets/` (gitignored)
- Runs: `output/` (gitignored)
- Subject / LoRA version config: `config/keyframes*.json` (gitignored)
- Optional live studio root: alex-samuel, indexed in place
  ([PERSONAL-MEDIA-SUITE.md](../PERSONAL-MEDIA-SUITE.md))

## Recommended architecture

```
proposal + shot list
        │
        ▼
┌───────────────────┐     ┌────────────────────┐
│ Tanya likeness    │     │ Slingsby style     │
│ authorized photos │     │ mood board + art   │
└─────────┬─────────┘     └──────────┬─────────┘
          │                          │
          ▼                          ▼
   Gemini refs  OR              style pack + refs
   subject LoRA                 (style LoRA later)
          │                          │
          └──────────┬───────────────┘
                     ▼
              prompt pack
              (one visual job per image)
                     ▼
              dry-run → generate → review
                     ▼
              approved/ → Canva / deck
```

### Default sequence

1. **Intake** — authorized likeness set, mood board, proposal, consent.
2. **Shot list** — turn the proposal into numbered visual jobs before any
   spend.
3. **Lock three style lanes** from the mood board (see below). The public
   artist language is only a hypothesis until then.
4. **Fast comps** — Gemini + global likeness refs + style refs. No train.
5. **Taste gate** — star / reject / regenerate in the portal.
6. **Train likeness LoRA** only if Gemini cannot hold her face across the
   required poses, wardrobe, and crops.
7. **Train style LoRA** only if the style pack + painting refs drift.
8. **Final batch** on the winning stack. Export approved assets.

Do not start by training two LoRAs. Training is spend, and the shot list
decides whether it is needed.

### Three style lanes (must be chosen, not blended by accident)

The public practice and the user brief suggest three different "her style"
readings. The mood board picks the winner, or names a stack.

1. **Presence** — how Tanya actually looks and dresses in rooms where
   families trust her. Hair, jewelry, posture, wardrobe. This is likeness
   support, not a painting LoRA.
2. **Haute Peinture** — her abstract language: open space, chromatic purity,
   arcs and ellipses, jewel-tone meridians, sanded resin/titanium-white
   surfaces, slow light. Use this when the proposal should feel like her
   studio, not a bank.
3. **Transition-office register** — quiet, exact, intergenerational. Paper,
   margins, stewardship. Not tech-bro, not mystic-woo, not generic UHNW
   marble.

Hard ban until Tanya or Kris override: glowing brains, robots, dashboards,
gold-serif "family office" clichés, invented sacred-geometry cosmograms that
are not her forms, and any nation-specific cultural symbols.

### Draft style suffix (registered, revisable)

`slingsby` is now a live `--style` key. The suffix lives in
`styles/styles.yaml` and the guide in `styles/slingsby.md`. It is a draft
from public artist language. The mood board can still replace it.

Face-free style plates (dry-runnable, no likeness):

`examples/slingsby-advisors-style-plates.md`

If the mood board is photographic and wardrobe-led rather than painterly,
drop the Haute Peinture geometry and write a tighter presence pack instead.
Do not force arcs into a straight headshot.

## Prompting system

Private working file (create locally, never commit):

`prompts/slingsby-advisors-proposal.md`

Use the existing numbered Markdown contract from `lib/prompts.py`:

```markdown
## 1. Hero portrait, three-quarter, quiet light
**For:** Proposal cover / about page
**Aspect Ratio:** 4:5
**Style:** slingsby
**Model:** flash
**Prompt:**
> [subject token] [shot] [wardrobe] [room] [style cues] [hard bans]
```

### Subject token

- Fast lane (Gemini + refs): describe her from the authorized notes, and
  attach 3–6 likeness plates as `--global-reference-images`. Do not invent
  facial details from memory.
- LoRA lane: trigger word `TANYA` (or the locked profile word) **plus** a
  short appearance lock written from the authorized set.

### Shot families (fill from the proposal)

Write one prompt per visual job. Typical proposal set, pending the actual
deck:

| ID | Job | Aspect | Likeness | Style weight |
|---|---|---|---|---|
| 01 | Cover / hero portrait | 4:5 or 16:9 | High | Presence + room |
| 02 | About / bio still | 4:5 | High | Quiet office or studio |
| 03 | Working table / stewardship | 16:9 | Medium | Transition-office |
| 04 | Studio / painter in her language | 4:5 | High | Haute Peinture |
| 05 | Conversation / two-chair counsel | 16:9 | Medium | Presence |
| 06 | Detail / hands, ring, page, pigment | 1:1 | Low | Style-forward |
| 07 | Landscape / Salt Spring or Vancouver light, no face | 16:9 | None | Style only |
| 08 | Abstract plate from her language, no figure | 1:1 | None | Haute Peinture |

The proposal may need fewer than this. Do not generate unused families.

### Prompt skeleton

```
[TOKEN], [age-accurate appearance lock from authorized notes],
[wardrobe from approved kit],
[shot: crop, eyeline, posture],
[room: Parker studio / quiet advisory room / undesignated],
[one style lane, named],
[what the image is for in the proposal],
generous negative space, no readable text,
[hard bans]
```

### Batch commands (after local files exist)

Style plates are already in-repo and dry-run clean (6/6, 2026-08-21):

```bash
python3 generate.py --prompt-file examples/slingsby-advisors-style-plates.md \
  --style slingsby \
  --output-dir output/slingsby-advisors \
  --dry-run --no-viewer
```

Likeness jobs (in-repo template; still needs authorized photos):

```bash
python3 generate.py --prompt-file examples/slingsby-advisors-likeness-jobs.md \
  --style slingsby \
  --reference-role likeness \
  --global-reference-images assets/slingsby/likeness/a.jpg,assets/slingsby/likeness/b.jpg \
  --output-dir output/slingsby-advisors \
  --dry-run --no-viewer
```

`--reference-role likeness` is required. The default `style` role tells Gemini
to treat photos as texture only, which will invent a different woman.
Execute without authorized photos now fails closed; dry-run still works so
the pack can be reviewed.

One-shot local runner (dry-run by default; `--execute` spends):

```bash
bash scripts/slingsby-proposal-generate.sh
bash scripts/slingsby-proposal-generate.sh --execute
```

It reads gitignored `assets/slingsby/style-refs/` and
`assets/slingsby/likeness/`. Style plates run always. Likeness jobs run only
when portraits are present.

Generate only after the dry-run parse looks right and spend is approved:

```bash
varlock run --inject vars -- npx rafiki prompts/slingsby-advisors-proposal.md \
  --style slingsby \
  --global-reference-images assets/slingsby/likeness/a.jpg,assets/slingsby/likeness/b.jpg,assets/slingsby/style-refs/mood-01.jpg \
  --output-dir output/slingsby-advisors
```

If a likeness LoRA is trained:

```bash
python generate.py train lora --subject tanya \
  --input-images-url <provider-accessible-zip-url>

python generate.py keyframes generate --beat 01-hero --num-outputs 4
```

Both commands default to dry-run. Pass `--execute` only after destination,
cost, and consent are explicit.

## Local layout (gitignored)

Create on the operator machine, not in git:

```
assets/slingsby/
  likeness/          # authorized face/body set only
  wardrobe/          # approved clothing / jewelry
  style-refs/        # mood board + painting plates
  proposal-refs/     # layouts, letterhead, existing pages (no secrets)
prompts/slingsby-advisors-proposal.md
output/slingsby-advisors/
```

Caption the likeness set in a local `NOTES.md` next to the photos: date,
hair, glasses, wardrobe, what to avoid. That file stays local.

## Intake — send this next

Nothing below should be committed to Rafiki.

### 1. Consent

- Written OK from Tanya to generate her likeness for this proposal
- Written OK to train a LoRA if the fast lane fails
- Confirmation these images are for the proposal only, or also public use

### 2. Likeness set (for a LoRA, aim for 15–30; for Gemini refs, 6–12 is enough)

- Recent, high-resolution, unfiltered
- Face sharp, not tiny in a group
- Variety: front, 3/4, profile, smile / rest, glasses on/off if she wears them
- A few full- or three-quarter-body shots
- Neutral and "her actual wardrobe" — not one costume repeated
- No other people in frame if possible
- No heavy Instagram filters, no screenshots of screens
- Prefer photos she owns or that she can license to this job

### 3. Style / mood board

- 8–20 images that define "her style" for this proposal
- Separate folders or a labeled board: *paintings I made* vs *rooms I like*
  vs *photos of me I want to look like* vs *proposal pages I like*
- Any "not this" references (generic family-office, mystic, tech)

### 4. The proposal and the needs

- The proposal itself, or the slide/page list
- Which pages need a photo of her vs an abstract plate vs a working scene
- Aspect ratios / bleed / safe type areas
- Firm name to print, if any: Slingsby Advisors vs Slingsby Legacy Advisors
- Existing letterhead, palette, type if already designed
- Deadline and how many options per shot (suggest 4)

### 5. Appearance lock (short written notes beat guessing)

- Current hair
- Glasses?
- Jewelry she always wears
- Wardrobe she wants in the proposal
- Anything she does not want shown

## Non-goals

- Scraping CreativeMornings, LinkedIn, HFF, or Saatchi for training photos
- Committing faces, the proposal, or the working prompt pack to this repo
- Training two LoRAs before a shot list exists
- Inventing a wordmark or letterhead
- Video, lip-sync, or Floyo unless a later brief asks for motion
- Shipping Tanya's face, the unpublished proposal, or a likeness prompt pack
  in this public repo
- Treating the draft `slingsby` suffix as final before the mood board

## Definition of done

- [x] Draft `slingsby` style is registered and face-free style plates parse
- [ ] Authorized likeness set and mood board are on disk (gitignored)
- [ ] Proposal shot list exists as a local prompt pack
- [ ] Style lane is locked (presence / Haute Peinture / transition-office, or a named stack)
- [ ] Fast-lane comps exist and have been reviewed
- [ ] LoRA training was either skipped with a reason, or trained with consent and a zip that is not in git
- [ ] Final approved images are exported for the proposal
- [ ] Nothing private was committed to Rafiki

## Next operator action

Send the intake packet. First concrete generation step after that is a
dry-run of the local prompt pack, then a small Gemini reference-image comp
set — not a training job.
