"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { fetchCases, fetchDashboardSummary } from "@/lib/api";
import { DashboardCards } from "@/components/DashboardCards";
import { RiskBadge } from "@/components/RiskBadge";
import { Card } from "@/components/ui/card";

export default function DashboardPage() {
  const summaryQuery = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary
  });
  const casesQuery = useQuery({
    queryKey: ["dashboard-cases"],
    queryFn: fetchCases
  });

  return (
    <main className="space-y-6">
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Operations dashboard
        </p>
        <h1 className="mt-2 text-4xl font-semibold text-ink">Risk, access, and supplier trend view</h1>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/75">
          Monitor case volume by risk, watch documentation bottlenecks for prior authorization, and identify supplier-risk patterns that need pharmacist escalation.
        </p>
      </Card>

      {summaryQuery.data ? <DashboardCards summary={summaryQuery.data} /> : null}
      {summaryQuery.isLoading ? <p className="text-sm text-ink/70">Loading dashboard metrics...</p> : null}

      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Recent case feed
        </p>
        <div className="mt-4 space-y-3">
          {casesQuery.data?.slice(0, 8).map((item) => (
            <Link
              key={item.id}
              href={`/cases/${item.id}`}
              className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-ink/10 bg-white p-4 hover:bg-sand"
            >
              <div>
                <p className="font-semibold text-ink">{item.drug_name || "Unknown drug"}</p>
                <p className="text-xs uppercase tracking-[0.18em] text-slateblue">
                  {item.case_type} · {item.payer_name || "No payer"}
                </p>
              </div>
              <RiskBadge level={item.final_risk_level || "LOW"} />
            </Link>
          ))}
          {!casesQuery.data?.length && !casesQuery.isLoading ? (
            <p className="text-sm text-ink/70">No cases yet. Seed the demo dataset and analyze the sample case.</p>
          ) : null}
        </div>
      </Card>
    </main>
  );
}
