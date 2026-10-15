import { notFound } from "next/navigation";

import { ThrowButton } from "./throw-button";

// MON-01 (frontend half): throws a test error so Sentry wiring can be checked.
// Only served when NEXT_PUBLIC_DEBUG_ENDPOINTS=true; never set it in production.
export default function SentryDebugPage() {
  if (process.env.NEXT_PUBLIC_DEBUG_ENDPOINTS !== "true") notFound();
  return (
    <main className="p-8">
      <h1 className="text-xl font-semibold">Sentry test</h1>
      <ThrowButton />
    </main>
  );
}
