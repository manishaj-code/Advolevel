"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ErrorPanel, Skeleton } from "@/components/ui/states";
import { lastOrg, pendingInviteToken } from "@/lib/active-org";
import { useMe } from "@/lib/api/hooks";

/** Pending invite → /invite; no organization yet → onboarding (WF-02); else the last-used org. */
export function HomeRedirect() {
  const router = useRouter();
  const me = useMe();

  useEffect(() => {
    if (pendingInviteToken()) {
      router.replace("/invite");
      return;
    }
    if (!me.data) return;
    const orgIds = me.data.memberships.map((m) => m.organization.id);
    if (orgIds.length === 0) {
      router.replace("/onboarding");
      return;
    }
    const remembered = lastOrg();
    router.replace(`/o/${remembered && orgIds.includes(remembered) ? remembered : orgIds[0]}`);
  }, [me.data, router]);

  if (me.error) return <ErrorPanel error={me.error} onRetry={() => me.refetch()} />;
  return <Skeleton label="Opening your workspace" />;
}
