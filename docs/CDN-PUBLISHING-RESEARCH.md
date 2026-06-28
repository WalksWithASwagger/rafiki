# CDN-Backed Approved Asset Publishing — Research Memo

Status: **proposed — pending maintainer decision** (issue #202). Research/spike only; this
memo recommends *whether* to proceed. No implementation, uploads, or new vendor
integration are in scope.

## Question

Should approved public assets get an optional CDN-backed publishing flow that gives them
stable URLs across sites — without breaking Rafiki's local-first, no-hosted-service
posture?

## Current state (what already exists)

- **Static deploy, Vercel only.** `lib/deploy/vercel.py` wraps `vercel deploy` to publish a
  viewer directory (`output/<project>/` or `output/<project>/approved/`) as a static site,
  returning the deployment URL. `lib/deploy/readiness.py` exposes read-only
  `/api/deploy-readiness` checks. Documented in [DEPLOYMENT.md](DEPLOYMENT.md).
- **Approval → state pipeline.** Rate (portal stars → `output/ratings.json`) → `approve`
  (copies starred images into `output/<project>/approved/` + `approved/index.json`) →
  viewer build → deploy or export. See [ARCHIVE.md](ARCHIVE.md), [ASSET-REGISTRY.md](ASSET-REGISTRY.md).
- **Export state is tracked.** `lib/archive_metadata.py` records per-asset states
  `{canva, notion, deployed, published, superseded}` in the gitignored
  `output/archive-metadata.json`. So "what has been published where" is already a
  first-class concept — the Phase 6 precondition ("registry/export state reliable locally")
  is met.
- **Local-first is a hard product line.** README: "There is no hosted Rafiki service."
  [SCOPE.md](SCOPE.md): v1 is not a SaaS/queue/multi-user platform. Generated outputs
  (`output/`, `prompts/`, `assets/`) are gitignored; `scripts/check-public-boundary.py`
  enforces that local/generated surfaces stay out of the public repo.

## Options

### Option 1 — Extend the existing Vercel static deploy to a stable public path
Reuse `lib/deploy/vercel.py`; publish approved assets to a stable production alias so URLs
don't churn between deploys; stamp `published` in archive-metadata.
- **Pros:** smallest change; no new vendor; reuses readiness checks and the approve flow.
- **Cons:** Vercel static hosting is page/site-shaped, not an asset CDN; per-asset stable
  URLs are awkward; couples publishing to one host.

### Option 2 — No-build object-store upload for explicitly-public approved assets
An opt-in uploader pushes only `approved/` assets flagged public to an operator-configured
bucket/CDN (S3 / Cloudflare R2 / Bunny), recording returned URLs in archive-metadata.
- **Pros:** true stable per-asset CDN URLs; operator owns the bucket and keys (local-first
  preserved); fits the existing approve→state model; vendor-agnostic via an S3-style API.
- **Cons:** new credential surface; privacy blast-radius if the public gate is wrong; a
  real (if small) integration to build and maintain.

### Option 3 — Do nothing (status quo)
Keep Vercel static deploy + local Canva/registry exports; no CDN.
- **Pros:** zero new surface; nothing to secure; fully local-first.
- **Cons:** no stable cross-site asset URLs (the original ask goes unmet).

## Privacy / local-first risks (apply to any option that uploads)

- **Public gate must be explicit and auditable.** Only assets in `approved/` *and* flagged
  public should ever leave the machine. Reuse `ARCHIVE_STATES` + a publish gate; never
  auto-publish from `run-*`.
- **No secret/path leakage.** Keep bucket creds in `.env` (untracked); never write URLs or
  keys into tracked files; respect `check-public-boundary.py`.
- **Opt-in, operator-controlled, reversible.** Default off; dry-run first; a publish must be
  undoable (delete object + clear `published` state).
- **Don't become a hosted service.** Rafiki orchestrates an upload to the *operator's*
  CDN; it must not run or proxy hosting itself.

## Minimal opt-in dry-run concept (for whoever implements later)

`rafiki publish <project> --dry-run` lists exactly which `approved/` + public-flagged
assets *would* upload, to which configured target, with the URLs they'd receive — writing
nothing, reusing the readiness-check pattern. A real run would upload, record `published`
URLs in archive-metadata, and support `--undo`.

## Recommendation

**Defer (Option 3 for now).** The original need — stable cross-site URLs — is real but P3,
and no current workflow is blocked by its absence. If/when pursued, choose **Option 2**
(operator-owned object store) over Option 1, because it actually delivers stable per-asset
URLs while keeping keys and ownership on the operator's machine. Gate any implementation on:
explicit per-asset public flag, opt-in + dry-run + undo, no new *required* vendor, and no
hosted-service drift. Until a concrete cross-site use case appears, the existing Vercel
static deploy plus local exports are sufficient.

## Follow-up (only if KK approves proceeding)

File an implementation issue for the opt-in object-store publisher (Option 2) with the
public-gate, dry-run/undo, and archive-metadata `published` requirements above.
