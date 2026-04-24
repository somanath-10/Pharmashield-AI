import type {
  CaseAnalyzeRequest,
  CaseAnalyzeResponse,
  CaseListItem,
  DashboardSummary,
  IngestResponse
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function analyzeCase(payload: CaseAnalyzeRequest): Promise<CaseAnalyzeResponse> {
  return request<CaseAnalyzeResponse>("/api/cases/analyze", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function fetchCase(caseId: string): Promise<CaseAnalyzeResponse> {
  return request<CaseAnalyzeResponse>(`/api/cases/${caseId}`);
}

export async function fetchCases(): Promise<CaseListItem[]> {
  return request<CaseListItem[]>("/api/cases");
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/api/cases/dashboard/summary");
}

export async function seedDemo(): Promise<IngestResponse> {
  return request<IngestResponse>("/api/ingest/demo", { method: "POST" });
}

export async function ingestPublic(): Promise<IngestResponse> {
  return request<IngestResponse>("/api/ingest/public", { method: "POST" });
}

export async function submitFeedback(payload: Record<string, unknown>) {
  return request<{ status: string; feedback_id: string }>("/api/feedback", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<{
    filename: string;
    content_type: string;
    chunks_indexed: number;
    message: string;
  }>;
}
