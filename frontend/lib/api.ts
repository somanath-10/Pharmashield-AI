/**
 * Phase 3 API client — all calls go through Next.js /api rewrite proxy to http://localhost:8000
 */

const API = "";  // Empty string = same origin, proxied by next.config.js rewrites

function getAuthToken() {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(/(^| )access_token=([^;]+)/);
  return match ? match[2] : null;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> ?? {}),
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API}${path}`, {
    ...init,
    headers,
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
  
  const token = getAuthToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`/api/cases/${caseId}/documents`, { 
    method: "POST", 
    body: formData, 
    headers,
    cache: "no-store" 
  });
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
// --- Patient Phase 2 & 7 Endpoints ---

export interface PatientDashboard {
  active_cases: number;
  adr_reports: number;
  adherence_status: string;
}

export async function getPatientDashboard(): Promise<PatientDashboard> {
  return req<PatientDashboard>('/api/patient/dashboard');
}

export async function getPatientCases(): Promise<any[]> {
  return req<any[]>('/api/patient/cases');
}

export async function reportSideEffect(data: {
  case_id: string;
  medicine_name: string;
  batch_number?: string;
  reaction: string;
  severity: string;
  timeline: string;
  patient_age_range?: string;
}): Promise<any> {
  return req<any>('/api/patient/side-effect-report', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAffordability(caseId: string): Promise<any> {
  return req<any>(`/api/patient/affordability/${caseId}`);
}

// --- Pharmacist Phase 2 & 7 Endpoints ---

export async function getPharmacistDashboard(): Promise<any> {
  return req<any>('/api/pharmacist/dashboard');
}

export async function getPharmacistReviewQueue(): Promise<any[]> {
  return req<any[]>('/api/pharmacist/review-queue');
}

export async function performBatchCheck(data: {
  case_id: string; medicine_name: string; batch_number: string;
  expiry_date?: string; manufacturer?: string; supplier?: string;
}): Promise<any> {
  return req<any>('/api/pharmacist/batch-check', { method: 'POST', body: JSON.stringify(data) });
}

export async function performPriceCheck(data: {
  case_id: string; medicine_name: string; mrp: number; charged_price: number;
}): Promise<any> {
  return req<any>('/api/pharmacist/price-check', { method: 'POST', body: JSON.stringify(data) });
}

export async function performSubstitutionCheck(data: {
  case_id: string; prescribed_medicine: string; substituted_medicine: string;
}): Promise<any> {
  return req<any>('/api/pharmacist/substitution-check', { method: 'POST', body: JSON.stringify(data) });
}

export async function createPharmacistADRDraft(data: {
  case_id: string; medicine_name: string; reaction: string; severity: string; timeline: string;
  patient_age_range?: string; batch_number?: string;
}): Promise<any> {
  return req<any>('/api/pharmacist/adr-draft', { method: 'POST', body: JSON.stringify(data) });
}

export async function submitPharmacistReview(caseId: string, data: { action_taken: string; notes: string; }): Promise<any> {
  return req<any>(`/api/pharmacist/reviews/${caseId}`, { method: 'PATCH', body: JSON.stringify(data) });
}

// --- Doctor Phase 2 & 7 Endpoints ---

export async function getDoctorDashboard(): Promise<any> {
  return req<any>('/api/doctor/dashboard');
}

export async function getDoctorPatients(): Promise<any[]> {
  return req<any[]>('/api/doctor/patients');
}

export async function getDoctorADRReviews(): Promise<any[]> {
  return req<any[]>('/api/doctor/adr-reviews');
}

export async function reviewDoctorADR(adrId: string, data: { action: string; notes: string }): Promise<any> {
  return req<any>(`/api/doctor/adr-review/${adrId}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export async function generateDoctorPrescription(data: { patient_name: string; medicines: string[]; notes: string }): Promise<any> {
  return req<any>('/api/doctor/prescription-verification', { method: 'POST', body: JSON.stringify(data) });
}

// --- Admin Phase 2 & 7 Endpoints ---

export async function getAdminAnalytics(): Promise<any> {
  return req<any>('/api/admin/analytics');
}

export async function getAdminAuditLogs(limit: number = 50): Promise<any> {
  return req<any>(`/api/admin/audit-logs?limit=${limit}`);
}
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

// ─── Admin Extended Endpoints ─────────────────────────────────────────────────

export const getAdminRiskQueues = () => req<any[]>('/api/admin/risk-queues');
export const getAdminDataSources = () => req<any[]>('/api/admin/data-sources');
export const getAdminModelQuality = () => req<any>('/api/admin/model-quality');
export const getAdminBatchAnalytics = () => req<any>('/api/admin/analytics/batches');
export const getAdminSellerAnalytics = () => req<any>('/api/admin/analytics/sellers');
export const getAdminPriceAnalytics = () => req<any>('/api/admin/analytics/prices');
export const getAdminADRMonitoring = () => req<any[]>('/api/admin/adr-monitoring');

// ─── Pharmacist Dispensing Decision ──────────────────────────────────────────

export async function recordDispensingDecision(data: {
  case_id?: string;
  medicine_name: string;
  dispensing_status: string;
  notes?: string;
}): Promise<any> {
  return req<any>('/api/pharmacist/dispensing-decision', { method: 'POST', body: JSON.stringify(data) });
}

export async function getDispensingStatuses(): Promise<{ status: string; description: string }[]> {
  return req('/api/pharmacist/dispensing-statuses');
}

// ─── Doctor Care Team Links ────────────────────────────────────────────────────

export async function createCareTeamLink(patientId: string): Promise<any> {
  return req('/api/doctor/care-team-links', { method: 'POST', body: JSON.stringify({ patient_id: patientId }) });
}

export async function getCareTeamLinks(): Promise<any[]> {
  return req('/api/doctor/care-team-links');
}

export async function revokeCareTeamLink(patientId: string): Promise<any> {
  return req(`/api/doctor/care-team-links/${patientId}`, { method: 'DELETE' });
}
