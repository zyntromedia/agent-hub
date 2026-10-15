
import { HttpError } from "@/lib/api/http-error";
import { withErrorHandling } from "@/lib/api/handler";

export const POST = withErrorHandling(async (request) => {
  const contentType = request.headers.get("content-type");

  if (!contentType?.includes("application/json")) {
    throw new HttpError(
      400,
      "BAD_REQUEST",
      "Content-Type must be application/json",
    );
  }

  const body: unknown = await request.json();

  return Response.json({
    status: "accepted",
    received: body !== null,
  });
});
