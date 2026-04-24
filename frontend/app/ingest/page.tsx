"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { ingestPublic, seedDemo, uploadDocument } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function IngestPage() {
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const seedMutation = useMutation({ mutationFn: seedDemo });
  const publicMutation = useMutation({ mutationFn: ingestPublic });

  return (
    <main className="grid gap-6 lg:grid-cols-2">
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Demo data
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Seed the GLP-1 dataset</h1>
        <p className="mt-3 text-sm leading-7 text-ink/75">
          Loads sample payer policies, shortage signals, suspicious supplier examples, synthetic evidence chunks, and memory notes.
        </p>
        <Button className="mt-6" onClick={() => seedMutation.mutate()} disabled={seedMutation.isPending}>
          {seedMutation.isPending ? "Seeding..." : "Run demo ingest"}
        </Button>
        {seedMutation.data ? (
          <p className="mt-4 text-sm text-slateblue">
            {seedMutation.data.message} Records created: {seedMutation.data.records_created}
          </p>
        ) : null}
      </Card>

      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Public sources
        </p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Run live public ingest</h2>
        <p className="mt-3 text-sm leading-7 text-ink/75">
          Attempts openFDA shortages, openFDA enforcement recalls, and DailyMed label metadata for the supported GLP-1 drug set.
        </p>
        <Button className="mt-6" onClick={() => publicMutation.mutate()} disabled={publicMutation.isPending}>
          {publicMutation.isPending ? "Fetching..." : "Run public ingest"}
        </Button>
        {publicMutation.data ? (
          <p className="mt-4 text-sm text-slateblue">
            {publicMutation.data.message} Records created: {publicMutation.data.records_created}
          </p>
        ) : null}
      </Card>

      <Card className="lg:col-span-2">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Document upload
        </p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Index pharmacy SOPs, denial letters, or notes</h2>
        <p className="mt-3 text-sm leading-7 text-ink/75">
          Accepted file types: PDF, TXT, and CSV. Uploaded documents are parsed into section-aware chunks and added to the retrieval layer.
        </p>
        <label className="mt-6 block rounded-[1.5rem] border border-dashed border-ink/20 bg-sand p-8 text-center">
          <input
            type="file"
            className="hidden"
            onChange={async (event) => {
              const file = event.target.files?.[0];
              if (!file) return;
              const response = await uploadDocument(file);
              setUploadMessage(`${response.message} Chunks indexed: ${response.chunks_indexed}`);
            }}
          />
          <span className="text-sm font-semibold text-ink">Choose a document to upload</span>
        </label>
        {uploadMessage ? <p className="mt-4 text-sm text-slateblue">{uploadMessage}</p> : null}
      </Card>
    </main>
  );
}
