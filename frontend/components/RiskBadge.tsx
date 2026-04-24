import { cn } from "@/lib/utils";

const toneMap = {
  LOW: "bg-mint text-ink",
  MEDIUM: "bg-amber-100 text-amber-800",
  HIGH: "bg-coral/20 text-red-700",
  CRITICAL: "bg-red-600 text-white"
} as const;

export function RiskBadge({ level }: { level: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]",
        toneMap[level as keyof typeof toneMap] ?? "bg-slate-200 text-slate-700"
      )}
    >
      {level}
    </span>
  );
}
