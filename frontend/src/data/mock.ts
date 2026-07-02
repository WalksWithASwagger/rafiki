// Deterministic mock data for the Rafiki UI shell.
// Numbers echo LIBRARY-VIEWER-DESIGNER-HANDOFF-2026-07.md.

export type ImageStatus = "present" | "failed" | "missing";
export type Rating = "starred" | "rejected" | null;

export interface ImageRecord {
  id: string;
  runId: string;
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
  swatch: string; // deterministic thumbnail color
  createdAt: string;
}

export interface RunRecord {
  id: string;
  projectId: string;
  label: string;
  createdAt: string;
  imageCount: number;
}

export type ProjectTag = "editorial" | "render" | "photo" | "wip" | "client";

export interface ProjectRecord {
  id: string;
  code: string;
  name: string;
  runCount: number;
  imageCount: number;
  updatedAt: string;
  health: "ok" | "warn" | "fail";
  tags: ProjectTag[];
}

export interface RegistryEntry {
  id: string;
  projectId: string;
  path: string;
  sizeMb: number;
  refs: number;
  lastSeen: string;
  status: "indexed" | "orphan" | "missing";
}

export interface HealthReport {
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
}

// -------- generators --------

const HUES = [12, 26, 42, 88, 148, 168, 196, 218, 252, 288, 322, 340];
const swatch = (i: number) => `oklch(0.38 0.08 ${HUES[i % HUES.length]})`;

const PROMPT_POOL = [
  "cinematic low angle shot of a brutalist concrete building with neon signs in a rainy night",
  "macro photography of liquid mercury forming architectural geometric shapes",
  "aerial view of a cyberpunk megacity with intense glowing orange traffic lines",
  "atmospheric fog rolling over a monolithic gallery interior at dawn",
  "close up macro texture of biological tissue with iridescent scales",
  "editorial fashion photograph, oversized wool coat, cold northern light",
  "isometric render of a modular deep-space research station",
  "long exposure of headlights across a wet basalt highway",
  "still life of ceramic vessels on raw linen, north-facing window",
  "minimalist interior with soft morning light hitting oak floors",
  "weathered stone texture with sparse green moss, macro",
  "sci-fi corridor with rim-lit figures walking away from camera",
];

const NAME_POOL = [
  "Structure Alpha",
  "Visceral Flow",
  "Urban Grid",
  "Fog Study",
  "Iridescent Tissue",
  "Cold Coat",
  "Modular Node",
  "Basalt Trail",
  "Vessel Set",
  "Oak Interior",
  "Moss Macro",
  "Corridor Walk",
];

const PROJECT_SEEDS: Array<{ code: string; name: string }> = [
  { code: "PRJ-0822", name: "Cybernetic Realism" },
  { code: "PRJ-0821", name: "Arch Visual Set 04" },
  { code: "PRJ-0819", name: "Editorial FW26" },
  { code: "PRJ-0817", name: "Studio Ceramics" },
  { code: "PRJ-0815", name: "Deep Space Modules" },
  { code: "PRJ-0812", name: "Basalt Highway" },
  { code: "PRJ-0809", name: "Tissue Macro" },
  { code: "PRJ-0805", name: "Fog Interiors" },
  { code: "PRJ-0801", name: "Corridor Studies" },
  { code: "PRJ-0798", name: "Vessel Grammar" },
  { code: "PRJ-0794", name: "Rain City Plates" },
  { code: "PRJ-0790", name: "Iridescent Skin" },
];

const MODELS = ["SDXL v1.0 Turbo", "Flux.1-S", "SD3.5 Large", "Flux.1-Pro"];
const SAMPLERS = ["DPM++ 2M SDE", "Euler a", "DPM++ 3M", "UniPC"];

function daysAgoISO(days: number): string {
  const d = new Date("2026-07-01T12:00:00Z");
  d.setUTCDate(d.getUTCDate() - days);
  return d.toISOString();
}

