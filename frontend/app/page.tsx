import { AppShell } from "@/components/features/app-shell";

// M0 placeholder. Real routes arrive with M1 (public/auth) and M3 (app shell, S-09).
export default function Home() {
  return (
    <AppShell>
      <h1 className="font-display text-[32px] leading-10 font-semibold">Good morning</h1>
      <p className="mt-2 text-text-secondary">
        The AdvoLevel workspace is being built. This is the M0 skeleton.
      </p>
    </AppShell>
  );
}
