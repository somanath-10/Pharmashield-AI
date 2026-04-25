"use client";

import { AlertCircle } from "lucide-react";
import { Finding } from "@/lib/types";

export function IndiaPharmacyNotice() {
  return (
    <div className="rounded-2xl border border-coral/30 bg-coral/5 p-4 text-sm mt-4">
      <div className="flex gap-2">
        <AlertCircle className="h-4 w-4 text-coral mt-0.5" />
        <p className="font-medium text-coral">India Pharmacy Operations Notice</p>
      </div>
      <p className="mt-1 ml-6 text-coral/80">Pharmacist review required before clinical, dispensing, substitution, or patient-specific action.</p>
    </div>
  );
}

export function PriceCheckPanel({ findings }: { findings: Finding[] }) {
  if (!findings || findings.length === 0) return null;
  return (
    <div className="rounded-xl bg-sand p-4">
      <p className="font-medium">Price & Jan Aushadhi</p>
      <ul className="mt-2 text-sm text-ink/80 list-disc list-inside">
        {findings.map((f, i) => <li key={i}>{f.title || f.detail}</li>)}
      </ul>
    </div>
  );
}

export function CompliancePanel({ findings }: { findings: Finding[] }) {
  if (!findings || findings.length === 0) return null;
  return (
    <div className="rounded-xl border border-coral/20 bg-coral/5 p-4">
      <p className="font-medium text-coral">Prescription Compliance Risk</p>
      <ul className="mt-2 text-sm text-coral/80 list-disc list-inside">
        {findings.map((f, i) => <li key={i}>{f.title || f.detail}</li>)}
      </ul>
    </div>
  );
}

export function NSQAlertPanel({ findings }: { findings: Finding[] }) {
  if (!findings || findings.length === 0) return null;
  return (
    <div className="rounded-xl border border-coral/50 bg-coral/10 p-4">
      <p className="font-bold text-coral">NSQ / Spurious Alert</p>
      <ul className="mt-2 text-sm text-coral/90 list-disc list-inside">
        {findings.map((f, i) => <li key={i}>{f.title || f.detail}</li>)}
      </ul>
    </div>
  );
}
