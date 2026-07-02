import { cn } from "@/lib/utils";

export function LoadingBlock({
  label = "Loading",
  variant = "grid",
  className,
}: {
  label?: string;
  variant?: "grid" | "list" | "single";
  className?: string;
}) {
  if (variant === "single") {
    return (
      <div className={cn("p-16 grid place-items-center", className)}>
        <div className="flex items-center gap-3 text-[11px] font-mono uppercase tracking-widest text-muted-foreground">
          <span className="size-2 rounded-full bg-brand rf-shimmer" />
          {label}…
        </div>
      </div>
    );
  }
  if (variant === "list") {
    return (
      <div className={cn("space-y-2 p-8", className)} aria-busy="true">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-10 rounded border border-border bg-sidebar rf-shimmer" />
        ))}
      </div>
    );
  }
  return (
    <div
      className={cn(
        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 p-8",
        className,
      )}
      aria-busy="true"
    >
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="aspect-[4/3] rounded-lg bg-sidebar border border-border rf-shimmer"
        />
      ))}
    </div>
  );
}
