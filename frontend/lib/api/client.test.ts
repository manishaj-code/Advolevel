import { afterEach, expect, test, vi } from "vitest";

import { ApiError, createApiClient, unwrap } from "./client";

afterEach(() => vi.unstubAllGlobals());

function stubFetch(status: number, body: unknown) {
  const fetchMock = vi.fn<(request: Request) => Promise<Response>>(
    async () =>
      new Response(JSON.stringify(body), {
        status,
        headers: {
          "content-type": status >= 400 ? "application/problem+json" : "application/json",
        },
      }),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

test("attaches the session token and returns data", async () => {
  const fetchMock = stubFetch(200, { user: { id: "u1" }, memberships: [] });
  const api = createApiClient({ getToken: async () => "tok_123", baseUrl: "http://api.test" });

  const me = await unwrap(api.GET("/api/v1/me"));

  expect(me.user.id).toBe("u1");
  const request = fetchMock.mock.calls[0][0];
  expect(request.headers.get("Authorization")).toBe("Bearer tok_123");
});

test("problem responses become ApiError with the request id", async () => {
  stubFetch(409, {
    status: 409,
    code: "invitation_pending",
    detail: "An invitation is already pending; resend it.",
    request_id: "req-abc",
  });
  const api = createApiClient({ baseUrl: "http://api.test" });

  const error = await unwrap(api.GET("/api/v1/me")).catch((e: unknown) => e);

  expect(error).toBeInstanceOf(ApiError);
  expect(error).toMatchObject({
    status: 409,
    code: "invitation_pending",
    requestId: "req-abc",
    message: "An invitation is already pending; resend it.",
  });
});
