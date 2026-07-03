import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Database } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { EmptyBlock } from "@/components/state/empty-block";
import { ErrorBlock } from "@/components/state/error-block";
import { getProject, useLibraryState } from "@/lib/rafiki-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/registry")({
  head: () => ({
    meta: [
      { title: "Registry — Rafiki" },
      {
        name: "description",
        content: "Local asset registry and cache index.",
      },
    ],
  }),
  errorComponent: ({ error, reset }) => (
    <AppShell>
      <ErrorBlock error={error} reset={reset} />
    </AppShell>
  ),
  component: RegistryPage,
});

const filters = ["all", "indexed", "orphan", "missing"] as const;
type F = (typeof filters)[number];

const statusStyle: Record<string, string> = {
  indexed: "text-brand bg-brand/10",
  orphan: "text-amber-400 bg-amber-400/10",
  missing: "text-destructive bg-destructive/10",
};

function RegistryPage() {
  const [filter, setFilter] = useState<F>("all");
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
        <PageHeader crumbs={[{ label: "SYSTEM", mono: true }, { label: "Registry" }]} />
        <div className="p-16 text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Loading registry…
        </div>
      </AppShell>
    );
  }

  const registry = data.registry.entries;
  const rows = registry.filter((r) => filter === "all" || r.status === filter);

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "SYSTEM", mono: true }, { label: "Registry" }]}
        actions={
          <div className="text-xs font-mono text-muted-foreground">{registry.length} entries</div>
        }
      />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold">Asset registry</h1>
            <p className="text-xs text-muted-foreground font-mono mt-1">
              Cached references across all projects.
            </p>
          </div>
          <div className="flex gap-1 p-1 border border-border rounded bg-sidebar">
            {filters.map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  "px-3 py-1 text-[11px] font-mono uppercase tracking-widest rounded",
                  filter === f
                    ? "bg-brand text-black"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-border bg-sidebar">
          <div className="grid min-w-[760px] grid-cols-[1.5fr_1fr_.7fr_.5fr_.8fr_.7fr] gap-4 px-4 py-3 border-b border-border text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
            <div>Path</div>
            <div>Project</div>
            <div>Size</div>
            <div>Refs</div>
            <div>Last seen</div>
            <div>Status</div>
          </div>
          {rows.map((r) => {
            const p = getProject(data, r.projectId);
            return (
              <div
                key={r.id}
                className="grid min-w-[760px] grid-cols-[1.5fr_1fr_.7fr_.5fr_.8fr_.7fr] gap-4 px-4 py-3 border-b border-border last:border-b-0 text-xs font-mono hover:bg-white/5"
              >
                <div className="truncate text-foreground/90">{r.path}</div>
                <div className="truncate text-muted-foreground">
                  {p ? `${p.code} · ${p.name}` : r.projectId || "Unknown"}
                </div>
                <div className="text-muted-foreground">{formatSize(r.sizeMb, r.exists)}</div>
                <div className="text-muted-foreground">{r.refs}</div>
                <div className="text-muted-foreground">{formatDate(r.lastSeen)}</div>
                <div>
                  <span
                    className={cn(
                      "px-1.5 py-0.5 rounded text-[10px] uppercase tracking-widest",
                      statusStyle[r.status],
                    )}
                  >
                    {r.status}
                  </span>
                </div>
              </div>
            );
          })}
          {rows.length === 0 && (
            <div className="p-6">
              <EmptyBlock
                icon={Database}
                title="No entries match this filter"
                hint="Try switching to All to see everything the registry knows about."
              />
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function formatSize(sizeMb: number, exists: boolean) {
  if (!exists) return "Missing";
  if (sizeMb < 0.01) return "<0.01 MB";
  return `${sizeMb.toLocaleString()} MB`;
}

function formatDate(value: string) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return date.toLocaleDateString();
}
