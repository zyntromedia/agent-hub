
import { errorResponse } from "./http-error";

type ApiHandler = (request: Request) => Promise<Response>;

export function withErrorHandling(
  handler: ApiHandler,
): ApiHandler {
  return async (request: Request): Promise<Response> => {
    try {
      return await handler(request);
    } catch (error: unknown) {
      return errorResponse(error);
    }
  };
}
