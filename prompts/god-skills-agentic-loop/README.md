# God Skills Agentic Loop Graphics

Public prompt pack for a nine-concept God Skills graphics bakeoff. The set is
intended for a later blog post about agentic-loop workflows, with a controlled
HOPECODE x BC + AI visual direction.

## Prompts

`image-prompts.md` contains nine 16:9 concepts:

- Clean Diagram: roster chart, workflow map, invocation cheat sheet.
- Mythic Poster: roster chart, workflow map, invocation cheat sheet.
- Ops Dashboard: roster chart, workflow map, invocation cheat sheet.

The prompts preserve the "God Skills" naming and use Hindu names only as small
mnemonic codenames. They explicitly ban deity portraits, religious parody,
caricature, impersonation, generic AI robots, glowing brains, and fake UI.

## Dry Run

Check that Rafiki parses exactly nine prompts before spending provider calls:

```bash
python generate.py -f prompts/god-skills-agentic-loop/image-prompts.md \
  -d output/god-skills-agentic-loop/dry-run \
  --style hopecode+bcai -m pro -a 16:9 --resolution 1K -w 1 --dry-run
```

## Bakeoff Runs

Run Gemini Pro 1K:

```bash
python generate.py -f prompts/god-skills-agentic-loop/image-prompts.md \
  -d output/god-skills-agentic-loop/gemini-pro-1k \
  --style hopecode+bcai -m pro -a 16:9 --resolution 1K -w 1
```

Run GPT Image 2:

```bash
python generate.py -f prompts/god-skills-agentic-loop/image-prompts.md \
  -d output/god-skills-agentic-loop/openai-gpt-image-2 \
  --style hopecode+bcai -m gpt-image-2 -a 16:9 -q high -w 1
```

Review side by side:

```bash
python generate.py library --open
```

## Review Criteria

- Titles and key labels are legible enough for blog use.
- No literal deity imagery or disrespectful religious visual treatment appears.
- HOPECODE texture is present without destroying diagram readability.
- BC + AI palette and mycelial ecosystem language are visible without generic
  tech branding.
