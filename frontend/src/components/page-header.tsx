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
        "min-h-16 border-b border-border flex flex-wrap items-center justify-between gap-3 px-4 py-3 shrink-0 bg-background/80 backdrop-blur sm:px-8",
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
      {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
    </header>
  );
}
