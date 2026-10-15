import type { Metadata } from "next";

import { OrganizationForm } from "./organization-form";

export const metadata: Metadata = { title: "Set up your organization" };

// S-06, WF-02 step 1. Plan choice (S-07, M11) and "Build your executive team" (S-15, M5)
// join this flow in later milestones.
export default function OnboardingPage() {
  return (
    <main className="mx-auto flex max-w-lg flex-col gap-6 px-4 py-12">
      <div>
        <p className="text-caption tracking-wide text-text-secondary uppercase">Step 1</p>
        <h1 className="font-display text-[28px] leading-9 font-semibold">
          Tell us about your organization
        </h1>
        <p className="mt-1 text-text-secondary">
          Your executives use this profile as context. You can change it later.
        </p>
      </div>
      <OrganizationForm />
    </main>
  );
}
