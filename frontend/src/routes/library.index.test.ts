import { describe, expect, it } from "vitest";
import { searchSchema } from "./library.index";

describe("library searchSchema", () => {
  it("applies defaults when params are absent", () => {
    expect(searchSchema.parse({})).toEqual({
      q: "",
      status: "all",
      tags: [],
      sort: "recent",
      dir: "desc",
      view: "grid",
    });
  });

  it("keeps valid values", () => {
    expect(
      searchSchema.parse({
        q: "poster",
        status: "starred",
        tags: ["kk", "bcai"],
        sort: "name",
        dir: "asc",
        view: "list",
      }),
    ).toEqual({
      q: "poster",
      status: "starred",
      tags: ["kk", "bcai"],
      sort: "name",
      dir: "asc",
      view: "list",
    });
  });

  it("falls back to defaults for invalid values instead of throwing", () => {
    expect(
      searchSchema.parse({
        q: 123,
        status: "bogus",
        tags: "not-an-array",
        sort: "nope",
        dir: "sideways",
        view: "hologram",
      }),
    ).toEqual({
      q: "",
      status: "all",
      tags: [],
      sort: "recent",
      dir: "desc",
      view: "grid",
    });
  });
});
