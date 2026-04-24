import { PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

export function Card({
  children,
  className
}: PropsWithChildren<{ className?: string }>) {
  return (
    <div
      className={cn(
        "rounded-[1.75rem] border border-white/60 bg-white/80 p-6 shadow-panel backdrop-blur",
        className
      )}
    >
      {children}
    </div>
  );
}
