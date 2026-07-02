# Rafiki — Design & Engineering Handoff

_Local-first creative operations tool for triaging, browsing, and delivering
generated image runs._

Version: **0.8.2** · Theme: Industrial Utilitarian (dark, keyboard-first)

---

## 1. What this app does

Rafiki solves three jobs that used to be spread across a file browser, a
review sheet, and an ad-hoc packager:

| Job        | Where it lives     | Primary interaction               |
| ---------- | ------------------ | --------------------------------- |
| **Triage** | `/viewer/:imageId` | J/K to move, S/X/E to act         |
| **Browse** | `/library`         | Search, filter, sort, bulk-select |
| **Export** | `/export`          | Customize manifest, deliver ZIP   |

Supporting surfaces: `/registry` (asset ledger), `/health` (archive health),
`/spend` (cost per run).

---

## 2. Routes

Flat file-based routing under `src/routes/` — TanStack Start convention.

```
/                       →  index.tsx           Landing / redirect to library
/library                →  library.index.tsx   Project grid, search & bulk mode
/library/:runId         →  library.$runId.tsx  Run detail, image grid
/viewer                 →  viewer.index.tsx    Empty-state / picker
/viewer/:imageId        →  viewer.$imageId.tsx Full-bleed triage viewer
/export                 →  export.tsx          Manifest editor & delivery
/registry               →  registry.tsx        Asset ledger
/health                 →  health.tsx          Archive health dashboard
/spend                  →  spend.tsx           Cost tracking
```

Every route with a loader provides `errorComponent` + `notFoundComponent`
using the shared components in `src/components/state/`.

---

## 3. Keyboard shortcuts

Registry lives in `src/lib/shortcuts.ts`. Press `?` anywhere to see the
in-app cheatsheet (`ShortcutSheet`).

### Global

| Key   | Action                                    |
| ----- | ----------------------------------------- |
| `?`   | Open shortcut sheet                       |
| `t`   | Toggle export dock (collapsed / expanded) |
| `g l` | Go to Library                             |
| `g v` | Go to Viewer                              |
| `g e` | Go to Export                              |
| `g r` | Go to Registry                            |
| `g h` | Go to Health                              |

### Viewer (`/viewer/:imageId`)

| Key       | Action           |
| --------- | ---------------- |
| `j` / `←` | Previous image   |
| `k` / `→` | Next image       |
| `s`       | Star (approve)   |
| `x`       | Reject           |
| `e`       | Stage for export |
| `Esc`     | Back to run grid |

### Library (`/library`)

| Key     | Action                                        |
| ------- | --------------------------------------------- |
| `/`     | Focus search                                  |
| `s`     | Cycle sort (recent → name → images → starred) |
| `a`     | Toggle multi-select mode                      |
| `c`     | Clear filters                                 |
| `1`–`5` | Filter by rating band                         |

### Export (`/export`)

| Key     | Action                          |
| ------- | ------------------------------- |
| `Enter` | Deliver current bundle          |
| `f`     | Cycle format (ZIP / CSV / JSON) |
| `r`     | Retry last failed job           |
| `d`     | Dismiss finished / errored job  |

---

## 4. State management

- **`src/stores/triage-store.ts`** — Zustand store for ratings, export tray,
  background jobs, dock UI state, shortcut sheet.
- **URL search params** — Library filters/sort/view live in the URL via
  `zodValidator` + `retainSearchParams`, so refresh & share both work.
- **TanStack Query** is available but not required; the mock data is
  synchronous and stateless.

---

## 5. Export pipeline

`src/lib/exporter.ts` renders image proxies on Canvas and bundles them with
JSZip. `src/lib/run-batch.ts` runs sequential jobs, tracks progress on the
store, and exposes `retryJob(id)`.

Manifest customization on `/export`:

- Filename tokens: `{date}`, `{count}`, `{project}`, `{format}`
- Toggleable manifest fields, in order: `id`, `seed`, `rating`, `prompt`,
  `model`, `swatch`, `createdAt`
- Formats: `ZIP` (proxies + manifest.json + index.csv), `CSV` only, `JSON` only

---

## 6. Design system

Single always-dark theme. Tokens in `src/styles.css`.

| Token                  | Value     | Use                            |
| ---------------------- | --------- | ------------------------------ |
| `--background`         | `#0c0c0c` | App backdrop                   |
| `--sidebar` / `--card` | `#141414` | Panels & cards                 |
| `--border`             | `#262626` | 1px hairlines                  |
| `--muted-foreground`   | `#888`    | Secondary text                 |
| `--brand`              | `#00ff41` | Action, active state, delivery |
| `--destructive`        | `#ef4444` | Rejects, errors                |

Type: **Inter** (UI), **JetBrains Mono** (chrome, kbd, tokens, IDs). Labels
are ALL-CAPS mono at 10–11px with `tracking-widest` — the "pro tool" tell.

### Motion tokens (all under 400ms, honors `prefers-reduced-motion`)

Defined as Tailwind v4 `@utility` in `src/styles.css`:

| Utility           | Purpose                                                |
| ----------------- | ------------------------------------------------------ |
| `rf-fade-in`      | Route content mount                                    |
| `rf-fade-in-fast` | Toggles, tray items                                    |
| `rf-slide-up`     | Export dock reveal                                     |
| `rf-shimmer`      | Loading skeletons, progress sheen                      |
| `rf-glow`         | Momentary confirm ring                                 |
| `rf-blink`        | Queued / pending indicator                             |
| `rf-hover-lift`   | Cards on hover (subtle 1px lift + brand-tinted border) |
| `rf-press`        | Tactile scale-down on `:active`                        |

Never use bouncy easings. Industrial motion is _short_ and _straight_.

---

## 7. Failure modes handled

- **Missing/failed images** → dashed placeholder inside `Thumbnail`.
- **Empty routes** → `EmptyBlock` with actionable CTA.
- **Loader errors** → `ErrorBlock` with `onRetry` re-invalidates the route.
- **Not-found params** → `NotFoundBlock` with a link home.
- **Export failure** → toast in dock + `Retry` on the errored job.
- **Reduced motion** → all animation durations collapse to ~0ms.

---

## 8. File map

```
src/
├── components/
│   ├── app-shell.tsx           Sidebar + main outlet + shortcut wiring
│   ├── export-dock.tsx         Persistent bottom tray (collapsed & expanded)
│   ├── page-header.tsx         Breadcrumb + right-side actions
│   ├── shortcut-sheet.tsx      ?-triggered cheatsheet modal
│   ├── thumbnail.tsx           Swatch tile w/ status + hover sheen
│   └── state/                  Loading / Empty / Error / NotFound blocks
├── data/mock.ts                Deterministic project/run/image fixtures
├── lib/
│   ├── exporter.ts             Canvas → JSZip bundle
│   ├── run-batch.ts            Sequential job runner + retryJob
│   ├── shortcuts.ts            useShortcuts + useSequenceShortcuts
│   └── utils.ts                cn()
├── routes/                     File-based routes (see §2)
├── stores/triage-store.ts      Zustand: ratings, tray, jobs, UI
└── styles.css                  Tokens, base, motion utilities
```

---

## 9. Shipping checklist

- [x] All routes have loading / empty / error / not-found states
- [x] Shortcuts work consistently and are documented in-app
- [x] Export produces real files (ZIP / CSV / JSON)
- [x] URL is the source of truth for Library filters
- [x] Motion respects `prefers-reduced-motion`
- [x] Focus-visible rings on all interactive elements
- [x] No hardcoded colors — all through semantic tokens
- [x] Typecheck (`tsgo --noEmit`) is clean

Ready to ship.
