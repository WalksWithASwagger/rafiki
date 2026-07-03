import { useEffect } from "react";

export type Scope = "global" | "viewer" | "library" | "export";

export interface Shortcut {
  combo: string;
  label: string;
  scope: Scope;
}

export const SHORTCUT_CATALOG: Shortcut[] = [
  { combo: "?", label: "Show shortcuts", scope: "global" },
  { combo: "g g", label: "Go to Generate", scope: "global" },
  { combo: "g l", label: "Go to Library", scope: "global" },
  { combo: "g v", label: "Go to Viewer", scope: "global" },
  { combo: "g e", label: "Go to Export", scope: "global" },
  { combo: "t", label: "Toggle export tray", scope: "global" },
  { combo: "esc", label: "Close overlay / back", scope: "global" },
  { combo: "/", label: "Focus search", scope: "library" },
  { combo: "1-5", label: "Filter by status", scope: "library" },
  { combo: "s", label: "Cycle sort", scope: "library" },
  { combo: "a", label: "Toggle select mode", scope: "library" },
  { combo: "c", label: "Clear filters", scope: "library" },
  { combo: "j", label: "Previous image", scope: "viewer" },
  { combo: "k", label: "Next image", scope: "viewer" },
  { combo: "s", label: "Star", scope: "viewer" },
  { combo: "x", label: "Reject", scope: "viewer" },
  { combo: "e", label: "Toggle export tray", scope: "viewer" },
  { combo: "shift+e", label: "Open Export", scope: "viewer" },
  { combo: "enter", label: "Deliver batch", scope: "export" },
  { combo: "f", label: "Cycle format", scope: "export" },
  { combo: "r", label: "Retry last failed job", scope: "export" },
  { combo: "d", label: "Dismiss completed jobs", scope: "export" },
];

interface Binding {
  combo: string;
  handler: (e: KeyboardEvent) => void;
}

function isTypingTarget(t: EventTarget | null): boolean {
  if (!(t instanceof HTMLElement)) return false;
  const tag = t.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (t.isContentEditable) return true;
  return false;
}

function normalize(e: KeyboardEvent): string {
  const parts: string[] = [];
  if (e.shiftKey) parts.push("shift");
  if (e.altKey) parts.push("alt");
  const raw = e.key === " " ? "space" : e.key.toLowerCase();
  const key = raw === "escape" ? "esc" : raw;
  parts.push(key);
  return parts.join("+");
}

export function useShortcuts(bindings: Binding[], enabled = true) {
  useEffect(() => {
    if (!enabled) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) return;
      if (isTypingTarget(e.target) && e.key !== "Escape") return;
      const combo = normalize(e);
      for (const b of bindings) {
        if (b.combo === combo) {
          e.preventDefault();
          b.handler(e);
          return;
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [bindings, enabled]);
}

export function useSequenceShortcuts(
  sequences: { combo: string; handler: () => void }[],
  enabled = true,
) {
  useEffect(() => {
    if (!enabled) return;
    let buffer = "";
    let timer: ReturnType<typeof setTimeout> | null = null;
    const reset = () => {
      buffer = "";
      if (timer) clearTimeout(timer);
      timer = null;
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (isTypingTarget(e.target)) return;
      if (e.key.length !== 1) return;
      buffer = (buffer + e.key.toLowerCase()).slice(-8);
      for (const s of sequences) {
        if (buffer.endsWith(s.combo.replace(/\s+/g, ""))) {
          e.preventDefault();
          s.handler();
          reset();
          return;
        }
      }
      if (timer) clearTimeout(timer);
      timer = setTimeout(reset, 800);
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      if (timer) clearTimeout(timer);
    };
  }, [sequences, enabled]);
}
