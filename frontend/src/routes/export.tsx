import { createFileRoute, Link, useRouter } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Trash2,
  Package,
  CheckCircle2,
  AlertTriangle,
  Download,
  X,
  ArrowUp,
  ArrowDown,
  RotateCcw,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { Thumbnail } from "@/components/thumbnail";
import { EmptyBlock } from "@/components/state/empty-block";
import { ErrorBlock } from "@/components/state/error-block";
import { getImage, getProject, useLibraryState, type LibraryState } from "@/lib/rafiki-data";
import { useTriageStore } from "@/stores/triage-store";
import { MANIFEST_FIELDS, type ExportFormat, type ManifestField } from "@/lib/exporter";
import { retryJob, startBatchExport } from "@/lib/run-batch";
import { useShortcuts } from "@/lib/shortcuts";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/export")({
  head: () => ({
    meta: [
      { title: "Export — Rafiki" },
      {
        name: "description",
        content: "Stage keepers and process a delivery batch.",
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
  component: ExportPage,
});

const FORMATS: { id: ExportFormat; label: string; hint: string }[] = [
  { id: "zip", label: "ZIP + manifest", hint: "Rendered PNGs + manifest.json" },
  { id: "manifest", label: "Manifest", hint: "Metadata JSON only" },
  { id: "csv", label: "CSV", hint: "Flat spreadsheet export" },
];

function ExportPage() {
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
        <PageHeader crumbs={[{ label: "LOCAL", mono: true }, { label: "Export" }]} />
        <div className="p-16 text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Loading staged assets…
        </div>
      </AppShell>
    );
  }

  return <ExportContent state={data} />;
}

