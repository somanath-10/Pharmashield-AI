import { CheckCircle2 } from "lucide-react";

import { Card } from "@/components/ui/card";

export function ActionPlan({ actions }: { actions: string[] }) {
  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-2xl font-semibold">Recommended Pharmacy Action Plan</h3>
        <span className="rounded-full bg-mint px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]">
          Reviewable
        </span>
      </div>
      <div className="space-y-3">
        {actions.map((action, index) => (
          <div
            key={`${action}-${index}`}
            className="flex gap-3 rounded-2xl border border-ink/10 bg-white p-4"
          >
            <CheckCircle2 className="mt-0.5 h-5 w-5 text-slateblue" />
            <p className="text-sm leading-6 text-ink">{action}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
