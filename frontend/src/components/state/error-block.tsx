import { useRouter } from "@tanstack/react-router";
import { AlertTriangle } from "lucide-react";

export function ErrorBlock({
  error,
  reset,
  onRetry,
  retryLabel = "Retry",
}: {
  error: Error | unknown;
  reset?: () => void;
  onRetry?: () => void;
  retryLabel?: string;
}) {
  const router = useRouter();
  const message = error instanceof Error ? error.message : "Something went wrong.";
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
      return;
    }
    router.invalidate();
    reset?.();
  };
  return (
    <div className="p-16 grid place-items-center">
      <div className="max-w-md text-center border border-destructive/30 bg-destructive/5 rounded-lg p-8">
        <AlertTriangle className="size-6 mx-auto text-destructive" strokeWidth={1.5} />
        <div className="mt-3 text-[10px] font-mono uppercase tracking-widest text-destructive">
          Route error
        </div>
        <h2 className="mt-2 text-lg font-semibold">This view failed to load</h2>
        <p className="mt-2 text-sm text-muted-foreground break-words">{message}</p>
        <div className="mt-5 flex justify-center gap-2">
          <button
            onClick={handleRetry}
            className="px-4 py-1.5 border border-brand text-brand text-xs font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors"
          >
            {retryLabel}
          </button>
          <a
            href="/library"
            className="px-4 py-1.5 border border-border text-muted-foreground text-xs font-mono uppercase tracking-widest rounded hover:text-foreground"
          >
            Library
          </a>
        </div>
      </div>
    </div>
  );
}
