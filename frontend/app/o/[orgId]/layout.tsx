import type { ReactNode } from "react";

import { AppShell } from "@/components/features/app-shell";

export default function OrgLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
