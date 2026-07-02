import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
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
  const navigate = useNavigate();
  const { data, error, isLoading, refetch } = useLibraryState();

  useEffect(() => {
    const first = data?.images.find((image) => image.status === "present");
    if (first) {
      void navigate({
        to: "/viewer/$imageId",
        params: { imageId: first.id },
        replace: true,
      });
    }
  }, [data, navigate]);

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
          title={isLoading ? "Loading viewer" : "No images available to view"}
          hint={
            isLoading ? "Reading the local archive." : "Generate a run or check archive health."
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
