"use client";

import { useMutation } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { submitFeedback } from "@/lib/api";
import type { AgentTraceItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function FeedbackPanel({
  caseId,
  agents
}: {
  caseId: string;
  agents: AgentTraceItem[];
}) {
  const [agentName, setAgentName] = useState(agents[0]?.agent_name ?? "coverage_agent");
  const [rating, setRating] = useState(4);
  const [feedbackText, setFeedbackText] = useState("");
  const [correctionText, setCorrectionText] = useState("");
  const options = useMemo(() => agents.map((item) => item.agent_name), [agents]);

  const mutation = useMutation({
    mutationFn: () =>
      submitFeedback({
        case_id: caseId,
        agent_name: agentName,
        rating,
        feedback_text: feedbackText,
        correction_text: correctionText
      })
  });

  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
            Pharmacist Feedback Loop
          </p>
          <h3 className="text-2xl font-semibold">Store corrections and memory</h3>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="text-sm font-medium text-ink">
          Agent
          <select
            value={agentName}
            onChange={(event) => setAgentName(event.target.value)}
            className="mt-2 w-full rounded-2xl border border-ink/10 bg-white px-4 py-3"
          >
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-ink">
          Rating
          <Input
            className="mt-2"
            type="number"
            min={1}
            max={5}
            value={rating}
            onChange={(event) => setRating(Number(event.target.value))}
          />
        </label>
      </div>
      <label className="mt-4 block text-sm font-medium text-ink">
        Feedback
        <textarea
          className="mt-2 min-h-24 w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm"
          value={feedbackText}
          onChange={(event) => setFeedbackText(event.target.value)}
          placeholder="Good, but missing BMI requirement."
        />
      </label>
      <label className="mt-4 block text-sm font-medium text-ink">
        Correction text
        <textarea
          className="mt-2 min-h-24 w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm"
          value={correctionText}
          onChange={(event) => setCorrectionText(event.target.value)}
          placeholder="For this payer, GLP-1 weight-loss coverage requires BMI documentation."
        />
      </label>
      <div className="mt-4 flex items-center gap-3">
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          {mutation.isPending ? "Saving feedback..." : "Submit feedback"}
        </Button>
        {mutation.isSuccess ? (
          <span className="text-sm text-slateblue">Feedback stored and memory updated.</span>
        ) : null}
      </div>
    </Card>
  );
}
