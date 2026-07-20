import JSZip from "jszip";
import type { ImageRecord, Rating } from "@/lib/rafiki-data";

export type ExportFormat = "zip" | "manifest" | "csv";

export const MANIFEST_FIELDS = [
  "id",
  "project",
  "run",
  "slot",
  "name",
  "seed",
  "steps",
  "cfg",
  "model",
  "sampler",
  "rating",
  "status",
  "swatch",
] as const;

export type ManifestField = (typeof MANIFEST_FIELDS)[number];

export const DEFAULT_MANIFEST_FIELDS: ManifestField[] = [
  "id",
  "project",
  "run",
  "slot",
  "name",
  "seed",
  "cfg",
  "model",
  "rating",
  "status",
];

export const DEFAULT_FILENAME_TEMPLATE = "rafiki-{project}-{date}";

export interface ExportOptions {
  format: ExportFormat;
  destination: string;
  template: string;
  filenameTemplate: string;
  fields: ManifestField[];
  simulateFailure?: boolean;
}

export interface ExportProgress {
  stage: "queued" | "encoding" | "packaging" | "done" | "error";
  processed: number;
  total: number;
  message?: string;
}

type Enriched = ImageRecord & { rating: Rating };

async function imageBlob(image: ImageRecord): Promise<Blob> {
  const response = await fetch(image.url);
  if (!response.ok) {
    throw new Error(`failed to fetch ${image.name}`);
  }
  return await response.blob();
}

function fileStem(template: string, image: ImageRecord): string {
  return template
    .replace("{project}", image.projectId)
    .replace("{run}", image.runId.slice(-7))
    .replace("{slot}", String(image.slot).padStart(4, "0"))
    .replace("{name}", image.name.replace(/\s+/g, "_"));
}

function fieldValue(row: Enriched, field: ManifestField): unknown {
  switch (field) {
    case "id":
      return row.id;
    case "project":
      return row.projectId;
    case "run":
      return row.runId;
    case "slot":
      return row.slot;
    case "name":
      return row.name;
    case "seed":
      return row.seed;
    case "steps":
      return row.steps;
    case "cfg":
      return row.cfg;
    case "model":
      return row.model;
    case "sampler":
      return row.sampler;
    case "rating":
      return row.rating ?? "unrated";
    case "status":
      return row.status;
    case "swatch":
      return row.swatch;
  }
}

export function toManifestJson(
  rows: Enriched[],
  fields: ManifestField[],
  destination: string,
): string {
  const items = rows.map((r) => {
    const o: Record<string, unknown> = {};
    for (const f of fields) o[f] = fieldValue(r, f);
    return o;
  });
  return JSON.stringify({ destination, fields, items }, null, 2);
}

function csvCell(v: unknown): string {
  if (v === null || v === undefined) return "";
  const s = String(v);
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function toCsv(rows: Enriched[], fields: ManifestField[], template: string): string {
  const header = ["file", ...fields].map(csvCell).join(",");
  const body = rows
    .map((r) =>
      [`${fileStem(template, r)}.png`, ...fields.map((f) => fieldValue(r, f))]
        .map(csvCell)
        .join(","),
    )
    .join("\n");
  return `${header}\n${body}\n`;
}

function resolveFilename(template: string, format: ExportFormat, rows: Enriched[]): string {
  const clean = (template || "").trim() || `rafiki-batch-${Date.now()}`;
  const now = new Date();
  const date = now.toISOString().slice(0, 10);
  const projects = Array.from(new Set(rows.map((r) => r.projectId)));
  const project = projects.length === 1 ? projects[0] : "mixed";
  const ext = format === "zip" ? "zip" : format === "csv" ? "csv" : "json";
  const stem = clean
    .replace(/{date}/g, date)
    .replace(/{count}/g, String(rows.length))
    .replace(/{project}/g, project)
    .replace(/{format}/g, format)
    .replace(/[^\w.-]+/g, "_");
  return `${stem}.${ext}`;
}

export interface ExportResult {
  filename: string;
  blob: Blob;
  sizeKb: number;
  itemCount: number;
}

export async function runExport(
  images: ImageRecord[],
  ratings: Record<string, Rating>,
  opts: ExportOptions,
  onProgress: (p: ExportProgress) => void,
): Promise<ExportResult> {
  const total = images.length;
  if (total === 0) throw new Error("Nothing staged");

  onProgress({ stage: "queued", processed: 0, total });

  const enriched: Enriched[] = images.map((i) => ({
    ...i,
    rating: ratings[i.key] ?? ratings[i.id] ?? i.rating ?? null,
  }));

  if (opts.format === "zip") {
    const bad = enriched.find((i) => i.status === "failed" || i.status === "missing");
    if (bad) {
      throw new Error(
        `Cannot export "${bad.name}" — source is ${bad.status}. Remove it from the tray or switch format to Manifest.`,
      );
    }
  }

  if (opts.simulateFailure) {
    await new Promise((r) => setTimeout(r, 400));
    throw new Error("Simulated delivery failure at packaging stage");
  }

  const fields = opts.fields.length ? opts.fields : DEFAULT_MANIFEST_FIELDS;

  if (opts.format === "manifest") {
    onProgress({ stage: "packaging", processed: total, total });
    const blob = new Blob([toManifestJson(enriched, fields, opts.destination)], {
      type: "application/json",
    });
    return {
      filename: resolveFilename(opts.filenameTemplate, "manifest", enriched),
      blob,
      sizeKb: Math.max(1, Math.round(blob.size / 1024)),
      itemCount: total,
    };
  }

  if (opts.format === "csv") {
    onProgress({ stage: "packaging", processed: total, total });
    const blob = new Blob([toCsv(enriched, fields, opts.template)], {
      type: "text/csv",
    });
    return {
      filename: resolveFilename(opts.filenameTemplate, "csv", enriched),
      blob,
      sizeKb: Math.max(1, Math.round(blob.size / 1024)),
      itemCount: total,
    };
  }

  const zip = new JSZip();
  zip.file("manifest.json", toManifestJson(enriched, fields, opts.destination));
  zip.file("manifest.csv", toCsv(enriched, fields, opts.template));

  for (let i = 0; i < enriched.length; i++) {
    const img = enriched[i];
    onProgress({
      stage: "encoding",
      processed: i,
      total,
      message: `Encoding ${img.name}`,
    });
    await new Promise((r) => setTimeout(r, 60));
    const png = await imageBlob(img);
    zip.file(`${fileStem(opts.template, img)}.png`, png);
  }

  onProgress({ stage: "packaging", processed: total, total, message: "Zipping" });
  const blob = await zip.generateAsync({ type: "blob" });
  return {
    filename: resolveFilename(opts.filenameTemplate, "zip", enriched),
    blob,
    sizeKb: Math.max(1, Math.round(blob.size / 1024)),
    itemCount: total,
  };
}
