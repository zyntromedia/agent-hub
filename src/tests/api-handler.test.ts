
import { describe, expect, it, vi } from "vitest";
import { withErrorHandling } from "../lib/api/handler";
import { HttpError } from "../lib/api/http-error";

describe("withErrorHandling", () => {
  it("returns a successful handler response", async () => {
    const handler = withErrorHandling(async () =>
      Response.json({ status: "ok" }),
    );

    const response = await handler(
      new Request("http://localhost/api/prompt"),
    );

    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toEqual({
      status: "ok",
    });
  });

  it("converts thrown errors to HTTP responses", async () => {
    const handler = withErrorHandling(async () => {
      throw new HttpError(
        403,
        "FORBIDDEN",
        "Access denied",
      );
    });

    const response = await handler(
      new Request("http://localhost/api/prompt"),
    );

    expect(response.status).toBe(403);
  });

  it("handles rejected promises", async () => {
    const handler = withErrorHandling(
      vi.fn().mockRejectedValue(
        new Error("unexpected failure"),
      ),
    );

    const response = await handler(
      new Request("http://localhost/api/prompt"),
    );

    expect(response.status).toBe(500);
  });
});
