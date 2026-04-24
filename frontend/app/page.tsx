import Link from "next/link";

import { CaseInput } from "@/components/CaseInput";
import { Card } from "@/components/ui/card";

const modules = [
  {
    title: "Shortages and substitutions",
    detail:
      "Monitor inventory pressure, shortage events, recall impact, and pharmacist-reviewed substitution workflows."
  },
  {
    title: "Prior authorization intelligence",
    detail:
      "Map payer coverage criteria to case data, identify documentation gaps, and draft appeal-ready packets."
  },
  {
    title: "GLP-1 authenticity and compliance",
    detail:
      "Flag suspicious supplier claims, compounding-compliance risks, and unsafe product marketing."
  }
];

export default function HomePage() {
  return (
    <main className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card className="overflow-hidden bg-white/85">
          <p className="text-xs font-semibold uppercase tracking-[0.26em] text-slateblue">
            Memory-aware multi-agent RAG platform
          </p>
          <h1 className="mt-3 max-w-3xl text-5xl font-semibold leading-tight text-ink">
            Built for pharmacy teams navigating GLP-1 shortages, payer friction, and unsafe supply-chain risk.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-8 text-ink/75">
            PharmaShield AI is not a generic chatbot. It coordinates shortage, coverage, and authenticity agents,
            grounds outputs in retrieved evidence, and returns pharmacist-reviewable recommendations with citations.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="#case-analyzer"
              className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white hover:bg-slateblue"
            >
              Start case
            </Link>
            <Link
              href="/dashboard"
              className="rounded-full border border-ink/10 bg-sand px-5 py-3 text-sm font-semibold text-ink hover:bg-mint"
            >
              View dashboard
            </Link>
          </div>
        </Card>

        <div className="grid gap-4">
          {modules.map((module, index) => (
            <Card
              key={module.title}
              className={index === 1 ? "border-coral/30 bg-coral/10" : index === 2 ? "border-mint/60 bg-mint/40" : ""}
            >
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
                Module {index + 1}
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-ink">{module.title}</h2>
              <p className="mt-3 text-sm leading-7 text-ink/75">{module.detail}</p>
            </Card>
          ))}
        </div>
      </section>

      <section id="case-analyzer" className="space-y-4">
        <CaseInput />
      </section>
    </main>
  );
}
