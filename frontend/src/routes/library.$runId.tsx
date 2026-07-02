import { createFileRoute, Link, useRouter } from "@tanstack/react-router";
import { Check, X, Plus, ImageOff } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ExportDock } from "@/components/export-dock";
import { Thumbnail } from "@/components/thumbnail";
import { EmptyBlock } from "@/components/state/empty-block";
import { ErrorBlock } from "@/components/state/error-block";
import { NotFoundBlock } from "@/components/state/not-found-block";
import {
  effectiveRating,
  getProject,
  getRun,
  imagesInRun,
  useLibraryState,
  type ImageRecord,
} from "@/lib/rafiki-data";
import { useTriageStore } from "@/stores/triage-store";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/library/$runId")({
  head: () => ({
    meta: [
      {
        title: "Run — Rafiki",
      },
      {
        name: "description",
        content: "Triage a run's images and stage keepers for export.",
      },
    ],
  }),
  notFoundComponent: () => (
    <AppShell>
      <NotFoundBlock label="Run not found" hint="That run isn't in the local archive." />
    </AppShell>
  ),
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
  component: RunPage,
});

function RunPage() {
  const { runId } = Route.useParams();
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
        <div className="p-16 text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Loading run…
        </div>
      </AppShell>
    );
  }

  const run = getRun(data, runId);
  if (!run) {
    return (
      <AppShell>
        <NotFoundBlock label="Run not found" hint="That run isn't in the local archive." />
      </AppShell>
    );
  }

  const project = getProject(data, run.projectId);
  const runImages = imagesInRun(data, run.id);

  return <RunContent run={run} project={project} runImages={runImages} />;
}

function RunContent({
  run,
  project,
  runImages,
}: {
  run: NonNullable<ReturnType<typeof getRun>>;
  project: ReturnType<typeof getProject>;
  runImages: ImageRecord[];
}) {
  const { ratings, star, reject, tray, toggleTray } = useTriageStore();

  return (
    <AppShell>
      <PageHeader
        crumbs={[
          { label: project?.code ?? run.projectId, mono: true },
          { label: project?.name ?? run.projectId },
          { label: run.label, mono: true },
        ]}
        actions={
          <>
            <div className="px-3 py-1.5 bg-white/5 border border-border rounded text-xs font-mono text-muted-foreground">
              {runImages.length} images
            </div>
            {runImages[0] && (
              <Link
                to="/viewer/$imageId"
                params={{ imageId: runImages[0].id }}
                className="px-4 py-1.5 bg-brand text-black text-xs font-bold rounded hover:bg-brand/90 font-mono tracking-wider uppercase"
              >
                Open Viewer
              </Link>
            )}
          </>
        }
      />

      <div className="relative flex-1 overflow-y-auto">
        <div className="p-4 pb-32 sm:p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-semibold tracking-tight">{run.label}</h1>
            <p className="mt-1 text-xs font-mono text-muted-foreground">
              {project?.name ?? run.projectId} · {runImages.length} images
            </p>
          </div>
          {runImages.length === 0 ? (
            <EmptyBlock
              icon={ImageOff}
              title="This run has no images yet"
              hint="Generate a batch or check that the run's manifest is intact."
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {runImages.map((img) => {
                const rating = effectiveRating(img, ratings);
                const staged = tray.includes(img.id);
                return (
                  <div
                    key={img.id}
                    className={cn(
                      "group bg-sidebar border rounded-lg overflow-hidden flex flex-col transition-colors",
                      rating === "starred"
                        ? "border-brand/60"
                        : rating === "rejected"
                          ? "border-destructive/50 opacity-70"
                          : "border-border hover:border-white/20",
                    )}
                  >
                    <Link
                      to="/viewer/$imageId"
                      params={{ imageId: img.id }}
                      className="relative block"
                    >
                      <Thumbnail image={img} className="w-full aspect-[4/3] rounded-none" />
                      {rating && (
                        <div
                          className={cn(
                            "absolute top-2 left-2 px-1.5 py-0.5 rounded text-[10px] font-mono uppercase tracking-widest",
                            rating === "starred"
                              ? "bg-brand text-black"
                              : "bg-destructive text-white",
                          )}
                        >
                          {rating}
                        </div>
                      )}
                      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            star(img.key);
                          }}
                          className="size-10 rounded-full bg-white text-black grid place-items-center hover:bg-brand"
                          aria-label="Star"
                        >
                          <Check className="size-4" strokeWidth={3} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            reject(img.key);
                          }}
                          className="size-10 rounded-full bg-white/15 backdrop-blur text-white grid place-items-center hover:bg-destructive"
                          aria-label="Reject"
                        >
                          <X className="size-4" strokeWidth={3} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            toggleTray(img.id);
                          }}
                          className={cn(
                            "size-10 rounded-full grid place-items-center",
                            staged
                              ? "bg-brand text-black"
                              : "bg-white/15 backdrop-blur text-white hover:bg-white/25",
                          )}
                          aria-label="Stage"
                        >
                          <Plus className="size-4" strokeWidth={3} />
                        </button>
                      </div>
                    </Link>
                    <div className="p-3 flex justify-between items-center border-t border-border">
                      <div className="min-w-0">
                        <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                          Step {img.steps} · Cfg {img.cfg}
                        </p>
                        <p className="text-sm truncate mt-0.5">{img.name}</p>
                      </div>
                      <div className="flex gap-1 shrink-0 ml-2">
                        {[0, 1, 2].map((i) => (
                          <div
                            key={i}
                            className={cn(
                              "size-1.5 rounded-full",
                              rating === "starred" && i < 3 ? "bg-brand" : "bg-white/10",
                            )}
                          />
                        ))}
                      </div>
                    </div>
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
