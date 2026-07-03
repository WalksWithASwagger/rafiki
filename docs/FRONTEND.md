# Frontend Shell

Rafiki's live portal shell is the TypeScript app in `frontend/`. It was imported
from `WalksWithASwagger/rafikki` and is now maintained as first-party code in
this repository. `python generate.py serve` remains the operator command: Python
owns local files, sidecars, provider/job mutations, and `/api/*`; the frontend
is spawned as an internal localhost service and rendered through the Python
server.

## Runtime Boundary

- Primary UI routes `/`, `/generate`, `/library`, `/viewer/*`, `/export`,
  `/registry`, `/health`, `/spend`, and frontend assets proxy to the TypeScript
  shell when its Nitro `node-server` build is available.
- Python continues to serve `/api/*`, `/output/*`, `/media/*`, auth, local
  sidecars, generation, registry, usage, and media APIs.
- `GET /api/library-state` is the read-only normalized archive payload used by
  the frontend for projects, runs, images, ratings, health, and registry
  summary data.
- `GET /api/generate-options` exposes safe model/style/aspect/reference-role
  options for the Generate screen.
- `POST /api/prompt-preview` parses Markdown prompt packs without writing files
  or calling providers.
- `POST /api/regen` remains the generation path. The React `/generate` route
  defaults to dry-run, records recent attempts in browser-local storage, and
  requires both a matching dry-run manifest and explicit confirmation before
  submitting `dry_run=false`; Python still resolves references, owns provider
  keys, and runs `run_batch`.
- Rollback routes stay available during migration: `/legacy-suite` for the old
  media-suite command center and `/legacy-library` for the old image library.

If `frontend/.output/server/index.mjs` does not exist, `generate.py serve`
attempts `npm --prefix frontend run build`. Set `RAFIKI_DISABLE_FRONTEND=1` to
force legacy fallback behavior while debugging.

## Open The Library

Start the local portal from the repo root:

```bash
python3 generate.py serve
```

Then open `http://localhost:7433/library`. The `/library` route is the new
TypeScript library, backed by `GET /api/library-state` and image files from
`/output/*`. The root route redirects into the same shell, and the legacy
rollback surfaces remain at `/legacy-suite` and `/legacy-library`.

## Development

Root scripts delegate into `frontend/`:

```bash
npm run frontend:dev
npm run frontend:build
npm run frontend:typecheck
npm run frontend:lint
npm run frontend:verify
```

Inside `frontend/`, npm is canonical. Keep `frontend/package-lock.json`
committed; do not commit `node_modules/`, `.output/`, `.wrangler/`, `.lovable/`,
`bun.lock`, or `bunfig.toml`. Source provenance is recorded in
`frontend/ORIGIN.md`.

## Verification

For frontend changes, run:

```bash
npm --prefix frontend ci
npm run frontend:verify
python3 -m pytest tests/test_server_endpoints.py tests/test_server_auth.py -q
npm run e2e:portal
```

The portal smoke creates a disposable archive, verifies the new live routes,
checks rating persistence through `/api/ratings`, confirms present images load
from `/output/*`, confirms missing records render placeholders, and captures
desktop/mobile nonblank screenshot metrics.

`npm run verify` remains the full repo closeout gate. It currently validates
the package boundary but does not package the frontend into the npm tarball.

## Packaging Follow-Up

This replacement is repo-first. The root `package.json` `files` list does not
yet ship `frontend/` in `npm pack`. Before an npm release depends on the new
shell, add an explicit packaging strategy for frontend source/build artifacts
and verify that `npx rafiki serve` can start the TypeScript UI from the
published package.
