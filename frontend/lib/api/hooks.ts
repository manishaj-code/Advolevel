"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";

import { createApiClient, unwrap, type ApiClient, type Schemas } from "./client";

export type Me = Schemas["MeOut"];
export type Member = Schemas["MemberOut"];
export type Invitation = Schemas["InvitationOut"];
export type Role = Member["role"];
export type AssignableRole = Exclude<Role, "owner">;

export const queryKeys = {
  me: ["me"] as const,
  members: (orgId: string) => ["org", orgId, "members"] as const,
  invitations: (orgId: string) => ["org", orgId, "invitations"] as const,
};

/** Tenant routes name the active org explicitly; the server re-checks membership (BR-T-02). */
const tenant = (orgId: string) => ({ "x-org-id": orgId });

/** API client carrying the Clerk session token. */
export function useApi(): ApiClient {
  const { getToken } = useAuth();
  return useMemo(() => createApiClient({ getToken: () => getToken() }), [getToken]);
}

export function useMe() {
  const api = useApi();
  const { isSignedIn } = useAuth();
  return useQuery({
    queryKey: queryKeys.me,
    queryFn: () => unwrap(api.GET("/api/v1/me")),
    enabled: Boolean(isSignedIn),
  });
}

export function useCreateOrganization() {
  const api = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Schemas["OrganizationCreate"]) => unwrap(api.POST("/api/v1/orgs", { body })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.me }),
  });
}

export function useMembers(orgId: string) {
  const api = useApi();
  return useQuery({
    queryKey: queryKeys.members(orgId),
    // Teams are small in V1; fetch every page so the table shows everyone.
    queryFn: async () => {
      const items: Member[] = [];
      let cursor: string | undefined;
      do {
        const page = await unwrap(
          api.GET("/api/v1/members", {
            params: { header: tenant(orgId), query: { limit: 100, cursor } },
          }),
        );
        items.push(...page.items);
        cursor = page.next_cursor ?? undefined;
      } while (cursor);
      return items;
    },
  });
}

export function useInvitations(orgId: string, enabled: boolean) {
  const api = useApi();
  return useQuery({
    queryKey: queryKeys.invitations(orgId),
    queryFn: () =>
      unwrap(
        api.GET("/api/v1/invitations", {
          params: { header: tenant(orgId), query: { limit: 100 } },
        }),
      ),
    enabled,
  });
}

/** Mutations in one org: refresh that org's queries and /me (roles or membership may change). */
function useOrgMutation<TVariables, TResult>(
  orgId: string,
  fn: (api: ApiClient, variables: TVariables) => Promise<TResult>,
) {
  const api = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: TVariables) => fn(api, variables),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ["org", orgId] }),
        queryClient.invalidateQueries({ queryKey: queryKeys.me }),
      ]),
  });
}

export function useInvite(orgId: string) {
  return useOrgMutation(orgId, (api, body: Schemas["InvitationCreate"]) =>
    unwrap(api.POST("/api/v1/invitations", { params: { header: tenant(orgId) }, body })),
  );
}

export function useResendInvitation(orgId: string) {
  return useOrgMutation(orgId, (api, invitationId: string) =>
    unwrap(
      api.POST("/api/v1/invitations/{invitation_id}/resend", {
        params: { header: tenant(orgId), path: { invitation_id: invitationId } },
      }),
    ),
  );
}

export function useRevokeInvitation(orgId: string) {
  return useOrgMutation(orgId, (api, invitationId: string) =>
    unwrap(
      api.DELETE("/api/v1/invitations/{invitation_id}", {
        params: { header: tenant(orgId), path: { invitation_id: invitationId } },
      }),
    ),
  );
}

export function useUpdateMember(orgId: string) {
  return useOrgMutation(
    orgId,
    (api, { membershipId, body }: { membershipId: string; body: Schemas["MemberUpdate"] }) =>
      unwrap(
        api.PATCH("/api/v1/members/{membership_id}", {
          params: { header: tenant(orgId), path: { membership_id: membershipId } },
          body,
        }),
      ),
  );
}

export function useRemoveMember(orgId: string) {
  return useOrgMutation(orgId, (api, membershipId: string) =>
    unwrap(
      api.DELETE("/api/v1/members/{membership_id}", {
        params: { header: tenant(orgId), path: { membership_id: membershipId } },
      }),
    ),
  );
}

export function useTransferOwnership(orgId: string) {
  return useOrgMutation(orgId, (api, newOwnerUserId: string) =>
    unwrap(
      api.POST("/api/v1/orgs/{org_id}/transfer-ownership", {
        params: { path: { org_id: orgId } },
        body: { new_owner_user_id: newOwnerUserId },
      }),
    ),
  );
}
