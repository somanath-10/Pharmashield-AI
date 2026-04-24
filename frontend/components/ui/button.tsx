import * as React from "react";

import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

const variantStyles: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-ink text-white shadow-panel transition hover:-translate-y-0.5 hover:bg-slateblue",
  secondary:
    "border border-ink/10 bg-white text-ink transition hover:border-coral/60 hover:bg-coral/10",
  ghost: "bg-transparent text-ink transition hover:bg-white/50"
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold",
          variantStyles[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
