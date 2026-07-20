import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { GenerateStatusBanner } from "./generate-status";

it("renders successful and failed generation states and clears on request", () => {
  const onClear = vi.fn();
  const { rerender } = render(
    <GenerateStatusBanner
      status={{ kind: "notice", title: "Run complete", message: "Archive refreshed." }}
      onClear={onClear}
    />,
  );

  expect(screen.getByTestId("generate-status")).toHaveAttribute("data-generate-status", "notice");
  expect(screen.getByText("Run complete")).toBeInTheDocument();

  rerender(
    <GenerateStatusBanner
      status={{
        kind: "generation-error",
        title: "Generation/backend failure",
        message: "Request rejected.",
      }}
      onClear={onClear}
    />,
  );

  expect(screen.getByTestId("generate-status")).toHaveAttribute(
    "data-generate-status",
    "generation-error",
  );
  expect(screen.getByText("Request rejected.")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Clear status" }));
  expect(onClear).toHaveBeenCalledOnce();
});
