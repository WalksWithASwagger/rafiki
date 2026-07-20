import { expect, it } from "vitest";
import { toCsv, toManifestJson } from "./exporter";
import type { ImageRecord, Rating } from "./rafiki-data";

const row: ImageRecord & { rating: Rating } = {
  id: "image-1",
  key: "futureproof/run-1/image-1",
  runId: "run-1",
  runKey: "futureproof/run-1",
  projectId: "futureproof",
  slot: 1,
  prompt: "prompt",
  name: 'Poster, "final"\ncut',
  seed: 1,
  steps: 20,
  cfg: 7,
  model: "model",
  sampler: "sampler",
  latencyMs: 10,
  status: "present",
  swatch: "#000000",
  createdAt: "2026-07-20T00:00:00Z",
  url: "/output/image-1.png",
  thumbnailUrl: "/output/image-1.png",
  rating: "starred",
  file: "image-1.png",
  ok: true,
};

it("escapes CSV cells containing commas, quotes, and newlines", () => {
  const csv = toCsv([row], ["name", "rating"], "{project}-{slot}");

  expect(csv).toBe('file,name,rating\nfutureproof-0001.png,"Poster, ""final""\ncut",starred\n');
});

it("serializes manifest strings without corrupting their contents", () => {
  const manifest = toManifestJson([row], ["name", "rating"], "review");

  expect(manifest).toContain('"name": "Poster, \\"final\\"\\ncut"');
  expect(JSON.parse(manifest)).toEqual({
    destination: "review",
    fields: ["name", "rating"],
    items: [{ name: row.name, rating: "starred" }],
  });
});
