// Per-browser conveniences only; the server re-checks membership on every request (BR-T-02).
const LAST_ORG_KEY = "advolevel:last-org";
const PENDING_INVITE_KEY = "advolevel:pending-invite";

function storage(kind: "local" | "session"): Storage | null {
  try {
    return kind === "local" ? window.localStorage : window.sessionStorage;
  } catch {
    return null;
  }
}

export function rememberOrg(orgId: string) {
  try {
    storage("local")?.setItem(LAST_ORG_KEY, orgId);
  } catch {}
}

export function lastOrg(): string | null {
  try {
    return storage("local")?.getItem(LAST_ORG_KEY) ?? null;
  } catch {
    return null;
  }
}

/** Keeps an invitation token across the sign-in/sign-up round trip (session-scoped). */
export function stashInviteToken(token: string) {
  try {
    storage("session")?.setItem(PENDING_INVITE_KEY, token);
  } catch {}
}

export function pendingInviteToken(): string | null {
  try {
    return storage("session")?.getItem(PENDING_INVITE_KEY) ?? null;
  } catch {
    return null;
  }
}

export function clearInviteToken() {
  try {
    storage("session")?.removeItem(PENDING_INVITE_KEY);
  } catch {}
}
