import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  useEffect,
  useMemo,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileSearch,
  Loader2,
  Play,
  Plus,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Square,
  Trash2,
  X,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ErrorBlock } from "@/components/state/error-block";
import {
  fetchMediaReferences,
  mediaReferenceUrl,
  previewPromptFile,
  resultImageUrl,
  runGenerate,
  useGenerateOptions,
  type GenerateOptions,
  type GeneratePayload,
  type GenerateResult,
  type InlinePrompt,
  type PromptPreviewResult,
} from "@/lib/generate";
import { useLibraryState, type ImageRecord } from "@/lib/rafiki-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/generate")({
  head: () => ({
    meta: [
      { title: "Generate - Rafiki" },
      {
        name: "description",
        content: "Create image generation runs from local prompts, styles, and references.",
      },
    ],
  }),
  errorComponent: ({ error, reset }) => (
    <AppShell>
      <ErrorBlock error={error} reset={reset} />
    </AppShell>
  ),
  component: GeneratePage,
});

type Mode = "single" | "batch-inline" | "batch-file";
type ReferenceBucket = "primary" | "global" | "composition";

interface PromptRow {
  id: string;
  name: string;
  prompt: string;
  model?: string;
  style?: string;
  aspectRatio?: string;
  quality?: string;
}

interface GenerateHistoryItem {
  id: string;
  createdAt: string;
  project: string;
  runId: string;
  mode: GeneratePayload["mode"];
  dryRun: boolean;
  status: "ok" | "partial";
  provider: string;
  model: string;
  promptCount: number;
  referenceCount: number;
  generated: number;
  total: number;
  draftHash: string;
  viewerUrl?: string;
  runViewerUrl?: string;
  libraryRunUrl: string;
  manifestUrl: string;
}

const HISTORY_KEY = "rafiki.generate.history.v1";
const HISTORY_LIMIT = 8;

const makePromptRow = (): PromptRow => ({
  id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  name: "",
  prompt: "",
});

