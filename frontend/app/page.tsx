import Link from "next/link";

// Minimal public entry until the public website (S-W1…S-W5) lands in M3.
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-navy-950 px-4 text-center text-stone-50">
      <p className="font-display text-xl font-semibold text-gold-300">AdvoLevel</p>
      <h1 className="font-display text-[40px] leading-[48px] font-semibold">
        Your AI executive team
      </h1>
      <p className="max-w-xl text-stone-200">
        Executives that know your organization, work together in boardrooms, and act only within the
        rules you set.
      </p>
      <div className="on-dark flex gap-3">
        <Link
          href="/sign-up"
          className="inline-flex h-10 items-center rounded-control bg-gold-500 px-5 font-medium text-navy-950 hover:bg-gold-300"
        >
          Get started
        </Link>
        <Link
          href="/sign-in"
          className="inline-flex h-10 items-center rounded-control border border-stone-400 px-5 font-medium hover:bg-navy-800"
        >
          Sign in
        </Link>
      </div>
    </main>
  );
}
