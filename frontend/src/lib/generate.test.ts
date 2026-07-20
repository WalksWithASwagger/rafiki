import { afterEach, describe, expect, it, vi } from "vitest";
import {
  mediaReferenceUrl,
  resultImageUrl,
  runGenerate,
  type GeneratePayload,
  type GenerateResult,
} from "./generate";

const payload: GeneratePayload = {
  mode: "single",
  project: "futureproof",
  model: "test-model",
  aspect_ratio: "1:1",
  quality: "standard",
  resolution: "1k",
  workers: 1,
  dry_run: true,
  prompt: "A real night sky",
};

const result: GenerateResult = {
  ok: true,
  all_ok: true,
  mode: "single",
  project: "futureproof",
  generated: 1,
  total: 1,
  run_id: "abc123",
  images: [{ name: "sky", ok: true, output_path: "nested\\sky.png" }],
};

afterEach(() => vi.unstubAllGlobals());

describe("runGenerate", () => {
  it("serializes the request and normalizes result paths", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(result),
    });
    vi.stubGlobal("fetch", fetchMock);

    const response = await runGenerate(payload);

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/regen",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(payload),
      }),
    );
    expect(response.images[0].output_path).toBe("sky.png");
  });

  it("combines backend error and detail without losing context", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: vi.fn().mockResolvedValue({ error: "Generation rejected", detail: "bad prompt" }),
      }),
    );

    await expect(runGenerate(payload)).rejects.toThrow("Generation rejected: bad prompt");
  });
});

it("builds result and reference URLs only from complete safe inputs", () => {
  expect(resultImageUrl(result, result.images[0])).toBe("/output/futureproof/run-abc123/sky.png");
  expect(resultImageUrl({ ...result, run_id: "" }, result.images[0])).toBe("");
  expect(mediaReferenceUrl({ id: "1", kind: "image", source_url: "/media/cache/sky.png" })).toBe(
    "/media/cache/sky.png",
  );
  expect(
    mediaReferenceUrl({
      id: "2",
      kind: "image",
      root_key: "archive",
      relative_path: "runs/sky.png",
    }),
  ).toBe("/media/archive/runs/sky.png");
  expect(mediaReferenceUrl({ id: "3", kind: "image", source_url: "https://example.com" })).toBe("");
});