const TAG_POOL: ProjectTag[][] = [
  ["editorial", "photo"],
  ["render", "wip"],
  ["editorial", "client"],
  ["photo"],
  ["render", "client"],
  ["photo", "wip"],
  ["render"],
  ["editorial", "wip"],
  ["client"],
  ["photo", "editorial"],
  ["render", "client"],
  ["wip"],
];

export const projects: ProjectRecord[] = PROJECT_SEEDS.map((s, i) => ({
  id: s.code.toLowerCase(),
  code: s.code,
  name: s.name,
  runCount: 3 + ((i * 7) % 6),
  imageCount: 24 + ((i * 13) % 40),
  updatedAt: daysAgoISO(i * 2 + 1),
  health: i % 5 === 0 ? "warn" : i % 11 === 0 ? "fail" : "ok",
  tags: TAG_POOL[i % TAG_POOL.length],
}));

export const runs: RunRecord[] = projects.flatMap((p, pi) =>
  Array.from({ length: 3 }).map((_, ri) => ({
    id: `${p.id}-run-${String(ri + 1).padStart(3, "0")}`,
    projectId: p.id,
    label: `Run ${String(ri + 1).padStart(3, "0")}`,
    createdAt: daysAgoISO(pi * 2 + ri),
    imageCount: 6 + ((pi + ri * 3) % 6),
  })),
);

export const images: ImageRecord[] = runs.flatMap((run, ri) => {
  const project = projects.find((p) => p.id === run.projectId)!;
  return Array.from({ length: run.imageCount }).map((_, si) => {
    const idx = ri * 10 + si;
    const status: ImageStatus = idx % 17 === 0 ? "failed" : idx % 23 === 0 ? "missing" : "present";
    return {
      id: `${run.id}-img-${String(si + 1).padStart(2, "0")}`,
      runId: run.id,
      projectId: run.projectId,
      slot: si + 1,
      prompt: PROMPT_POOL[idx % PROMPT_POOL.length],
      name: NAME_POOL[idx % NAME_POOL.length],
      seed: 100000 + idx * 1237,
      steps: 30 + (idx % 4) * 5,
      cfg: 6 + (idx % 5),
      model: MODELS[idx % MODELS.length],
      sampler: SAMPLERS[idx % SAMPLERS.length],
      latencyMs: 3200 + ((idx * 137) % 4200),
      status,
      swatch: swatch(idx + project.code.charCodeAt(4)),
      createdAt: run.createdAt,
    };
  });
});

export const registry: RegistryEntry[] = images.slice(0, 40).map((img, i) => ({
  id: `ast_${img.id.slice(-8)}`,
  projectId: img.projectId,
  path: `output/${img.projectId}/${img.runId}/${img.slot}.png`,
  sizeMb: +(0.4 + ((i * 0.37) % 4.2)).toFixed(2),
  refs: 1 + (i % 4),
  lastSeen: img.createdAt,
  status: img.status === "missing" ? "missing" : i % 9 === 0 ? "orphan" : "indexed",
}));

export const healthReport: HealthReport = {
  totalProjects: 167,
  totalRuns: 214,
  manifestImages: 2106,
  presentImages: 1567,
  missingRecords: 539,
  failedImages: 270,
  imageFiles: 2311,
  duplicateGroups: 474,
  cleanupRisk: 549,
  malformedRuns: 8,
  ratings: { starred: 8, rejected: 10 },
  outputSizeGb: 4.3,
};

// -------- helpers --------

export function getProject(id: string) {
  return projects.find((p) => p.id === id);
}
export function getRun(id: string) {
  return runs.find((r) => r.id === id);
}
export function getImage(id: string) {
  return images.find((i) => i.id === id);
}
export function imagesInRun(runId: string) {
  return images.filter((i) => i.runId === runId);
}
export function runsInProject(projectId: string) {
  return runs.filter((r) => r.projectId === projectId);
}
export function latestRunForProject(projectId: string) {
  return runsInProject(projectId)[0];
}
export function projectThumbSwatches(projectId: string): string[] {
  return images
    .filter((i) => i.projectId === projectId && i.status === "present")
    .slice(0, 4)
    .map((i) => i.swatch);
}