function GeneratePage() {
  const optionsQuery = useGenerateOptions();
  const libraryQuery = useLibraryState();
  const queryClient = useQueryClient();
  const mediaQuery = useQuery({
    queryKey: ["generate-media-refs"],
    queryFn: fetchMediaReferences,
    staleTime: 30_000,
  });

  const options = optionsQuery.data;
  const defaultStyle = options?.styles.find((style) => style.default)?.key || "none";
  const [mode, setMode] = useState<Mode>("single");
  const [project, setProject] = useState("studio");
  const [model, setModel] = useState("");
  const [style, setStyle] = useState("none");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [quality, setQuality] = useState("high");
  const [resolution, setResolution] = useState("1K");
  const [workers, setWorkers] = useState(1);
  const [dryRun, setDryRun] = useState(true);
  const [confirmExecute, setConfirmExecute] = useState(false);
  const [singleName, setSingleName] = useState("");
  const [singlePrompt, setSinglePrompt] = useState("");
  const [promptRows, setPromptRows] = useState<PromptRow[]>([makePromptRow(), makePromptRow()]);
  const [promptFile, setPromptFile] = useState("");
  const [promptPreview, setPromptPreview] = useState<PromptPreviewResult | null>(null);
  const [previewBusy, setPreviewBusy] = useState(false);
  const [referenceRole, setReferenceRole] = useState("style");
  const [localReference, setLocalReference] = useState("");
  const [primaryReference, setPrimaryReference] = useState("");
  const [globalReferences, setGlobalReferences] = useState<string[]>([]);
  const [compositionReferences, setCompositionReferences] = useState<string[]>([]);
  const [perPromptReferences, setPerPromptReferences] = useState("");
  const [referenceSearch, setReferenceSearch] = useState("");
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [lastPayload, setLastPayload] = useState<GeneratePayload | null>(null);
  const [history, setHistory] = useState<GenerateHistoryItem[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  useEffect(() => {
    setHistory(readGenerateHistory());
  }, []);

  useEffect(() => {
    if (!options) return;
    setModel((current) => current || options.defaultModel);
    setStyle((current) => current || defaultStyle);
    setAspectRatio((current) => current || options.aspectRatios[0] || "16:9");
    setQuality((current) => current || options.qualities[0] || "high");
    setResolution((current) => current || options.resolutions[0] || "1K");
    setReferenceRole((current) => current || options.referenceRoles[0] || "style");
  }, [defaultStyle, options]);

  const presentImages = useMemo(
    () =>
      (libraryQuery.data?.images ?? [])
        .filter((image) => image.status === "present" && image.url)
        .slice(0, 80),
    [libraryQuery.data],
  );

  const filteredImages = useMemo(() => {
    const query = referenceSearch.trim().toLowerCase();
    if (!query) return presentImages.slice(0, 18);
    return presentImages
      .filter((image) =>
        [image.name, image.projectId, image.prompt, image.model].some((value) =>
          value.toLowerCase().includes(query),
        ),
      )
      .slice(0, 18);
  }, [presentImages, referenceSearch]);

  const mediaReferences = useMemo(
    () =>
      (mediaQuery.data ?? [])
        .map((entry) => ({
          id: entry.id,
          title: entry.title || entry.relative_path || entry.id,
          url: mediaReferenceUrl(entry),
        }))
        .filter((entry) => entry.url)
        .slice(0, 10),
    [mediaQuery.data],
  );

  const selectedReferenceCount =
    (primaryReference ? 1 : 0) + globalReferences.length + compositionReferences.length;
  const totalReferenceCount = selectedReferenceCount + splitReferences(perPromptReferences).length;
  const currentModel = model || options?.defaultModel || "gemini-2.5-flash-image";
  const currentPromptCount = promptCountForDraft(mode, singlePrompt, promptRows, promptPreview);
  const modelSelectOptions = modelOptionsFor(options);
  const styleSelectOptions = styleOptionsFor(options);
  const aspectSelectOptions = aspectOptionsFor(options);
  const qualitySelectOptions = qualityOptionsFor(options);
  const rowModelOptions = inheritOptions("Run model", modelSelectOptions);
  const rowStyleOptions = inheritOptions("Run style", styleSelectOptions);
  const rowAspectOptions = inheritOptions("Run aspect", aspectSelectOptions);
  const rowQualityOptions = inheritOptions("Run quality", qualitySelectOptions);
  const currentDraftHash = useMemo(
    () =>
      draftHashForState({
        project,
        mode,
        model: currentModel,
        style,
        aspectRatio,
        quality,
        resolution,
        singleName,
        singlePrompt,
        promptRows,
        promptFile,
        primaryReference,
        globalReferences,
        compositionReferences,
        perPromptReferences,
        referenceRole,
      }),
    [
      project,
      mode,
      currentModel,
      style,
      aspectRatio,
      quality,
      resolution,
      singleName,
      singlePrompt,
      promptRows,
      promptFile,
      primaryReference,
      globalReferences,
      compositionReferences,
      perPromptReferences,
      referenceRole,
    ],
  );
  const latestDryRunForDraft = useMemo(
    () => history.find((item) => item.dryRun && item.draftHash === currentDraftHash),
    [currentDraftHash, history],
  );
  const currentProvider = providerLabelForModel(currentModel);

  const addReference = (source: string, bucket: ReferenceBucket) => {
    const value = source.trim();
    if (!value) return;
    if (bucket === "primary") {
      setPrimaryReference(value);
    } else if (bucket === "global") {
      setGlobalReferences((current) => uniq([...current, value]));
    } else {
      setCompositionReferences((current) => uniq([...current, value]));
    }
    setNotice(`${bucketLabel(bucket)} reference added.`);
  };

  const saveHistoryItem = (item: GenerateHistoryItem) => {
    setHistory((current) => {
      const next = [
        item,
        ...current.filter(
          (entry) => !(entry.project === item.project && entry.runId === item.runId),
        ),
      ].slice(0, HISTORY_LIMIT);
      writeGenerateHistory(next);
      return next;
    });
  };

  const addLocalReference = (bucket: ReferenceBucket) => {
    addReference(localReference, bucket);
    setLocalReference("");
  };

  const buildPayload = (): GeneratePayload => {
    const shared = {
      project,
      model: model || options?.defaultModel || "gemini-2.5-flash-image",
      aspect_ratio: aspectRatio || "16:9",
      quality,
      resolution,
      style: style && style !== "none" ? style : undefined,
      workers,
      dry_run: dryRun,
      confirm_execute: confirmExecute,
      reference_image: primaryReference || undefined,
      reference_images: splitReferences(perPromptReferences),
      global_reference_images: globalReferences,
      reference_role: referenceRole,
      composition_references: compositionReferences,
    };

    if (!shared.project.trim()) throw new Error("Project slug is required.");

    if (mode === "single") {
      if (!singlePrompt.trim()) throw new Error("Single prompt is required.");
      return {
        ...shared,
        mode: "single",
        name: singleName.trim() || undefined,
        prompt: singlePrompt.trim(),
      };
    }

    if (mode === "batch-file") {
      if (!promptFile.trim()) throw new Error("Prompt file path is required.");
      return {
        ...shared,
        mode: "batch",
        prompt_file: promptFile.trim(),
      };
    }

    const prompts = promptRows.map(inlinePromptFromRow).filter((row) => row.prompt);
    if (!prompts.length) throw new Error("Add at least one inline batch prompt.");
    return {
      ...shared,
      mode: "batch",
      prompts,
    };
  };

  const submit = async () => {
    setError("");
    setNotice("");
    let payload: GeneratePayload;
    try {
      payload = buildPayload();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      return;
    }
    if (!payload.dry_run && !latestDryRunForDraft) {
      setError("Run a matching dry-run before provider execution.");
      return;
    }
    if (!payload.dry_run && !confirmExecute) {
      setError("Real provider execution requires the confirmation checkbox.");
      return;
    }

    const controller = new AbortController();
    const submittedDraftHash = currentDraftHash;
    setAbortController(controller);
    setBusy(true);
    setLastPayload(payload);
    try {
      const response = await runGenerate(payload, controller.signal);
      setResult(response);
      saveHistoryItem(historyItemFromResult(response, payload, submittedDraftHash));
      setNotice(
        payload.dry_run
          ? "Dry run complete. No provider spend was triggered."
          : "Run complete. Refresh the library to load the new archive state.",
      );
      if (!payload.dry_run) {
        void queryClient.invalidateQueries({ queryKey: ["library-state"] });
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setNotice(
          "Stopped waiting in this browser. This does not cancel provider work already handed off.",
        );
      } else {
        setError(err instanceof Error ? err.message : String(err));
      }
    } finally {
      setBusy(false);
      setAbortController(null);
    }
  };

  const previewPrompt = async () => {
    setError("");
    setPromptPreview(null);
    if (!promptFile.trim()) {
      setError("Prompt file path is required.");
      return;
    }
    setPreviewBusy(true);
    try {
      setPromptPreview(await previewPromptFile(promptFile.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setPreviewBusy(false);
    }
  };

  if (optionsQuery.error || libraryQuery.error) {
    return (
      <AppShell>
        <ErrorBlock
          error={optionsQuery.error || libraryQuery.error}
          reset={() => {
            void optionsQuery.refetch();
            void libraryQuery.refetch();
          }}
        />
      </AppShell>
    );
  }

  const loading = optionsQuery.isLoading || libraryQuery.isLoading || !options;

  return (
    <AppShell>
      <PageHeader
        crumbs={[{ label: "PROJECT", mono: true }, { label: "Generate" }]}
        actions={
          <div className="flex flex-wrap items-center justify-end gap-2">
            <span
              className={cn(
                "rounded border px-2 py-1 text-[10px] font-mono uppercase tracking-widest",
                dryRun
                  ? "border-brand/30 bg-brand/10 text-brand"
                  : "border-amber-400/30 bg-amber-400/10 text-amber-300",
              )}
            >
              {dryRun ? "Dry-run default" : "Provider run"}
            </span>
            <button
              onClick={() => void queryClient.invalidateQueries({ queryKey: ["library-state"] })}
              className="flex items-center gap-2 rounded border border-border px-3 py-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className="size-3.5" strokeWidth={1.5} />
              Refresh library
            </button>
          </div>
        }
      />

      <div className="flex-1 overflow-y-auto p-4 sm:p-8">
        {loading ? (
          <div className="grid min-h-[420px] place-items-center text-xs font-mono uppercase tracking-widest text-muted-foreground">
            Loading generation controls...
          </div>
        ) : (
          <div className="mx-auto flex max-w-[1600px] flex-col gap-6">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-brand">
                  <Sparkles className="size-3.5" strokeWidth={1.5} />
                  Image generation
                </div>
                <h1 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">Generate</h1>
                <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
                  Build a run from local prompt text, prompt packs, and existing archive references.
                  Dry-run stays on until you explicitly confirm provider spend.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-px overflow-hidden rounded border border-border bg-border text-center">
                <MiniStat label="Mode" value={modeLabel(mode)} />
                <MiniStat label="Refs" value={totalReferenceCount} />
                <MiniStat label="Model" value={currentModel} compact />
              </div>
            </div>

            {(error || notice) && (
              <StatusBanner
                tone={error ? "error" : "info"}
                message={error || notice}
                onClear={() => {
                  setError("");
                  setNotice("");
                }}
              />
            )}

            <RunHistoryPanel
              items={history}
              onClear={() => {
                writeGenerateHistory([]);
                setHistory([]);
              }}
            />

            <div className="grid grid-cols-1 gap-6 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
              <SectionPanel title="Run setup" eyebrow="Config">
                <div className="space-y-4">
                  <TextField
                    label="Project slug"
                    value={project}
                    onChange={setProject}
                    placeholder="campaign-visuals"
                    testId="generate-project"
                  />

                  <div>
                    <FieldLabel>Mode</FieldLabel>
                    <div className="grid grid-cols-3 gap-1 rounded border border-border bg-background p-1">
                      {(["single", "batch-inline", "batch-file"] as const).map((nextMode) => (
                        <button
                          key={nextMode}
                          onClick={() => setMode(nextMode)}
                          data-generate-mode={nextMode}
                          className={cn(
                            "rounded px-2 py-2 text-[10px] font-mono uppercase tracking-widest transition-colors",
                            mode === nextMode
                              ? "bg-brand text-black"
                              : "text-muted-foreground hover:text-foreground",
                          )}
                        >
                          {modeLabel(nextMode)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <SelectField
                    label="Model"
                    value={model}
                    onChange={setModel}
                    options={modelSelectOptions}
                  />

                  <SelectField
                    label="Style composition"
                    value={style}
                    onChange={setStyle}
                    options={styleSelectOptions}
                  />

                  <div className="grid grid-cols-2 gap-3">
                    <SelectField
                      label="Aspect"
                      value={aspectRatio}
                      onChange={setAspectRatio}
                      options={aspectSelectOptions}
                    />
                    <SelectField
                      label="Quality"
                      value={quality}
                      onChange={setQuality}
                      options={qualitySelectOptions}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <SelectField
                      label="Resolution"
                      value={resolution}
                      onChange={setResolution}
                      options={options.resolutions.map((entry) => ({
                        value: entry,
                        label: entry,
                      }))}
                    />
                    <NumberField
                      label="Workers"
                      value={workers}
                      onChange={(value) => setWorkers(Math.min(Math.max(value, 1), 8))}
                    />
                  </div>

                  <ToggleRow
                    label="Dry-run"
                    hint="Validates and writes run metadata without provider spend."
                    checked={dryRun}
                    testId="generate-dry-run-toggle"
                    onChange={(checked) => {
                      setDryRun(checked);
                      if (checked) setConfirmExecute(false);
                    }}
                  />

                  <ExecutionBrief
                    dryRun={dryRun}
                    provider={currentProvider}
                    model={currentModel}
                    promptCount={currentPromptCount}
                    referenceCount={totalReferenceCount}
                    manifestUrl={latestDryRunForDraft?.manifestUrl || ""}
                    confirmed={confirmExecute}
                  />

                  {!dryRun && (
                    <ToggleRow
                      label="Confirm provider spend"
                      hint="Required before a real generation request leaves the browser."
                      checked={confirmExecute}
                      onChange={setConfirmExecute}
                      tone="warn"
                      testId="generate-confirm-execute"
                    />
                  )}

                  <div className="flex flex-col gap-2 pt-2">
                    <button
                      onClick={() => void submit()}
                      disabled={busy}
                      data-testid="generate-submit"
                      className="flex items-center justify-center gap-2 rounded bg-brand px-4 py-3 text-xs font-bold uppercase tracking-widest text-black transition-opacity disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {busy ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Play className="size-4" fill="currentColor" />
                      )}
                      {busy ? "Running" : dryRun ? "Dry-run" : "Execute run"}
                    </button>
                    {busy && (
                      <button
                        onClick={() => abortController?.abort()}
                        className="flex items-center justify-center gap-2 rounded border border-border px-4 py-2 text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                      >
                        <Square className="size-3.5" />
                        Stop waiting
                      </button>
                    )}
                  </div>
                </div>
              </SectionPanel>

              <SectionPanel title="Prompt editor" eyebrow="Input">
                {mode === "single" && (
                  <div className="space-y-4">
                    <TextField
                      label="Image name"
                      value={singleName}
                      onChange={setSingleName}
                      placeholder="Hero portrait"
                      testId="generate-single-name"
                    />
                    <TextAreaField
                      label="Prompt"
                      value={singlePrompt}
                      onChange={setSinglePrompt}
                      placeholder="Describe the image you want Rafiki to make..."
                      minRows={14}
                      testId="generate-single-prompt"
                    />
                  </div>
                )}

                {mode === "batch-inline" && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-xs text-muted-foreground">
                        Add one prompt per row. Leave row controls on run defaults or choose
                        prompt-specific overrides.
                      </p>
                      <button
                        onClick={() => setPromptRows((current) => [...current, makePromptRow()])}
                        className="flex shrink-0 items-center gap-2 rounded border border-border px-3 py-1.5 text-[11px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                      >
                        <Plus className="size-3.5" />
                        Row
                      </button>
                    </div>
                    <div className="space-y-3">
                      {promptRows.map((row, index) => (
                        <div
                          key={row.id}
                          className="rounded border border-border bg-background p-3"
                        >
                          <div className="mb-2 flex items-center justify-between gap-2">
                            <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                              Prompt {index + 1}
                            </span>
                            <button
                              onClick={() =>
                                setPromptRows((current) =>
                                  current.length === 1
                                    ? [makePromptRow()]
                                    : current.filter((item) => item.id !== row.id),
                                )
                              }
                              className="grid size-7 place-items-center rounded border border-border text-muted-foreground hover:text-foreground"
                              aria-label="Remove prompt row"
                            >
                              <Trash2 className="size-3.5" />
                            </button>
                          </div>
                          <input
                            value={row.name}
                            onChange={(event) =>
                              updatePromptRow(setPromptRows, row.id, { name: event.target.value })
                            }
                            placeholder="Optional name"
                            data-testid="generate-batch-name"
                            className="mb-2 w-full rounded border border-border bg-sidebar px-3 py-2 text-sm outline-none focus:border-brand"
                          />
                          <textarea
                            value={row.prompt}
                            onChange={(event) =>
                              updatePromptRow(setPromptRows, row.id, { prompt: event.target.value })
                            }
                            placeholder="Prompt text"
                            rows={5}
                            data-testid="generate-batch-prompt"
                            className="w-full resize-y rounded border border-border bg-sidebar px-3 py-2 text-sm outline-none focus:border-brand"
                          />
                          <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 2xl:grid-cols-4">
                            <SelectField
                              label="Model override"
                              value={row.model || ""}
                              onChange={(value) =>
                                updatePromptRow(setPromptRows, row.id, { model: value })
                              }
                              options={rowModelOptions}
                              testId="generate-batch-model"
                            />
                            <SelectField
                              label="Style override"
                              value={row.style || ""}
                              onChange={(value) =>
                                updatePromptRow(setPromptRows, row.id, { style: value })
                              }
                              options={rowStyleOptions}
                              testId="generate-batch-style"
                            />
                            <SelectField
                              label="Aspect override"
                              value={row.aspectRatio || ""}
                              onChange={(value) =>
                                updatePromptRow(setPromptRows, row.id, { aspectRatio: value })
                              }
                              options={rowAspectOptions}
                              testId="generate-batch-aspect"
                            />
                            <SelectField
                              label="Quality override"
                              value={row.quality || ""}
                              onChange={(value) =>
                                updatePromptRow(setPromptRows, row.id, { quality: value })
                              }
                              options={rowQualityOptions}
                              testId="generate-batch-quality"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {mode === "batch-file" && (
                  <div className="space-y-4">
                    <TextField
                      label="Markdown prompt file"
                      value={promptFile}
                      onChange={setPromptFile}
                      placeholder="examples/quickstart-image-prompts.md"
                      testId="generate-prompt-file"
                    />
                    <button
                      onClick={() => void previewPrompt()}
                      disabled={previewBusy}
                      data-testid="generate-preview-prompt-file"
                      className="flex items-center gap-2 rounded border border-brand px-4 py-2 text-xs font-mono uppercase tracking-widest text-brand hover:bg-brand hover:text-black disabled:opacity-50"
                    >
                      {previewBusy ? (
                        <Loader2 className="size-3.5 animate-spin" />
                      ) : (
                        <FileSearch className="size-3.5" />
                      )}
                      Preview prompt file
                    </button>
                    {promptPreview && (
                      <div className="rounded border border-border bg-background p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="text-sm font-semibold">
                              {promptPreview.count} prompt
                              {promptPreview.count === 1 ? "" : "s"} parsed
                            </div>
                            <div className="mt-1 text-xs font-mono text-muted-foreground">
                              {promptPreview.promptFile}
                            </div>
                          </div>
                          <CheckCircle2 className="size-5 text-brand" strokeWidth={1.5} />
                        </div>
                        <div className="mt-4 max-h-72 space-y-2 overflow-y-auto pr-1">
                          {promptPreview.prompts.slice(0, 8).map((prompt, index) => (
                            <div
                              key={`${prompt.name}-${index}`}
                              className="rounded border border-border bg-sidebar p-3"
                            >
                              <div className="text-xs font-semibold">{prompt.name}</div>
                              <p className="mt-1 line-clamp-3 text-xs text-muted-foreground">
                                {prompt.prompt}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="mt-6 rounded border border-border bg-background p-4">
                  <FieldLabel>Per-prompt reference list</FieldLabel>
                  <textarea
                    value={perPromptReferences}
                    onChange={(event) => setPerPromptReferences(event.target.value)}
                    placeholder="/output/project/run-20260101-100000/ref.png&#10;/output/project/run-20260101-100000/second.png"
                    rows={3}
                    className="w-full resize-y rounded border border-border bg-sidebar px-3 py-2 text-xs font-mono outline-none focus:border-brand"
                  />
                  <p className="mt-2 text-xs text-muted-foreground">
                    Optional. One source is reused for all prompts; multiple sources must match the
                    prompt count.
                  </p>
                </div>
              </SectionPanel>

              <SectionPanel title="Reference rail" eyebrow="Sources">
                <div className="space-y-5">
                  <SelectField
                    label="Reference role"
                    value={referenceRole}
                    onChange={setReferenceRole}
                    options={options.referenceRoles.map((entry) => ({
                      value: entry,
                      label: entry,
                    }))}
                  />

                  <div>
                    <FieldLabel>Local or archive path</FieldLabel>
                    <input
                      value={localReference}
                      onChange={(event) => setLocalReference(event.target.value)}
                      placeholder="/output/project/run-.../image.png"
                      className="w-full rounded border border-border bg-background px-3 py-2 text-xs font-mono outline-none focus:border-brand"
                    />
                    <div className="mt-2 grid grid-cols-3 gap-1">
                      {(["primary", "global", "composition"] as const).map((bucket) => (
                        <button
                          key={bucket}
                          onClick={() => addLocalReference(bucket)}
                          className="rounded border border-border px-2 py-1.5 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                        >
                          {bucketLabel(bucket)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <SelectedReferences
                    primary={primaryReference}
                    global={globalReferences}
                    composition={compositionReferences}
                    onClearPrimary={() => setPrimaryReference("")}
                    onRemoveGlobal={(source) =>
                      setGlobalReferences((current) => current.filter((item) => item !== source))
                    }
                    onRemoveComposition={(source) =>
                      setCompositionReferences((current) =>
                        current.filter((item) => item !== source),
                      )
                    }
                  />

                  <div>
                    <FieldLabel>Pick from library</FieldLabel>
                    <input
                      value={referenceSearch}
                      onChange={(event) => setReferenceSearch(event.target.value)}
                      placeholder="Search project, prompt, model"
                      className="mb-3 w-full rounded border border-border bg-background px-3 py-2 text-sm outline-none focus:border-brand"
                    />
                    <div className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
                      {filteredImages.map((image) => (
                        <ReferenceImageRow
                          key={image.id}
                          image={image}
                          onUsePrimary={() => addReference(image.url, "primary")}
                          onUseGlobal={() => addReference(image.url, "global")}
                        />
                      ))}
                      {!filteredImages.length && (
                        <div className="rounded border border-border bg-background p-4 text-xs text-muted-foreground">
                          No present library images match.
                        </div>
                      )}
                    </div>
                  </div>

                  {mediaReferences.length > 0 && (
                    <div>
                      <FieldLabel>Media image references</FieldLabel>
                      <div className="space-y-2">
                        {mediaReferences.map((entry) => (
                          <div
                            key={entry.id}
                            className="flex items-center justify-between gap-3 rounded border border-border bg-background p-2"
                          >
                            <div className="min-w-0">
                              <div className="truncate text-xs">{entry.title}</div>
                              <div className="truncate font-mono text-[10px] text-muted-foreground">
                                {entry.url}
                              </div>
                            </div>
                            <button
                              onClick={() => addReference(entry.url, "global")}
                              className="shrink-0 rounded border border-border px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                            >
                              Global
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </SectionPanel>
            </div>

            <ResultPanel
              result={result}
              payload={lastPayload}
              onRefreshLibrary={() => {
                void queryClient.invalidateQueries({ queryKey: ["library-state"] });
                setNotice("Library refresh requested.");
              }}
            />
          </div>
        )}
      </div>
    </AppShell>
  );
}

function SectionPanel({
  title,
  eyebrow,
  children,
}: {
  title: string;
  eyebrow: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-border bg-sidebar">
      <div className="border-b border-border px-4 py-3">
        <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
          {eyebrow}
        </div>
        <h2 className="mt-1 text-lg font-semibold">{title}</h2>
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}

function FieldLabel({ children }: { children: ReactNode }) {
  return (
    <label className="mb-1.5 block text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
      {children}
    </label>
  );
}

function TextField({
  label,
  value,
  onChange,
  placeholder,
  testId,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  testId?: string;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        data-testid={testId}
        className="w-full rounded border border-border bg-background px-3 py-2 text-sm outline-none focus:border-brand"
      />
    </div>
  );
}

function TextAreaField({
  label,
  value,
  onChange,
  placeholder,
  minRows,
  testId,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minRows: number;
  testId?: string;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        rows={minRows}
        data-testid={testId}
        className="w-full resize-y rounded border border-border bg-background px-3 py-2 text-sm outline-none focus:border-brand"
      />
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  testId,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  testId?: string;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        data-testid={testId}
        className="w-full rounded border border-border bg-background px-3 py-2 text-sm outline-none focus:border-brand"
      >
        {options.map((entry) => (
          <option key={entry.value} value={entry.value}>
            {entry.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <input
        type="number"
        min={1}
        max={8}
        value={value}
        onChange={(event) => onChange(Number(event.target.value || 1))}
        className="w-full rounded border border-border bg-background px-3 py-2 text-sm outline-none focus:border-brand"
      />
    </div>
  );
}

function ToggleRow({
  label,
  hint,
  checked,
  onChange,
  tone = "default",
  testId,
}: {
  label: string;
  hint: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  tone?: "default" | "warn";
  testId?: string;
}) {
  return (
    <label
      className={cn(
        "flex cursor-pointer items-start gap-3 rounded border p-3",
        tone === "warn" ? "border-amber-400/30 bg-amber-400/5" : "border-border bg-background",
      )}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        data-testid={testId}
        className="mt-1"
      />
      <span>
        <span className="block text-sm font-medium">{label}</span>
        <span className="mt-1 block text-xs text-muted-foreground">{hint}</span>
      </span>
    </label>
  );
}

function ExecutionBrief({
  dryRun,
  provider,
  model,
  promptCount,
  referenceCount,
  manifestUrl,
  confirmed,
}: {
  dryRun: boolean;
  provider: string;
  model: string;
  promptCount: string;
  referenceCount: number;
  manifestUrl: string;
  confirmed: boolean;
}) {
  const gateText = dryRun
    ? "Dry-run mode"
    : manifestUrl
      ? confirmed
        ? "Ready for provider execution"
        : "Confirmation required"
      : "Matching dry-run required";

  return (
    <div
      data-testid="generate-real-brief"
      className={cn(
        "rounded border p-3",
        dryRun || manifestUrl
          ? "border-border bg-background"
          : "border-amber-400/30 bg-amber-400/5",
      )}
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
          <ShieldCheck className="size-3.5" strokeWidth={1.5} />
          Execution gate
        </div>
        <span
          data-testid="generate-real-gate"
          className={cn(
            "rounded border px-2 py-1 text-[10px] font-mono uppercase tracking-widest",
            dryRun || (manifestUrl && confirmed)
              ? "border-brand/30 bg-brand/10 text-brand"
              : "border-amber-400/30 bg-amber-400/10 text-amber-300",
          )}
        >
          {gateText}
        </span>
      </div>
      <dl className="space-y-2 text-xs">
        <MetaRow label="Provider" value={provider} />
        <MetaRow label="Model" value={model} />
        <MetaRow label="Prompts" value={promptCount} />
        <MetaRow label="Refs" value={String(referenceCount)} />
        <MetaRow label="Manifest" value={manifestUrl || "Run dry-run first"} />
      </dl>
      {manifestUrl && (
        <a
          href={manifestUrl}
          data-testid="generate-dry-run-manifest"
          className="mt-3 inline-flex min-w-0 max-w-full items-center gap-2 rounded border border-border px-2 py-1.5 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
        >
          <ExternalLink className="size-3.5 shrink-0" strokeWidth={1.5} />
          <span className="truncate">Dry-run manifest</span>
        </a>
      )}
    </div>
  );
}

function MiniStat({
  label,
  value,
  compact,
}: {
  label: string;
  value: string | number;
  compact?: boolean;
}) {
  return (
    <div className="min-w-0 bg-sidebar px-4 py-3">
      <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        {label}
      </div>
      <div
        className={cn(
          "mt-1 truncate font-mono text-sm text-foreground",
          compact && "max-w-[180px]",
        )}
      >
        {value}
      </div>
    </div>
  );
}

function RunHistoryPanel({
  items,
  onClear,
}: {
  items: GenerateHistoryItem[];
  onClear: () => void;
}) {
  return (
    <section className="rounded-lg border border-border bg-sidebar" data-testid="generate-history">
      <div className="flex flex-col gap-3 border-b border-border px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
            <Clock3 className="size-3.5" strokeWidth={1.5} />
            Recent attempts
          </div>
          <h2 className="mt-1 text-lg font-semibold">Run history</h2>
        </div>
        {items.length > 0 && (
          <button
            onClick={onClear}
            className="flex items-center gap-2 self-start rounded border border-border px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground sm:self-auto"
          >
            <Trash2 className="size-3.5" strokeWidth={1.5} />
            Clear
          </button>
        )}
      </div>
      {items.length === 0 ? (
        <div className="p-4 text-sm text-muted-foreground">
          Dry-runs and provider runs from this browser will appear here.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 p-4 lg:grid-cols-2 2xl:grid-cols-4">
          {items.map((item) => (
            <article
              key={item.id}
              data-testid="generate-history-item"
              className="min-w-0 rounded border border-border bg-background p-3"
            >
              <div className="mb-3 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="truncate font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    {item.dryRun ? "Dry-run" : "Provider"} · {item.provider}
                  </div>
                  <div className="mt-1 truncate text-sm font-semibold">
                    {item.project} / {runDirectorySegment(item.runId)}
                  </div>
                </div>
                <span
                  className={cn(
                    "shrink-0 rounded border px-1.5 py-0.5 text-[10px] font-mono uppercase tracking-widest",
                    item.status === "ok"
                      ? "border-brand/30 bg-brand/10 text-brand"
                      : "border-amber-400/30 bg-amber-400/10 text-amber-300",
                  )}
                >
                  {item.generated}/{item.total}
                </span>
              </div>
              <dl className="space-y-1.5 text-[11px]">
                <MetaRow label="Model" value={item.model} />
                <MetaRow label="Prompts" value={String(item.promptCount)} />
                <MetaRow label="Refs" value={String(item.referenceCount)} />
                <MetaRow label="When" value={formatHistoryTime(item.createdAt)} />
              </dl>
              <div className="mt-3 flex flex-wrap gap-1.5">
                <HistoryLink href={item.runViewerUrl} label="Run viewer" />
                <HistoryLink href={item.viewerUrl} label="Project viewer" />
                <HistoryLink href={item.libraryRunUrl} label="Library run" />
                <HistoryLink href={item.manifestUrl} label="Manifest" />
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function HistoryLink({ href, label }: { href?: string; label: string }) {
  if (!href) return null;
  return (
    <a
      href={href}
      className="inline-flex items-center gap-1 rounded border border-border px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
    >
      {label}
      <ExternalLink className="size-3" strokeWidth={1.5} />
    </a>
  );
}

function StatusBanner({
  tone,
  message,
  onClear,
}: {
  tone: "info" | "error";
  message: string;
  onClear: () => void;
}) {
  return (
    <div
      className={cn(
        "flex items-start justify-between gap-3 rounded border px-4 py-3 text-sm",
        tone === "error"
          ? "border-destructive/30 bg-destructive/5 text-destructive"
          : "border-brand/30 bg-brand/5 text-foreground",
      )}
    >
      <div className="flex min-w-0 items-start gap-2">
        {tone === "error" ? (
          <AlertTriangle className="mt-0.5 size-4 shrink-0" />
        ) : (
          <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand" />
        )}
        <span className="break-words">{message}</span>
      </div>
      <button
        onClick={onClear}
        className="grid size-6 shrink-0 place-items-center rounded text-muted-foreground hover:text-foreground"
        aria-label="Clear status"
      >
        <X className="size-4" />
      </button>
    </div>
  );
}

function ReferenceImageRow({
  image,
  onUsePrimary,
  onUseGlobal,
}: {
  image: ImageRecord;
  onUsePrimary: () => void;
  onUseGlobal: () => void;
}) {
  return (
    <div className="flex gap-3 rounded border border-border bg-background p-2">
      <img
        src={image.thumbnailUrl}
        alt=""
        className="h-16 w-16 shrink-0 rounded object-cover"
        loading="lazy"
      />
      <div className="min-w-0 flex-1">
        <div className="truncate text-xs font-medium">{image.name || image.file}</div>
        <div className="mt-1 truncate font-mono text-[10px] text-muted-foreground">{image.url}</div>
        <div className="mt-2 flex flex-wrap gap-1">
          <button
            onClick={onUsePrimary}
            data-testid="generate-reference-primary"
            className="rounded border border-border px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
          >
            Primary
          </button>
          <button
            onClick={onUseGlobal}
            data-testid="generate-reference-global"
            className="rounded border border-border px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
          >
            Global
          </button>
        </div>
      </div>
    </div>
  );
}

function SelectedReferences({
  primary,
  global,
  composition,
  onClearPrimary,
  onRemoveGlobal,
  onRemoveComposition,
}: {
  primary: string;
  global: string[];
  composition: string[];
  onClearPrimary: () => void;
  onRemoveGlobal: (source: string) => void;
  onRemoveComposition: (source: string) => void;
}) {
  const empty = !primary && global.length === 0 && composition.length === 0;
  return (
    <div>
      <FieldLabel>Selected references</FieldLabel>
      {empty ? (
        <div className="rounded border border-border bg-background p-4 text-xs text-muted-foreground">
          No references selected.
        </div>
      ) : (
        <div className="space-y-2">
          {primary && <ReferenceChip label="Primary" source={primary} onRemove={onClearPrimary} />}
          {global.map((source) => (
            <ReferenceChip
              key={`global-${source}`}
              label="Global"
              source={source}
              onRemove={() => onRemoveGlobal(source)}
            />
          ))}
          {composition.map((source) => (
            <ReferenceChip
              key={`composition-${source}`}
              label="Composition"
              source={source}
              onRemove={() => onRemoveComposition(source)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ReferenceChip({
  label,
  source,
  onRemove,
}: {
  label: string;
  source: string;
  onRemove: () => void;
}) {
  return (
    <div className="flex items-center gap-2 rounded border border-border bg-background px-3 py-2">
      <span className="shrink-0 rounded bg-brand/10 px-1.5 py-0.5 text-[10px] font-mono uppercase tracking-widest text-brand">
        {label}
      </span>
      <span className="min-w-0 flex-1 truncate font-mono text-[10px] text-muted-foreground">
        {source}
      </span>
      <button
        onClick={onRemove}
        className="grid size-6 place-items-center rounded text-muted-foreground hover:text-foreground"
        aria-label={`Remove ${label} reference`}
      >
        <X className="size-3.5" />
      </button>
    </div>
  );
}

function ResultPanel({
  result,
  payload,
  onRefreshLibrary,
}: {
  result: GenerateResult | null;
  payload: GeneratePayload | null;
  onRefreshLibrary: () => void;
}) {
  if (!result && !payload) return null;
  return (
    <section className="rounded-lg border border-border bg-sidebar" data-testid="generate-result">
      <div className="border-b border-border px-4 py-3">
        <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
          Result
        </div>
        <h2 className="mt-1 text-lg font-semibold">
          {result ? "Generation response" : "Planned run"}
        </h2>
      </div>
      <div className="grid grid-cols-1 gap-5 p-4 lg:grid-cols-[1fr_360px]">
        <div>
          {result ? (
            <>
              <div className="grid grid-cols-2 gap-px overflow-hidden rounded border border-border bg-border sm:grid-cols-4">
                <MiniStat label="Project" value={result.project} />
                <MiniStat label="Run" value={result.run_id} compact />
                <MiniStat label="Generated" value={`${result.generated}/${result.total}`} />
                <MiniStat label="Status" value={result.all_ok ? "ok" : "partial"} />
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {result.run_viewer_url && (
                  <a
                    href={result.run_viewer_url}
                    className="rounded border border-brand px-3 py-1.5 text-xs font-mono uppercase tracking-widest text-brand hover:bg-brand hover:text-black"
                  >
                    Open run
                  </a>
                )}
                {result.viewer_url && (
                  <a
                    href={result.viewer_url}
                    className="rounded border border-border px-3 py-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                  >
                    Open viewer
                  </a>
                )}
                <Link
                  to="/library"
                  className="rounded border border-border px-3 py-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                >
                  Library
                </Link>
                <button
                  onClick={onRefreshLibrary}
                  className="rounded border border-border px-3 py-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
                >
                  Refresh library
                </button>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
                {result.images.map((image, index) => {
                  const url = resultImageUrl(result, image);
                  const showImage = Boolean(url && image.ok && !payload?.dry_run);
                  return (
                    <div
                      key={`${image.name}-${index}`}
                      className="rounded border border-border p-2"
                    >
                      {showImage ? (
                        <img
                          src={url}
                          alt=""
                          className="aspect-square w-full rounded object-cover"
                          loading="lazy"
                        />
                      ) : (
                        <div className="grid aspect-square place-items-center rounded bg-background text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                          {payload?.dry_run && image.ok ? "Dry run" : "Failed"}
                        </div>
                      )}
                      <div className="mt-2 truncate text-xs">{image.name}</div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <div className="rounded border border-border bg-background p-4 text-sm text-muted-foreground">
              Submit a dry-run to validate the payload and create a planned run summary.
            </div>
          )}
        </div>
        {payload && (
          <div className="rounded border border-border bg-background p-4">
            <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              Last payload
            </div>
            <dl className="mt-3 space-y-2 text-xs">
              <MetaRow label="Mode" value={payload.mode} />
              <MetaRow label="Project" value={payload.project} />
              <MetaRow label="Model" value={payload.model} />
              <MetaRow label="Style" value={payload.style || "none"} />
              <MetaRow label="Aspect" value={payload.aspect_ratio} />
              <MetaRow label="Dry run" value={payload.dry_run ? "true" : "false"} />
              <MetaRow
                label="Prompts"
                value={payload.mode === "single" ? "1" : String(payload.prompts?.length || "file")}
              />
              <MetaRow
                label="Refs"
                value={String(
                  (payload.reference_image ? 1 : 0) +
                    (payload.global_reference_images?.length || 0) +
                    (payload.composition_references?.length || 0),
                )}
              />
            </dl>
            {payload.prompts?.length ? (
              <div
                className="mt-4 rounded border border-border bg-sidebar p-3"
                data-testid="generate-row-overrides"
              >
                <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                  Inline row overrides
                </div>
                <dl className="mt-2 space-y-2 text-xs">
                  {payload.prompts.map((prompt, index) => (
                    <MetaRow
                      key={`${prompt.name || "prompt"}-${index}`}
                      label={inlinePromptLabel(prompt, index)}
                      value={inlinePromptOverrideText(prompt)}
                    />
                  ))}
                </dl>
              </div>
            ) : null}
            <pre
              data-testid="generate-last-payload-json"
              className="mt-4 max-h-56 overflow-auto rounded border border-border bg-sidebar p-3 text-[10px] leading-relaxed text-muted-foreground"
            >
              {JSON.stringify(payload, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="font-mono uppercase tracking-widest text-muted-foreground">{label}</dt>
      <dd className="min-w-0 truncate text-right font-mono text-foreground">{value}</dd>
    </div>
  );
}

function modeLabel(mode: Mode) {
  if (mode === "single") return "Single";
  if (mode === "batch-file") return "Prompt file";
  return "Inline batch";
}

function bucketLabel(bucket: ReferenceBucket) {
  if (bucket === "primary") return "Primary";
  if (bucket === "global") return "Global";
  return "Comp";
}

function modelOptionsFor(options: GenerateOptions | undefined) {
  return (options?.models ?? []).map((entry) => ({
    value: entry.id,
    label: entry.aliases.length ? `${entry.id} (${entry.aliases.join(", ")})` : entry.id,
  }));
}

function styleOptionsFor(options: GenerateOptions | undefined) {
  return (options?.styles ?? []).map((entry) => ({
    value: entry.key,
    label: entry.default ? `${entry.name} - default` : entry.name,
  }));
}

function aspectOptionsFor(options: GenerateOptions | undefined) {
  return [
    ...(options?.aspectRatios ?? []).map((ratio) => ({ value: ratio, label: ratio })),
    ...(options?.aspectPresets ?? []).map((preset) => ({
      value: preset.key,
      label: `${preset.key} -> ${preset.value}`,
    })),
  ];
}

function qualityOptionsFor(options: GenerateOptions | undefined) {
  return (options?.qualities ?? []).map((entry) => ({ value: entry, label: entry }));
}

function inheritOptions(label: string, options: Array<{ value: string; label: string }>) {
  return [{ value: "", label }, ...options];
}

function splitReferences(value: string) {
  return value
    .split(/[\n,]/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function uniq(values: string[]) {
  return Array.from(new Set(values));
}

function updatePromptRow(
  setRows: Dispatch<SetStateAction<PromptRow[]>>,
  id: string,
  patch: Partial<PromptRow>,
) {
  setRows((current) => current.map((row) => (row.id === id ? { ...row, ...patch } : row)));
}

function inlinePromptFromRow(row: PromptRow): InlinePrompt {
  const prompt: InlinePrompt = {
    name: row.name.trim(),
    prompt: row.prompt.trim(),
  };
  const model = row.model?.trim();
  const style = row.style?.trim();
  const aspectRatio = row.aspectRatio?.trim();
  const quality = row.quality?.trim();
  if (model) prompt.model = model;
  if (style) prompt.style = style;
  if (aspectRatio) prompt.aspect_ratio = aspectRatio;
  if (quality) prompt.quality = quality;
  return prompt;
}

function inlinePromptLabel(prompt: InlinePrompt, index: number) {
  return prompt.name?.trim() || `Prompt ${index + 1}`;
}

function inlinePromptOverrideText(prompt: InlinePrompt) {
  const overrides = [
    prompt.model ? `model: ${prompt.model}` : "",
    prompt.style ? `style: ${prompt.style}` : "",
    prompt.aspect_ratio ? `aspect: ${prompt.aspect_ratio}` : "",
    prompt.quality ? `quality: ${prompt.quality}` : "",
  ].filter(Boolean);
  return overrides.length ? overrides.join(" / ") : "run defaults";
}

function readGenerateHistory(): GenerateHistoryItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((entry): entry is GenerateHistoryItem => isGenerateHistoryItem(entry))
      .slice(0, HISTORY_LIMIT);
  } catch {
    return [];
  }
}

function writeGenerateHistory(items: GenerateHistoryItem[]) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, HISTORY_LIMIT)));
  } catch {
    // Browser storage can be disabled; generation should still work without history.
  }
}

function isGenerateHistoryItem(entry: unknown): entry is GenerateHistoryItem {
  if (!entry || typeof entry !== "object") return false;
  const item = entry as Partial<GenerateHistoryItem>;
  return Boolean(item.id && item.project && item.runId && item.manifestUrl && item.libraryRunUrl);
}

function historyItemFromResult(
  result: GenerateResult,
  payload: GeneratePayload,
  draftHash: string,
): GenerateHistoryItem {
  const runId = normaliseRunId(result.run_id);
  return {
    id: `${Date.now()}-${result.project}-${runId}`,
    createdAt: new Date().toISOString(),
    project: result.project,
    runId,
    mode: result.mode,
    dryRun: payload.dry_run,
    status: result.all_ok ? "ok" : "partial",
    provider: providerLabelForModel(payload.model),
    model: payload.model,
    promptCount: promptCountFromPayload(payload, result),
    referenceCount: referenceCountFromPayload(payload),
    generated: result.generated,
    total: result.total,
    draftHash,
    viewerUrl: result.viewer_url,
    runViewerUrl: result.run_viewer_url,
    libraryRunUrl: libraryRunUrlFor(result.project, runId),
    manifestUrl: manifestUrlFor(result.project, runId),
  };
}

function promptCountForDraft(
  mode: Mode,
  singlePrompt: string,
  promptRows: PromptRow[],
  promptPreview: PromptPreviewResult | null,
) {
  if (mode === "single") return singlePrompt.trim() ? "1" : "0";
  if (mode === "batch-file") return promptPreview ? String(promptPreview.count) : "file";
  return String(promptRows.filter((row) => row.prompt.trim()).length);
}

function promptCountFromPayload(payload: GeneratePayload, result: GenerateResult) {
  if (payload.mode === "single") return 1;
  if (payload.prompts?.length) return payload.prompts.length;
  return result.total || 0;
}

function referenceCountFromPayload(payload: GeneratePayload) {
  return (
    (payload.reference_image ? 1 : 0) +
    (payload.reference_images?.length || 0) +
    (payload.global_reference_images?.length || 0) +
    (payload.composition_references?.length || 0)
  );
}

function providerLabelForModel(model: string) {
  const text = model.toLowerCase();
  if (text.includes("gemini")) return "Google Gemini";
  if (text.includes("gpt") || text.includes("dall")) return "OpenAI";
  return "Configured provider";
}

function draftHashForState(state: {
  project: string;
  mode: Mode;
  model: string;
  style: string;
  aspectRatio: string;
  quality: string;
  resolution: string;
  singleName: string;
  singlePrompt: string;
  promptRows: PromptRow[];
  promptFile: string;
  primaryReference: string;
  globalReferences: string[];
  compositionReferences: string[];
  perPromptReferences: string;
  referenceRole: string;
}) {
  return hashString(
    JSON.stringify({
      ...state,
      project: state.project.trim(),
      style: state.style || "none",
      singleName: state.singleName.trim(),
      singlePrompt: state.singlePrompt.trim(),
      promptRows: state.promptRows.map((row) => ({
        name: row.name.trim(),
        prompt: row.prompt.trim(),
        model: row.model?.trim() || "",
        style: row.style?.trim() || "",
        aspectRatio: row.aspectRatio?.trim() || "",
        quality: row.quality?.trim() || "",
      })),
      promptFile: state.promptFile.trim(),
      primaryReference: state.primaryReference.trim(),
      globalReferences: state.globalReferences.slice().sort(),
      compositionReferences: state.compositionReferences.slice().sort(),
      perPromptReferences: splitReferences(state.perPromptReferences),
    }),
  );
}

function hashString(value: string) {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(index);
    hash |= 0;
  }
  return Math.abs(hash).toString(36);
}

function normaliseRunId(runId: string) {
  return runId.startsWith("run-") ? runId.slice(4) : runId;
}

function runDirectorySegment(runId: string) {
  return runId.startsWith("run-") ? runId : `run-${runId}`;
}

function manifestUrlFor(project: string, runId: string) {
  return `/output/${encodeURIComponent(project)}/${encodeURIComponent(runDirectorySegment(runId))}/run.json`;
}

function libraryRunUrlFor(project: string, runId: string) {
  return `/library/${encodeURIComponent(`${project}/${runDirectorySegment(runId)}`)}`;
}

function formatHistoryTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "unknown";
  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
