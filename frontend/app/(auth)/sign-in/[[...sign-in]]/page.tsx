import { SignIn } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Suspense } from "react";

import { Skeleton } from "@/components/ui/states";

export const metadata: Metadata = { title: "Sign in" };

// S-01. Clerk handles credentials, MFA, SSO and password reset (S-04 merged here); its errors
// are generic, so they do not reveal whether an account exists.
export default function SignInPage() {
  return (
    <Suspense fallback={<Skeleton lines={4} label="Loading sign-in" />}>
      <SignIn />
    </Suspense>
  );
}
