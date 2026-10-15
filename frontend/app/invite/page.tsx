import type { Metadata } from "next";

import { AcceptInvitation } from "./accept-invitation";

export const metadata: Metadata = { title: "Accept invitation" };

// S-05 / WF-03. Public: the preview works before sign-in; accepting requires the invited account.
export default function InvitePage() {
  return (
    <main className="mx-auto flex max-w-md flex-col gap-6 px-4 py-16">
      <p className="font-display text-2xl font-semibold">AdvoLevel</p>
      <AcceptInvitation />
    </main>
  );
}
