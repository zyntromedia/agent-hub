
import { describe, expect, it } from "vitest";
import {
  HttpError,
  errorResponse,
} from "../lib/api/http-error";

describe("API error handling", () => {
  it("returns the expected status for HTTP errors", async () => {
    const response = errorResponse(
      new HttpError(
        429,
        "RATE_LIMIT_EXCEEDED",
        "Try again later",
      ),
    );

    expect(response.status).toBe(429);
    await expect(response.json()).resolves.toEqual({
      error: "RATE_LIMIT_EXCEEDED",
      message: "Try again later",
    });
  });

  it("does not expose internal exception details", async () => {
    const response = errorResponse(
      new Error("database password leaked"),
    );

    expect(response.status).toBe(500);
    const body = await response.json();

    expect(body.error).toBe("INTERNAL_SERVER_ERROR");
    expect(body.message).not.toContain("password");
    expect(body.message).not.toContain("database");
  });

  it("preserves a 401 response", async () => {
    const response = errorResponse(
      new HttpError(
        401,
        "UNAUTHORIZED",
        "Authentication required",
      ),
    );

    expect(response.status).toBe(401);
  });
});
