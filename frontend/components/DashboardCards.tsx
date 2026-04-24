"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { DashboardSummary } from "@/lib/types";
import { Card } from "@/components/ui/card";

export function DashboardCards({ summary }: { summary: DashboardSummary }) {
  const riskData = Object.entries(summary.risk_counts).map(([name, value]) => ({ name, value }));
  const paData = Object.entries(summary.pa_missing_evidence_counts).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total cases" value={summary.total_cases.toString()} accent="bg-mint" />
        <MetricCard
          label="Shortage cases"
          value={summary.shortage_cases.toString()}
          accent="bg-amber-100"
        />
        <MetricCard
          label="Supplier risk cases"
          value={summary.supplier_risk_cases.toString()}
          accent="bg-coral/20"
        />
        <MetricCard
          label="Feedback acceptance"
          value={`${Math.round(summary.feedback_acceptance_rate * 100)}%`}
          accent="bg-sky-100"
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
            Cases by Risk Level
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskData}>
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b4b74" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
            PA Missing Evidence
          </p>
          <div className="mt-4 space-y-3">
            {paData.length ? (
              paData.map((item) => (
                <div key={item.name} className="rounded-2xl border border-ink/10 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-ink">{item.name}</span>
                    <span className="text-sm font-semibold text-slateblue">{item.value}</span>
                  </div>
                  <div className="h-2 rounded-full bg-sand">
                    <div
                      className="h-2 rounded-full bg-coral"
                      style={{ width: `${Math.min(item.value * 20, 100)}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-ink/70">No prior authorization gaps recorded yet.</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  accent
}: {
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <Card className="p-0">
      <div className={`rounded-t-[1.75rem] ${accent} px-6 py-3 text-xs font-semibold uppercase tracking-[0.22em] text-ink`}>
        {label}
      </div>
      <div className="px-6 py-5">
        <p className="text-4xl font-semibold text-ink">{value}</p>
      </div>
    </Card>
  );
}
