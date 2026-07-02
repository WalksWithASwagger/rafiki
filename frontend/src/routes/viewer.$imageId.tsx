import { createFileRoute, Link, useNavigate, useRouter } from "@tanstack/react-router";
import { useCallback } from "react";
import { ArrowLeft, Star, X, Plus, ChevronLeft, ChevronRight } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { Thumbnail } from "@/components/thumbnail";
import { NotFoundBlock } from "@/components/state/not-found-block";
import { ErrorBlock } from "@/components/state/error-block";
import {
  effectiveRating,
  getImage,
  getProject,
  getRun,
  imagesInRun,
  useLibraryState,
  type ImageRecord,
  type LibraryState,
} from "@/lib/rafiki-data";
import { useTriageStore } from "@/stores/triage-store";
import { useShortcuts } from "@/lib/shortcuts";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/viewer/$imageId")({
  head: () => ({
    meta: [
      { title: "Image — Viewer" },
      {
        name: "description",
        content: "Keyboard-driven triage viewer for a single image.",
      },
    ],
  }),
  notFoundComponent: () => (
    <AppShell>
      <NotFoundBlock label="Image not found" hint="That image id isn't in the local manifest." />
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
  component: ViewerPage,
});

function ViewerPage() {
  const { imageId } = Route.useParams();
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
          Loading viewer…
        </div>
      </AppShell>
    );
  }

  const image = getImage(data, imageId);
  if (!image) {
    return (
      <AppShell>
        <NotFoundBlock label="Image not found" hint="That image id isn't in the local manifest." />
      </AppShell>
    );
  }

  return <ViewerContent state={data} image={image} />;
}

