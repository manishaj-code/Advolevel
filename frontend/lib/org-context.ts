"use client";

import { useParams } from "next/navigation";

import { useMe } from "@/lib/api/hooks";

/** The active org from the URL plus the caller's membership in it (from /me). */
export function useOrgContext() {
  const params = useParams<{ orgId: string }>();
  const orgId = params.orgId;
  const me = useMe();
  const membership = me.data?.memberships.find((m) => m.organization.id === orgId);
  return { orgId, me, membership, role: membership?.role };
}
