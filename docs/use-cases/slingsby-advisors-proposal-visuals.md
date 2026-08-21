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

**Handoff — stills not generated.** Pipeline, style pack, prompt packs,
authorized likeness (10 Gemini / 22 LoRA), written consent, and the local
runner are ready. **0 PNGs** in `output/slingsby-advisors/`. Blocked on a
stills key: `GOOGLE_API_KEY` (preferred) or `OPENAI_API_KEY` (`gpt-image-2`
fallback). Floyo is video-only. This cloud VM does not have Mac Varlock
value files (`~/.agents/env/values/`). Full mood-board pages stay archived;
style refs default to face-free crops; likeness refs default to
nametag-cropped face plates.

```bash
python3 scripts/slingsby-proposal-prep-refs.py
```

That photographic register — through-glass, golden hour, candid counsel —
is the locked `--style slingsby` language. Style plates can generate the
moment `GOOGLE_API_KEY` is set:

```bash
bash scripts/slingsby-proposal-generate.sh --status
bash scripts/slingsby-proposal-generate.sh --execute --style-only
```

Likeness jobs stay fail-closed until authorized portraits and written
consent are on disk. Do not scrape public photos of Tanya. Do not train
two LoRAs first.

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

### Locked style suffix

`slingsby` is a live `--style` key. The suffix lives in
`styles/styles.yaml` and the guide in `styles/slingsby.md`. It is locked
to the operator mood board (candid high-end advisory photography), not
to Tanya's public painting series. Haute Peinture remains useful as art
on a wall only if a later plate asks for it.

Face-free style plates (dry-runnable, no likeness):

`examples/slingsby-advisors-style-plates.md`

If the mood board is photographic and wardrobe-led rather than painterly,
drop the Haute Peinture geometry and write a tighter presence pack instead.
Do not force arcs into a straight headshot.

## Prompting system

Private working file (create locally, never commit):

`prompts/slingsby-advisors-proposal.md`

The runner prefers that file for likeness jobs when it exists. Fill it from
`assets/slingsby/NOTES.md` (hair, jewelry, age, bans). Public-safe fallback:
`examples/slingsby-advisors-likeness-jobs.md`. Template:
`examples/slingsby-advisors-intake/PROPOSAL.example.md`.

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

