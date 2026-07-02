import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Rating } from "@/lib/rafiki-data";
import {
  DEFAULT_FILENAME_TEMPLATE,
  DEFAULT_MANIFEST_FIELDS,
  type ExportFormat,
  type ManifestField,
} from "@/lib/exporter";

export type JobStage = "queued" | "encoding" | "packaging" | "done" | "error";

export interface JobSnapshot {
  format: ExportFormat;
  destination: string;
  template: string;
  filenameTemplate: string;
  fields: ManifestField[];
  simulateFailure?: boolean;
}

export interface ExportJob {
  id: string;
  label: string;
  imageIds: string[];
  format: ExportFormat;
  stage: JobStage;
  processed: number;
  total: number;
  message?: string;
  error?: string;
  snapshot: JobSnapshot;
  result?: {
    filename: string;
    blobUrl: string;
    sizeKb: number;
  };
  startedAt: number;
}

export interface ManifestPrefs {
  filenameTemplate: string;
  fields: ManifestField[];
}

function apiRating(value: Rating) {
  if (value === "starred") return "star";
  if (value === "rejected") return "reject";
  return null;
}

function persistRating(key: string, value: Rating) {
  void fetch("/api/ratings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value: apiRating(value) }),
  });
}

interface TriageState {
  ratings: Record<string, Rating>;
  tray: string[];
  jobs: ExportJob[];
  shortcutSheetOpen: boolean;
  dockExpanded: boolean;
  manifestPrefs: ManifestPrefs;
  librarySelection: string[];
  selectMode: boolean;
  star: (id: string) => void;
  reject: (id: string) => void;
  clearRating: (id: string) => void;
  toggleTray: (id: string) => void;
  addToTray: (ids: string[]) => void;
  removeFromTray: (id: string) => void;
  clearTray: () => void;
  addJob: (job: ExportJob) => void;
  updateJob: (id: string, patch: Partial<ExportJob>) => void;
  dismissJob: (id: string) => void;
  dismissCompleted: () => void;
  clearJobs: () => void;
  setShortcutSheetOpen: (open: boolean) => void;
  setDockExpanded: (open: boolean) => void;
  toggleDockExpanded: () => void;
  setManifestPrefs: (prefs: Partial<ManifestPrefs>) => void;
  hydrateRatings: (ratings: Record<string, Rating>) => void;
  setSelectMode: (on: boolean) => void;
  toggleSelectMode: () => void;
  toggleLibrarySelection: (id: string) => void;
  setLibrarySelection: (ids: string[]) => void;
  clearLibrarySelection: () => void;
}

export const useTriageStore = create<TriageState>()(
  persist(
    (set, get) => ({
      ratings: {},
      tray: [],
      jobs: [],
      shortcutSheetOpen: false,
      dockExpanded: true,
      manifestPrefs: {
        filenameTemplate: DEFAULT_FILENAME_TEMPLATE,
        fields: DEFAULT_MANIFEST_FIELDS,
      },
      librarySelection: [],
      selectMode: false,
      star: (id) =>
        set((s) => {
          const next = s.ratings[id] === "starred" ? null : "starred";
          persistRating(id, next);
          return { ratings: { ...s.ratings, [id]: next } };
        }),
      reject: (id) =>
        set((s) => {
          const next = s.ratings[id] === "rejected" ? null : "rejected";
          persistRating(id, next);
          return { ratings: { ...s.ratings, [id]: next } };
        }),
      clearRating: (id) =>
        set((s) => {
          persistRating(id, null);
          return { ratings: { ...s.ratings, [id]: null } };
        }),
      toggleTray: (id) => {
        const inTray = get().tray.includes(id);
        set((s) => ({
          tray: inTray ? s.tray.filter((t) => t !== id) : [...s.tray, id],
        }));
      },
      addToTray: (ids) =>
        set((s) => {
          const set2 = new Set(s.tray);
          for (const id of ids) set2.add(id);
          return { tray: Array.from(set2) };
        }),
      removeFromTray: (id) => set((s) => ({ tray: s.tray.filter((t) => t !== id) })),
      clearTray: () => set({ tray: [] }),
      addJob: (job) => set((s) => ({ jobs: [job, ...s.jobs].slice(0, 12) })),
      updateJob: (id, patch) =>
        set((s) => ({
          jobs: s.jobs.map((j) => (j.id === id ? { ...j, ...patch } : j)),
        })),
      dismissJob: (id) => set((s) => ({ jobs: s.jobs.filter((j) => j.id !== id) })),
      dismissCompleted: () =>
        set((s) => ({
          jobs: s.jobs.filter((j) => j.stage !== "done"),
        })),
      clearJobs: () => set({ jobs: [] }),
      setShortcutSheetOpen: (open) => set({ shortcutSheetOpen: open }),
      setDockExpanded: (open) => set({ dockExpanded: open }),
      toggleDockExpanded: () => set((s) => ({ dockExpanded: !s.dockExpanded })),
      setManifestPrefs: (prefs) =>
        set((s) => ({ manifestPrefs: { ...s.manifestPrefs, ...prefs } })),
      hydrateRatings: (ratings) => set({ ratings }),
      setSelectMode: (on) =>
        set({ selectMode: on, librarySelection: on ? get().librarySelection : [] }),
      toggleSelectMode: () =>
        set((s) => ({
          selectMode: !s.selectMode,
          librarySelection: !s.selectMode ? s.librarySelection : [],
        })),
      toggleLibrarySelection: (id) =>
        set((s) => ({
          librarySelection: s.librarySelection.includes(id)
            ? s.librarySelection.filter((x) => x !== id)
            : [...s.librarySelection, id],
        })),
      setLibrarySelection: (ids) => set({ librarySelection: ids }),
      clearLibrarySelection: () => set({ librarySelection: [] }),
    }),
    {
      name: "rafiki-triage",
      partialize: (s) => ({
        ratings: s.ratings,
        tray: s.tray,
        manifestPrefs: s.manifestPrefs,
      }),
    },
  ),
);
