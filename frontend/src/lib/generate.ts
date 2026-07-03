import { useQuery } from "@tanstack/react-query";

export interface GenerateModelOption {
  id: string;
  label: string;
  aliases: string[];
}

export interface GenerateStyleOption {
  key: string;
  name: string;
  description?: string;
  useContext?: string;
  default?: boolean;
  special?: boolean;
}

export interface GenerateOptions {
  defaultModel: string;
  models: GenerateModelOption[];
  aliases: Record<string, string>;
  aspectPresets: Array<{ key: string; label: string; value: string }>;
  aspectRatios: string[];
  qualities: string[];
  resolutions: string[];
  referenceRoles: string[];
  styles: GenerateStyleOption[];
}

export interface InlinePrompt {
  name?: string;
  prompt: string;
  model?: string;
  style?: string;
  aspect_ratio?: string;
  quality?: string;
}

export interface GeneratePayload {
  mode: "single" | "batch";
  project: string;
  model: string;
  aspect_ratio: string;
  quality: string;
  resolution: string;
  style?: string;
  workers: number;
  dry_run: boolean;
  confirm_execute?: boolean;
  reference_image?: string;
  reference_images?: string[];
  global_reference_images?: string[];
  reference_role?: string;
  composition_references?: string[];
  name?: string;
  prompt?: string;
  prompt_file?: string;
  prompts?: InlinePrompt[];
}

export interface GenerateResultImage {
  name: string;
  ok: boolean;
  output_path?: string;
}

export interface GenerateResult {
  ok: boolean;
  all_ok: boolean;
  mode: "single" | "batch";
  project: string;
  generated: number;
  total: number;
  run_id: string;
  viewer_url?: string;
  run_viewer_url?: string;
  library_url?: string;
  images: GenerateResultImage[];
  registry?: Record<string, unknown>;
}

export interface PromptPreviewResult {
  ok: boolean;
  promptFile: string;
  count: number;
  prompts: InlinePrompt[];
  metadata: {
    source: string;
    format: string;
  };
}

export interface MediaReference {
  id: string;
  kind: string;
  title?: string;
  relative_path?: string;
  root_key?: string;
  source_url?: string;
}

export async function fetchGenerateOptions(): Promise<GenerateOptions> {
  const response = await fetch("/api/generate-options", {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Generate options failed: ${response.status}`);
  }
  return response.json();
}

export function useGenerateOptions() {
  return useQuery({
    queryKey: ["generate-options"],
    queryFn: fetchGenerateOptions,
    staleTime: 60_000,
  });
}

export async function previewPromptFile(promptFile: string): Promise<PromptPreviewResult> {
  const response = await fetch("/api/prompt-preview", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ prompt_file: promptFile }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(errorMessageFromPayload(payload, `Prompt preview failed: ${response.status}`));
  }
  return payload;
}

export async function runGenerate(
  payload: GeneratePayload,
  signal?: AbortSignal,
): Promise<GenerateResult> {
  const response = await fetch("/api/regen", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok || !data.ok) {
    throw new Error(errorMessageFromPayload(data, `Generation failed: ${response.status}`));
  }
  return {
    ...data,
    images: Array.isArray(data.images)
      ? data.images.map((image: GenerateResultImage) => ({
          ...image,
          output_path: image.output_path?.split(/[\\/]/).pop(),
        }))
      : [],
  };
}

export async function fetchMediaReferences(): Promise<MediaReference[]> {
  const response = await fetch("/api/media?kind=image&view=review", {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) return [];
  const payload = await response.json().catch(() => ({}));
  return Array.isArray(payload.entries) ? payload.entries : [];
}

export function resultImageUrl(result: GenerateResult, image: GenerateResultImage) {
  const fileName = image.output_path?.split(/[\\/]/).pop();
  if (!fileName || !result.project || !result.run_id) return "";
  return `/output/${result.project}/run-${result.run_id}/${fileName}`;
}

export function mediaReferenceUrl(entry: MediaReference) {
  if (entry.source_url?.startsWith("/media/")) return entry.source_url;
  if (entry.root_key && entry.relative_path) {
    return `/media/${entry.root_key}/${entry.relative_path}`;
  }
  return "";
}

function errorMessageFromPayload(payload: Record<string, unknown>, fallback: string) {
  const error = typeof payload.error === "string" ? payload.error : "";
  const detail = typeof payload.detail === "string" ? payload.detail : "";
  if (error && detail && detail !== error) return `${error}: ${detail}`;
  return error || detail || fallback;
}
