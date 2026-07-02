import { runExport, type ExportOptions } from "@/lib/exporter";
import { useTriageStore, type ExportJob } from "@/stores/triage-store";
import { getCachedImage } from "@/lib/rafiki-data";

let jobCounter = 0;
function jobId() {
  jobCounter += 1;
  return `job_${Date.now().toString(36)}_${jobCounter}`;
}

export interface JobGroup {
  label: string;
  imageIds: string[];
}

/**
 * Dispatch one ExportJob per group and process them sequentially so we
 * don't spike the browser main thread with parallel zip work.
 * Returns when every job has finished (done or error).
 */
export async function startBatchExport(
  groups: JobGroup[],
  baseOptions: Omit<ExportOptions, "simulateFailure"> & {
    simulateFailure?: boolean;
  },
): Promise<void> {
  const store = useTriageStore.getState();

  const created: ExportJob[] = groups
    .filter((g) => g.imageIds.length > 0)
    .map((g) => ({
      id: jobId(),
      label: g.label,
      imageIds: g.imageIds.slice(),
      format: baseOptions.format,
      stage: "queued" as const,
      processed: 0,
      total: g.imageIds.length,
      snapshot: {
        format: baseOptions.format,
        destination: baseOptions.destination,
        template: baseOptions.template,
        filenameTemplate: baseOptions.filenameTemplate,
        fields: baseOptions.fields,
        simulateFailure: baseOptions.simulateFailure,
      },
      startedAt: Date.now(),
    }));

  for (const job of created) store.addJob(job);

  for (const job of created) {
    await runSingleJob(job);
  }
}

async function runSingleJob(job: ExportJob): Promise<void> {
  const { updateJob, removeFromTray } = useTriageStore.getState();
  const ratings = useTriageStore.getState().ratings;
  const images = job.imageIds
    .map((id) => getCachedImage(id))
    .filter((x): x is NonNullable<typeof x> => Boolean(x));

  try {
    const result = await runExport(
      images,
      ratings,
      {
        format: job.snapshot.format,
        destination: job.snapshot.destination,
        template: job.snapshot.template,
        filenameTemplate: job.snapshot.filenameTemplate,
        fields: job.snapshot.fields,
        simulateFailure: job.snapshot.simulateFailure,
      },
      (p) => {
        updateJob(job.id, {
          stage: p.stage,
          processed: p.processed,
          total: p.total,
          message: p.message,
        });
      },
    );
    const blobUrl = URL.createObjectURL(result.blob);
    updateJob(job.id, {
      stage: "done",
      processed: result.itemCount,
      total: result.itemCount,
      error: undefined,
      message: `${result.itemCount} items · ${(result.sizeKb / 1024).toFixed(2)} MB`,
      result: {
        filename: result.filename,
        blobUrl,
        sizeKb: result.sizeKb,
      },
    });
    // Clear staged tray items that landed successfully (only when the job
    // is delivering exactly what's staged — safe idempotent removal).
    job.imageIds.forEach((id) => removeFromTray(id));
  } catch (err) {
    updateJob(job.id, {
      stage: "error",
      error: err instanceof Error ? err.message : "Delivery failed",
    });
  }
}

export async function retryJob(id: string): Promise<void> {
  const state = useTriageStore.getState();
  const job = state.jobs.find((j) => j.id === id);
  if (!job) return;
  state.updateJob(id, {
    stage: "queued",
    processed: 0,
    error: undefined,
    message: "Retrying…",
    result: undefined,
  });
  const refreshed = useTriageStore.getState().jobs.find((j) => j.id === id);
  if (refreshed) await runSingleJob(refreshed);
}
