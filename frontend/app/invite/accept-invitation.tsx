"use client";

import { SignInButton, SignOutButton, SignUpButton, useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useSyncExternalStore } from "react";

import { Button } from "@/components/ui/button";
import { ErrorPanel, Skeleton } from "@/components/ui/states";
import {
  clearInviteToken,
  pendingInviteToken,
  rememberOrg,
  stashInviteToken,
} from "@/lib/active-org";
import { ApiError, unwrap } from "@/lib/api/client";
import { queryKeys, useApi } from "@/lib/api/hooks";
import { ROLE_LABELS } from "@/lib/permissions";

const DEAD_LINK: Record<string, string> = {
  invitation_not_found: "This invitation link is not valid.",
  invitation_expired: "This invitation has expired.",
  invitation_used: "This invitation has already been used.",
  invitation_revoked: "This invitation was withdrawn.",
};

/** Token arrives as `/invite#token=…`: fragments never reach servers, logs or analytics. */
function hashToken(): string | null {
  return new URLSearchParams(window.location.hash.slice(1)).get("token");
}

const noSubscription = () => () => {};
const readToken = () => hashToken() ?? pendingInviteToken();
const serverToken = () => undefined; // unknown until hydration

export function AcceptInvitation() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isLoaded, isSignedIn } = useAuth();
  const api = useApi();
  const token = useSyncExternalStore(noSubscription, readToken, serverToken);

  // Keep the token for the sign-in round trip, and take it out of the address bar and history.
  useEffect(() => {
    const fromHash = hashToken();
    if (fromHash) {
      stashInviteToken(fromHash);
      window.history.replaceState(null, "", window.location.pathname);
    }
  }, []);

  const preview = useQuery({
    queryKey: ["invitation-preview", token],
    queryFn: () => unwrap(api.POST("/api/v1/invitations/preview", { body: { token: token! } })),
    enabled: Boolean(token),
    retry: false,
  });

  const accept = useMutation({
    mutationFn: () => unwrap(api.POST("/api/v1/invitations/accept", { body: { token: token! } })),
    onSuccess: async (membership) => {
      clearInviteToken();
      rememberOrg(membership.organization.id);
      await queryClient.invalidateQueries({ queryKey: queryKeys.me });
      router.replace(`/o/${membership.organization.id}`);
    },
  });

  if (token === undefined || (token && preview.isPending)) {
    return <Skeleton label="Checking your invitation" />;
  }

  const deadCode = !token
    ? "invitation_not_found"
    : preview.error instanceof ApiError && preview.error.code in DEAD_LINK
      ? preview.error.code
      : null;
  if (deadCode) {
    return (
      <section className="flex flex-col gap-3">
        <h1 className="font-display text-[28px] leading-9 font-semibold">{DEAD_LINK[deadCode]}</h1>
        <p className="text-text-secondary">
          Ask the person who invited you to send a new invitation.
        </p>
        <Button
          variant="secondary"
          onClick={() => {
            clearInviteToken();
            router.push("/home");
          }}
        >
          Go to AdvoLevel
        </Button>
      </section>
    );
  }
  if (preview.error || !preview.data) {
    return <ErrorPanel error={preview.error} onRetry={() => preview.refetch()} />;
  }

  const invite = preview.data;
  const wrongAccount =
    accept.error instanceof ApiError && accept.error.code === "invitation_email_mismatch";

  return (
    <section className="flex flex-col gap-4">
      <h1 className="font-display text-[28px] leading-9 font-semibold">
        Join {invite.organization_name}
      </h1>
      <p className="text-text-secondary">
        {invite.inviter_name ?? "A colleague"} invited you to join as{" "}
        <strong className="text-text-primary">
          {ROLE_LABELS[invite.role as keyof typeof ROLE_LABELS] ?? invite.role}
        </strong>
        . This invitation is for <span className="font-mono">{invite.email_hint}</span>.
      </p>

      {!isLoaded ? (
        <Skeleton lines={1} />
      ) : !isSignedIn ? (
        <div className="flex flex-wrap gap-3">
          <SignInButton forceRedirectUrl="/invite">
            <Button>Sign in to accept</Button>
          </SignInButton>
          <SignUpButton forceRedirectUrl="/invite">
            <Button variant="secondary">Create an account</Button>
          </SignUpButton>
        </div>
      ) : wrongAccount ? (
        <div role="alert" className="flex flex-col gap-3 rounded-card bg-warning-50 p-4">
          <p className="text-warning-600">{accept.error?.message}</p>
          <SignOutButton redirectUrl="/invite">
            <Button variant="secondary">Switch account</Button>
          </SignOutButton>
        </div>
      ) : (
        <>
          {accept.error ? <ErrorPanel error={accept.error} /> : null}
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => accept.mutate()} disabled={accept.isPending}>
              {accept.isPending ? "Joining…" : "Accept invitation"}
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                clearInviteToken();
                router.push("/home");
              }}
            >
              Decline
            </Button>
          </div>
        </>
      )}
    </section>
  );
}
