"use client";

import { useMutation } from "@tanstack/react-query";
import { AlertCircle, ArrowRight, RefreshCcw, FileSearch, Info } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { analyzeCase } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const demoPayload = {
  query: "Semaglutide prescribed. Stock not available. Patient found cheap generic Ozempic online without prescription. Patient wants cheaper legal option.",
  drug_name: "semaglutide",
  brand_name: "Ozempic",
  location_state: "Telangana",
  prescription_context: {
    prescription_available: true,
    doctor_name: "Dr. Demo",
    prescription_date: "2026-04-20"
  },
  inventory_context: {
    quantity_on_hand: 0,
    same_molecule_available: false
  },
  patient_context: {
    condition: "type 2 diabetes",
    budget_sensitive: true,
    scheme_context: {
      pmjay_eligible: null,
      hospitalized: false,
      corporate_opd: null
    }
  },
  product_context: {
    seller_type: "online",
    seller_name: "Cheap Semaglutide India",
    claim_text: "generic Ozempic without prescription",
    batch_number: null,
    manufacturer: null,
    license_number: null,
    mrp: null,
    expiry_date: null
  }
};

function pretty(value: unknown) {
  return JSON.stringify(value, null, 2);
}

export function CaseInput() {
  const router = useRouter();
  const [query, setQuery] = useState(demoPayload.query);
  const [drugName, setDrugName] = useState(demoPayload.drug_name);
  const [brandName, setBrandName] = useState(demoPayload.brand_name);
  const [locationState, setLocationState] = useState(demoPayload.location_state);
  
  const [prescriptionJson, setPrescriptionJson] = useState(pretty(demoPayload.prescription_context));
  const [patientJson, setPatientJson] = useState(pretty(demoPayload.patient_context));
  const [inventoryJson, setInventoryJson] = useState(pretty(demoPayload.inventory_context));
  const [productJson, setProductJson] = useState(pretty(demoPayload.product_context));
  
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
    setBrandName(demoPayload.brand_name);
    setLocationState(demoPayload.location_state);
    setPrescriptionJson(pretty(demoPayload.prescription_context));
    setPatientJson(pretty(demoPayload.patient_context));
    setInventoryJson(pretty(demoPayload.inventory_context));
    setProductJson(pretty(demoPayload.product_context));
    setFormError(null);
  }

  function handleSubmit() {
    try {
      const payload = {
        query,
        drug_name: drugName,
        brand_name: brandName,
        location_state: locationState,
        prescription_context: JSON.parse(prescriptionJson),
        patient_context: JSON.parse(patientJson),
        inventory_context: JSON.parse(inventoryJson),
        product_context: JSON.parse(productJson)
      };
      setFormError(null);
      mutation.mutate(payload as any);
    } catch (error) {
       setFormError("Check your JSON field syntax (likely a missing comma or bracket).");
    }
  }

  return (
    <div className="glass-panel rounded-[3rem] overflow-hidden border-white/5 p-8 md:p-12">
      <div className="grid gap-12 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-8">
          <div className="flex items-center gap-4">
               <div className="h-14 w-14 rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                    <FileSearch className="w-7 h-7" />
               </div>
               <div>
                    <h3 className="text-3xl font-bold text-white">Manual Entry Analyzer</h3>
                    <p className="text-slate-500 font-medium">Define granular context for the AI agents.</p>
               </div>
          </div>

          <div className="space-y-3">
               <label className="text-sm font-bold text-slate-300 uppercase tracking-widest ml-1">
               Query Description
               </label>
               <textarea
               className="min-h-32 w-full rounded-2xl border border-white/10 bg-slate-950/50 px-6 py-4 text-base focus:border-sky-500 focus:ring-1 focus:ring-sky-500/30 transition-all text-white placeholder:text-slate-700"
               value={query}
               onChange={(event) => setQuery(event.target.value)}
               placeholder="Enter the pharmacy situation or query here..."
               />
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <InputField label="Drug Molecule" value={drugName} onChange={setDrugName} placeholder="semaglutide" />
            <InputField label="Brand Name" value={brandName} onChange={setBrandName} placeholder="Ozempic" />
            <InputField label="Location State" value={locationState} onChange={setLocationState} placeholder="Maharashtra" />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <JsonField label="Prescription Context" value={prescriptionJson} onChange={setPrescriptionJson} />
            <JsonField label="Inventory Context" value={inventoryJson} onChange={setInventoryJson} />
            <JsonField label="Patient Context" value={patientJson} onChange={setPatientJson} />
            <JsonField label="Product Context" value={productJson} onChange={setProductJson} />
          </div>
        </div>

        <div className="space-y-8 bg-slate-950/40 rounded-[2.5rem] p-8 border border-white/5 self-start sticky top-12">
          <div>
               <p className="text-xs font-bold uppercase tracking-widest text-sky-400 mb-4 flex items-center gap-2">
                    <Zap className="w-3 h-3" />
                    Agent Orchestration
               </p>
               <div className="space-y-5">
                    <ModuleCard title="Affordability" detail="MRP & Jan Aushadhi Kendra evaluation."/>
                    <ModuleCard title="Supply Chain" detail="CDSCO Alerts & Batch verification."/>
                    <ModuleCard title="Legality" detail="Schedule H/X Prescription compliance."/>
               </div>
          </div>

          <div className="pt-6 border-t border-white/5 space-y-4">
            <button 
               onClick={handleSubmit} 
               disabled={mutation.isPending} 
               className="w-full py-5 btn-primary text-slate-950 font-bold rounded-2xl flex items-center justify-center gap-3 active:scale-95 disabled:opacity-50"
            >
              {mutation.isPending ? "Executing Agent Pipeline..." : "Initialize Analysis"}
              <ArrowRight className="w-5 h-5" />
            </button>
            <button 
               onClick={loadDemo} 
               className="w-full py-4 bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold rounded-2xl border border-white/5 transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCcw className="w-4 h-4" />
              Reset to Demo Params
            </button>
          </div>

          {formError && (
            <div className="flex gap-3 rounded-2xl border border-rose-500/20 bg-rose-500/5 p-5 text-sm text-rose-300">
              <AlertCircle className="shrink-0 h-5 w-5" />
              <p>{formError}</p>
            </div>
          )}

          <div className="flex gap-3 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 p-5 text-xs leading-relaxed text-indigo-300/80">
            <Info className="shrink-0 h-4 w-4" />
            <p>Pharmacist review required before clinical, dispensing, or patient-specific action.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function InputField({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (v: string) => void, placeholder: string }) {
     return (
          <div className="space-y-2">
               <label className="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">
                    {label}
               </label>
               <Input 
                    className="h-14 rounded-xl border border-white/10 bg-slate-950/50 px-5 text-white focus:border-sky-500 transition-all font-medium" 
                    value={value} 
                    onChange={(event) => onChange(event.target.value)} 
                    placeholder={placeholder}
               />
          </div>
     )
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
    <div className="space-y-2">
      <label className="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">
        {label}
      </label>
      <textarea
        className="min-h-48 w-full rounded-2xl border border-white/10 bg-slate-950/50 px-5 py-4 font-mono text-[11px] leading-relaxed text-sky-300 focus:border-sky-500 transition-all"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

function ModuleCard({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="flex gap-4">
         <div className="mt-1 h-2 w-2 rounded-full bg-sky-500 shadow-lg shadow-sky-500/50" />
         <div>
               <p className="font-bold text-white text-sm">{title}</p>
               <p className="text-slate-500 text-xs mt-1 leading-relaxed">{detail}</p>
         </div>
    </div>
  );
}

const Zap = ({ className }: { className?: string }) => (
     <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" ><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
)
