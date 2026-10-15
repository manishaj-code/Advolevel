import type { ErrorEvent } from "@sentry/nextjs";

import { scrub } from "./scrub";

export function beforeSend(event: ErrorEvent): ErrorEvent {
  return {
    ...event,
    request: event.request && scrub(event.request),
    extra: event.extra && scrub(event.extra),
    contexts: event.contexts && scrub(event.contexts),
    breadcrumbs: event.breadcrumbs && scrub(event.breadcrumbs),
    user: event.user && scrub(event.user),
  };
}

export const sharedSentryOptions = {
  environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT ?? "local",
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE,
  sendDefaultPii: false,
  tracesSampleRate: 0,
  beforeSend,
};
