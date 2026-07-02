import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AlertTriangle, Copy, FileX, ShieldAlert, XCircle } from "lucide-react";
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
        content: "Archive health: missing, failed, duplicates, malformed.",
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
  const [toast, setToast] = useState<string | null>(null);
  const { data, error, isLoading, refetch } = useLibraryState();
  const fire = (label: string) => {
    setToast(`Queued: ${label}`);
    setTimeout(() => setToast(null), 2400);
  };

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
  const cards = [
    {
      key: "missing",
      label: "Missing files",
      value: healthReport.missingRecords,
      icon: FileX,
      tone: "destructive" as const,
      hint: "Manifest records that point to missing image files on disk.",
      action: "Remove missing entries",
    },
    {
      key: "failed",
      label: "Failed generations",
      value: healthReport.failedImages,
      icon: XCircle,
      tone: "destructive" as const,
      hint: "Image records that were flagged as failed outputs.",
      action: "Purge failed",
    },
    {
      key: "duplicates",
      label: "Duplicate groups",
      value: healthReport.duplicateGroups,
      icon: Copy,
      tone: "warn" as const,
      hint: "Filename groups shared across runs — usually reruns or slot repeats.",
      action: "Dedupe",
    },
    {
      key: "malformed",
      label: "Malformed runs",
      value: healthReport.malformedRuns,
      icon: AlertTriangle,
      tone: "warn" as const,
      hint: "Run folders with missing or malformed manifests.",
      action: "Rescan",
    },
    {
      key: "cleanup",
      label: "Cleanup risk",
      value: healthReport.cleanupRisk,
      icon: ShieldAlert,
      tone: "warn" as const,
      hint: "Advisory items flagged by the cleanup pass.",
      action: "Review",
    },
  ];

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "SYSTEM", mono: true }, { label: "Health" }]}
        actions={
          <button
            onClick={() => fire("Full archive rescan")}
            className="px-4 py-1.5 border border-brand text-brand text-xs font-bold font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors"
          >
            Rescan All
          </button>
        }
      />
      <div className="flex-1 overflow-y-auto p-8">
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
                  c.tone === "destructive" ? "border-destructive/30" : "border-amber-400/30",
                )}
              >
                <div className="flex items-start justify-between mb-4">
                  <Icon
                    className={cn(
                      "size-5",
                      c.tone === "destructive" ? "text-destructive" : "text-amber-400",
                    )}
                    strokeWidth={1.5}
                  />
                  <span
                    className={cn(
                      "text-3xl font-mono font-semibold tracking-tight",
                      c.tone === "destructive" ? "text-destructive" : "text-amber-400",
                    )}
                  >
                    {c.value.toLocaleString()}
                  </span>
                </div>
                <div className="text-sm font-medium">{c.label}</div>
                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{c.hint}</p>
                <button
                  onClick={() => fire(c.action)}
                  className="mt-4 w-full py-1.5 border border-border rounded text-[11px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground hover:border-white/30"
                >
                  {c.action}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-6 right-6 bg-sidebar border border-brand/40 rounded px-4 py-3 text-xs font-mono text-brand shadow-2xl">
          {toast}
        </div>
      )}
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
