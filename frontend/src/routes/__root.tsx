import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
          Error 404
        </div>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">
          Route not found
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          That path isn't wired up in this local node.
        </p>
        <div className="mt-6">
          <Link
            to="/library"
            className="inline-flex items-center justify-center rounded border border-brand text-brand px-4 py-2 text-xs font-mono font-bold tracking-widest uppercase hover:bg-brand hover:text-black transition-colors"
          >
            Back to Library
          </Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <div className="text-[10px] font-mono uppercase tracking-widest text-destructive">
          Runtime fault
        </div>
        <h1 className="mt-3 text-xl font-semibold tracking-tight text-foreground">
          Something failed to render
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {error.message || "Try re-running the route."}
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <button
            onClick={() => {
              router.invalidate();
              reset();
            }}
            className="inline-flex items-center justify-center rounded border border-brand text-brand px-4 py-2 text-xs font-mono font-bold tracking-widest uppercase hover:bg-brand hover:text-black transition-colors"
          >
            Retry
          </button>
          <a
            href="/library"
            className="inline-flex items-center justify-center rounded border border-border px-4 py-2 text-xs font-mono font-bold tracking-widest uppercase text-muted-foreground hover:text-foreground"
          >
            Library
          </a>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Rafiki: Local Creative Ops" },
      {
        name: "description",
        content:
          "Local-first creative operations for AI image generation: browse runs, triage keepers, and stage deliveries.",
      },
      { property: "og:title", content: "Rafiki: Local Creative Ops" },
      {
        property: "og:description",
        content:
          "Local-first creative operations for AI image generation: browse runs, triage keepers, and stage deliveries.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "Rafiki: Local Creative Ops" },
      {
        name: "description",
        content: "Redesigns and modernizes existing tools with a TypeScript-based framework.",
      },
      {
        property: "og:description",
        content: "Redesigns and modernizes existing tools with a TypeScript-based framework.",
      },
      {
        name: "twitter:description",
        content: "Redesigns and modernizes existing tools with a TypeScript-based framework.",
      },
      {
        property: "og:image",
        content:
          "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/ec055115-5065-4190-aa63-baac9679debe/id-preview-57a7459a--d9344d79-8ee9-4ab7-b6ca-2967dc476665.lovable.app-1782936845538.png",
      },
      {
        name: "twitter:image",
        content:
          "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/ec055115-5065-4190-aa63-baac9679debe/id-preview-57a7459a--d9344d79-8ee9-4ab7-b6ca-2967dc476665.lovable.app-1782936845538.png",
      },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      {
        rel: "preconnect",
        href: "https://fonts.gstatic.com",
        crossOrigin: "anonymous",
      },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap",
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  );
}
