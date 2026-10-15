import createClient, { type Middleware } from "openapi-fetch";

import type { components, paths } from "./schema";

export type Schemas = components["schemas"];

/** RFC 9457 problem body returned by every API error (spec 08 §1). */
export type Problem = {
  type?: string;
  title?: string;
  status: number;
  code: string;
  detail?: string;
  request_id?: string;
  errors?: { field: string; message: string }[];
};

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId?: string;
  readonly fieldErrors: { field: string; message: string }[];

  constructor(problem: Problem) {
    super(problem.detail ?? problem.title ?? problem.code);
    this.name = "ApiError";
    this.status = problem.status;
    this.code = problem.code;
    this.requestId = problem.request_id;
    this.fieldErrors = problem.errors ?? [];
  }
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export type TokenGetter = () => Promise<string | null>;

export function createApiClient({
  getToken,
  baseUrl = API_BASE_URL,
}: {
  getToken?: TokenGetter;
  baseUrl?: string;
}) {
  const client = createClient<paths>({ baseUrl });
  const auth: Middleware = {
    async onRequest({ request }) {
      const token = getToken ? await getToken() : null;
      if (token) request.headers.set("Authorization", `Bearer ${token}`);
      return request;
    },
  };
  client.use(auth);
  return client;
}

export type ApiClient = ReturnType<typeof createApiClient>;

function toProblem(error: unknown, response: Response): Problem {
  if (error && typeof error === "object" && "code" in error) return error as Problem;
  return { status: response.status, code: response.status >= 500 ? "internal_error" : "error" };
}

/** Turns an openapi-fetch result into data or a thrown ApiError. */
export async function unwrap<T>(
  call: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await call;
  if (!response.ok) throw new ApiError(toProblem(error, response));
  return data as T;
}
