import type { ReactNode } from "react";

import { ApiError } from "@/lib/api/client";

import { Button } from "./button";

/** Spec 04 §0 error state: message, retry, and the correlation ID for support. */
export function ErrorPanel({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const apiError = error instanceof ApiError ? error : null;
  return (
    <div role="alert" className="rounded-card border border-danger-600/30 bg-danger-50 p-4">
      <p className="font-medium text-danger-600">
        {apiError?.message ?? "Something went wrong. Please try again."}
      </p>
      {apiError?.requestId ? (
        <p className="mt-1 text-caption text-text-secondary">
          Reference: <span className="font-mono">{apiError.requestId}</span>
        </p>
      ) : null}
      {onRetry ? (
        <Button variant="secondary" className="mt-3" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}

/** Spec 04 §0 loading state: a skeleton, not a bare spinner. */
export function Skeleton({ lines = 3, label = "Loading" }: { lines?: number; label?: string }) {
  return (
    <div role="status" aria-label={label} className="flex flex-col gap-3">
      {Array.from({ length: lines }, (_, i) => (
        <div key={i} className="h-5 animate-pulse rounded-control bg-stone-200" />
      ))}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="rounded-card border border-dashed border-border bg-surface p-8 text-center">
      <p className="font-medium">{title}</p>
      {children ? <div className="mt-2 text-text-secondary">{children}</div> : null}
    </div>
  );
}

export function Notice({
  tone = "info",
  children,
}: {
  tone?: "info" | "success" | "warning";
  children: ReactNode;
}) {
  const tones = {
    info: "bg-info-50 text-info-600",
    success: "bg-success-50 text-success-600",
    warning: "bg-warning-50 text-warning-600",
  };
  return (
    <div role="status" className={`rounded-card p-3 text-sm ${tones[tone]}`}>
      {children}
    </div>
  );
}
