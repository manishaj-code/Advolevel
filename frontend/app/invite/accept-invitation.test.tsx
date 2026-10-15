import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { AcceptInvitation } from "./accept-invitation";

const auth = vi.hoisted(() => ({ isLoaded: true, isSignedIn: false }));
const replace = vi.hoisted(() => vi.fn());

vi.mock("@clerk/nextjs", () => ({
  useAuth: () => ({ ...auth, getToken: async () => (auth.isSignedIn ? "tok" : null) }),
  SignInButton: ({ children }: { children: ReactNode }) => children,
  SignUpButton: ({ children }: { children: ReactNode }) => children,
  SignOutButton: ({ children }: { children: ReactNode }) => children,
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace, push: vi.fn() }) }));

const PREVIEW = {
  organization_name: "Acme Legal",
  inviter_name: "Olive Owner",
  role: "admin",
  email_hint: "b***@example.com",
  expires_at: "2026-10-22T00:00:00Z",
};

function respond(routes: Record<string, { status: number; body: unknown }>) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (request: Request) => {
      const path = new URL(request.url).pathname;
      const { status, body } = routes[path] ?? { status: 404, body: { status: 404, code: "x" } };
      return new Response(JSON.stringify(body), {
        status,
        headers: { "content-type": "application/json" },
      });
    }),
  );
}

function renderInvite() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <AcceptInvitation />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  sessionStorage.clear();
  auth.isSignedIn = false;
  window.history.replaceState(null, "", "/invite#token=tok_aaaaaaaaaaaaaaaaaaaaaaaa");
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test("shows the invitation, keeps the token and removes it from the URL", async () => {
  respond({ "/api/v1/invitations/preview": { status: 200, body: PREVIEW } });
  renderInvite();

  expect(await screen.findByRole("heading", { name: "Join Acme Legal" })).toBeDefined();
  expect(screen.getByText("b***@example.com")).toBeDefined();
  expect(screen.getByRole("button", { name: "Sign in to accept" })).toBeDefined();
  expect(window.location.hash).toBe("");
  expect(sessionStorage.getItem("advolevel:pending-invite")).toBe("tok_aaaaaaaaaaaaaaaaaaaaaaaa");
});

test("expired invitations explain what to do next", async () => {
  respond({
    "/api/v1/invitations/preview": {
      status: 410,
      body: { status: 410, code: "invitation_expired", detail: "This invitation has expired." },
    },
  });
  renderInvite();

  expect(
    await screen.findByRole("heading", { name: "This invitation has expired." }),
  ).toBeDefined();
  expect(screen.getByText(/send a new invitation/)).toBeDefined();
});

test("a missing token is treated as an invalid link", async () => {
  window.history.replaceState(null, "", "/invite");
  renderInvite();
  expect(
    await screen.findByRole("heading", { name: "This invitation link is not valid." }),
  ).toBeDefined();
});

test("signed in with the wrong account offers to switch", async () => {
  auth.isSignedIn = true;
  respond({
    "/api/v1/invitations/preview": { status: 200, body: PREVIEW },
    "/api/v1/invitations/accept": {
      status: 403,
      body: {
        status: 403,
        code: "invitation_email_mismatch",
        detail: "This invitation is for b***@example.com. Sign in with that address to accept it.",
      },
    },
  });
  renderInvite();

  fireEvent.click(await screen.findByRole("button", { name: "Accept invitation" }));

  expect(await screen.findByRole("button", { name: "Switch account" })).toBeDefined();
  expect(replace).not.toHaveBeenCalled();
});
