import Link from "next/link";

/** Same message whether the org does not exist or the user is not in it (no tenant leaks). */
export function NotAMember() {
  return (
    <div className="flex flex-col gap-2">
      <h1 className="font-display text-[28px] leading-9 font-semibold">Organization not found</h1>
      <p className="text-text-secondary">
        It may not exist, or you are not a member. Ask an admin to invite you.
      </p>
      <Link href="/home" className="text-navy-700 underline">
        Go to your organizations
      </Link>
    </div>
  );
}
