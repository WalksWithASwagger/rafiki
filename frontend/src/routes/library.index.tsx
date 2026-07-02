import { createFileRoute, Link, useNavigate, useRouter } from "@tanstack/react-router";
import { useMemo, useRef } from "react";
import {
  Plus,
  Search,
  X,
  PackageOpen,
  CheckSquare,
  Square,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import { z } from "zod";
import { fallback, zodValidator } from "@tanstack/zod-adapter";
import { retainSearchParams } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ExportDock } from "@/components/export-dock";
import { EmptyBlock } from "@/components/state/empty-block";
import { ErrorBlock } from "@/components/state/error-block";
import {
  latestRunForProject,
  projectThumbs,
  runsInProject,
  effectiveRating,
  useLibraryState,
  type ImageRecord,
  type LibraryState,
  type ProjectRecord,
} from "@/lib/rafiki-data";
import { useTriageStore } from "@/stores/triage-store";
import { useShortcuts } from "@/lib/shortcuts";
import { startBatchExport } from "@/lib/run-batch";
import { cn } from "@/lib/utils";

const STATUSES = ["all", "starred", "rejected", "unrated", "failed"] as const;
const SORTS = ["recent", "name", "images", "starred"] as const;
const DIRS = ["asc", "desc"] as const;
const VIEWS = ["grid", "list"] as const;

const searchSchema = z.object({
  q: fallback(z.string(), "").default(""),
  status: fallback(z.enum(STATUSES), "all").default("all"),
  tags: fallback(z.array(z.string()), []).default([]),
  sort: fallback(z.enum(SORTS), "recent").default("recent"),
  dir: fallback(z.enum(DIRS), "desc").default("desc"),
  view: fallback(z.enum(VIEWS), "grid").default("grid"),
});

export const Route = createFileRoute("/library/")({
  validateSearch: zodValidator(searchSchema),
  search: {
    middlewares: [retainSearchParams(["q", "status", "tags", "sort", "dir", "view"])],
  },
  head: () => ({
    meta: [
      { title: "Library — Rafiki" },
      {
        name: "description",
        content: "Browse projects and runs across your local Rafiki archive.",
      },
      { property: "og:title", content: "Library — Rafiki" },
      {
        property: "og:description",
        content: "Browse projects and runs across your local Rafiki archive.",
      },
    ],
  }),
  errorComponent: ({ error, reset }) => {
    const RetryAware = () => {
      const router = useRouter();
      return (
        <AppShell>
          <ErrorBlock
            error={error}
            reset={reset}
            onRetry={() => {
              reset();
              router.invalidate();
            }}
          />
        </AppShell>
      );
    };
    return <RetryAware />;
  },
  component: LibraryIndex,
});

const HEALTH_DOT: Record<string, string> = {
  ok: "bg-brand",
  warn: "bg-amber-400",
  fail: "bg-destructive",
};

type SearchState = {
  q: string;
  status: (typeof STATUSES)[number];
  tags: string[];
  sort: (typeof SORTS)[number];
  dir: (typeof DIRS)[number];
  view: (typeof VIEWS)[number];
};

function LibraryIndex() {
  const { data, error, isLoading, refetch } = useLibraryState();

  if (error) {
    return (
      <AppShell>
        <ErrorBlock error={error} reset={() => void refetch()} />
      </AppShell>
    );
  }

  if (isLoading || !data) {
    return (
      <AppShell>
        <PageHeader crumbs={[{ label: "LOCAL", mono: true }, { label: "Library" }]} />
        <div className="p-16 text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Loading archive…
        </div>
      </AppShell>
    );
  }

  return <LibraryContent state={data} />;
}

