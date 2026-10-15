// Frontend counterpart of backend/app/core/redaction.py (spec 13 §10). Keep the rules in sync.
export const REDACTED = "[REDACTED]";

const SENSITIVE_KEY = /token|secret|password|api[_-]?key|authorization|cookie/i;
const DENY_LIST_KEYS = new Set(["content", "prompt", "completion", "text"]);
const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
const CARD = /\b(?:\d[ -]?){13,19}\b/g;
const BEARER = /\bBearer\s+[A-Za-z0-9._~+/-]+=*/gi;

export function isSensitiveKey(key: string): boolean {
  return SENSITIVE_KEY.test(key) || DENY_LIST_KEYS.has(key.toLowerCase());
}

export function scrubString(value: string): string {
  return value
    .replace(BEARER, `Bearer ${REDACTED}`)
    .replace(EMAIL, REDACTED)
    .replace(CARD, REDACTED);
}

export function scrub<T>(value: T, depth = 0): T {
  if (depth > 20) return REDACTED as T;
  if (typeof value === "string") return scrubString(value) as T;
  if (Array.isArray(value)) return value.map((v) => scrub(v, depth + 1)) as T;
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([k, v]) => [
        k,
        isSensitiveKey(k) ? REDACTED : scrub(v, depth + 1),
      ]),
    ) as T;
  }
  return value;
}
