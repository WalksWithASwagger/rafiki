import { AlertTriangle, CheckCircle2, Loader2, X } from "lucide-react";
import { cn } from "@/lib/utils";

export type GenerateStatusKind = "notice" | "validation" | "generation-error" | "loading";

export interface GenerateStatus {
  kind: GenerateStatusKind;
  title: string;
  message: string;
  detail?: string;
}

export function GenerateStatusBanner({
  status,
  onClear,
}: {
  status: GenerateStatus;
  onClear: () => void;
}) {
  const visual = statusVisual(status.kind);
  const Icon = visual.icon;
  return (
    <div
      data-testid="generate-status"
      data-generate-status={status.kind}
      className={cn(
        "flex items-start justify-between gap-3 rounded border px-4 py-3 text-sm",
        visual.className,
      )}
    >
      <div className="flex min-w-0 items-start gap-2">
        <Icon className={cn("mt-0.5 size-4 shrink-0", visual.iconClassName)} strokeWidth={1.5} />
        <div className="min-w-0">
          <div className="text-[10px] font-mono uppercase tracking-widest">{status.title}</div>
          <p className="mt-1 break-words text-foreground">{status.message}</p>
          {status.detail && (
            <p className="mt-1 break-words text-xs text-muted-foreground">{status.detail}</p>
          )}
        </div>
      </div>
      <button
        onClick={onClear}
        className="grid size-6 shrink-0 place-items-center rounded text-muted-foreground hover:text-foreground"
        aria-label="Clear status"
      >
        <X className="size-4" />
      </button>
    </div>
  );
}

function statusVisual(kind: GenerateStatusKind) {
  if (kind === "validation") {
    return {
      icon: AlertTriangle,
      className: "border-amber-400/30 bg-amber-400/5 text-amber-300",
      iconClassName: "text-amber-300",
    };
  }
  if (kind === "generation-error") {
    return {
      icon: AlertTriangle,
      className: "border-destructive/30 bg-destructive/5 text-destructive",
      iconClassName: "text-destructive",
    };
  }
  if (kind === "loading") {
    return {
      icon: Loader2,
      className: "border-brand/30 bg-brand/5 text-brand",
      iconClassName: "animate-spin text-brand",
    };
  }
  return {
    icon: CheckCircle2,
    className: "border-brand/30 bg-brand/5 text-brand",
    iconClassName: "text-brand",
  };
}
