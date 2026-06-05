# Prompt And Media Release Policy

Rafiki has two public boundaries:

- the public GitHub repository
- the narrower public npm package

Once the GitHub repository is public, any tracked prompt, asset, or doc should
be treated as public. Do not commit material that depends on private source
photos, unpublished campaign details, private archive paths, or live local-only
media.

The public npm package ships runtime code, docs, styles, config examples, and a
small set of explicitly listed public fixtures. It does not ship private prompt
libraries, campaign briefs, generated outputs, or local media folders by
default.

## Public Fixtures

The packaged fixtures are:

- `examples/quickstart-image-prompts.md`
- `examples/keynote-visual-workflow-prompt-pack.md`

They are intentionally safe for onboarding, dry-run smoke tests, and product
use-case discussion:

```bash
npx rafiki examples/quickstart-image-prompts.md --dry-run --no-viewer
npx rafiki examples/keynote-visual-workflow-prompt-pack.md --dry-run --no-viewer
```

## Private Prompt Libraries

Keep private working prompt collections outside the public repo or in another
private repo. They can still be used with Rafiki by passing paths explicitly:

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

Historical tracked examples in `prompts/` and `assets/` are public GitHub repo
content for this release. They remain outside the npm package unless explicitly
added to `files`.
