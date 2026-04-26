# kb-ecosystem-mirror — Prompt Corpus Catalog

**Last updated:** 2026-04-25  
**Total files:** 51 prompt files across 4 major areas  
**Rafiki-ready:** files marked ✓ in Batch-ready column can run today with `python generate.py -f <file>`  

---

## Quality Tiers

| Tier | Meaning | Action |
|------|---------|--------|
| **A** | Full prompts, specific language, strong visual direction | Run now |
| **B** | Prompts exist but use Midjourney flags, fenced code, or wrong header format | Convert to Rafiki format first |
| **C** | Stub scaffolds with TBD prompts | Prompts written — ready to run |

---

## KK Thought-Leadership Articles (`articles/kris-krug-thought-leadership/`)

22 articles, all using `--style kk` (dark editorial, teal/purple). Hero 16:9, sections 1:1.  
Batch output dir: `output/kk-articles`

```bash
# Run all 22 articles in sequence (same output dir = one viewer with all runs)
for f in prompts/kb-ecosystem-mirror/articles/kris-krug-thought-leadership/*/image-prompts.md; do
  python generate.py -f "$f" -d output/kk-articles --style kk -m flash --workers 4
done
```

| File | Title | Prompts | Tier | Batch-ready? |
|------|-------|---------|------|-------------|
| `articles/kris-krug-thought-leadership/01-build-tools-next-job/image-prompts.md` | Build Tools For Your Next Job | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/02-distill-dont-dump/image-prompts.md` | Distill, Don't Dump | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/03-dream-intern/image-prompts.md` | The Dream Intern | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/04-more-you-learn-optimistic/image-prompts.md` | The More You Learn, The More Optimistic | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/05-permission-point/image-prompts.md` | The Permission Point | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/06-systems-over-oneoffs/image-prompts.md` | Systems Over One-Offs | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/07-preparation-over-tools/image-prompts.md` | Preparation Over Tools | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/08-voice-memo-workflow/image-prompts.md` | The Voice Memo Workflow | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/09-two-ais-competing/image-prompts.md` | Two AIs Competing | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/10-regulatory-opportunity/image-prompts.md` | The Regulatory Opportunity | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/11-non-extractive-profit/image-prompts.md` | Non-Extractive Profit | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/12-building-in-public/image-prompts.md` | Building In Public | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/13-margin-shapes-culture/image-prompts.md` | The Margin Shapes The Culture | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/14-decade-trust-building/image-prompts.md` | A Decade of Trust Building | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/15-optionality-over-destination/image-prompts.md` | Optionality Over Destination | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/16-both-hands-full/image-prompts.md` | Both Hands Full | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/17-taste-as-moat/image-prompts.md` | Taste As Moat | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/18-moment-no-permission/image-prompts.md` | The Moment Requires No Permission | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/19-clarity-as-exposure/image-prompts.md` | Clarity As Exposure | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/20-mycorrhizal-network/image-prompts.md` | The Mycorrhizal Network Model | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/21-who-sets-direction/image-prompts.md` | Who Sets Direction | 5 | C→A | ✓ |
| `articles/kris-krug-thought-leadership/your-judgment-is-the-moat/image-prompts.md` | Your Judgment Is The Moat | 5 | C→A | ✓ |

---

## BC + AI Website Articles (`articles/bc-ai-website/`)

| File | Title | Prompts | Tier | Style | Batch-ready? |
|------|-------|---------|------|-------|-------------|
| `articles/bc-ai-website/rap-certification-launch/image-prompts.md` | RAP Certification Launch | 8 | B | upgrade | ✗ — generic prompts, convert format |
| `articles/bc-ai-website/ai-animation-accelerator/image-prompts.md` | AI Animation Accelerator | — | — | — | Check |

---

## Ed-AI Education Meetup (`projects/ed-ai-education-meetup/`)

```bash
# v1 — 12 style variations (already Rafiki-ready, no-style mode)
python generate.py -f prompts/kb-ecosystem-mirror/projects/ed-ai-education-meetup/image-prompts-ed-ai-meetup-12-variations.md \
  -d output/ed-ai --no-style -m flash --workers 4

# v2 hopecode lane (4 prompts, hopecode style)
python generate.py -f prompts/kb-ecosystem-mirror/projects/ed-ai-education-meetup/image-prompts-ed-ai-meetup-v2-hopecode-4.md \
  -d output/ed-ai --style hopecode -m flash --workers 4

# v2 bcai lane (4 prompts)  
python generate.py -f prompts/kb-ecosystem-mirror/projects/ed-ai-education-meetup/image-prompts-ed-ai-meetup-v2-bcai-4.md \
  -d output/ed-ai --style bcai -m flash --workers 4
```

| File | Prompts | Tier | Style | Batch-ready? |
|------|---------|------|-------|-------------|
| `image-prompts-ed-ai-meetup-12-variations.md` | 12 | A | no-style | ✓ |
| `image-prompts-ed-ai-meetup-v2-hopecode-4.md` | 4 | A | hopecode | ✓ |
| `image-prompts-ed-ai-meetup-v2-bcai-4.md` | 4 | A | bcai | ✓ |
| `image-prompts-ed-ai-meetup-v2-biolum-4.md` | 4 | A | kk | ✓ |
| `image-prompts-round2-sporeprint-typography.md` | 10 | A | hopecode | ✓ |

---

## Apparel / Screen Print (`projects/apparel-screen-print/`)

