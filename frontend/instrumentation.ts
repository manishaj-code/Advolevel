import * as Sentry from "@sentry/nextjs";

import { sharedSentryOptions } from "@/lib/observability/sentry-options";

export function register() {
  const dsn = process.env.SENTRY_DSN ?? process.env.NEXT_PUBLIC_SENTRY_DSN;
  if (dsn) {
    Sentry.init({ dsn, ...sharedSentryOptions });
  }
}

export const onRequestError = Sentry.captureRequestError;
