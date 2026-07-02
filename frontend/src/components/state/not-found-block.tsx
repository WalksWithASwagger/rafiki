import { Link } from "@tanstack/react-router";
import { Search } from "lucide-react";

export function NotFoundBlock({ label, hint }: { label: string; hint?: string }) {
  return (
    <div className="p-16 grid place-items-center">
      <div className="max-w-md text-center">
        <Search className="size-6 mx-auto text-muted-foreground/60" strokeWidth={1.5} />
        <div className="mt-3 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
          Not found
        </div>
        <h2 className="mt-2 text-lg font-semibold">{label}</h2>
        {hint && <p className="mt-2 text-sm text-muted-foreground">{hint}</p>}
        <Link
          to="/library"
          className="mt-6 inline-block px-4 py-1.5 border border-brand text-brand text-xs font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors"
        >
          Back to Library
        </Link>
      </div>
    </div>
  );
}