```bash
# Dark drippy shirts — best batch
python generate.py -f prompts/kb-ecosystem-mirror/projects/apparel-screen-print/image-prompts-show-shirts-five-dark-drippy.md \
  -d output/apparel --style zine -m flash --workers 4
```

| File | Prompts | Tier | Style | Batch-ready? | Notes |
|------|---------|------|-------|-------------|-------|
| `image-prompts-show-shirts-five-dark-drippy.md` | 5 | A | zine | ✓ | Best batch |
| `image-prompts-vancouver-ai-5-variations.md` | 5 | A | zine | ✓ | 5 style variations |
| `image-prompts-vancouver-ai-round2-drippy-dark-dye.md` | 5 | A | zine | ✓ | Round 2 |
| `image-prompts-mockups-on-real-dyed-shirts.md` | 3 | A | — | ⚠️ | Needs --reference-image for mockup mode |
| `image-prompts-vancouver-ai-round3-lottee-photo-refs.md` | 5 | B | — | ⚠️ | Needs photo references |
| `image-prompt-mockup-shirt03-finalist-blend.md` | 1 | A | — | ⚠️ | Needs --reference-image |
| `image-prompts.md` | 1 | B | — | ✗ | Stub |

---

## BC + AI Festival Week (`projects/02-bc-ai-ecosystem-nonprofit/events/2026/bc-ai-festival-week/`)

```bash
# Direction 1: Bioluminescent aurora (bcai style)
python generate.py -f prompts/kb-ecosystem-mirror/projects/02-bc-ai-ecosystem-nonprofit/events/2026/bc-ai-festival-week/branding/image-prompts.md \
  -d output/bc-ai-festival --style bcai -m flash --workers 4
```

| File | Prompts | Tier | Style | Batch-ready? |
|------|---------|------|-------|-------------|
| `branding/image-prompts.md` | 8 | A | bcai (Dir 1) / hopecode (Dir 2) | ✓ |

---

## Upgrade AI Training (`projects/03-theupgrade-ai-training/`)

### RAP Certification

```bash
python generate.py -f prompts/kb-ecosystem-mirror/projects/03-theupgrade-ai-training/certification-programs/responsible-ai-professional/marketing/image-prompts.md \
  -d output/rap-cert --style upgrade -m flash --workers 4
```

| File | Prompts | Tier | Style | Batch-ready? | Notes |
|------|---------|------|-------|-------------|-------|
| `certification/.../marketing/image-prompts.md` | 7 | B→A | upgrade | ✓ | Converted from MJ format |
| `certification/.../marketing/assets/infographics/image-prompts.md` | 4 | A | upgrade | ✓ |
| `certification/.../marketing/assets/infographics/image-prompts-regen.md` | 3 | A | upgrade | ✓ |

### UAI Film Festival Brazil 2026

```bash
python generate.py -f prompts/kb-ecosystem-mirror/projects/03-theupgrade-ai-training/speaking-engagements/uai-film-festival-brazil-2026/image-prompts.md \
  -d output/uai-film --style zine -m flash --workers 4
```

| File | Prompts | Tier | Style | Batch-ready? |
|------|---------|------|-------|-------------|
| `uai-film-festival-brazil-2026/image-prompts.md` | 21 | A | zine | ✓ |

---

## Upgrade Marketing Hub (`projects/05-marketing-and-outreach/upgrade-marketing-hub/`)

All verticals use the `upgrade` style. Each has been converted from nested `###` format to Rafiki `## N.` format.

```bash
# Healthcare first (highest quality)
python generate.py -f prompts/kb-ecosystem-mirror/projects/05-marketing-and-outreach/upgrade-marketing-hub/healthcare-pros/images/image-prompts.md \
  -d output/upgrade-hub --style upgrade -m flash --workers 4
```

| Vertical | File | Prompts | Tier | Batch-ready? |
|----------|------|---------|------|-------------|
| Healthcare | `healthcare-pros/images/image-prompts.md` | 23 | B→A | ✓ |
| Legal | `legal-pros/images/image-prompts.md` | ~8 | B→A | ✓ |
| HR | `hr-pros/images/image-prompts.md` | ~8 | B→A | ✓ |
| Creative Pros | `creative-pros/images/image-prompts.md` | ~8 | B→A | ✓ |
| Journalists | `journalists/images/image-prompts.md` | ~8 | B→A | ✓ |
| PR & Comms | `pr-comms/images/image-prompts.md` | ~8 | B→A | ✓ |
| Sales Leaders | `sales-leaders/images/image-prompts.md` | ~8 | B→A | ✓ |
| All Programs | `all-programs/images/image-prompts.md` | — | B | Check |

---

## Creative Mornings Vancouver (`projects/02-bc-ai-ecosystem-nonprofit/.../creative-mornings-vancouver-may-2026/`)

```bash
python generate.py -f prompts/kb-ecosystem-mirror/projects/02-bc-ai-ecosystem-nonprofit/speaking-engagements/2026/creative-mornings-vancouver-may-2026/slides/image-gen-prompts.md \
  -d output/creative-mornings --style zine -m flash --workers 4
```

| File | Prompts | Tier | Style | Batch-ready? |
|------|---------|------|-------|-------------|
| `slides/image-gen-prompts.md` | ~18 | B→A | zine | ✓ |

---

## After Running Batches

```bash
# Rebuild master library after any batch
python generate.py library --open
```
