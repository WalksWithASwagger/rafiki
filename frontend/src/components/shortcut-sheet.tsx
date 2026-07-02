import { useEffect } from "react";
import { X } from "lucide-react";
import { SHORTCUT_CATALOG, type Scope } from "@/lib/shortcuts";
import { useTriageStore } from "@/stores/triage-store";

const SCOPE_LABEL: Record<Scope, string> = {
  global: "Global",
  library: "Library",
  viewer: "Viewer",
  export: "Export",
};

function Kbd({ combo }: { combo: string }) {
  const parts = combo.split(/\s+/);
  return (
    <span className="inline-flex items-center gap-1">
      {parts.map((p, i) => (
        <kbd
          key={i}
          className="bg-white/5 border border-border px-1.5 py-0.5 rounded text-[10px] font-mono min-w-[24px] text-center text-foreground uppercase"
        >
          {p}
        </kbd>
      ))}
    </span>
  );
}

export function ShortcutSheet() {
  const open = useTriageStore((s) => s.shortcutSheetOpen);
  const setOpen = useTriageStore((s) => s.setShortcutSheetOpen);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  if (!open) return null;

  const scopes: Scope[] = ["global", "library", "viewer", "export"];

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/60 backdrop-blur-sm p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Keyboard shortcuts"
      onClick={() => setOpen(false)}
    >
      <div
        className="w-full max-w-3xl bg-sidebar border border-border rounded-lg shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div>
            <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              Reference
            </div>
            <h2 className="text-base font-semibold mt-0.5">Keyboard shortcuts</h2>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="size-8 grid place-items-center rounded border border-border text-muted-foreground hover:text-foreground"
            aria-label="Close"
          >
            <X className="size-4" />
          </button>
        </header>
        <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-6">
          {scopes.map((scope) => (
            <section key={scope}>
              <h3 className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground mb-3">
                {SCOPE_LABEL[scope]}
              </h3>
              <ul className="space-y-2">
                {SHORTCUT_CATALOG.filter((s) => s.scope === scope).map((s) => (
                  <li
                    key={`${scope}-${s.combo}`}
                    className="flex items-center justify-between gap-2 text-xs"
                  >
                    <span className="text-muted-foreground">{s.label}</span>
                    <Kbd combo={s.combo} />
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
        <footer className="px-6 py-3 border-t border-border text-[10px] font-mono uppercase tracking-widest text-muted-foreground flex justify-between">
          <span>Press ? anywhere to reopen</span>
          <span>Esc to close</span>
        </footer>
      </div>
    </div>
  );
}