function ExportContent({ state }: { state: LibraryState }) {
  const tray = useTriageStore((s) => s.tray);
  const removeFromTray = useTriageStore((s) => s.removeFromTray);
  const clearTray = useTriageStore((s) => s.clearTray);
  const jobs = useTriageStore((s) => s.jobs);
  const dismissJob = useTriageStore((s) => s.dismissJob);
  const dismissCompleted = useTriageStore((s) => s.dismissCompleted);
  const manifestPrefs = useTriageStore((s) => s.manifestPrefs);
  const setManifestPrefs = useTriageStore((s) => s.setManifestPrefs);

  const [destination, setDestination] = useState("~/Deliveries/Rafiki");
  const [format, setFormat] = useState<ExportFormat>("zip");
  const [template, setTemplate] = useState("{project}_{run}_{slot}");
  const [simulateFailure, setSimulateFailure] = useState(false);

  const items = tray
    .map((id) => getImage(state, id))
    .filter((x): x is NonNullable<typeof x> => Boolean(x));

  const activeJob = jobs.find(
    (j) => j.stage === "queued" || j.stage === "encoding" || j.stage === "packaging",
  );
  const lastFailed = jobs.find((j) => j.stage === "error");
  const doneCount = jobs.filter((j) => j.stage === "done").length;

  const handleDeliver = async () => {
    if (items.length === 0 || activeJob) return;
    await startBatchExport([{ label: "Staged batch", imageIds: items.map((i) => i.id) }], {
      format,
      destination,
      template,
      filenameTemplate: manifestPrefs.filenameTemplate,
      fields: manifestPrefs.fields,
      simulateFailure,
    });
  };

  const cycleFormat = () => {
    setFormat((f) => (f === "zip" ? "manifest" : f === "manifest" ? "csv" : "zip"));
  };

  useShortcuts([
    { combo: "enter", handler: () => void handleDeliver() },
    { combo: "f", handler: () => cycleFormat() },
    { combo: "r", handler: () => lastFailed && void retryJob(lastFailed.id) },
    { combo: "d", handler: () => dismissCompleted() },
  ]);

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "LOCAL", mono: true }, { label: "Export" }]}
        actions={
          <div className="text-xs font-mono text-muted-foreground">
            {tray.length} staged · {jobs.length} jobs
          </div>
        }
      />

      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_420px] gap-0 min-h-full">
          <section className="p-8 border-r border-border space-y-8">
            <div>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-2xl font-semibold">Staged for delivery</h1>
                  <p className="text-xs text-muted-foreground font-mono mt-1">
                    Items you've added from the Viewer or Library.
                  </p>
                </div>
                {tray.length > 0 && (
                  <button
                    onClick={clearTray}
                    className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground hover:text-destructive flex items-center gap-2"
                  >
                    <Trash2 className="size-3.5" />
                    Clear all
                  </button>
                )}
              </div>

              {items.length === 0 ? (
                <EmptyBlock
                  icon={Package}
                  title="Nothing staged yet"
                  hint={
                    <>
                      Press <kbd className="border border-border px-1 rounded">E</kbd> in the
                      Viewer, use + on a thumbnail, or bulk-select in the Library.
                    </>
                  }
                  action={
                    <Link
                      to="/library"
                      className="inline-block px-4 py-1.5 border border-brand text-brand text-xs font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors"
                    >
                      Browse Library
                    </Link>
                  }
                />
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {items.map((img) => {
                    const project = getProject(state, img.projectId);
                    const bad = img.status === "failed" || img.status === "missing";
                    return (
                      <div
                        key={img.id}
                        className={cn(
                          "group bg-sidebar border rounded-lg overflow-hidden",
                          bad ? "border-destructive/40" : "border-border",
                        )}
                      >
                        <Thumbnail image={img} className="w-full aspect-square rounded-none" />
                        <div className="p-3">
                          <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest truncate">
                            {project?.code}
                          </div>
                          <div className="text-sm truncate">{img.name}</div>
                          {bad && (
                            <div className="mt-1 text-[10px] font-mono text-destructive uppercase tracking-widest">
                              Source {img.status}
                            </div>
                          )}
                          <button
                            onClick={() => removeFromTray(img.id)}
                            className="mt-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-destructive"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {jobs.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
                    Jobs · {doneCount}/{jobs.length} complete
                    {lastFailed && <span className="text-destructive"> · 1+ failed</span>}
                  </h2>
                  <div className="flex items-center gap-2">
                    {lastFailed && (
                      <button
                        onClick={() => void retryJob(lastFailed.id)}
                        className="px-2.5 py-1 border border-destructive/50 text-destructive text-[10px] font-mono uppercase tracking-widest rounded hover:bg-destructive/10 flex items-center gap-1.5"
                      >
                        <RotateCcw className="size-3" />
                        Retry last
                        <kbd className="ml-1 border border-border px-1 rounded">R</kbd>
                      </button>
                    )}
                    {doneCount > 0 && (
                      <button
                        onClick={dismissCompleted}
                        className="px-2.5 py-1 border border-border text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground rounded flex items-center gap-1.5"
                      >
                        Dismiss done
                        <kbd className="ml-1 border border-border px-1 rounded">D</kbd>
                      </button>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  {jobs.map((j) => {
                    const pct = j.total === 0 ? 0 : Math.round((j.processed / j.total) * 100);
                    return (
                      <div
                        key={j.id}
                        className={cn(
                          "border rounded-lg p-4 bg-sidebar",
                          j.stage === "done"
                            ? "border-brand/40"
                            : j.stage === "error"
                              ? "border-destructive/40"
                              : "border-border",
                        )}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2 min-w-0">
                            {j.stage === "done" && (
                              <CheckCircle2 className="size-4 text-brand shrink-0" />
                            )}
                            {j.stage === "error" && (
                              <AlertTriangle className="size-4 text-destructive shrink-0" />
                            )}
                            <span className="text-xs font-mono uppercase tracking-widest truncate">
                              {j.label} · {j.stage} · {j.total} · {j.format}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            {j.stage === "error" && (
                              <button
                                onClick={() => void retryJob(j.id)}
                                className="px-2.5 py-1 border border-destructive/50 text-destructive text-[10px] font-mono uppercase tracking-widest rounded hover:bg-destructive/10 flex items-center gap-1"
                              >
                                <RotateCcw className="size-3" />
                                Retry
                              </button>
                            )}
                            {j.stage === "done" && j.result && (
                              <a
                                href={j.result.blobUrl}
                                download={j.result.filename}
                                className="px-3 py-1 border border-brand text-brand text-[10px] font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors flex items-center gap-1.5"
                              >
                                <Download className="size-3" />
                                Download
                              </a>
                            )}
                            {(j.stage === "done" || j.stage === "error") && (
                              <button
                                onClick={() => {
                                  if (j.result) URL.revokeObjectURL(j.result.blobUrl);
                                  dismissJob(j.id);
                                }}
                                className="size-6 grid place-items-center rounded border border-border text-muted-foreground hover:text-foreground"
                                aria-label="Dismiss"
                              >
                                <X className="size-3" />
                              </button>
                            )}
                          </div>
                        </div>
                        {j.stage !== "error" && (
                          <div className="h-1.5 bg-black/60 rounded overflow-hidden">
                            <div
                              className={cn(
                                "h-full transition-all",
                                j.stage === "done" ? "bg-brand" : "bg-brand/60",
                              )}
                              style={{
                                width: `${Math.max(j.stage === "done" ? 100 : 4, pct)}%`,
                              }}
                            />
                          </div>
                        )}
                        <div className="mt-2 text-[10px] font-mono text-muted-foreground">
                          {j.error ?? j.message ?? (j.stage === "queued" ? "Waiting…" : "")}
                          {j.stage === "done" && j.result && <span> · {j.result.filename}</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </section>

          <aside className="p-8 bg-sidebar/40 space-y-6">
            <div>
              <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-6">
                Delivery
              </h2>
              <div className="space-y-5">
                <Field label="Destination folder">
                  <input
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="w-full bg-black border border-border rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-brand"
                  />
                </Field>

                <Field
                  label={
                    <>
                      Format{" "}
                      <kbd className="ml-1 border border-border px-1 rounded text-[9px]">F</kbd>
                    </>
                  }
                >
                  <div className="space-y-2">
                    {FORMATS.map((f) => (
                      <button
                        key={f.id}
                        onClick={() => setFormat(f.id)}
                        className={cn(
                          "w-full text-left px-3 py-2 rounded border transition-colors",
                          format === f.id
                            ? "bg-brand/10 border-brand/50 text-foreground"
                            : "border-border text-muted-foreground hover:text-foreground",
                        )}
                      >
                        <div className="text-xs font-mono uppercase tracking-widest">{f.label}</div>
                        <div className="text-[10px] font-mono text-muted-foreground mt-0.5">
                          {f.hint}
                        </div>
                      </button>
                    ))}
                  </div>
                </Field>

                <Field label="File-name template (per image)">
                  <input
                    value={template}
                    onChange={(e) => setTemplate(e.target.value)}
                    className="w-full bg-black border border-border rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-brand"
                  />
                  <p className="text-[10px] font-mono text-muted-foreground mt-1.5">
                    Tokens:{" "}
                    <span className="text-foreground/80">{"{project} {run} {slot} {name}"}</span>
                  </p>
                </Field>

                <label className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground cursor-pointer">
                  <input
                    type="checkbox"
                    checked={simulateFailure}
                    onChange={(e) => setSimulateFailure(e.target.checked)}
                    className="accent-destructive"
                  />
                  Simulate failure
                </label>

                <button
                  disabled={items.length === 0 || Boolean(activeJob)}
                  onClick={() => void handleDeliver()}
                  className="w-full py-3 bg-brand text-black text-xs font-bold font-mono uppercase tracking-widest rounded hover:bg-brand/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {activeJob ? "Delivering…" : `Deliver ${items.length || ""}`}
                  {!activeJob && items.length > 0 && (
                    <kbd className="ml-1 bg-black/20 border border-black/20 px-1 rounded text-[9px]">
                      ↵
                    </kbd>
                  )}
                </button>
              </div>
            </div>

            <ManifestOptions prefs={manifestPrefs} onChange={setManifestPrefs} />
          </aside>
        </div>
      </div>
    </AppShell>
  );
}

function ManifestOptions({
  prefs,
  onChange,
}: {
  prefs: { filenameTemplate: string; fields: ManifestField[] };
  onChange: (patch: { filenameTemplate?: string; fields?: ManifestField[] }) => void;
}) {
  const filenamePreview = useMemo(() => {
    const stem =
      prefs.filenameTemplate
        .replace(/{date}/g, new Date().toISOString().slice(0, 10))
        .replace(/{count}/g, "12")
        .replace(/{project}/g, "prj-0822")
        .replace(/{format}/g, "zip")
        .replace(/[^\w.-]+/g, "_") || "rafiki-batch";
    return `${stem}.zip`;
  }, [prefs.filenameTemplate]);

  const toggleField = (f: ManifestField) => {
    if (prefs.fields.includes(f)) {
      onChange({ fields: prefs.fields.filter((x) => x !== f) });
    } else {
      onChange({ fields: [...prefs.fields, f] });
    }
  };

  const move = (idx: number, dir: -1 | 1) => {
    const next = prefs.fields.slice();
    const j = idx + dir;
    if (j < 0 || j >= next.length) return;
    [next[idx], next[j]] = [next[j], next[idx]];
    onChange({ fields: next });
  };

  const inactive = MANIFEST_FIELDS.filter((f) => !prefs.fields.includes(f));

  return (
    <div className="border-t border-border pt-6">
      <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">
        Manifest
      </h2>
      <div className="space-y-5">
        <Field label="Bundle file name">
          <input
            value={prefs.filenameTemplate}
            onChange={(e) => onChange({ filenameTemplate: e.target.value })}
            placeholder="rafiki-{project}-{date}"
            className="w-full bg-black border border-border rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-brand"
          />
          <p className="text-[10px] font-mono text-muted-foreground mt-1.5">
            Tokens:{" "}
            <span className="text-foreground/80">{"{date} {count} {project} {format}"}</span>
          </p>
          <p className="text-[10px] font-mono text-muted-foreground mt-1">
            Preview: <span className="text-foreground/80">{filenamePreview}</span>
          </p>
        </Field>

        <Field label={`Fields (${prefs.fields.length})`}>
          <ol className="space-y-1">
            {prefs.fields.map((f, i) => (
              <li
                key={f}
                className="flex items-center justify-between gap-2 px-2 py-1 rounded border border-border bg-black/40"
              >
                <span className="text-[11px] font-mono text-foreground">
                  {i + 1}. {f}
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => move(i, -1)}
                    disabled={i === 0}
                    className="size-5 grid place-items-center border border-border rounded text-muted-foreground hover:text-foreground disabled:opacity-30"
                    aria-label={`Move ${f} up`}
                  >
                    <ArrowUp className="size-3" />
                  </button>
                  <button
                    onClick={() => move(i, 1)}
                    disabled={i === prefs.fields.length - 1}
                    className="size-5 grid place-items-center border border-border rounded text-muted-foreground hover:text-foreground disabled:opacity-30"
                    aria-label={`Move ${f} down`}
                  >
                    <ArrowDown className="size-3" />
                  </button>
                  <button
                    onClick={() => toggleField(f)}
                    className="size-5 grid place-items-center border border-border rounded text-muted-foreground hover:text-destructive"
                    aria-label={`Remove ${f}`}
                  >
                    <X className="size-3" />
                  </button>
                </div>
              </li>
            ))}
          </ol>
          {inactive.length > 0 && (
            <div className="mt-2">
              <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground mb-1.5">
                Add
              </div>
              <div className="flex flex-wrap gap-1.5">
                {inactive.map((f) => (
                  <button
                    key={f}
                    onClick={() => toggleField(f)}
                    className="px-2 py-1 border border-border rounded text-[10px] font-mono text-muted-foreground hover:text-brand hover:border-brand/50"
                  >
                    + {f}
                  </button>
                ))}
              </div>
            </div>
          )}
        </Field>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-[10px] font-mono uppercase tracking-widest text-muted-foreground mb-2">
        {label}
      </label>
      {children}
    </div>
  );
}
