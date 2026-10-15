import { Suspense } from "react";

import { Skeleton } from "@/components/ui/states";

import { OrgDashboard } from "./org-dashboard";

// Placeholder for S-09 (M3).
export default function OrgHomePage() {
  return (
    <Suspense fallback={<Skeleton />}>
      <OrgDashboard />
    </Suspense>
  );
}
