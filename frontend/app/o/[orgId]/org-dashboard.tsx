"use client";

import Link from "next/link";
import { useEffect } from "react";

import { ErrorPanel, Skeleton } from "@/components/ui/states";
import { rememberOrg } from "@/lib/active-org";
import { ROLE_LABELS } from "@/lib/permissions";
import { useOrgContext } from "@/lib/org-context";

import { NotAMember } from "./not-a-member";

export function OrgDashboard() {
  const { orgId, me, membership } = useOrgContext();

  useEffect(() => {
    if (membership) rememberOrg(orgId);
  }, [membership, orgId]);

  if (me.error) return <ErrorPanel error={me.error} onRetry={() => me.refetch()} />;
  if (!me.data) return <Skeleton />;
  if (!membership) return <NotAMember />;

  return (
    <div className="flex flex-col gap-2">
      <h1 className="font-display text-[32px] leading-10 font-semibold">
        {membership.organization.name}
      </h1>
      <p className="text-text-secondary">
        Signed in as {me.data.user.name ?? me.data.user.email} · {ROLE_LABELS[membership.role]}
      </p>
      <p className="mt-6 text-text-secondary">
        The dashboard arrives with the application shell (M3). Meanwhile you can manage your{" "}
        <Link className="text-navy-700 underline" href={`/o/${orgId}/settings/team`}>
          team and roles
        </Link>
        .
      </p>
    </div>
  );
}
