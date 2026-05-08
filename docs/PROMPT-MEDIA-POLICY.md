# Prompt And Media Release Policy

Rafiki's public package ships runtime code, docs, styles, config examples, and
a tiny quickstart fixture. It does not ship private prompt libraries, campaign
briefs, mirrored knowledge-base material, generated assets, or local media
references.

## Public Fixture

The packaged fixture is:

- `examples/quickstart-image-prompts.md`

It is intentionally generic and safe for onboarding. Use it for dry-run smoke
tests and first batch runs:

```bash
npx rafiki examples/quickstart-image-prompts.md --dry-run --no-viewer
```

## Private Prompt Libraries

Keep working prompt collections in your own checkout or another private repo.
They can still be used with Rafiki by passing paths explicitly:

```bash
npx rafiki /path/to/private/image-prompts.md --output-dir /path/to/output
```

Do not commit:

- source photos or reference media for private people, campaigns, or archives
- absolute local media paths
- API keys, account IDs, or provider secrets
- generated output folders intended only for local review

## Package Boundary

The npm `files` allowlist excludes `prompts/`, `assets/`, `output/`, `data/`,
`tools/`, tests, scripts, and local dependency folders. Add new public examples
only when they are small, generic, and free of private media assumptions.

Private examples may remain tracked in the working repository for now, but they
are not part of the public npm package unless explicitly added to `files`.
