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
  defaults to dry-run, records clearable recent attempts in browser-local
  storage, requires both a dry-run manifest matching the active
  prompt/config draft and explicit confirmation before submitting
  `dry_run=false`; Python still resolves references, owns provider keys, and
  runs `run_batch` synchronously before the request returns.
- Rollback routes stay available during migration: `/legacy-suite` for the old
  media-suite command center and `/legacy-library` for the old image library.

If `frontend/.output/server/index.mjs` does not exist, `generate.py serve`
attempts `npm --prefix frontend run build`. Set `RAFIKI_DISABLE_FRONTEND=1` to
force legacy fallback behavior while debugging.

## Package Boundary

`npm pack --dry-run` is the source of truth for the public npm package. The
issue #298 audit reports 146 package entries: the Node CLI entry, Python runtime
code, selected scripts, docs, styles, config examples, requirements files, and
the public example prompt packs. The dry run includes `README.md`,
`docs/FRONTEND.md`, `generate.py`, `index.js`, `lib/server.py`, and
`package.json`.

The current release strategy is intentional fallback, not frontend inclusion.
The root `package.json` `files` allowlist does not ship `frontend/`,
`frontend/package.json`, frontend source, or `frontend/.output/` Nitro build
artifacts. `npm run pack:check` verifies that boundary with
`npm pack --dry-run --json` and fails if any `frontend/` path enters the tarball
before a maintainer approves the package-content change.

For package installs, `rafiki serve` can start the Python local server and the
legacy portal routes, but it cannot build or start the TypeScript shell from the
package alone because the frontend workspace and build output are absent.
Verification of the TypeScript UI through `npx rafiki serve` from a published
package is deferred until the maintainer chooses whether to ship frontend source
or prebuilt frontend artifacts.

## Generate Wait Semantics

V1/V1.5 Generate runs are request-scoped from the frontend perspective and
synchronous from the Python perspective. The `/generate` route submits one
`/api/regen` request, then waits for Python to finish `run_batch` and return
the run payload or an error. There is no durable local job record, provider
polling loop, resumable run state, or provider cancellation path behind the React
screen today.

**Stop Waiting** aborts only the current browser wait/request and returns the UI
to an operator-ready state. It does not cancel Python work already running,
cancel provider work already handed off, or prove that the local output path is
final. After stopping the wait, operators should verify the run folder or library
state before retrying.

Any future background job design should start with a Python-owned local job
ledger. Python must be the only writer for ledger entries, provider identifiers,
status transitions, terminal states, errors, timestamps, and output paths. React
should remain a reader/operator shell that displays that state and submits operator
intents; it should not own provider state persistence. Implementing that ledger,
true cancellation, provider polling, and resumable runs is intentionally deferred.
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

`npm run verify` remains the full repo closeout gate. It validates the package
boundary but does not package the frontend into the npm tarball.
