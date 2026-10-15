import type { ReactNode } from "react";

// Placeholder shell (spec 05 §4): dark navy sidebar, light content area. Replaced in M3.
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <nav
        aria-label="Primary"
        className="on-dark hidden w-sidebar shrink-0 flex-col bg-navy-950 px-4 py-6 text-stone-50 md:flex"
      >
        <span className="font-display text-xl font-semibold text-gold-300">AdvoLevel</span>
      </nav>
      <main className="flex-1 px-4 py-8 md:px-8">
        <div className="mx-auto max-w-content">{children}</div>
      </main>
    </div>
  );
}
