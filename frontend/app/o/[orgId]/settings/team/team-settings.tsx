"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { SelectField, TextField } from "@/components/ui/field";
import { EmptyState, ErrorPanel, Notice, Skeleton } from "@/components/ui/states";
import { ApiError } from "@/lib/api/client";
import {
  useInvitations,
  useInvite,
  useMembers,
  useRemoveMember,
  useResendInvitation,
  useRevokeInvitation,
  useTransferOwnership,
  useUpdateMember,
  type AssignableRole,
  type Invitation,
  type Member,
  type Role,
} from "@/lib/api/hooks";
import { useOrgContext } from "@/lib/org-context";
import {
  CAPABILITIES,
  ROLE_DESCRIPTIONS,
  ROLE_LABELS,
  ROLE_PERMISSIONS,
  can,
  type CapabilityId,
  type Permission,
} from "@/lib/permissions";

import { NotAMember } from "../../not-a-member";

const ASSIGNABLE: AssignableRole[] = ["admin", "member", "viewer"];
const ROLE_OPTIONS = ASSIGNABLE.map((r) => ({ value: r, label: ROLE_LABELS[r] }));

export function TeamSettings() {
  const { orgId, me, role } = useOrgContext();
  const [tab, setTab] = useState<"members" | "roles">("members");

  if (me.error) return <ErrorPanel error={me.error} onRetry={() => me.refetch()} />;
  if (!me.data) return <Skeleton lines={5} />;
  if (!role) return <NotAMember />;

  return (
    <div className="flex flex-col gap-6">
      <div role="tablist" aria-label="Team settings" className="flex gap-1 border-b border-border">
        {(
          [
            ["members", "Members"],
            ["roles", "Roles & permissions"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            role="tab"
            id={`tab-${id}`}
            aria-selected={tab === id}
            aria-controls={`panel-${id}`}
            onClick={() => setTab(id)}
            className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium ${tab === id ? "border-gold-500 text-text-primary" : "border-transparent text-text-secondary hover:text-text-primary"}`}
          >
            {label}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
        {tab === "members" ? (
          <MembersTab orgId={orgId} role={role} currentUserId={me.data.user.id} />
        ) : (
          <RolesTab orgId={orgId} role={role} />
        )}
      </div>
    </div>
  );
}

// ---- members ------------------------------------------------------------------------------

function MembersTab({
  orgId,
  role,
  currentUserId,
}: {
  orgId: string;
  role: Role;
  currentUserId: string;
}) {
  const canInvite = can(role, "members:invite");
  const members = useMembers(orgId);
  const invitations = useInvitations(orgId, canInvite);

  return (
    <div className="flex flex-col gap-8">
      {canInvite ? <InviteForm orgId={orgId} /> : null}

      <section aria-labelledby="members-heading" className="flex flex-col gap-3">
        <h2 id="members-heading" className="text-lg font-semibold">
          Members
        </h2>
        {members.error ? (
          <ErrorPanel error={members.error} onRetry={() => members.refetch()} />
        ) : !members.data ? (
          <Skeleton />
        ) : (
          <MembersTable
            orgId={orgId}
            role={role}
            currentUserId={currentUserId}
            members={members.data}
          />
        )}
      </section>

      {canInvite ? (
        <section aria-labelledby="invites-heading" className="flex flex-col gap-3">
          <h2 id="invites-heading" className="text-lg font-semibold">
            Pending invitations
          </h2>
          {invitations.error ? (
            <ErrorPanel error={invitations.error} onRetry={() => invitations.refetch()} />
          ) : !invitations.data ? (
            <Skeleton lines={2} />
          ) : invitations.data.items.length === 0 ? (
            <EmptyState title="No pending invitations" />
          ) : (
            <InvitationsTable orgId={orgId} invitations={invitations.data.items} />
          )}
        </section>
      ) : null}
    </div>
  );
}

function InviteForm({ orgId }: { orgId: string }) {
  const invite = useInvite(orgId);
  const [sentTo, setSentTo] = useState<string | null>(null);
  const emailError =
    invite.error instanceof ApiError
      ? invite.error.fieldErrors.find((e) => e.field === "email")?.message
      : undefined;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setSentTo(null);
    const result = await invite
      .mutateAsync({
        email: String(form.get("email") ?? "").trim(),
        role: form.get("role") as AssignableRole,
      })
      .catch(() => null);
    if (result) {
      setSentTo(result.email);
      formElement.reset();
    }
  }

  return (
    <section aria-labelledby="invite-heading" className="rounded-card bg-surface p-4 shadow-1">
      <h2 id="invite-heading" className="mb-3 text-lg font-semibold">
        Invite people
      </h2>
      <form onSubmit={onSubmit} className="grid gap-3 md:grid-cols-[1fr_180px_auto] md:items-end">
        <TextField
          label="Email"
          name="email"
          type="email"
          required
          autoComplete="off"
          error={emailError}
        />
        <SelectField label="Role" name="role" defaultValue="member" options={ROLE_OPTIONS} />
        <Button type="submit" disabled={invite.isPending}>
          {invite.isPending ? "Sending…" : "Send invite"}
        </Button>
      </form>
      <div className="mt-3">
        {sentTo ? (
          <Notice tone="success">Invitation sent to {sentTo}. The link expires in 7 days.</Notice>
        ) : null}
        {invite.error && !emailError ? <ErrorPanel error={invite.error} /> : null}
      </div>
    </section>
  );
}

/** Two-step confirm without browser dialogs: the first click arms, the second performs. */
function ConfirmButton({
  label,
  confirmLabel,
  onConfirm,
  disabled,
}: {
  label: string;
  confirmLabel: string;
  onConfirm: () => void;
  disabled?: boolean;
}) {
  const [armed, setArmed] = useState(false);
  return armed ? (
    <span className="inline-flex gap-1">
      <Button
        variant="danger"
        disabled={disabled}
        onClick={() => {
          setArmed(false);
          onConfirm();
        }}
      >
        {confirmLabel}
      </Button>
      <Button variant="ghost" onClick={() => setArmed(false)}>
        Cancel
      </Button>
    </span>
  ) : (
    <Button variant="ghost" disabled={disabled} onClick={() => setArmed(true)}>
      {label}
    </Button>
  );
}

function MembersTable({
  orgId,
  role,
  currentUserId,
  members,
}: {
  orgId: string;
  role: Role;
  currentUserId: string;
  members: Member[];
}) {
  const update = useUpdateMember(orgId);
  const remove = useRemoveMember(orgId);
  const transfer = useTransferOwnership(orgId);
  const error = update.error ?? remove.error ?? transfer.error;

  return (
    <div className="flex flex-col gap-3">
      {error ? <ErrorPanel error={error} /> : null}
      <div className="overflow-x-auto rounded-card border border-border bg-surface">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border text-caption text-text-secondary uppercase">
            <tr>
              <th scope="col" className="px-4 py-2 font-medium">
                Member
              </th>
              <th scope="col" className="px-4 py-2 font-medium">
                Role
              </th>
              <th scope="col" className="px-4 py-2 font-medium">
                Status
              </th>
              <th scope="col" className="px-4 py-2 font-medium">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => {
              const isOwner = m.role === "owner";
              const isSelf = m.user.id === currentUserId;
              const editable = can(role, "members:update") && !isOwner;
              return (
                <tr key={m.id} className="border-b border-border last:border-0">
                  <td className="px-4 py-3">
                    <div className="font-medium">
                      {m.user.name ?? m.user.email}
                      {isSelf ? <span className="text-text-secondary"> (you)</span> : null}
                    </div>
                    <div className="text-caption text-text-secondary">{m.user.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    {editable ? (
                      <select
                        aria-label={`Role for ${m.user.email}`}
                        className="h-8 rounded-control border border-border bg-surface px-2"
                        value={m.role}
                        disabled={update.isPending}
                        onChange={(e) =>
                          update.mutate({
                            membershipId: m.id,
                            body: { role: e.target.value as AssignableRole },
                          })
                        }
                      >
                        {ROLE_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>
                            {o.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      ROLE_LABELS[m.role]
                    )}
                  </td>
                  <td className="px-4 py-3 capitalize">{m.status}</td>
                  <td className="px-4 py-3 text-right whitespace-nowrap">
                    {role === "owner" && !isOwner && m.status === "active" ? (
                      <ConfirmButton
                        label="Make owner"
                        confirmLabel="Transfer ownership"
                        disabled={transfer.isPending}
                        onConfirm={() => transfer.mutate(m.user.id)}
                      />
                    ) : null}
                    {can(role, "members:remove") && !isOwner ? (
                      <ConfirmButton
                        label={isSelf ? "Leave" : "Remove"}
                        confirmLabel={isSelf ? "Leave organization" : "Remove member"}
                        disabled={remove.isPending}
                        onConfirm={() => remove.mutate(m.id)}
                      />
                    ) : null}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function InvitationsTable({ orgId, invitations }: { orgId: string; invitations: Invitation[] }) {
  const resend = useResendInvitation(orgId);
  const revoke = useRevokeInvitation(orgId);
  const error = resend.error ?? revoke.error;
  const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: "medium" });

  return (
    <div className="flex flex-col gap-3">
      {error ? <ErrorPanel error={error} /> : null}
      {resend.isSuccess ? <Notice tone="success">Invitation sent again.</Notice> : null}
      <ul className="divide-y divide-border rounded-card border border-border bg-surface">
        {invitations.map((i) => (
          <li key={i.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <div>
              <div className="font-medium">{i.email}</div>
              <div className="text-caption text-text-secondary">
                {ROLE_LABELS[i.role as Role] ?? i.role} · expires{" "}
                {dateFormat.format(new Date(i.expires_at))}
              </div>
            </div>
            <span className="inline-flex gap-1">
              <Button
                variant="ghost"
                disabled={resend.isPending}
                onClick={() => resend.mutate(i.id)}
              >
                Resend
              </Button>
              <ConfirmButton
                label="Revoke"
                confirmLabel="Revoke invitation"
                disabled={revoke.isPending}
                onConfirm={() => revoke.mutate(i.id)}
              />
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ---- roles --------------------------------------------------------------------------------

const MATRIX_ROWS: { permission: Permission; label: string }[] = [
  { permission: "org:read", label: "View organization" },
  { permission: "org:update", label: "Edit organization settings" },
  { permission: "members:invite", label: "Invite members" },
  { permission: "members:update", label: "Change roles and capabilities" },
  { permission: "members:remove", label: "Remove members" },
  { permission: "org:transfer_ownership", label: "Transfer ownership" },
  { permission: "org:delete", label: "Delete organization" },
];
const ROLES: Role[] = ["owner", "admin", "member", "viewer"];

function RolesTab({ orgId, role }: { orgId: string; role: Role }) {
  const members = useMembers(orgId);
  const update = useUpdateMember(orgId);
  const editable = can(role, "members:update");

  return (
    <div className="flex flex-col gap-8">
      <section aria-labelledby="matrix-heading" className="flex flex-col gap-3">
        <h2 id="matrix-heading" className="text-lg font-semibold">
          What each role can do
        </h2>
        <ul className="grid gap-2 md:grid-cols-2">
          {ROLES.map((r) => (
            <li key={r} className="rounded-card border border-border bg-surface p-3">
              <div className="font-medium">{ROLE_LABELS[r]}</div>
              <div className="text-sm text-text-secondary">{ROLE_DESCRIPTIONS[r]}</div>
            </li>
          ))}
        </ul>
        <div className="overflow-x-auto rounded-card border border-border bg-surface">
          <table className="w-full text-sm">
            <caption className="sr-only">Permissions by role</caption>
            <thead className="border-b border-border text-caption text-text-secondary uppercase">
              <tr>
                <th scope="col" className="px-4 py-2 text-left font-medium">
                  Action
                </th>
                {ROLES.map((r) => (
                  <th key={r} scope="col" className="px-4 py-2 font-medium">
                    {ROLE_LABELS[r]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MATRIX_ROWS.map(({ permission, label }) => (
                <tr key={permission} className="border-b border-border last:border-0">
                  <th scope="row" className="px-4 py-2 text-left font-normal">
                    {label}
                  </th>
                  {ROLES.map((r) => (
                    <td key={r} className="px-4 py-2 text-center">
                      {ROLE_PERMISSIONS[r].has(permission) ? (
                        <span aria-label="Allowed">✓</span>
                      ) : (
                        <span aria-label="Not allowed" className="text-stone-400">
                          —
                        </span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section aria-labelledby="caps-heading" className="flex flex-col gap-3">
        <h2 id="caps-heading" className="text-lg font-semibold">
          Capabilities
        </h2>
        <p className="text-sm text-text-secondary">
          Extra permissions you can grant to individual people on top of their role.
        </p>
        {update.error ? <ErrorPanel error={update.error} /> : null}
        {members.error ? (
          <ErrorPanel error={members.error} onRetry={() => members.refetch()} />
        ) : !members.data ? (
          <Skeleton />
        ) : (
          <div className="overflow-x-auto rounded-card border border-border bg-surface">
            <table className="w-full text-sm">
              <caption className="sr-only">Capabilities by member</caption>
              <thead className="border-b border-border text-caption text-text-secondary uppercase">
                <tr>
                  <th scope="col" className="px-4 py-2 text-left font-medium">
                    Member
                  </th>
                  {CAPABILITIES.map((c) => (
                    <th
                      key={c.id}
                      scope="col"
                      className="px-4 py-2 font-medium"
                      title={c.description}
                    >
                      {c.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {members.data.map((m) => (
                  <tr key={m.id} className="border-b border-border last:border-0">
                    <th scope="row" className="px-4 py-2 text-left font-normal">
                      {m.user.name ?? m.user.email}
                    </th>
                    {CAPABILITIES.map((c) => {
                      const checked = m.capabilities.includes(c.id);
                      return (
                        <td key={c.id} className="px-4 py-2 text-center">
                          <input
                            type="checkbox"
                            aria-label={`${c.label} for ${m.user.email}`}
                            checked={checked}
                            disabled={!editable || m.role === "owner" || update.isPending}
                            onChange={() => {
                              const next = checked
                                ? m.capabilities.filter((x) => x !== c.id)
                                : [...m.capabilities, c.id];
                              update.mutate({
                                membershipId: m.id,
                                body: { capabilities: next as CapabilityId[] },
                              });
                            }}
                          />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