Style plates are already in-repo and dry-run clean (8 plates; last verified 2026-08-21):

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
bash scripts/slingsby-proposal-generate.sh --status
bash scripts/slingsby-proposal-generate.sh
bash scripts/slingsby-proposal-generate.sh --execute --style-only
bash scripts/slingsby-proposal-generate.sh --execute
bash scripts/slingsby-proposal-generate.sh --train-lora-plan
```

If `varlock` is on `PATH`, the runner re-execs through
`varlock run --inject vars` before dotenv. That is how Mac value files in
`~/.agents/env/values/` reach spend. Cloud agents do not have that directory
unless it is copied onto the VM or `GOOGLE_API_KEY` is set on the environment.

It also loads `.env` / `.env.local` the same way `generate.py` does (setdefault,
never prints values). It reads gitignored `assets/slingsby/style-refs/` and
`assets/slingsby/likeness/`. Style plates run always. Likeness jobs run only
when portraits are present, `--reference-role likeness` is set, and
`assets/slingsby/CONSENT.md` (or `SLINGSBY_LIKENESS_CONSENT=1`) exists.

The runner prefers sanitized local dirs when present:

1. `assets/slingsby/style-refs/moodboard/face-free/` (architecture/light crops)
2. else `moodboard/selected/` (full pages — stock faces, archive only)
3. else public painting `_orig` plates

Likeness prefers `assets/slingsby/likeness-clean/` (nametag-cropped) over
the raw `likeness/` album picks. Do not commit any of those sets. After a
spend, `bash scripts/slingsby-proposal-generate.sh --review` rebuilds
`output/slingsby-advisors/viewer.html`.
Intake templates: `examples/slingsby-advisors-intake/`.
Likeness PDF / zip / folder:

```bash
bash scripts/slingsby-proposal-ingest.sh --likeness /path/to/portraits.pdf
```

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
- Treating Tanya's public painting series as the proposal's primary camera
  language after the operator mood board locked a photographic register

## Definition of done

- [x] Draft `slingsby` style is registered and face-free style plates parse
- [x] Public painting refs can be ingested locally (gitignored); runner
      attaches them as style refs when no mood board is present
- [x] Operator mood board ingested locally as page screenshots + tiles
- [x] `--style slingsby` locked to that photographic register
- [x] Likeness job list, consent gate, and LoRA dry-run plan exist
- [x] Authorized likeness set is on disk locally (gitignored; Gemini 10 + LoRA 22)
- [x] Written consent file is present (local `assets/slingsby/CONSENT.md`)
- [x] Face-free style crops and nametag-cropped likeness plates can be built locally
- [ ] `GOOGLE_API_KEY` is available and style plates have been generated
- [x] First-batch shot list exists (`examples/slingsby-advisors-style-plates.md` +
      `examples/slingsby-advisors-likeness-jobs.md`)
- [x] Local appearance-locked pack can live at `prompts/slingsby-advisors-proposal.md`
      (gitignored; runner prefers it)
- [ ] Fast-lane comps exist and have been reviewed
- [ ] LoRA training was either skipped with a reason, or trained with consent and a zip that is not in git
- [ ] Final approved images are exported for the proposal
- [x] Nothing private was committed to Rafiki

## Next agent

Branch: `cursor/slingsby-proposal-visuals-prep-516d`
PR: https://github.com/WalksWithASwagger/rafiki/pull/444
Prior agent: https://cursor.com/agents/bc-01a025f5-ea25-799e-a8e6-59c4337a516d
Environment: https://cursor.com/dashboard/cloud-agents/environments/e/e9a8081b-9d9c-11f1-a7d1-d6b4613131ce
Snapshot of the intake VM (ready): `snapshot-20260821-a42fdc82-2278-4083-977f-bf3a245718c2`

**Do this first**

1. Confirm `assets/slingsby/likeness-clean/` has 10 jpgs and
   `assets/slingsby/CONSENT.md` exists. If not, this is a bare checkout —
   re-ingest the authorized Google Photos album (operator has the share;
   do not scrape LinkedIn/HFF) into `assets/slingsby/album/raw/`, pick
   plates, run `python3 scripts/slingsby-proposal-prep-refs.py`, and copy
   `examples/slingsby-advisors-intake/CONSENT.example.md` to
   `assets/slingsby/CONSENT.md`. Local appearance lock:
   `assets/slingsby/NOTES.md` + `prompts/slingsby-advisors-proposal.md`
   (gitignored).
2. Confirm a stills key with
   `varlock run --inject vars -- python3 -c 'import os; print(bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY")))'`
   Do not `cat` `.env` or `varlock reveal`. Mac
   `~/.agents/env/values/.env.shared.local` is **not** on cloud VMs.
   Save `GOOGLE_API_KEY` (preferred) or `OPENAI_API_KEY` on the
   environment above. Floyo is video-only.
3. Spend:

```bash
bash scripts/slingsby-proposal-generate.sh --status
bash scripts/slingsby-proposal-generate.sh --execute --smoke --style-only
bash scripts/slingsby-proposal-generate.sh --execute --style-only
bash scripts/slingsby-proposal-generate.sh --execute --likeness-only
bash scripts/slingsby-proposal-generate.sh --review
```

**Hard rules**

- `--reference-role likeness` on likeness jobs. Default `style` invents
  another woman.
- Do not attach moodboard pages/selected tiles (stock faces).
- Do not attach the raw 150-photo album (other people).
- Do not train a LoRA first. Replicate zip URL + token only if Gemini/OpenAI
  cannot hold her face.
- Do not invent Tanya's face. Do not generate nametags / Vancouver AI / MAC.
- Confirm "Slingsby Advisors" vs "Slingsby Legacy Advisors Inc." before
  wordmarks.
- CI `test` is red on `main` too (`js-yaml` / `nanoid` frontend audit).
  Do not bump the lockfile on this PR.

`--smoke` spends the first job only. The runner attaches at most six
full-face likeness plates (drops eyes-only 086). It re-execs through
`varlock run --inject vars` when `varlock` is on `PATH`.
