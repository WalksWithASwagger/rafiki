import { expect, it } from "vitest";
import { normalizeState, type ImageRecord, type LibraryStatePayload } from "./rafiki-data";

function image(id: string, status: ImageRecord["status"]): ImageRecord {
  return {
    id,
    key: `project/run/${id}`,
    runId: "run-1",
    runKey: "project/run-1",
    projectId: "project",
    slot: 1,
    prompt: "prompt",
    name: id,
    seed: 1,
    steps: 20,
    cfg: 7,
    model: "model",
    sampler: "sampler",
    latencyMs: 10,
    status,
    swatch: "#000000",
    createdAt: "2026-07-20T00:00:00Z",
    url: `/output/${id}.png`,
    thumbnailUrl: `/output/${id}.png`,
    rating: null,
    file: `${id}.png`,
    ok: status === "present",
  };
}

it("normalizes ratings and derives visible and archive totals", () => {
  const present = image("present", "present");
  const missing = image("missing", "missing");
  const payload: LibraryStatePayload = {
    version: 1,
    source: "fixture",
    outputRoot: "/tmp/output",
    projects: [
      {
        id: "project",
        code: "P",
        name: "Project",
        runCount: 1,
        imageCount: 2,
        presentCount: 1,
        failedCount: 0,
        missingCount: 1,
        updatedAt: "2026-07-20T00:00:00Z",
        health: "warn",
        tags: [],
      },
    ],
    runs: [
      {
        id: "run-1",
        key: "project/run-1",
        projectId: "project",
        label: "Run 1",
        createdAt: "2026-07-20T00:00:00Z",
        imageCount: 2,
        model: "model",
        style: "style",
        aspectRatio: "1:1",
        promptFile: "prompts.txt",
      },
    ],
    images: [present, missing],
    ratings: { [present.key]: "star", [missing.key]: "reject" },
    health: {
      ok: false,
      totalProjects: 3,
      totalRuns: 4,
      manifestImages: 5,
      presentImages: 3,
      missingRecords: 1,
      failedImages: 1,
      imageFiles: 6,
      duplicateGroups: 0,
      cleanupRisk: 0,
      malformedRuns: 0,
      ratings: { starred: 1, rejected: 1 },
      outputSizeGb: 1,
      warnings: [],
    },
    registry: { entries: [], summary: { entries: 0, approved: 0, unapproved: 0 } },
  };

  const state = normalizeState(payload);

  expect(state.ratings).toEqual({ [present.key]: "starred", [missing.key]: "rejected" });
  expect(state.images.map((entry) => entry.rating)).toEqual(["starred", "rejected"]);
  expect(state.totals.visible).toEqual({
    projects: 1,
    runs: 1,
    images: 2,
    present: 1,
    missing: 1,
    failed: 0,
    starred: 1,
    rejected: 1,
  });
  expect(state.totals.archive).toMatchObject({ projects: 3, runs: 4, images: 5, files: 6 });
  expect(state.sourceWarnings).toEqual([]);
});
