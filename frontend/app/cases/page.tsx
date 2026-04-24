"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { fetchCases } from "@/lib/api";
import { CaseInput } from "@/components/CaseInput";
import { RiskBadge } from "@/components/RiskBadge";
import { Card } from "@/components/ui/card";

export default function CasesPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["cases"],
    queryFn: fetchCases
  });

  return (
    <main className="space-y-6">
      <CaseInput />
      <Card>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
              Recent cases
            </p>
            <h2 className="text-2xl font-semibold text-ink">Analyst work queue</h2>
          </div>
        </div>
        {isLoading ? <p className="text-sm text-ink/70">Loading cases...</p> : null}
        {error ? <p className="text-sm text-red-700">Unable to load cases.</p> : null}
        <div className="space-y-3">
          {data?.map((item) => (
            <Link
              href={`/cases/${item.id}`}
              key={item.id}
              className="block rounded-2xl border border-ink/10 bg-white p-4 hover:border-coral/40 hover:bg-sand"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-ink">
                    {item.drug_name || "Unknown drug"} · {item.payer_name || "No payer"}
                  </p>
                  <p className="text-xs uppercase tracking-[0.18em] text-slateblue">
                    {item.case_type} · {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <RiskBadge level={item.final_risk_level || "LOW"} />
              </div>
            </Link>
          ))}
          {!data?.length && !isLoading ? (
            <p className="text-sm text-ink/70">No analyzed cases yet. Run the demo case to populate the queue.</p>
          ) : null}
        </div>
      </Card>
    </main>
  );
}
