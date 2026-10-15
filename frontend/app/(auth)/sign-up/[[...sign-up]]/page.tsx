import { SignUp } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Suspense } from "react";

import { Skeleton } from "@/components/ui/states";

export const metadata: Metadata = { title: "Create your account" };

// S-02 (email verification, S-03, is a state of this flow). The password policy and
// verification requirement are configured in the Clerk dashboard (see README).
export default function SignUpPage() {
  return (
    <Suspense fallback={<Skeleton lines={4} label="Loading sign-up" />}>
      <SignUp />
    </Suspense>
  );
}
