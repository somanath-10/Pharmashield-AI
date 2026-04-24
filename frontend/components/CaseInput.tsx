"use client";

import { useMutation } from "@tanstack/react-query";
import { AlertCircle, ArrowRight, RefreshCcw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { analyzeCase } from "@/lib/api";
import { caseRequestSchema } from "@/lib/validators";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const demoPayload = {
  query:
    "Ozempic is out of stock, Wegovy was denied by insurance, and patient found a cheaper semaglutide supplier online claiming generic Ozempic with no prescription needed. What should pharmacy staff do?",
  drug_name: "Ozempic",
  payer_name: "Demo Health Plan",
  patient_context: {
    age: 52,
    diagnoses: ["type 2 diabetes"],
    labs: { a1c: "8.7" },
    previous_therapies: ["metformin"],
    allergies: []
  },
  inventory_context: {
    location_id: "PHARMACY_001",
    quantity_on_hand: 0,
    reorder_threshold: 2
  },
  product_context: {
    supplier_name: "Online Semaglutide Discount Pharmacy",
    claim_text: "Generic Ozempic, same active ingredient, no prescription needed",
    ndc: null,
    lot_number: null,
    manufacturer: null
  },
  denial_letter_text: null
};

function pretty(value: unknown) {
  return JSON.stringify(value, null, 2);
}

export function CaseInput() {
  const router = useRouter();
  const [query, setQuery] = useState(demoPayload.query);
  const [drugName, setDrugName] = useState(demoPayload.drug_name);
  const [payerName, setPayerName] = useState(demoPayload.payer_name);
  const [patientJson, setPatientJson] = useState(pretty(demoPayload.patient_context));
  const [inventoryJson, setInventoryJson] = useState(pretty(demoPayload.inventory_context));
  const [productJson, setProductJson] = useState(pretty(demoPayload.product_context));
  const [denialLetter, setDenialLetter] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: analyzeCase,
    onSuccess: (data) => {
      router.push(`/cases/${data.case_id}`);
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : "Unable to analyze case.");
    }
  });

  function loadDemo() {
    setQuery(demoPayload.query);
    setDrugName(demoPayload.drug_name);
    setPayerName(demoPayload.payer_name);
    setPatientJson(pretty(demoPayload.patient_context));
    setInventoryJson(pretty(demoPayload.inventory_context));
    setProductJson(pretty(demoPayload.product_context));
    setDenialLetter("");
    setFormError(null);
  }

  function handleSubmit() {
    try {
      const payload = caseRequestSchema.parse({
        query,
        drug_name: drugName,
        payer_name: payerName,
        patient_context: JSON.parse(patientJson),
        inventory_context: JSON.parse(inventoryJson),
        product_context: JSON.parse(productJson),
        denial_letter_text: denialLetter || null
      });
      setFormError(null);
      mutation.mutate(payload);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Check your case JSON fields.");
    }
  }

  return (
    <Card className="overflow-hidden">
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-5">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slateblue">
              Case Analyzer
            </p>
            <h2 className="text-3xl font-semibold text-ink">Run the multi-agent GLP-1 workflow</h2>
            <p className="max-w-2xl text-sm leading-7 text-ink/75">
              The coordinator routes the case across shortage, coverage, and authenticity/compliance agents,
              then returns a pharmacist-reviewable action plan with citations and draft messages.
            </p>
          </div>

          <label className="block text-sm font-medium text-ink">
            Pharmacy case
            <textarea
              className="mt-2 min-h-32 w-full rounded-[1.5rem] border border-ink/10 bg-white px-4 py-3 text-sm leading-6"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm font-medium text-ink">
              Drug name
              <Input className="mt-2" value={drugName} onChange={(event) => setDrugName(event.target.value)} />
            </label>
            <label className="text-sm font-medium text-ink">
              Payer name
              <Input className="mt-2" value={payerName} onChange={(event) => setPayerName(event.target.value)} />
            </label>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <JsonField label="Patient context JSON" value={patientJson} onChange={setPatientJson} />
            <JsonField label="Inventory context JSON" value={inventoryJson} onChange={setInventoryJson} />
            <JsonField label="Product context JSON" value={productJson} onChange={setProductJson} />
          </div>

          <label className="block text-sm font-medium text-ink">
            Denial letter text
            <textarea
              className="mt-2 min-h-24 w-full rounded-[1.5rem] border border-ink/10 bg-white px-4 py-3 text-sm"
              value={denialLetter}
              onChange={(event) => setDenialLetter(event.target.value)}
              placeholder="Paste denial letter excerpts here when available."
            />
          </label>
        </div>

        <div className="rounded-[1.75rem] bg-ink p-6 text-white">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-mint">
            Included modules
          </p>
          <div className="mt-5 space-y-4">
            <ModuleCard
              title="Shortage and substitution"
              detail="Checks local inventory context, shortage evidence, and pharmacist-reviewed substitution workflow."
            />
            <ModuleCard
              title="Coverage and PA"
              detail="Compares payer criteria with patient context, identifies missing evidence, and drafts documentation requests."
            />
            <ModuleCard
              title="Authenticity and compliance"
              detail="Flags suspicious GLP-1 supplier claims, missing identifiers, and unsafe marketing language."
            />
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={handleSubmit} disabled={mutation.isPending} className="bg-coral text-ink hover:bg-mint">
              {mutation.isPending ? "Analyzing..." : "Analyze case"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button variant="secondary" onClick={loadDemo} className="border-white/20 bg-white/10 text-white hover:bg-white/20">
              <RefreshCcw className="mr-2 h-4 w-4" />
              Load demo case
            </Button>
          </div>

          {formError ? (
            <div className="mt-5 flex gap-3 rounded-2xl border border-coral/50 bg-white/10 p-4 text-sm">
              <AlertCircle className="mt-0.5 h-5 w-5 text-coral" />
              <p>{formError}</p>
            </div>
          ) : null}

          <p className="mt-8 text-sm leading-7 text-white/80">
            Pharmacist review required before clinical, dispensing, substitution, or patient-specific action.
          </p>
        </div>
      </div>
    </Card>
  );
}

function JsonField({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-sm font-medium text-ink">
      {label}
      <textarea
        className="mt-2 min-h-64 w-full rounded-[1.5rem] border border-ink/10 bg-white px-4 py-3 font-mono text-xs leading-6"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function ModuleCard({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/10 p-4">
      <p className="font-semibold">{title}</p>
      <p className="mt-2 text-sm leading-6 text-white/80">{detail}</p>
    </div>
  );
}
