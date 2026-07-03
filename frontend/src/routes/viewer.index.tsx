import { createFileRoute, Link } from "@tanstack/react-router";
import { Eye } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { EmptyBlock } from "@/components/state/empty-block";
import { ErrorBlock } from "@/components/state/error-block";
import { useLibraryState } from "@/lib/rafiki-data";

export const Route = createFileRoute("/viewer/")({
  head: () => ({
    meta: [
      { title: "Viewer — Rafiki" },
      {
        name: "description",
        content: "Keyboard-driven triage viewer.",
      },
    ],
  }),
  errorComponent: ({ error, reset }) => (
    <AppShell>
      <ErrorBlock error={error} reset={reset} />
    </AppShell>
  ),
  component: ViewerIndex,
});

function ViewerIndex() {
  const { data, error, isLoading, refetch } = useLibraryState();

  if (error) {
    return (
      <AppShell>
        <ErrorBlock error={error} reset={() => void refetch()} />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="p-16">
        <EmptyBlock
          icon={Eye}
          title={isLoading ? "Loading viewer" : "Choose an image to view"}
          hint={
            isLoading
              ? "Reading the local archive."
              : `${data?.images.filter((image) => image.status === "present").length ?? 0} present images are available from the library.`
          }
          action={
            <Link
              to="/library"
              className="inline-block px-4 py-1.5 border border-brand text-brand text-xs font-mono uppercase tracking-widest rounded hover:bg-brand hover:text-black transition-colors"
            >
              Browse Library
            </Link>
          }
        />
      </div>
    </AppShell>
  );
}
