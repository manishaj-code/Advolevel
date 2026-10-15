import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-navy-900 text-stone-0 hover:bg-navy-800 disabled:bg-navy-500",
  secondary:
    "border border-border bg-surface text-text-primary hover:bg-stone-100 disabled:text-stone-400",
  ghost: "text-text-primary hover:bg-stone-100 disabled:text-stone-400",
  danger: "bg-danger-600 text-stone-0 hover:opacity-90 disabled:opacity-60",
};

export function Button({
  variant = "primary",
  className = "",
  type = "button",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      type={type}
      className={`inline-flex h-9 items-center justify-center gap-2 rounded-control px-4 text-sm font-medium transition-colors disabled:cursor-not-allowed ${VARIANTS[variant]} ${className}`}
      {...props}
    />
  );
}
