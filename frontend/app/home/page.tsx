import type { Metadata } from "next";

import { HomeRedirect } from "./home-redirect";

export const metadata: Metadata = { title: "Loading" };

// Landing route after sign-in/sign-up (NEXT_PUBLIC_CLERK_*_FALLBACK_REDIRECT_URL).
export default function HomePage() {
  return (
    <main className="mx-auto max-w-md px-4 py-16">
      <HomeRedirect />
    </main>
  );
}
