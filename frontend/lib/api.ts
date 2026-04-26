/**
 * Phase 3 API client — all calls go through Next.js /api rewrite proxy to http://localhost:8000
 */

const API = "";  // Empty string = same origin, proxied by next.config.js rewrites

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ─── Cases ───────────────────────────────────────────────────────────────────

export interface CreateCasePayload {
  role: "PATIENT" | "PHARMACIST" | "DOCTOR" | "ADMIN";
  case_type: string;
  title: string;
  query: string;
}

export interface CaseRecord {
  case_id: string;
  role: string;
  case_type: string;
  title: string;
  query: string;
  status: string;
  risk_level: string;
}

export async function createCase(payload: CreateCasePayload): Promise<CaseRecord> {
  return req<CaseRecord>("/api/cases", { method: "POST", body: JSON.stringify(payload) });
}

export async function listCases(): Promise<CaseRecord[]> {
  return req<CaseRecord[]>("/api/cases");
}

export async function getCase(caseId: string): Promise<CaseRecord> {
  return req<CaseRecord>(`/api/cases/${caseId}`);
}

// ─── Documents ───────────────────────────────────────────────────────────────

export async function uploadDocument(caseId: string, file: File): Promise<{
  document_id: string;
  status: string;
  document_type: string;
  chunks_created: number;
}> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`/api/cases/${caseId}/documents`, { method: "POST", body: formData, cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ─── Analyze ─────────────────────────────────────────────────────────────────

export interface AnalyzeContext {
  drug_name?: string;
  composition?: string;
  mrp?: number;
  budget_sensitive?: boolean;
  prescription_available?: boolean;
  quantity_on_hand?: number;
  batch_number?: string;
  manufacturer?: string;
  seller_type?: string;
  claim_text?: string;
  scheme_name?: string;
  purchase_context?: string;
  hospitalized?: boolean;
  location_id?: string;
}

export interface AnalyzeResult {
  case_id: string;
  role: string;
  risk_level: string;
  status: string;
  agents_run: string[];
  answer: Record<string, unknown>;
  intel_findings: string[];
  action_plan: string[];
  citations: Citation[];
  mandatory_disclaimer: string;
}

export async function analyzeCase(
  caseId: string,
  question?: string,
  context?: AnalyzeContext
): Promise<AnalyzeResult> {
  const body: Record<string, unknown> = {};
  if (question) body.question = question;
  if (context) body.context = context;
  return req<AnalyzeResult>(`/api/cases/${caseId}/analyze`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ─── Intelligence ─────────────────────────────────────────────────────────────

export async function checkPrice(payload: {
  drug_name: string;
  composition?: string;
  mrp?: number;
  patient_budget_sensitive?: boolean;
}) {
  return req("/api/intelligence/price-check", { method: "POST", body: JSON.stringify(payload) });
}

export async function checkNSQ(payload: {
  drug_name: string;
  manufacturer?: string;
  batch_number?: string;
  brand_name?: string;
}) {
  return req("/api/intelligence/nsq-check", { method: "POST", body: JSON.stringify(payload) });
}

export async function checkSchedule(payload: {
  medicine_name: string;
  prescription_available: boolean;
  claim_text?: string;
}) {
  return req("/api/intelligence/schedule-check", { method: "POST", body: JSON.stringify(payload) });
}

export async function checkSellerRisk(payload: {
  seller_type?: string;
  seller_name?: string;
  claim_text?: string;
  license_number?: string;
}) {
  return req("/api/intelligence/seller-risk-check", { method: "POST", body: JSON.stringify(payload) });
}

export async function checkScheme(payload: {
  scheme_name?: string;
  hospitalized?: boolean;
  purchase_context?: string;
}) {
  return req("/api/intelligence/scheme-check", { method: "POST", body: JSON.stringify(payload) });
}

export async function searchJanAushadhi(payload: {
  drug_name: string;
  patient_budget_sensitive?: boolean;
}) {
  return req("/api/intelligence/janaushadhi-search", { method: "POST", body: JSON.stringify(payload) });
}

// ─── Feedback ────────────────────────────────────────────────────────────────

export async function submitFeedback(caseId: string, payload: {
  rating: number;
  feedback_text: string;
  correction_text?: string;
}) {
  return req<{ feedback_id: string; status: string }>(
    `/api/cases/${caseId}/feedback`,
    { method: "POST", body: JSON.stringify(payload) }
  );
}

// ─── Admin Analytics ─────────────────────────────────────────────────────────

export interface AdminAnalytics {
  total_cases: number;
  patient_cases: number;
  doctor_cases: number;
  pharmacist_cases: number;
  admin_cases: number;
  high_risk_cases: number;
  medium_risk_cases: number;
  nsq_matches: number;
  online_seller_risk_cases: number;
  prescription_compliance_warnings: number;
  affordability_requests: number;
  agent_run_breakdown: Record<string, number>;
  average_feedback_rating: number | null;
  recent_audit_logs: AuditLogEntry[];
}

export interface AuditLogEntry {
  id: string;
  user_id: string;
  role: string;
  action: string;
  entity_type: string;
  case_id?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export async function fetchAdminAnalytics(): Promise<AdminAnalytics> {
  return req<AdminAnalytics>("/api/admin/analytics");
}

export async function fetchAuditLogs(limit = 20): Promise<{ count: number; logs: AuditLogEntry[] }> {
  return req(`/api/admin/audit-logs?limit=${limit}`);
}

// ─── Shared types ─────────────────────────────────────────────────────────────

export interface Citation {
  document_name: string;
  page_number?: number;
  source_snippet: string;
  source?: string;
}
