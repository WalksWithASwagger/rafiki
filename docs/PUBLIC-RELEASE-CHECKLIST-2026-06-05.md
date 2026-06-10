# Public Release Checklist - 2026-06-05

Repository: `WalksWithASwagger/rafiki`

Public release decision: make the existing GitHub repository public after a
secrets-only gate. Non-secret prompt examples, generated/sample media,
historical local paths, and working notes are accepted as public repository
content for this release. They are still excluded from the npm package unless
explicitly listed in `package.json`.

## Boundary

- Existing repo, not a new clean-room repo.
- Gate on true credentials, provider keys, account secrets, and tokens.
- Do not stage unrelated local work such as generated prompt packs or output
  assets (these live in a private knowledge base; `prompts/` and `assets/` are
  gitignored).
- Treat any tracked prompt, asset, or doc as public once repository visibility
  changes.
- Keep live provider keys in environment variables or an untracked `.env`.

## Secret Scans

Run before changing visibility:

```bash
gitleaks detect --source . --redact --no-banner --verbose
trufflehog git file:///Users/kk/Code/rafiki --only-verified --no-update --json
git check-ignore -v .env node_modules output .venv
git ls-files '.env*' '*secret*' '*key*' '*token*' '*credential*' '*.pem' '*.p12' '*.key' '*.env'
```

2026-06-05 result:

- `gitleaks detect --source . --redact --no-banner --verbose`: passed,
  scanned 149 commits, no leaks found.
- `trufflehog git file:///Users/kk/Code/rafiki --only-verified --no-update --json`:
  passed, `verified_secrets:0`, `unverified_secrets:0`.
- `git check-ignore -v .env node_modules output .venv`: passed; `.env`,
  `node_modules/`, `output/`, and `.venv/` are ignored.
- `git ls-files ...`: matched `.env.example` and a WAIFF keynote prompt file
  because the filename contains `keynote`; neither is a credential.

Known gitleaks false positive:

- Fingerprint:
  `6cc1ef728eac04d6719b90abaa31793fd78eb3bf:docs/image-pipeline-operator.md:generic-api-key:132`
- Historical text was a style/use-case phrase in the operator guide, not a
  credential.
- The fingerprint is allowlisted in `.gitleaksignore` so the release scan can
  fail only on new or real findings.

## Verification Commands

Run before changing visibility:

```bash
npm run verify
npm run e2e:portal
npm pack --dry-run
```

2026-06-05 result:

- `npm run verify`: passed; 322 Python tests passed, docs links resolved,
  dry-run smoke passed, and npm package dry-run completed.
- `npm run e2e:portal`: passed; local portal desktop/mobile smoke verified
  library, review queue, image loading, metadata save, feedback save, and
  evaluation save.

## Visibility Flip

After scans and verification pass:

```bash
gh repo edit WalksWithASwagger/rafiki \
  --visibility public \
  --accept-visibility-change-consequences \
  --enable-issues
```

Verify after the flip:

```bash
gh repo view WalksWithASwagger/rafiki --json nameWithOwner,isPrivate,visibility,url,defaultBranchRef,description
```

Expected result: `isPrivate` is `false`, `visibility` is `PUBLIC`, and the URL
is `https://github.com/WalksWithASwagger/rafiki`.

## Blog Follow-Up

After the repository is public, update the KrisKrug.co article to include a
grounded link to Rafiki as the local-first tool used to batch, review, and
export image candidates for the keynote visual workflow.
