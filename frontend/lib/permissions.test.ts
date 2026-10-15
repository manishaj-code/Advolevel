import { expect, test } from "vitest";

import { ROLE_PERMISSIONS, can, type Permission } from "./permissions";

// Same table as backend/tests/test_identity_units.py::SPEC_02 (spec 02 §2).
const SPEC_02: Record<Permission, string[]> = {
  "org:read": ["owner", "admin", "member", "viewer"],
  "org:update": ["owner", "admin"],
  "org:delete": ["owner"],
  "org:transfer_ownership": ["owner"],
  "members:read": ["owner", "admin", "member", "viewer"],
  "members:invite": ["owner", "admin"],
  "members:update": ["owner", "admin"],
  "members:remove": ["owner", "admin"],
};

test("UI permission mirror matches spec 02", () => {
  for (const [permission, roles] of Object.entries(SPEC_02) as [Permission, string[]][]) {
    const granted = Object.entries(ROLE_PERMISSIONS)
      .filter(([, permissions]) => permissions.has(permission))
      .map(([role]) => role);
    expect(granted.sort(), permission).toEqual([...roles].sort());
  }
  expect(can(undefined, "org:read")).toBe(false);
});
