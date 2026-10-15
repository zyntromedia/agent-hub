
import { HttpError } from "@/lib/api/http-error";

export function requireApiKey(
  request: Request,
): void {
  const expectedKey = process.env.INTERNAL_API_KEY;
  const providedKey = request.headers.get("x-api-key");

  if (!expectedKey || !providedKey) {
    throw new HttpError(
      401,
      "UNAUTHORIZED",
      "Valid API credentials are required",
    );
  }

  // Replace this comparison with a constant-time
  // comparison for production deployments.
  if (providedKey !== expectedKey) {
    throw new HttpError(
      401,
      "UNAUTHORIZED",
      "Valid API credentials are required",
    );
  }
}
