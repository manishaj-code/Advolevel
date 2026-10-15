"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { rememberOrg } from "@/lib/active-org";
import { useOrgContext } from "@/lib/org-context";

const NAV = [
  { href: "", label: "Dashboard" },
  { href: "/settings/team", label: "Team & roles" },
];

export function OrgNav() {
  const { orgId } = useOrgContext();
  const pathname = usePathname();
  if (!orgId) return null;
  return NAV.map(({ href, label }) => {
    const target = `/o/${orgId}${href}`;
    const active = pathname === target;
    return (
      <Link
        key={label}
        href={target}
        aria-current={active ? "page" : undefined}
        className={`rounded-control px-3 py-2 text-sm ${active ? "bg-navy-800 text-stone-0" : "text-stone-200 hover:bg-navy-900"}`}
      >
        {label}
      </Link>
    );
  });
}

export function OrgSwitcher() {
  const router = useRouter();
  const { orgId, me } = useOrgContext();
  const memberships = me.data?.memberships ?? [];
  if (!me.data) return <div className="h-9 rounded-control bg-navy-800" />;

  return (
    <label className="flex flex-col gap-1 text-caption text-stone-200">
      Organization
      <select
        className="h-9 rounded-control border border-navy-700 bg-navy-900 px-2 text-sm text-stone-0"
        value={orgId ?? ""}
        onChange={(event) => {
          const next = event.target.value;
          if (next === "__new") {
            router.push("/onboarding");
            return;
          }
          rememberOrg(next);
          router.push(`/o/${next}`);
        }}
      >
        {memberships.map((m) => (
          <option key={m.organization.id} value={m.organization.id}>
            {m.organization.name}
          </option>
        ))}
        <option value="__new">+ New organization</option>
      </select>
    </label>
  );
}
