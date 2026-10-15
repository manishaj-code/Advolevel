// Mirror of backend/app/identity/permissions.py (spec 02 §2), used only to hide or disable UI.
// The API enforces every rule; keep the two in sync (permissions.test.ts pins this table).
import type { Role } from "@/lib/api/hooks";

export type Permission =
  | "org:read"
  | "org:update"
  | "org:delete"
  | "org:transfer_ownership"
  | "members:read"
  | "members:invite"
  | "members:update"
  | "members:remove";

const ADMIN: Permission[] = [
  "org:read",
  "org:update",
  "members:read",
  "members:invite",
  "members:update",
  "members:remove",
];

export const ROLE_PERMISSIONS: Record<Role, ReadonlySet<Permission>> = {
  owner: new Set([...ADMIN, "org:delete", "org:transfer_ownership"]),
  admin: new Set(ADMIN),
  member: new Set(["org:read", "members:read"]),
  viewer: new Set(["org:read", "members:read"]),
};

export function can(role: Role | undefined, permission: Permission): boolean {
  return role !== undefined && ROLE_PERMISSIONS[role].has(permission);
}

export const ROLE_LABELS: Record<Role, string> = {
  owner: "Owner",
  admin: "Admin",
  member: "Member",
  viewer: "Viewer",
};

export const ROLE_DESCRIPTIONS: Record<Role, string> = {
  owner: "Full control, including billing and deleting the organization. Exactly one per org.",
  admin: "Manages members, executives, integrations and governance.",
  member: "Works with executives, boardrooms, work items and content.",
  viewer: "Read-only access to shared work items and decisions.",
};

export const CAPABILITIES = [
  {
    id: "approver",
    label: "Approver",
    description: "Can decide approval requests.",
  },
  {
    id: "executive_configurator",
    label: "Executive configurator",
    description: "Can edit executive persona, knowledge scope and tools.",
  },
  {
    id: "knowledge_manager",
    label: "Knowledge manager",
    description: "Can upload and delete documents and edit Org DNA.",
  },
  {
    id: "content_publisher",
    label: "Content publisher",
    description: "Can approve Content Factory items for publishing.",
  },
] as const;

export type CapabilityId = (typeof CAPABILITIES)[number]["id"];
