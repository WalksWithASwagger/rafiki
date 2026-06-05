# Keynote Visual Workflow Use Case

Public source: [AI Keynote Slides Need Taste Before Prompts](https://kriskrug.co/2026/06/04/ai-keynote-slides-visual-workflow/)

This use case describes the creative workflow Rafiki needs to support better:
turning a talk idea into a reusable chain of prompts, graphics, slide assets,
website art, posts, and guide material.

The core lesson is not "generate AI keynote slides." The useful workflow is a
taste gate. Raw notes become a talk spine. The talk spine becomes visual jobs.
Visual jobs become prompt batches. The batch is reviewed hard. Only the useful
images move into manual finishing, deck work, and downstream publishing.

## The Artifact Chain

| Stage | Operator question | Rafiki job |
|---|---|---|
| Raw words | What am I actually trying to say? | Preserve source notes and the public-safe story behind the batch. |
| Talk spine | What are the beats? | Group prompts by slide beat, section, or intended asset. |
| Reference kit | What should this feel like? | Make style and reference choices visible before generation. |
| Prompt pack | What visual job does each image need to do? | Parse numbered Markdown prompts with use, aspect ratio, style, and constraints. |
| Batch run | What did the model actually make? | Keep candidates isolated by run with model, style, prompt, and reference metadata. |
| Review gate | What should be approved, rebuilt, regenerated, or rejected? | Make selection state durable and searchable. |
| Slide work | What needs to become editable by hand? | Export approved candidates with Canva/manual rebuild notes. |
| Downstream assets | What else can this idea become? | Track whether an image fed a post, guide, site page, social asset, or speaker kit. |

## Public Example

The Both Hands Full / WAIFF thread is the model for this workflow at a high
level. A raw idea like "both hands full" can become:

- a talk map about critique, curiosity, taste, and writing for the bot
- a prompt pack with specific visual jobs and refusal lines
- generated candidates that are reviewed instead of blindly accepted
- slide assets that get rebuilt or cleaned up manually
- a blog post, internal guide, social set, speaker page, or event/festival asset

The important part is provenance. A rejected batch is still useful because it
records what did not match the speaker's taste. The system should make it hard
to mistake rejected candidates for approved artwork.

## Product Lessons

### Library

The library should understand artifact chains, not just image files. A useful
record can answer:

- which talk, article, or campaign started this image
- which prompt and style produced it
- whether it was approved, rejected, regenerated, exported, or published
- where it was reused downstream
- what manual cleanup is still needed

### Style Chooser

The style chooser should be reference-first. Operators need to see style names,
plain-language descriptions, example use cases, and warnings before they run a
batch. A text-only style input is too easy to misuse when the difference
between Hope Code, BC AI, zine, and other style lanes carries the taste of the
whole output set.

### Interface

The interface should guide the actual loop:

1. capture the source idea
2. pick a reference/style lane
3. build or load a prompt pack
4. dry-run the batch
5. generate
6. review candidates
7. export approved assets
8. record downstream use

That is the difference between "an image generator" and a creative operations
tool for keynote visuals, editorial assets, and reusable brand systems.

## Public-Safety Boundaries

This use case should stay public-safe:

- link to the published article, not private archive paths
- do not expose rejected image batches unless they are explicitly approved for
  publication
- do not include organizer details, private prep notes, or unpublished contacts
- keep reference-image paths local and out of public examples
- treat tracked GitHub examples as public once the repo is public
