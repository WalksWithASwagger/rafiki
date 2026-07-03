import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, Copy, FileX, History, ShieldAlert } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { useLibraryState } from "@/lib/rafiki-data";
import { cn } from "@/lib/utils";

import { ErrorBlock } from "@/components/state/error-block";

export const Route = createFileRoute("/health")({
  head: () => ({
    meta: [
      { title: "Health — Rafiki" },
      {
        name: "description",
        content: "Archive health: missing, historical failures, filename reuse, malformed.",
      },
    ],
  }),
  errorComponent: ({ error, reset }) => (
    <AppShell>
      <ErrorBlock error={error} reset={reset} />
    </AppShell>
  ),
  component: HealthPage,
});

function HealthPage() {
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
        <PageHeader crumbs={[{ label: "SYSTEM", mono: true }, { label: "Health" }]} />
        <div className="p-16 text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Loading archive health…
        </div>
      </AppShell>
    );
  }

  const healthReport = data.health;
  const offlineRoots = data.sourceWarnings.filter(
    (warning) => warning.kind === "missing-extra-root",
  );
  const otherSourceWarnings = data.sourceWarnings.filter(
    (warning) => warning.kind !== "missing-extra-root",
  );
  const cards = [
    {
      key: "missing",
      label: "Missing files",
      value: healthReport.missingRecords,
      icon: FileX,
      tone: healthReport.missingRecords > 0 ? ("destructive" as const) : ("ok" as const),
      hint: "Manifest records that point to missing image files on disk.",
      nextStep: healthReport.missingRecords > 0 ? "Repair or quarantine stale records." : "Clear.",
    },
    {
      key: "failed",
      label: "Historical failures",
      value: healthReport.failedImages,
      icon: History,
      tone: "info" as const,
      hint: "Generation attempts that failed and are kept as run history.",
      nextStep: "Accepted. No regeneration planned.",
    },
    {
      key: "duplicates",
      label: "Filename reuse",
      value: healthReport.duplicateGroups,
      icon: Copy,
      tone: "info" as const,
      hint: "Repeated filenames across runs. Exact byte duplicates are handled by repair.",
      nextStep: "Informational unless deleting reruns.",
    },
    {
      key: "malformed",
      label: "Malformed runs",
      value: healthReport.malformedRuns,
      icon: AlertTriangle,
      tone: healthReport.malformedRuns > 0 ? ("warn" as const) : ("ok" as const),
      hint: "Run folders with missing or malformed manifests.",
      nextStep: healthReport.malformedRuns > 0 ? "Repair or quarantine malformed runs." : "Clear.",
    },
    {
      key: "cleanup",
      label: "Cleanup risk",
      value: healthReport.cleanupRisk,
      icon: ShieldAlert,
      tone: healthReport.cleanupRisk > 0 ? ("warn" as const) : ("ok" as const),
      hint: "Advisory items flagged by the cleanup pass.",
      nextStep: healthReport.cleanupRisk > 0 ? "Resolve before destructive cleanup." : "Clear.",
    },
  ];

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "SYSTEM", mono: true }, { label: "Health" }]}
        actions={
          <span className="inline-flex items-center gap-2 rounded border border-border px-3 py-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground">
            <CheckCircle2 className="size-3.5 text-brand" strokeWidth={1.5} />
            Read-only report
          </span>
        }
      />
      <div className="flex-1 overflow-y-auto p-4 sm:p-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border border border-border rounded-lg overflow-hidden mb-10">
          <Summary label="Manifest images" value={healthReport.manifestImages} />
          <Summary label="Present" value={healthReport.presentImages} tone="brand" />
          <Summary label="Files on disk" value={healthReport.imageFiles} />
          <Summary label="Output size" value={`${healthReport.outputSizeGb} GB`} />
        </div>

        <h1 className="text-2xl font-semibold mb-6">Advisories</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cards.map((c) => {
            const Icon = c.icon;
            return (
              <div
                key={c.key}
                className={cn(
                  "border rounded-lg p-5 bg-sidebar",
                  c.tone === "destructive" && "border-destructive/30",
                  c.tone === "warn" && "border-amber-400/30",
                  c.tone === "info" && "border-blue-300/20",
                  c.tone === "ok" && "border-brand/25",
                )}
              >
                <div className="flex items-start justify-between mb-4">
                  <Icon
                    className={cn(
                      "size-5",
                      c.tone === "destructive" && "text-destructive",
                      c.tone === "warn" && "text-amber-400",
                      c.tone === "info" && "text-blue-300",
                      c.tone === "ok" && "text-brand",
                    )}
                    strokeWidth={1.5}
                  />
                  <span
                    className={cn(
                      "text-3xl font-mono font-semibold tracking-tight",
                      c.tone === "destructive" && "text-destructive",
                      c.tone === "warn" && "text-amber-400",
                      c.tone === "info" && "text-blue-300",
                      c.tone === "ok" && "text-brand",
                    )}
                  >
                    {c.value.toLocaleString()}
                  </span>
                </div>
                <div className="text-sm font-medium">{c.label}</div>
                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{c.hint}</p>
                <div className="mt-4 rounded border border-border px-3 py-2 text-[11px] font-mono uppercase tracking-widest text-muted-foreground">
                  {c.nextStep}
                </div>
              </div>
            );
          })}
        </div>

        {(offlineRoots.length > 0 ||
          otherSourceWarnings.length > 0 ||
          healthReport.warnings.length > 0) && (
          <section className="mt-10 space-y-3">
            <h2 className="text-lg font-semibold">Archive notes</h2>
            {offlineRoots.length > 0 && (
              <div className="rounded border border-border bg-sidebar p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                      Offline local mounts
                    </div>
                    <p className="mt-2 text-sm text-foreground">
                      {offlineRoots.length.toLocaleString()} configured extra output root
                      {offlineRoots.length === 1 ? " is" : "s are"} not mounted. These do not block
                      archive review.
                    </p>
                  </div>
                  <span className="font-mono text-2xl text-muted-foreground">
                    {offlineRoots.length.toLocaleString()}
                  </span>
                </div>
                <div className="mt-3 grid gap-2 text-xs font-mono text-muted-foreground">
                  {offlineRoots.slice(0, 6).map((warning) => (
                    <div key={`${warning.kind}-${warning.project}`} className="min-w-0">
                      <span className="text-foreground">{warning.project}</span>
                      <span className="mx-2">·</span>
                      <span className="break-all">{warning.path}</span>
                    </div>
                  ))}
                  {offlineRoots.length > 6 && (
                    <div>
                      {(offlineRoots.length - 6).toLocaleString()} more local mount notes hidden.
                    </div>
                  )}
                </div>
              </div>
            )}
            {otherSourceWarnings.map((warning) => (
              <div
                key={`${warning.kind}-${warning.project}`}
                className="rounded border border-border bg-sidebar p-4"
              >
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  {warning.project}
                </div>
                <p className="mt-2 text-sm text-foreground">{warning.message}</p>
                <p className="mt-1 break-all text-xs font-mono text-muted-foreground">
                  {warning.path}
                </p>
              </div>
            ))}
            {healthReport.warnings.map((warning) => (
              <div key={warning} className="rounded border border-border bg-sidebar p-4 text-sm">
                {warning}
              </div>
            ))}
          </section>
        )}
      </div>
    </AppShell>
  );
}

function Summary({
  label,
  value,
  tone,
}: {
  label: string;
  value: number | string;
  tone?: "brand";
}) {
  return (
    <div className="bg-sidebar p-5">
      <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
        {label}
      </div>
      <div
        className={cn(
          "text-2xl font-semibold mt-2 font-mono tracking-tight",
          tone === "brand" && "text-brand",
        )}
      >
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
    </div>
  );
}
