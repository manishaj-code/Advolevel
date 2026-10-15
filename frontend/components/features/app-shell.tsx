import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { Suspense, type ReactNode } from "react";

import { OrgNav, OrgSwitcher } from "./org-nav";

// Spec 05 §4: dark navy sidebar, light content area. Full shell (S-09, S-10, S-11) is M3.
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="on-dark flex shrink-0 flex-col gap-6 bg-navy-950 px-4 py-4 text-stone-50 md:min-h-screen md:w-sidebar md:py-6">
        <div className="flex items-center justify-between">
          <Link href="/home" className="font-display text-xl font-semibold text-gold-300">
            AdvoLevel
          </Link>
          <div className="md:hidden">
            <UserButton />
          </div>
        </div>
        <Suspense fallback={<div className="h-9 rounded-control bg-navy-800" />}>
          <OrgSwitcher />
        </Suspense>
        <nav aria-label="Primary" className="flex flex-col gap-1">
          <Suspense fallback={null}>
            <OrgNav />
          </Suspense>
        </nav>
        <div className="mt-auto hidden items-center gap-3 md:flex">
          <UserButton />
          <Link href="/account" className="text-sm text-stone-200 hover:text-stone-0">
            Profile &amp; security
          </Link>
        </div>
      </aside>
      <main className="flex-1 px-4 py-8 md:px-8">
        <div className="mx-auto max-w-content">{children}</div>
      </main>
    </div>
  );
}
