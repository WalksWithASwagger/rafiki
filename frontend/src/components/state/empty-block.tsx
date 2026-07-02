import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function EmptyBlock({
  icon: Icon,
  title,
  hint,
  action,
  className,
}: {
  icon: LucideIcon;
  title: string;
  hint?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "border border-dashed border-border rounded-lg p-16 text-center bg-sidebar/30",
        className,
      )}
    >
      <Icon className="size-8 mx-auto text-muted-foreground/40" strokeWidth={1.5} />
      <p className="mt-4 text-sm text-foreground">{title}</p>
      {hint && (
        <div className="text-[11px] font-mono text-muted-foreground/70 mt-2 leading-relaxed">
          {hint}
        </div>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
