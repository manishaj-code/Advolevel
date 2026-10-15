import { describe, expect, it } from "vitest";

import { REDACTED, scrub, scrubString } from "./scrub";

describe("scrub (SD-01, frontend)", () => {
  it.each(["Authorization", "cookie", "access_token", "client_secret", "password", "api_key"])(
    "redacts the sensitive key %s",
    (key) => {
      expect(scrub({ [key]: "value" })).toEqual({ [key]: REDACTED });
    },
  );

  it.each(["content", "prompt", "completion", "text"])("redacts the deny-listed key %s", (key) => {
    expect(scrub({ [key]: "board minutes" })).toEqual({ [key]: REDACTED });
  });

  it("masks emails, cards and bearer tokens inside strings", () => {
    const out = scrubString("jane@example.com paid 4111 1111 1111 1111 with Bearer abc.def");
    expect(out).not.toContain("jane@example.com");
    expect(out).not.toContain("4111 1111 1111 1111");
    expect(out).not.toContain("abc.def");
  });

  it("walks nested objects and arrays, leaving safe values alone", () => {
    expect(scrub({ user: { email: "a@b.co", id: 7 }, items: [{ token: "x" }, "ok"] })).toEqual({
      user: { email: REDACTED, id: 7 },
      items: [{ token: REDACTED }, "ok"],
    });
  });
});
