import { Link } from "@tanstack/react-router";
import { RotateCcw, X } from "lucide-react";
import { useTriageStore } from "@/stores/triage-store";
import { getCachedImage } from "@/lib/rafiki-data";
import { retryJob } from "@/lib/run-batch";
import { Thumbnail } from "./thumbnail";
import { cn } from "@/lib/utils";

export function ExportDock() {
  const tray = useTriageStore((s) => s.tray);
  const jobs = useTriageStore((s) => s.jobs);
  const dismissJob = useTriageStore((s) => s.dismissJob);
  const dockExpanded = useTriageStore((s) => s.dockExpanded);
  const toggleDockExpanded = useTriageStore((s) => s.toggleDockExpanded);

  const activeJobs = jobs.filter(
    (j) => j.stage === "encoding" || j.stage === "packaging" || j.stage === "queued",
  );
  const errored = jobs.find((j) => j.stage === "error");
  const totalActive = activeJobs.reduce((n, j) => n + j.total, 0);
  const doneActive = activeJobs.reduce((n, j) => n + j.processed, 0);
  const pct = totalActive === 0 ? 0 : Math.round((doneActive / totalActive) * 100);

  if (tray.length === 0 && activeJobs.length === 0 && !errored) return null;

  // Collapsed strip
  const rootBase =
    "absolute bottom-0 left-0 right-0 border-t border-border bg-sidebar/95 backdrop-blur-xl z-20 rf-slide-up";

  if (!dockExpanded) {
    return (
      <div className={cn(rootBase, "px-6 py-2 flex items-center justify-between")}>
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
            {activeJobs.length > 0
              ? `Delivering ${activeJobs.length} · ${pct}%`
              : errored
                ? `1 job failed`
                : `${tray.length} staged`}
          </span>
        </div>
        <button
          onClick={toggleDockExpanded}
          className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
        >
          Show <kbd className="ml-1 border border-border px-1 rounded">T</kbd>
        </button>
      </div>
    );
  }

  return (
    <div className={cn(rootBase, "px-6 py-3 space-y-2")}>
      {errored && !activeJobs.length && (
        <div className="flex items-center justify-between gap-4 border border-destructive/40 bg-destructive/10 rounded px-3 py-2">
          <span className="text-[11px] font-mono uppercase tracking-widest text-destructive truncate">
            {errored.label} failed · {errored.error ?? "Delivery error"}
          </span>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => void retryJob(errored.id)}
              className="px-2.5 py-1 border border-destructive/60 text-destructive text-[10px] font-mono uppercase tracking-widest rounded hover:bg-destructive/20 flex items-center gap-1"
            >
              <RotateCcw className="size-3" />
              Retry
            </button>
            <button
              onClick={() => dismissJob(errored.id)}
              className="size-6 grid place-items-center rounded border border-border text-muted-foreground hover:text-foreground"
              aria-label="Dismiss"
            >
              <X className="size-3" />
            </button>
          </div>
        </div>
      )}

      {activeJobs.length > 0 ? (
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0 flex-1">
            <span className="text-[11px] font-mono uppercase tracking-widest text-brand shrink-0">
              {activeJobs.length > 1
                ? `Delivering ${activeJobs.length} jobs · ${pct}%`
                : `Delivering ${activeJobs[0].total} · ${pct}%`}
            </span>
            <div className="relative flex-1 h-1.5 bg-black/60 rounded overflow-hidden">
              <div
                className="h-full bg-brand transition-[width] duration-500 ease-out"
                style={{ width: `${Math.max(4, pct)}%` }}
              />
              <div className="pointer-events-none absolute inset-0 rf-shimmer opacity-70" />
            </div>
            <div className="flex gap-1 shrink-0">
              {activeJobs.slice(0, 6).map((j) => {
                const jp = j.total === 0 ? 0 : Math.round((j.processed / j.total) * 100);
                return (
                  <div
                    key={j.id}
                    title={`${j.label} · ${jp}%`}
                    className={cn(
                      "size-2 rounded-full transition-colors",
                      j.stage === "queued" ? "bg-white/20 rf-blink" : "bg-brand",
                    )}
                  />
                );
              })}
            </div>
          </div>
          <button
            onClick={toggleDockExpanded}
            className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
          >
            Hide <kbd className="ml-1 border border-border px-1 rounded">T</kbd>
          </button>
          <Link
            to="/export"
            className="px-4 py-1.5 border border-border text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground rounded"
          >
            Details
          </Link>
        </div>
      ) : (
        tray.length > 0 && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground">
                Staged for export ({tray.length})
              </span>
              <div className="flex -space-x-2">
                {tray.slice(0, 5).map((id) => {
                  const img = getCachedImage(id);
                  if (!img) return null;
                  return (
                    <Thumbnail
                      key={id}
                      image={img}
                      showLabel={false}
                      className="size-9 rounded border border-border ring-2 ring-sidebar"
                    />
                  );
                })}
                {tray.length > 5 && (
                  <div className="size-9 rounded border border-border ring-2 ring-sidebar bg-black grid place-items-center text-[10px] font-mono text-muted-foreground">
                    +{tray.length - 5}
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleDockExpanded}
                className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
              >
                Hide <kbd className="ml-1 border border-border px-1 rounded">T</kbd>
              </button>
              <Link
                to="/export"
                className="px-5 py-2 border border-brand text-brand text-xs font-bold rounded hover:bg-brand hover:text-black transition-colors tracking-wider font-mono"
              >
                DELIVER {tray.length} ASSETS
              </Link>
            </div>
          </div>
        )
      )}
    </div>
  );
}