function ViewerContent({ state, image }: { state: LibraryState; image: ImageRecord }) {
  const navigate = useNavigate();
  const run = getRun(state, image.runId);
  const project = getProject(state, image.projectId);
  const siblings = run ? imagesInRun(state, run.id) : [image];
  const index = siblings.findIndex((i) => i.id === image.id);
  const prev = siblings[index - 1];
  const next = siblings[index + 1];

  const rating = useTriageStore((s) => effectiveRating(image, s.ratings));
  const inTray = useTriageStore((s) => s.tray.includes(image.id));
  const star = useTriageStore((s) => s.star);
  const reject = useTriageStore((s) => s.reject);
  const toggleTray = useTriageStore((s) => s.toggleTray);
  const sheetOpen = useTriageStore((s) => s.shortcutSheetOpen);

  const go = useCallback(
    (id?: string) => {
      if (!id) return;
      navigate({ to: "/viewer/$imageId", params: { imageId: id } });
    },
    [navigate],
  );

  useShortcuts(
    [
      { combo: "j", handler: () => go(prev?.id) },
      { combo: "k", handler: () => go(next?.id) },
      { combo: "s", handler: () => star(image.key) },
      { combo: "x", handler: () => reject(image.key) },
      { combo: "e", handler: () => toggleTray(image.id) },
      {
        combo: "shift+e",
        handler: () => navigate({ to: "/export" }),
      },
      {
        combo: "esc",
        handler: () =>
          navigate({ to: "/library/$runId", params: { runId: run?.id ?? image.runId } }),
      },
    ],
    !sheetOpen,
  );

  return (
    <AppShell>
      <header className="min-h-16 border-b border-border flex flex-wrap items-center justify-between gap-3 px-4 py-3 shrink-0 bg-background/80 backdrop-blur sm:px-8">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            to="/library/$runId"
            params={{ runId: run?.id ?? image.runId }}
            className="flex items-center gap-2 text-xs font-mono text-muted-foreground hover:text-foreground uppercase tracking-widest"
          >
            <ArrowLeft className="size-3.5" strokeWidth={2} />
            Back to run
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-mono text-muted-foreground">
            {project?.code ?? image.projectId}
          </span>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm">{run?.label ?? image.runId}</span>
          <span className="text-muted-foreground">·</span>
          <span className="text-xs font-mono text-muted-foreground">
            {index + 1} / {siblings.length}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => go(prev?.id)}
            disabled={!prev}
            className="size-8 grid place-items-center border border-border rounded text-muted-foreground hover:text-foreground disabled:opacity-30"
            aria-label="Previous"
          >
            <ChevronLeft className="size-4" />
          </button>
          <button
            onClick={() => go(next?.id)}
            disabled={!next}
            className="size-8 grid place-items-center border border-border rounded text-muted-foreground hover:text-foreground disabled:opacity-30"
            aria-label="Next"
          >
            <ChevronRight className="size-4" />
          </button>
        </div>
      </header>

      <div className="flex-1 flex flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <section className="grid min-h-[45vh] place-items-center overflow-hidden bg-black/40 p-4 sm:p-8 lg:min-h-0 lg:flex-1">
          <div className="h-full max-h-full w-full max-w-4xl aspect-square">
            <Thumbnail image={image} className="w-full h-full rounded" showLabel={false} />
          </div>
        </section>

        <aside className="w-full shrink-0 border-t border-border bg-sidebar flex flex-col overflow-hidden lg:w-96 lg:border-l lg:border-t-0">
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                Image
              </span>
              {rating && (
                <span
                  className={cn(
                    "text-[10px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded",
                    rating === "starred"
                      ? "bg-brand text-black"
                      : "bg-destructive/20 text-destructive",
                  )}
                >
                  {rating}
                </span>
              )}
            </div>
            <h1 className="text-lg font-semibold">{image.name}</h1>
            <p className="text-[11px] font-mono text-muted-foreground mt-1">
              slot #{image.slot.toString().padStart(4, "0")}
            </p>
          </div>

          <div className="p-6 flex-1 overflow-y-auto space-y-6">
            <Section title="Prompt">
              <p className="text-[12px] leading-relaxed text-foreground/90 bg-black/40 p-3 rounded border border-border">
                {image.prompt}
              </p>
            </Section>

            <Section title="Parameters">
              <dl className="grid grid-cols-2 gap-y-2 text-[11px] font-mono">
                <Meta label="Model" value={image.model} />
                <Meta label="Sampler" value={image.sampler} />
                <Meta label="Seed" value={image.seed.toString()} />
                <Meta label="Steps" value={image.steps.toString()} />
                <Meta label="CFG" value={image.cfg.toString()} />
                <Meta label="Latency" value={`${(image.latencyMs / 1000).toFixed(2)}s`} />
              </dl>
            </Section>

            <Section title="Triage">
              <div className="flex gap-2">
                <button
                  onClick={() => star(image.key)}
                  className={cn(
                    "flex-1 py-2 rounded border text-xs font-mono uppercase tracking-widest flex items-center justify-center gap-2 transition-colors",
                    rating === "starred"
                      ? "bg-brand text-black border-brand"
                      : "border-border text-muted-foreground hover:text-brand hover:border-brand/50",
                  )}
                >
                  <Star className="size-3.5" />
                  Star
                </button>
                <button
                  onClick={() => reject(image.key)}
                  className={cn(
                    "flex-1 py-2 rounded border text-xs font-mono uppercase tracking-widest flex items-center justify-center gap-2 transition-colors",
                    rating === "rejected"
                      ? "bg-destructive text-white border-destructive"
                      : "border-border text-muted-foreground hover:text-destructive hover:border-destructive/50",
                  )}
                >
                  <X className="size-3.5" />
                  Reject
                </button>
              </div>
              <button
                onClick={() => toggleTray(image.id)}
                className={cn(
                  "mt-2 w-full py-2 rounded border text-xs font-mono uppercase tracking-widest flex items-center justify-center gap-2",
                  inTray
                    ? "bg-brand/15 text-brand border-brand/40"
                    : "border-border text-muted-foreground hover:text-foreground",
                )}
              >
                <Plus className="size-3.5" />
                {inTray ? "Remove from tray" : "Add to export tray"}
              </button>
            </Section>
          </div>

          <div className="p-4 border-t border-border bg-black/30">
            <div className="grid grid-cols-2 gap-y-2 text-[10px] font-mono text-muted-foreground">
              <Kbd k="J" label="Prev" />
              <Kbd k="K" label="Next" />
              <Kbd k="S" label="Star" />
              <Kbd k="X" label="Reject" />
              <Kbd k="E" label="Tray" />
              <Kbd k="Esc" label="Back" />
            </div>
          </div>
        </aside>
      </div>
    </AppShell>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">
        {title}
      </h3>
      {children}
    </section>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <>
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-foreground text-right truncate">{value}</dd>
    </>
  );
}

function Kbd({ k, label }: { k: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="bg-white/5 border border-border px-1.5 py-0.5 rounded text-[10px] font-mono min-w-[24px] text-center text-foreground">
        {k}
      </span>
      <span>{label}</span>
    </div>
  );
}
