import Link from "next/link";
import type { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 px-4 py-10">
      <Link href="/" className="font-display text-2xl font-semibold text-navy-900">
        AdvoLevel
      </Link>
      {children}
    </main>
  );
}
