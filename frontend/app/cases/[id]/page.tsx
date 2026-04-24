"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { fetchCase } from "@/lib/api";
import { ActionPlan } from "@/components/ActionPlan";
import { AgentTrace } from "@/components/AgentTrace";
import { DraftMessages } from "@/components/DraftMessages";
import { EvidencePanel } from "@/components/EvidencePanel";
import { FeedbackPanel } from "@/components/FeedbackPanel";
import { RiskBadge } from "@/components/RiskBadge";
import { Card } from "@/components/ui/card";

export default function CaseDetailPage() {
  const params = useParams() as { id: string };
  const { data, isLoading, error } = useQuery({
    queryKey: ["case", params.id],
    queryFn: () => fetchCase(params.id)
  });

  if (isLoading) {
    return <p className="text-sm text-ink/70">Loading case analysis...</p>;
  }

  if (error || !data) {
    return <p className="text-sm text-red-700">Unable to load the selected case.</p>;
  }

  return (
    <main className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
              Multi-agent case result
            </p>
            <h1 className="mt-2 text-4xl font-semibold text-ink">Case {data.case_id}</h1>
            <p className="mt-3 max-w-4xl whitespace-pre-wrap text-sm leading-7 text-ink/80">
              {data.summary}
            </p>
          </div>
          <div className="space-y-3 text-right">
            <RiskBadge level={data.risk_level} />
            <p className="text-xs uppercase tracking-[0.18em] text-slateblue">
              Intent: {data.intent}
            </p>
          </div>
        </div>
      </Card>

      <ActionPlan actions={data.action_plan} />
      <DraftMessages
        prescriberMessage={data.draft_prescriber_message}
        patientMessage={data.draft_patient_message}
      />
      <AgentTrace trace={data.agent_trace} />
      <EvidencePanel citations={data.citations} />
      <FeedbackPanel caseId={data.case_id} agents={data.agent_trace} />
    </main>
  );
}