function LibraryContent({ state }: { state: LibraryState }) {
  const { q, status, tags, sort, dir, view } = Route.useSearch() as SearchState;
  const navigate = useNavigate({ from: "/library" });
  const ratings = useTriageStore((s) => s.ratings);
  const manifestPrefs = useTriageStore((s) => s.manifestPrefs);
  const selectMode = useTriageStore((s) => s.selectMode);
  const toggleSelectMode = useTriageStore((s) => s.toggleSelectMode);
  const librarySelection = useTriageStore((s) => s.librarySelection);
  const toggleLibrarySelection = useTriageStore((s) => s.toggleLibrarySelection);
  const setLibrarySelection = useTriageStore((s) => s.setLibrarySelection);
  const clearLibrarySelection = useTriageStore((s) => s.clearLibrarySelection);
  const addToTray = useTriageStore((s) => s.addToTray);
  const searchRef = useRef<HTMLInputElement>(null);
  const projects = state.projects;
  const images = state.images;
  const healthReport = state.health;

  const tagOptions = useMemo(
    () => Array.from(new Set(projects.flatMap((project) => project.tags))).slice(0, 12),
    [projects],
  );

  const setSearch = (patch: Partial<SearchState>) => {
    navigate({
      search: (prev: SearchState) => ({ ...prev, ...patch }),
      replace: true,
    });
  };

  const cycleSort = () => {
    const idx = SORTS.indexOf(sort);
    setSearch({ sort: SORTS[(idx + 1) % SORTS.length] });
  };

  const clearFilters = () =>
    setSearch({
      q: "",
      status: "all",
      tags: [],
      sort: "recent",
      dir: "desc",
    });

  const visibleProjects = useMemo(() => {
    const query = q.trim().toLowerCase();
    const filtered = projects.filter((p) => {
      if (tags.length && !tags.some((t) => p.tags.includes(t))) return false;
      if (query) {
        const runLabels = runsInProject(state, p.id)
          .map((r) => r.label.toLowerCase())
          .join(" ");
        const hay = [p.name.toLowerCase(), p.code.toLowerCase(), p.tags.join(" "), runLabels].join(
          " ",
        );
        if (!hay.includes(query)) return false;
      }
      if (status !== "all") {
        const pImages = images.filter((i) => i.projectId === p.id);
        if (status === "failed" && !pImages.some((i) => i.status === "failed")) return false;
        if (status === "starred" && !pImages.some((i) => effectiveRating(i, ratings) === "starred"))
          return false;
        if (
          status === "rejected" &&
          !pImages.some((i) => effectiveRating(i, ratings) === "rejected")
        )
          return false;
        if (
          status === "unrated" &&
          !pImages.some((i) => !effectiveRating(i, ratings) && i.status === "present")
        )
          return false;
      }
      return true;
    });

    const starredFor = (p: ProjectRecord) =>
      images.filter((i) => i.projectId === p.id && effectiveRating(i, ratings) === "starred")
        .length;

    const cmp = (a: ProjectRecord, b: ProjectRecord) => {
      switch (sort) {
        case "name":
          return a.name.localeCompare(b.name);
        case "images":
          return a.imageCount - b.imageCount;
        case "starred":
          return starredFor(a) - starredFor(b);
        case "recent":
        default:
          return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
      }
    };
    const sorted = filtered.slice().sort(cmp);
    return dir === "desc" ? sorted.reverse() : sorted;
  }, [q, status, tags, sort, dir, ratings, projects, images, state]);

  useShortcuts([
    {
      combo: "/",
      handler: () => {
        searchRef.current?.focus();
        searchRef.current?.select();
      },
    },
    { combo: "c", handler: () => clearFilters() },
    { combo: "s", handler: () => cycleSort() },
    { combo: "a", handler: () => toggleSelectMode() },
    { combo: "1", handler: () => setSearch({ status: "all" }) },
    { combo: "2", handler: () => setSearch({ status: "starred" }) },
    { combo: "3", handler: () => setSearch({ status: "rejected" }) },
    { combo: "4", handler: () => setSearch({ status: "unrated" }) },
    { combo: "5", handler: () => setSearch({ status: "failed" }) },
    {
      combo: "esc",
      handler: () => {
        if (selectMode) toggleSelectMode();
      },
    },
  ]);

  const filtersActive =
    q || status !== "all" || tags.length > 0 || sort !== "recent" || dir !== "desc";

  const selectAllVisible = () => setLibrarySelection(visibleProjects.map((p) => p.id));

  const stageSelected = () => {
    const ids = librarySelection.flatMap((pid) =>
      images.filter((i) => i.projectId === pid && i.status === "present").map((i) => i.id),
    );
    if (ids.length) addToTray(ids);
  };

  const deliverAsJobs = async () => {
    const groups = librarySelection
      .map((pid) => {
        const proj = projects.find((p) => p.id === pid);
        const ids = images
          .filter((i) => i.projectId === pid && i.status === "present")
          .map((i) => i.id);
        return { label: proj?.name ?? pid, imageIds: ids };
      })
      .filter((g) => g.imageIds.length > 0);
    if (!groups.length) return;
    await startBatchExport(groups, {
      format: "zip",
      destination: "~/Deliveries/Rafiki",
      template: "{project}_{run}_{slot}",
      filenameTemplate: manifestPrefs.filenameTemplate,
      fields: manifestPrefs.fields,
    });
  };

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "LOCAL", mono: true }, { label: "Library" }]}
        actions={
          <>
            <button
              onClick={toggleSelectMode}
              className={cn(
                "px-3 py-1.5 border text-xs font-mono uppercase tracking-widest rounded flex items-center gap-2",
                selectMode
                  ? "border-brand text-brand"
                  : "border-border text-muted-foreground hover:text-foreground",
              )}
            >
              {selectMode ? <CheckSquare className="size-3.5" /> : <Square className="size-3.5" />}
              {selectMode ? "Cancel" : "Select"}
              <kbd className="border border-border/60 px-1 rounded text-[9px] ml-1">A</kbd>
            </button>
            <button className="px-4 py-1.5 bg-brand text-black text-xs font-bold rounded hover:bg-brand/90 transition-colors font-mono tracking-wider uppercase flex items-center gap-2">
              <Plus className="size-3.5" strokeWidth={3} />
              New Run
            </button>
          </>
        }
      />

      <div className="relative flex-1 overflow-y-auto">
        <div className="p-8 pb-32">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-px bg-border border border-border rounded-lg overflow-hidden mb-8">
            <Stat label="Projects" value={healthReport.totalProjects} />
            <Stat label="Runs" value={healthReport.totalRuns} />
            <Stat label="Present" value={healthReport.presentImages.toLocaleString()} />
            <Stat label="Failed" value={healthReport.failedImages} tone="destructive" />
            <Stat
              label="Starred"
              value={Object.values(ratings).filter((r) => r === "starred").length}
              tone="brand"
            />
          </div>

          <div className="flex flex-col md:flex-row gap-3 mb-4">
            <div className="relative flex-1 min-w-0">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <input
                ref={searchRef}
                value={q}
                onChange={(e) => setSearch({ q: e.target.value })}
                placeholder="Search projects, runs, tags…"
                className="w-full bg-sidebar border border-border rounded pl-10 pr-16 py-2.5 text-sm font-mono focus:outline-none focus:border-brand"
              />
              <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono text-muted-foreground bg-white/5 border border-border px-1.5 py-0.5 rounded">
                /
              </kbd>
            </div>
            <div className="flex gap-1 p-1 border border-border rounded bg-sidebar">
              {STATUSES.map((f, i) => (
                <button
                  key={f}
                  onClick={() => setSearch({ status: f })}
                  className={cn(
                    "px-3 py-1 text-[11px] font-mono uppercase tracking-widest rounded flex items-center gap-1.5",
                    status === f
                      ? "bg-brand text-black"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {f}
                  <span
                    className={cn("text-[9px] opacity-60", status === f ? "text-black/60" : "")}
                  >
                    {i + 1}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 mb-6">
            <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground mr-1">
              Tags
            </span>
            {tagOptions.map((t) => {
              const on = tags.includes(t);
              return (
                <button
                  key={t}
                  onClick={() =>
                    setSearch({
                      tags: on ? tags.filter((x) => x !== t) : [...tags, t],
                    })
                  }
                  className={cn(
                    "px-2.5 py-1 text-[10px] font-mono uppercase tracking-widest rounded border",
                    on
                      ? "bg-brand/15 border-brand/50 text-brand"
                      : "border-border text-muted-foreground hover:text-foreground",
                  )}
                >
                  {t}
                </button>
              );
            })}

            <div className="ml-auto flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                Sort
              </span>
              <select
                value={sort}
                onChange={(e) => setSearch({ sort: e.target.value as SearchState["sort"] })}
                className="bg-sidebar border border-border rounded px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-foreground focus:outline-none focus:border-brand"
              >
                {SORTS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setSearch({ dir: dir === "asc" ? "desc" : "asc" })}
                className="size-7 grid place-items-center border border-border rounded text-muted-foreground hover:text-foreground"
                aria-label="Toggle sort direction"
              >
                {dir === "asc" ? (
                  <ArrowUp className="size-3.5" />
                ) : (
                  <ArrowDown className="size-3.5" />
                )}
              </button>
              <div className="flex border border-border rounded overflow-hidden">
                {VIEWS.map((v) => (
                  <button
                    key={v}
                    onClick={() => setSearch({ view: v })}
                    className={cn(
                      "px-2 py-1 text-[10px] font-mono uppercase tracking-widest",
                      view === v
                        ? "bg-brand text-black"
                        : "text-muted-foreground hover:text-foreground",
                    )}
                  >
                    {v}
                  </button>
                ))}
              </div>
              {filtersActive && (
                <button
                  onClick={clearFilters}
                  className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-destructive flex items-center gap-1"
                >
                  <X className="size-3" />
                  Reset
                  <kbd className="border border-border/60 px-1 rounded text-[9px] ml-1">C</kbd>
                </button>
              )}
            </div>
          </div>

          {selectMode && (
            <div className="mb-6 flex flex-wrap items-center gap-2 border border-brand/40 bg-brand/5 rounded px-3 py-2 text-[11px] font-mono uppercase tracking-widest">
              <span className="text-brand">{librarySelection.length} selected</span>
              <button
                onClick={selectAllVisible}
                className="px-2 py-1 border border-border rounded text-muted-foreground hover:text-foreground"
              >
                Select visible ({visibleProjects.length})
              </button>
              <button
                onClick={clearLibrarySelection}
                className="px-2 py-1 border border-border rounded text-muted-foreground hover:text-foreground"
              >
                Clear
              </button>
              <div className="ml-auto flex items-center gap-2">
                <button
                  disabled={!librarySelection.length}
                  onClick={stageSelected}
                  className="px-3 py-1 border border-brand text-brand rounded hover:bg-brand hover:text-black disabled:opacity-40"
                >
                  Stage → tray
                </button>
                <button
                  disabled={!librarySelection.length}
                  onClick={() => void deliverAsJobs()}
                  className="px-3 py-1 bg-brand text-black rounded hover:bg-brand/90 disabled:opacity-40"
                >
                  Deliver as {librarySelection.length} jobs
                </button>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
              <p className="text-xs text-muted-foreground font-mono mt-1">
                {visibleProjects.length} of {projects.length} shown · {healthReport.outputSizeGb} GB
                on disk · sort {sort}/{dir}
              </p>
            </div>
          </div>

          {visibleProjects.length === 0 ? (
            <EmptyBlock
              icon={PackageOpen}
              title="No projects match these filters"
              hint={
                <>
                  {q && (
                    <div>
                      Query: <span className="text-foreground">"{q}"</span>
                    </div>
                  )}
                  Try clearing filters or a broader search.
                </>
              }
              action={
                <button
                  onClick={clearFilters}
                  className="px-4 py-1.5 border border-brand text-brand text-xs font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors"
                >
                  Clear filters
                </button>
              }
            />
          ) : view === "list" ? (
            <div className="border border-border rounded-lg overflow-hidden divide-y divide-border">
              {visibleProjects.map((p) => {
                const latest = latestRunForProject(state, p.id);
                const selected = librarySelection.includes(p.id);
                const runCount = runsInProject(state, p.id).length;
                const row = (
                  <div className="flex items-center gap-4 px-4 py-3 bg-sidebar hover:bg-white/[0.03]">
                    {selectMode && (
                      <div
                        className={cn(
                          "size-4 border rounded grid place-items-center shrink-0",
                          selected ? "bg-brand border-brand" : "border-border",
                        )}
                      >
                        {selected && <CheckSquare className="size-3 text-black" />}
                      </div>
                    )}
                    <span className={cn("size-1.5 rounded-full shrink-0", HEALTH_DOT[p.health])} />
                    <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest w-24 shrink-0">
                      {p.code}
                    </span>
                    <span className="flex-1 min-w-0 truncate text-sm">{p.name}</span>
                    <span className="text-[10px] font-mono text-muted-foreground shrink-0">
                      {runCount} runs
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground shrink-0">
                      {p.imageCount} img
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground shrink-0">
                      {new Date(p.updatedAt).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })}
                    </span>
                  </div>
                );
                return selectMode ? (
                  <button
                    key={p.id}
                    onClick={() => toggleLibrarySelection(p.id)}
                    className="w-full text-left"
                  >
                    {row}
                  </button>
                ) : latest ? (
                  <Link key={p.id} to="/library/$runId" params={{ runId: latest.id }}>
                    {row}
                  </Link>
                ) : (
                  <div key={p.id} className="opacity-70">
                    {row}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {visibleProjects.map((p) => {
                const latest = latestRunForProject(state, p.id);
                const thumbs = projectThumbs(state, p.id);
                const thumbTiles: Array<ImageRecord | null> = thumbs.length
                  ? thumbs
                  : [null, null, null, null];
                const runCount = runsInProject(state, p.id).length;
                const selected = librarySelection.includes(p.id);
                const inner = (
                  <>
                    <div className="grid grid-cols-2 grid-rows-2 gap-px aspect-[16/9] bg-black relative">
                      {thumbTiles.map((thumb, i) => (
                        <div
                          key={i}
                          className="relative w-full h-full overflow-hidden"
                          style={{
                            background: thumb
                              ? `linear-gradient(135deg, ${thumb.swatch} 0%, #0c0c0c 140%)`
                              : "#0c0c0c",
                          }}
                        >
                          {thumb && (
                            <img
                              src={thumb.thumbnailUrl || thumb.url}
                              alt={thumb.name}
                              className="absolute inset-0 h-full w-full object-cover"
                              loading="lazy"
                            />
                          )}
                        </div>
                      ))}
                      {selectMode && (
                        <div
                          className={cn(
                            "absolute top-2 left-2 size-6 rounded border grid place-items-center backdrop-blur",
                            selected ? "bg-brand border-brand" : "bg-black/60 border-border",
                          )}
                        >
                          {selected && <CheckSquare className="size-3.5 text-black" />}
                        </div>
                      )}
                    </div>
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                          {p.code}
                        </span>
                        <span className={cn("size-1.5 rounded-full", HEALTH_DOT[p.health])} />
                      </div>
                      <h3 className="text-sm font-medium">{p.name}</h3>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {p.tags.map((t) => (
                          <span
                            key={t}
                            className="text-[9px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded bg-white/5 text-muted-foreground"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center gap-4 mt-3 text-[11px] font-mono text-muted-foreground">
                        <span>{runCount} runs</span>
                        <span>{p.imageCount} images</span>
                        <span className="ml-auto">
                          {new Date(p.updatedAt).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                          })}
                        </span>
                      </div>
                    </div>
                  </>
                );
                if (selectMode) {
                  return (
                    <button
                      key={p.id}
                      onClick={() => toggleLibrarySelection(p.id)}
                      className={cn(
                        "text-left group bg-sidebar border rounded-lg overflow-hidden rf-hover-lift rf-press",
                        selected ? "border-brand" : "border-border",
                      )}
                    >
                      {inner}
                    </button>
                  );
                }
                return latest ? (
                  <Link
                    key={p.id}
                    to="/library/$runId"
                    params={{ runId: latest.id }}
                    className="group bg-sidebar border border-border rounded-lg overflow-hidden rf-hover-lift rf-press"
                  >
                    {inner}
                  </Link>
                ) : (
                  <div
                    key={p.id}
                    className="group bg-sidebar border border-border rounded-lg overflow-hidden opacity-70"
                  >
                    {inner}
                  </div>
                );
              })}
            </div>
          )}
        </div>
        <ExportDock />
      </div>
    </AppShell>
  );
}

function Stat({
  label,
  value,
  tone,
}: {
  label: string;
  value: number | string;
  tone?: "destructive" | "brand";
}) {
  return (
    <div className="bg-sidebar p-4">
      <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
        {label}
      </div>
      <div
        className={cn(
          "text-2xl font-semibold mt-2 font-mono tracking-tight",
          tone === "destructive" && "text-destructive",
          tone === "brand" && "text-brand",
        )}
      >
        {value}
      </div>
    </div>
  );
}
