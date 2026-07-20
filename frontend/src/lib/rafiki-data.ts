import { useQuery } from "@tanstack/react-query";
import { useTriageStore } from "@/stores/triage-store";

export type ImageStatus = "present" | "failed" | "missing";
export type Rating = "starred" | "rejected" | null;

export interface ImageRecord {
  id: string;
  key: string;
  runId: string;
  runKey: string;
  projectId: string;
  slot: number;
  prompt: string;
  name: string;
  seed: number;
  steps: number;
  cfg: number;
  model: string;
  sampler: string;
  latencyMs: number;
  status: ImageStatus;
  swatch: string;
  createdAt: string;
  url: string;
  thumbnailUrl: string;
  rating: Rating;
  file: string;
  ok: boolean;
}

export interface RunRecord {
  id: string;
  key: string;
  projectId: string;
  label: string;
  createdAt: string;
  imageCount: number;
  model: string;
  style: string;
  aspectRatio: string;
  promptFile: string;
}

export interface ProjectRecord {
  id: string;
  code: string;
  name: string;
  runCount: number;
  imageCount: number;
  presentCount: number;
  failedCount: number;
  missingCount: number;
  updatedAt: string;
  health: "ok" | "warn" | "fail";
  tags: string[];
}

export interface RegistryEntry {
  id: string;
  projectId: string;
  path: string;
  sizeMb: number;
  refs: number;
  lastSeen: string;
  status: "indexed" | "orphan" | "missing";
  exists: boolean;
  title?: string;
  approvalStatus?: string;
}

export interface LibraryTotals {
  projects: number;
  runs: number;
  images: number;
  present: number;
  missing: number;
  failed: number;
  files?: number;
  starred?: number;
  rejected?: number;
}

export interface SourceWarning {
  kind: string;
  project: string;
  path: string;
  message: string;
}

export interface HealthReport {
  ok: boolean;
  totalProjects: number;
  totalRuns: number;
  manifestImages: number;
  presentImages: number;
  missingRecords: number;
  failedImages: number;
  imageFiles: number;
  duplicateGroups: number;
  cleanupRisk: number;
  malformedRuns: number;
  ratings: { starred: number; rejected: number };
  outputSizeGb: number;
  warnings: string[];
}

export interface LibraryState {
  version: number;
  source: string;
  outputRoot: string;
  projects: ProjectRecord[];
  runs: RunRecord[];
  images: ImageRecord[];
  ratings: Record<string, Rating>;
  totals: {
    archive: LibraryTotals;
    visible: LibraryTotals;
  };
  sourceWarnings: SourceWarning[];
  health: HealthReport;
  registry: {
    entries: RegistryEntry[];
    summary: { entries: number; approved: number; unapproved: number };
  };
}

export type LibraryStatePayload = Omit<LibraryState, "ratings" | "totals" | "sourceWarnings"> & {
  ratings?: Record<string, unknown>;
  totals?: LibraryState["totals"];
  sourceWarnings?: SourceWarning[];
};

let cachedState: LibraryState | null = null;

function toUiRating(value: unknown): Rating {
  if (value === "star" || value === "starred") return "starred";
  if (value === "reject" || value === "rejected") return "rejected";
  return null;
}

export function normalizeState(payload: LibraryStatePayload): LibraryState {
  const ratings: Record<string, Rating> = {};
  for (const [key, value] of Object.entries(payload.ratings ?? {})) {
    ratings[key] = toUiRating(value);
  }
  const images = payload.images.map((image) => ({
    ...image,
    rating: toUiRating(image.rating ?? ratings[image.key]),
  }));
  const visible =
    payload.totals?.visible ?? deriveVisibleTotals(payload.projects, payload.runs, images, ratings);
  const archive = payload.totals?.archive ?? {
    projects: payload.health.totalProjects,
    runs: payload.health.totalRuns,
    images: payload.health.manifestImages,
    present: payload.health.presentImages,
    missing: payload.health.missingRecords,
    failed: payload.health.failedImages,
    files: payload.health.imageFiles,
  };
  return {
    ...payload,
    ratings,
    images,
    totals: { archive, visible },
    sourceWarnings: payload.sourceWarnings ?? [],
  };
}

function deriveVisibleTotals(
  projects: ProjectRecord[],
  runs: RunRecord[],
  images: ImageRecord[],
  ratings: Record<string, Rating>,
): LibraryTotals {
  return {
    projects: projects.length,
    runs: runs.length,
    images: images.length,
    present: images.filter((image) => image.status === "present").length,
    missing: images.filter((image) => image.status === "missing").length,
    failed: images.filter((image) => image.status === "failed").length,
    starred: Object.values(ratings).filter((rating) => rating === "starred").length,
    rejected: Object.values(ratings).filter((rating) => rating === "rejected").length,
  };
}

export async function fetchLibraryState(): Promise<LibraryState> {
  const response = await fetch("/api/library-state", { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Library state failed: ${response.status}`);
  }
  cachedState = normalizeState(await response.json());
  useTriageStore.getState().hydrateRatings(cachedState.ratings);
  return cachedState;
}

export function useLibraryState() {
  return useQuery({
    queryKey: ["library-state"],
    queryFn: fetchLibraryState,
    staleTime: 10_000,
  });
}

export function getCachedImage(id: string) {
  return cachedState?.images.find((image) => image.id === id);
}

export function getCachedProject(id: string) {
  return cachedState?.projects.find((project) => project.id === id);
}

export function getCachedRun(id: string) {
  return cachedState?.runs.find((run) => run.id === id);
}

export function getImage(state: LibraryState, id: string) {
  return state.images.find((image) => image.id === id);
}

export function getProject(state: LibraryState, id: string) {
  return state.projects.find((project) => project.id === id);
}

export function getRun(state: LibraryState, id: string) {
  return state.runs.find((run) => run.id === id);
}

export function imagesInRun(state: LibraryState, runId: string) {
  return state.images.filter((image) => image.runId === runId);
}

export function runsInProject(state: LibraryState, projectId: string) {
  return state.runs.filter((run) => run.projectId === projectId);
}

export function latestRunForProject(state: LibraryState, projectId: string) {
  return runsInProject(state, projectId).sort((a, b) => b.createdAt.localeCompare(a.createdAt))[0];
}

export function projectThumbs(state: LibraryState, projectId: string): ImageRecord[] {
  return state.images
    .filter((image) => image.projectId === projectId && image.status === "present")
    .slice(0, 4);
}

export function effectiveRating(image: ImageRecord, ratings: Record<string, Rating>): Rating {
  return ratings[image.key] ?? image.rating ?? null;
}
