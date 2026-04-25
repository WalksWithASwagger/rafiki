# BC AI Community Centre Prompt Library

Welcome to the BC AI Community Centre prompt library - example prompts demonstrating how to generate ecosystem diagrams in the BC AI visual style.

## What is BC AI Style?

The BC AI Community Centre visual identity is built on the mycelial network metaphor - nature's original decentralized system. This style bridges organic beauty with innovation, creating professional yet naturally-rooted visualizations.

**Key characteristics:**
- Mycelial network aesthetic (organic, branching connections)
- BC natural environment colors (forest greens, coast blues, earth browns)
- Professional yet organic
- Emphasis on connection, growth, and collaboration

See the full [BC AI Style Guide](../../styles/bcai.md) for complete aesthetic principles.

## Using These Prompts

All prompts in this library work with:

```bash
npx image-gen ./prompts/bcai/[file].md --style bcai
```

The `--style bcai` flag automatically applies the BC AI aesthetic, so you don't need to include style directives in individual prompts.

### Single Prompt Usage

Extract individual prompts:

```bash
npx image-gen --prompt "BC AI ecosystem as interconnected mycelial network with ethics at center" \
  --style bcai \
  --aspect-ratio 16:9 \
  --output bc-ai-ecosystem.png
```

## Prompt Library Contents

### [ecosystem-diagrams.md](./ecosystem-diagrams.md)

Prompts for BC AI ecosystem visualizations:
- Core ecosystem mycelial network diagrams
- Stakeholder and partnership connection maps
- Data flow and infrastructure visualizations
- Leadership and governance structures
- Community collaboration networks
- Innovation pipeline diagrams
- Talent and training ecosystems

**Best for:** Board presentations, investor pitches, partner communications, community updates

### [bcai-hopecode-visual-prompts.md](./bcai-hopecode-visual-prompts.md)

**Master compendium** of HOPECODE / “dark mode aurora” prompts for BC+AI: website headers (1280×500), researcher–subject meta diagrams, situated knowledge, fractal subgroups, rhythm–ritual–reach playbook, Mycelial org chart, Surrey/Women’s/Squamish/Mind node maps, atmospheric BC-coast vignettes, **BC Studies “Reflection” paper** diagram set, **20× membership-launch** scene+line table, one-line title bank, two-line series, **solarpunk hopecore** (labor / surveillance / abundance / transcendence), and **Indigenomics / nation-based economics** headers (consent-forward, non-GDP). **Broader KK prompt index:** [`prompts/kk-kb/README-diagram-visual-resources.md`](../kk-kb/README-diagram-visual-resources.md). **Publishing / research thread (kk-b):** `content/projects/02-bc-ai-ecosystem-nonprofit/publishing/bc-grassroots-ai-asset-kit.md`.

**Best for:** Regenerating article art, map thumbnails, funding/hackathon tiles, and ecosystem storytelling without WIRED/ corporate chart defaults

### [context-creator-field-journals.md](./context-creator-field-journals.md)

A single high-detail scene: three torn journal pages (different hands, different subject matter) with the same two words — **CONTEXT CREATOR** — circled on each, linked by mycelial threads to a bioluminescent node. “Three altitudes, same word, no coordination” — convergent independent discovery; found-object / documentary look, not deck zine.

**Best for:** Keynote or article art, Theory of Change / narrative about alignment without coordination

## Writing BC AI Prompts

When writing prompts for BC AI style, focus on:

### Content Focus

- **Central Hub**: Often ethics, compliance, standards, social license
- **Key Nodes**: Major ecosystem components (data, compute, talent, leadership)
- **Connections**: Relationships and flows between components
- **Growth Patterns**: How the ecosystem expands and evolves

### Structural Elements

The BC AI style suffix automatically handles:
- Mycelial network visual metaphor
- BC natural environment color palette
- Organic branching connection patterns
- Node styling with radial gradients
- Glowing edges on connections
- Professional yet natural composition

### Prompt Focus Areas

**Describe WHAT to show:**
- Core ecosystem components
- Relationships between elements
- Hierarchy and importance (through node size)
- Flow direction and strength

**Let the style handle HOW:**
- Visual aesthetic (organic, professional)
- Color choices (forest green, coast blue, etc.)
- Connection styles (glowing, branching)
- Overall composition (natural flow, white space)

## Prompt Format

All prompts follow this structure:

```markdown
## N. Title — Purpose

**For:** Usage context (presentation, report, etc.)
**Aspect:** Aspect ratio (16:9, 1:1, etc.)
**File name:** suggested-filename.png

**Prompt:**
> Describe the ecosystem diagram content, focusing on components,
> relationships, and meaning. The BC AI style handles the aesthetics.
```

## Best Practices

1. **Emphasize structure**: Clearly describe nodes and their relationships
2. **Indicate importance**: Larger/central nodes for core concepts
3. **Show flow**: Describe how information, resources, or influence move
4. **Include context**: What story does this diagram tell?
5. **Trust the style**: Don't over-specify visual details

## Batch Processing

Generate all prompts from a file:

```bash
npx image-gen ./prompts/bcai/ecosystem-diagrams.md \
  --style bcai \
  --output-dir ./bcai-diagrams/
```

Creates numbered output files like:
- `01-core-ecosystem.png`
- `02-stakeholder-map.png`
- etc.

## Comparison with Other Styles

**BC AI vs. kk (personal brand):**
- BC AI emphasizes natural, mycelial networks
- kk uses dark tech aesthetic with teal/purple
- BC AI more organic, kk more modern/editorial

**BC AI vs. HOPECODE:**
- BC AI is professional-organic (polished nature)
- HOPECODE is anti-corporate-organic (messy, radical)
- BC AI for community/ecosystem, HOPECODE for personal/critical thought

## Use Cases

BC AI style works best for:

- **Ecosystem Visualizations**: Showing how BC AI components interconnect
- **Stakeholder Maps**: Partnership and collaboration networks
- **Strategic Planning**: Infrastructure, talent, innovation pipelines
- **Community Communications**: Updates, progress reports, vision documents
- **Professional Presentations**: Board meetings, investor decks, partner pitches

## Related: KK personal creative practice (HOPECODE)

[prompts/kk-kb/hopecode-creative-big-ideas-prompts.md](../kk-kb/hopecode-creative-big-ideas-prompts.md) — KK's personal creative stack, cognitive exoskeleton, daily rhythm, and field journal prompts in the same HOPECODE visual language. Different themes (personal creative practice vs community theory), same aesthetic.

Runnable batch companion: [prompts/kk-kb/hopecode-big-ideas-batch.md](../kk-kb/hopecode-big-ideas-batch.md)

## Contributing

These prompts are evolving documents. As the BC AI Community Centre grows, these examples should grow with it. Fork them, adapt them, make them your own.

---

**Remember:** We're not just visualizing an AI ecosystem - we're representing a quantum fusion point where ancient forests meet cutting-edge innovation, where community drives technology, where BC's natural wisdom guides our artificial intelligence future.
