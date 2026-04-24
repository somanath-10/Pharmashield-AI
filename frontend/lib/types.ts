export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Citation {
  id: string;
  source_name: string;
  source_url?: string | null;
  document_title?: string | null;
  section_title?: string | null;
  snippet: string;
  source_type: string;
  note?: string | null;
}

export interface Finding {
  title: string;
  detail: string;
  evidence_ids: string[];
}

export interface AgentTraceItem {
  agent_name: string;
  status: string;
  risk_level: RiskLevel;
  findings: Finding[];
  recommended_actions: string[];
  citations: Citation[];
  details: Record<string, unknown>;
}

export interface CaseAnalyzeRequest {
  query: string;
  drug_name?: string | null;
  payer_name?: string | null;
  patient_context: {
    age?: number | null;
    diagnoses: string[];
    labs: Record<string, string>;
    previous_therapies: string[];
    allergies: string[];
  };
  inventory_context: {
    location_id?: string | null;
    quantity_on_hand?: number | null;
    reorder_threshold?: number | null;
    lot_number?: string | null;
  };
  product_context: {
    supplier_name?: string | null;
    claim_text?: string | null;
    ndc?: string | null;
    lot_number?: string | null;
    manufacturer?: string | null;
  };
  denial_letter_text?: string | null;
}

export interface CaseAnalyzeResponse {
  case_id: string;
  risk_level: RiskLevel;
  intent: string;
  detected_intents: string[];
  summary: string;
  action_plan: string[];
  agent_outputs: Record<string, Record<string, unknown>>;
  agent_trace: AgentTraceItem[];
  citations: Citation[];
  draft_prescriber_message: string;
  draft_patient_message: string;
  pharmacist_review_required: boolean;
  memory_notes: Record<string, unknown>[];
  created_at?: string;
  updated_at?: string;
}

export interface CaseListItem {
  id: string;
  case_type: string;
  status: string;
  drug_name?: string | null;
  payer_name?: string | null;
  final_risk_level?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  total_cases: number;
  risk_counts: Record<string, number>;
  pa_missing_evidence_counts: Record<string, number>;
  shortage_cases: number;
  supplier_risk_cases: number;
  feedback_acceptance_rate: number;
}

export interface IngestResponse {
  status: string;
  message: string;
  records_created: number;
}
