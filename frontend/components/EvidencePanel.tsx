import type { Citation } from "@/lib/types";

import { Card } from "@/components/ui/card";

export function EvidencePanel({ citations }: { citations: Citation[] }) {
  return (
    <Card>
      <div className="mb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Evidence and Citations
        </p>
        <h3 className="text-2xl font-semibold text-ink">Source-backed signals</h3>
      </div>
      <div className="space-y-3">
        {citations.map((citation) => (
          <div key={citation.id} className="rounded-2xl border border-ink/10 bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold text-ink">{citation.document_title || citation.source_name}</p>
                <p className="text-xs uppercase tracking-[0.18em] text-slateblue">
                  {citation.source_name}
                  {citation.section_title ? ` · ${citation.section_title}` : ""}
                </p>
              </div>
              {citation.source_url ? (
                <a
                  className="text-sm font-semibold text-slateblue underline-offset-4 hover:underline"
                  href={citation.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open source
                </a>
              ) : null}
            </div>
            <p className="mt-3 text-sm leading-6 text-ink/80">{citation.snippet}</p>
            {citation.note ? (
              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.18em] text-coral">
                {citation.note}
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </Card>
  );
}
