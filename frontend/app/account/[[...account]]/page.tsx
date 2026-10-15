import { UserProfile } from "@clerk/nextjs";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { Skeleton } from "@/components/ui/states";

export const metadata: Metadata = { title: "Profile & security" };

// S-53: name, avatar, email addresses, password, MFA and active sessions are managed by Clerk.
// Notification preferences arrive with notifications (M3); personal API tokens are out of V1.
export default function AccountPage() {
  return (
    <main className="mx-auto flex max-w-content flex-col gap-6 px-4 py-8">
      <Link href="/home" className="text-sm text-navy-700 underline">
        Back to AdvoLevel
      </Link>
      <Suspense fallback={<Skeleton lines={6} label="Loading profile" />}>
        <UserProfile />
      </Suspense>
    </main>
  );
}
