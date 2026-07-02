import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { Library, Eye, Package, Database, Activity, DollarSign, Keyboard } from "lucide-react";
import { useTriageStore } from "@/stores/triage-store";
import { cn } from "@/lib/utils";
import { useSequenceShortcuts, useShortcuts } from "@/lib/shortcuts";
import { ShortcutSheet } from "@/components/shortcut-sheet";

const projectNav = [
  { to: "/library", label: "Library", icon: Library },
  { to: "/viewer", label: "Viewer", icon: Eye },
  { to: "/export", label: "Export", icon: Package },
] as const;

const systemNav = [
  { to: "/registry", label: "Registry", icon: Database },
  { to: "/health", label: "Health", icon: Activity, badge: "98%" },
  { to: "/spend", label: "Spend", icon: DollarSign },
] as const;

function NavLink({
  to,
  label,
  icon: Icon,
  badge,
  active,
}: {
  to: string;
  label: string;
  icon: typeof Library;
  badge?: string;
  active: boolean;
}) {
  return (
    <Link
      to={to}
      className={cn(
        "group relative flex items-center gap-3 px-3 py-2 rounded-md text-sm rf-press",
        "transition-colors duration-150",
        active
          ? "bg-brand-muted text-brand"
          : "text-muted-foreground hover:text-foreground hover:bg-white/5",
      )}
    >
      <span
        className={cn(
          "absolute left-0 top-1/2 -translate-y-1/2 w-0.5 rounded-r bg-brand transition-all duration-200",
          active ? "h-5 opacity-100" : "h-0 opacity-0",
        )}
        aria-hidden
      />
      <Icon
        className={cn(
          "size-4 shrink-0 transition-transform duration-150",
          "group-hover:translate-x-0.5",
        )}
        strokeWidth={1.5}
      />
      <span className="flex-1">{label}</span>
      {badge && (
        <span
          className={cn(
            "text-[10px] px-1.5 py-0.5 rounded font-mono transition-colors",
            active ? "bg-brand/20 text-brand" : "bg-white/5 text-muted-foreground",
          )}
        >
          {badge}
        </span>
      )}
    </Link>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const tray = useTriageStore((s) => s.tray);
  const setSheetOpen = useTriageStore((s) => s.setShortcutSheetOpen);
  const toggleDock = useTriageStore((s) => s.toggleDockExpanded);
  const navigate = useNavigate();

  const isActive = (to: string) =>
    to === "/library"
      ? pathname === "/library" || pathname.startsWith("/library/")
      : to === "/viewer"
        ? pathname.startsWith("/viewer")
        : pathname === to;

  useShortcuts([
    { combo: "?", handler: () => setSheetOpen(true) },
    { combo: "shift+?", handler: () => setSheetOpen(true) },
    { combo: "t", handler: () => toggleDock() },
  ]);

  useSequenceShortcuts([
    { combo: "gl", handler: () => navigate({ to: "/library" }) },
    { combo: "gv", handler: () => navigate({ to: "/viewer" }) },
    { combo: "ge", handler: () => navigate({ to: "/export" }) },
    { combo: "gr", handler: () => navigate({ to: "/registry" }) },
    { combo: "gh", handler: () => navigate({ to: "/health" }) },
  ]);

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      <aside className="w-64 shrink-0 border-r border-border bg-sidebar flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="size-8 bg-brand text-black rounded flex items-center justify-center font-bold text-lg tracking-tighter font-mono">
            R
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-semibold tracking-tight">RAFIKI</span>
            <span className="text-[10px] text-muted-foreground font-mono mt-1">v0.8.2 local</span>
          </div>
        </div>

        <nav className="flex-1 px-3 space-y-1">
          <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest px-3 mb-2">
            Project
          </div>
          {projectNav.map((n) => (
            <NavLink key={n.to} {...n} active={isActive(n.to)} />
          ))}

          <div className="pt-6 text-[10px] font-mono text-muted-foreground uppercase tracking-widest px-3 mb-2">
            System
          </div>
          {systemNav.map((n) => (
            <NavLink key={n.to} {...n} active={isActive(n.to)} />
          ))}
        </nav>

        <div className="p-6 border-t border-border space-y-3">
          <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
            <span className="relative flex size-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-60" />
              <span className="relative inline-flex rounded-full size-2 bg-brand" />
            </span>
            <span>Local Node: Active</span>
          </div>
          {tray.length > 0 && (
            <Link
              to="/export"
              className="flex items-center justify-between text-[11px] font-mono uppercase tracking-widest px-3 py-2 bg-brand/10 text-brand rounded border border-brand/20 hover:bg-brand/15 transition-colors rf-fade-in rf-press"
            >
              <span>Deliver</span>
              <span className="tabular-nums">{tray.length}</span>
            </Link>
          )}
          <button
            onClick={() => setSheetOpen(true)}
            className="w-full flex items-center justify-between text-[11px] font-mono uppercase tracking-widest px-3 py-2 border border-border rounded text-muted-foreground hover:text-foreground hover:border-white/20 transition-colors rf-press"
          >
            <span className="flex items-center gap-2">
              <Keyboard className="size-3.5" strokeWidth={1.5} />
              Shortcuts
            </span>
            <kbd className="bg-white/5 border border-border px-1.5 py-0.5 rounded text-[10px]">
              ?
            </kbd>
          </button>
        </div>
      </aside>

      <main key={pathname} className="flex-1 flex flex-col overflow-hidden rf-fade-in">
        {children}
      </main>

      <ShortcutSheet />
    </div>
  );
}
