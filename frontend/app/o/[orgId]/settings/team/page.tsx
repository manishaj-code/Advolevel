import type { Metadata } from "next";
import { Suspense } from "react";

import { Skeleton } from "@/components/ui/states";

import { TeamSettings } from "./team-settings";

export const metadata: Metadata = { title: "Team & roles" };

// S-49 Team, Roles & Permissions (S-50 merged as a tab). WF-03 starts here.
export default function TeamPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-[28px] leading-9 font-semibold">Team &amp; roles</h1>
      <Suspense fallback={<Skeleton lines={5} />}>
        <TeamSettings />
      </Suspense>
    </div>
  );
}
