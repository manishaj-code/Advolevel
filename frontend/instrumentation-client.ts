import * as Sentry from "@sentry/nextjs";

import { sharedSentryOptions } from "@/lib/observability/sentry-options";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
if (dsn) {
  Sentry.init({ dsn, ...sharedSentryOptions });
}
