import type { AgentTraceItem } from "@/lib/types";

import { RiskBadge } from "@/components/RiskBadge";
import { Card } from "@/components/ui/card";

export function AgentTrace({ trace }: { trace: AgentTraceItem[] }) {
  return (
    <div className="space-y-4">
      {trace.map((item) => (
        <Card key={item.agent_name}>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slateblue">
                Agent Trace
              </p>
              <h3 className="text-xl font-semibold text-ink">{item.agent_name}</h3>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-sand px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]">
                {item.status}
              </span>
              <RiskBadge level={item.risk_level} />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
                Findings
              </p>
              <div className="space-y-3">
                {item.findings.length ? (
                  item.findings.map((finding) => (
                    <div key={finding.title} className="rounded-2xl border border-ink/10 p-4">
                      <p className="font-semibold text-ink">{finding.title}</p>
                      <p className="mt-1 text-sm leading-6 text-ink/80">{finding.detail}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-ink/70">No additional findings recorded.</p>
                )}
              </div>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
                Recommended Actions
              </p>
              <div className="space-y-2">
                {item.recommended_actions.length ? (
                  item.recommended_actions.map((action, index) => (
                    <div key={`${action}-${index}`} className="rounded-2xl bg-sand p-3 text-sm">
                      {action}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-ink/70">No agent-specific actions recorded.</p>
                )}
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
