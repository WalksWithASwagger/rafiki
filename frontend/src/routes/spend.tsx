import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AlertTriangle, DollarSign, RefreshCw } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ErrorBlock } from "@/components/state/error-block";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/spend")({
  head: () => ({
    meta: [
      { title: "Spend — Rafiki" },
      {
        name: "description",
        content: "Local generation spend tracking.",
      },
    ],
  }),
  errorComponent: ({ error, reset }) => (
    <AppShell>
      <ErrorBlock error={error} reset={reset} />
    </AppShell>
  ),
  component: SpendPage,
});

type UsageSummary = {
  usage_log?: {
    entries?: number;
    successful_entries?: number;
    failed_entries?: number;
    total_images?: number;
  };
  archive?: {
    projects?: number;
    runs?: number;
    images?: number;
    failed_images?: number;
    duration_seconds?: number;
    spend?: { currency?: string; amount?: number; basis?: string };
    estimated_cost?: {
      amount?: number;
      profile_estimated_images?: number;
      unpriced_images?: number;
    };
    by_model?: Array<{ model: string; images: number }>;
    by_provider?: Array<{ provider: string; images: number }>;
  };
  provider_billing?: { entries?: number; amount?: number };
  recent_runs?: Array<{
    project?: string;
    run_id?: string;
    image_count?: number;
    failed_images?: number;
    known_cost?: number;
    profile_estimated_cost?: number;
  }>;
  pricing_note?: string;
};

function SpendPage() {
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUsage = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/usage", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`Usage failed: ${response.status}`);
      setUsage(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadUsage();
  }, []);

  if (error) {
    return (
      <AppShell>
        <ErrorBlock error={error} reset={() => void loadUsage()} />
      </AppShell>
    );
  }

  const archive = usage?.archive;
  const spend = archive?.spend;
  const billing = usage?.provider_billing;

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "SYSTEM", mono: true }, { label: "Spend" }]}
        actions={
          <button
            onClick={() => void loadUsage()}
            className="px-4 py-1.5 border border-brand text-brand text-xs font-bold font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors flex items-center gap-2"
          >
            <RefreshCw className={cn("size-3.5", loading && "animate-spin")} />
            Refresh
          </button>
        }
      />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border border border-border rounded-lg overflow-hidden mb-8">
          <Summary label="Spend" value={formatUsd(spend?.amount)} tone="brand" />
          <Summary label="Images" value={archive?.images ?? 0} />
          <Summary label="Runs" value={archive?.runs ?? 0} />
          <Summary label="Billing rows" value={billing?.entries ?? 0} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_420px] gap-6">
          <section className="space-y-6">
            <div className="border border-border rounded-lg bg-sidebar p-5">
              <div className="flex items-center gap-2 mb-4">
                <DollarSign className="size-4 text-brand" />
                <h1 className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
                  Cost basis
                </h1>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Metric label="Spend basis" value={spend?.basis ?? "loading"} />
                <Metric
                  label="Estimated total"
                  value={formatUsd(archive?.estimated_cost?.amount)}
                />
                <Metric label="Failed images" value={archive?.failed_images ?? 0} tone="warn" />
              </div>
              {usage?.pricing_note && (
                <p className="text-xs text-muted-foreground mt-4 leading-relaxed">
                  {usage.pricing_note}
                </p>
              )}
            </div>

            <div className="border border-border rounded-lg bg-sidebar overflow-hidden">
              <div className="px-4 py-3 border-b border-border text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                Recent runs
              </div>
              {(usage?.recent_runs ?? []).map((run) => (
                <div
                  key={`${run.project}/${run.run_id}`}
                  className="grid grid-cols-[1fr_.5fr_.5fr_.6fr] gap-4 px-4 py-3 border-b border-border last:border-b-0 text-xs font-mono"
                >
                  <div className="truncate">
                    <span className="text-muted-foreground">{run.project}</span> / {run.run_id}
                  </div>
                  <div className="text-muted-foreground">{run.image_count ?? 0} img</div>
                  <div className="text-muted-foreground">{run.failed_images ?? 0} failed</div>
                  <div className="text-right">
                    {formatUsd(run.known_cost ?? run.profile_estimated_cost)}
                  </div>
                </div>
              ))}
              {!loading && (usage?.recent_runs ?? []).length === 0 && (
                <div className="p-6 text-xs text-muted-foreground font-mono">
                  No usage runs found in the local archive yet.
                </div>
              )}
            </div>
          </section>

          <aside className="space-y-6">
            <Breakdown
              title="Models"
              rows={(archive?.by_model ?? []).map((row) => [row.model, row.images])}
            />
            <Breakdown
              title="Providers"
              rows={(archive?.by_provider ?? []).map((row) => [row.provider, row.images])}
            />
            {(archive?.estimated_cost?.unpriced_images ?? 0) > 0 && (
              <div className="border border-amber-400/30 rounded-lg bg-sidebar p-5">
                <AlertTriangle className="size-5 text-amber-400 mb-3" />
                <div className="text-sm font-medium">Unpriced images</div>
                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                  {archive?.estimated_cost?.unpriced_images?.toLocaleString()} images are missing
                  manifest cost and pricing-profile coverage.
                </p>
              </div>
            )}
          </aside>
        </div>
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

function Metric({ label, value, tone }: { label: string; value: number | string; tone?: "warn" }) {
  return (
    <div className="bg-black/40 border border-border rounded p-3">
      <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
        {label}
      </div>
      <div className={cn("text-sm mt-2 font-mono", tone === "warn" && "text-amber-400")}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
    </div>
  );
}

function Breakdown({ title, rows }: { title: string; rows: Array<[string, number]> }) {
  return (
    <div className="border border-border rounded-lg bg-sidebar overflow-hidden">
      <div className="px-4 py-3 border-b border-border text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        {title}
      </div>
      {rows.slice(0, 8).map(([label, count]) => (
        <div
          key={label}
          className="flex items-center justify-between gap-4 px-4 py-2 border-b border-border last:border-b-0 text-xs font-mono"
        >
          <span className="truncate">{label}</span>
          <span className="text-muted-foreground">{count.toLocaleString()}</span>
        </div>
      ))}
      {!rows.length && (
        <div className="p-4 text-xs text-muted-foreground font-mono">No records yet.</div>
      )}
    </div>
  );
}

function formatUsd(value?: number) {
  return `$${(value ?? 0).toFixed(2)}`;
}
