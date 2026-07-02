import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface Crumb {
  label: string;
  mono?: boolean;
}

export function PageHeader({
  crumbs,
  actions,
  className,
}: {
  crumbs: Crumb[];
  actions?: ReactNode;
  className?: string;
}) {
  return (
    <header
      className={cn(
        "h-16 border-b border-border flex items-center justify-between px-8 shrink-0 bg-background/80 backdrop-blur",
        className,
      )}
    >
      <div className="flex items-center gap-3 min-w-0">
        {crumbs.map((c, i) => (
          <div key={i} className="flex items-center gap-3 min-w-0">
            {i > 0 && <span className="text-muted-foreground">/</span>}
            <span
              className={cn(
                "text-sm truncate",
                c.mono ? "font-mono text-muted-foreground" : "text-foreground",
              )}
            >
              {c.label}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded border border-border bg-white/5 text-[11px] font-mono text-muted-foreground">
          <span>Search</span>
          <kbd className="text-[10px] bg-white/5 border border-border px-1 rounded">⌘K</kbd>
        </div>
        {actions}
      </div>
    </header>
  );
}
