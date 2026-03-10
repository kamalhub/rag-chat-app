/**
 * API client for the RAG backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ChatResponse {
  answer: string;
  sources: { content: string; source: string }[];
}

export interface StatusResponse {
  status: string;
  num_documents: number;
}

export interface IngestResponse {
  message: string;
  num_chunks: number;
}

export interface ModelOption {
  id: string;
  name: string;
  description: string;
}

export interface ModelsResponse {
  models: ModelOption[];
}

export async function getModels(): Promise<ModelsResponse> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function sendMessage(
  message: string,
  model?: string | null
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(model ? { message, model } : { message }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export async function uploadFile(file: File): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export interface DocumentSummary {
  filename: string;
  num_chunks: number;
  ingested_at: string;
}

export interface DocumentsListResponse {
  documents: DocumentSummary[];
}

export async function getDocuments(): Promise<DocumentsListResponse> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getDocument(filename: string): Promise<unknown> {
  const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`);
  if (!res.ok) {
    if (res.status === 404) throw new Error("Document not found");
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

export interface MortgageApplicationSummary {
  documentID: string;
  label: string;
}

export interface MortgageApplicationsResponse {
  applications: MortgageApplicationSummary[];
}

export async function getMortgageApplications(): Promise<MortgageApplicationsResponse> {
  const res = await fetch(`${API_BASE}/mortgage-applications`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getMortgageApplication(documentID: string): Promise<unknown> {
  const res = await fetch(
    `${API_BASE}/mortgage-applications/${encodeURIComponent(documentID)}`
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Mortgage application not found");
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

export async function getStatus(): Promise<StatusResponse> {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export interface ExportMessage {
  role: string;
  text: string;
  sources?: { content: string; source: string }[];
}

export async function exportChat(messages: ExportMessage[]): Promise<void> {
  const res = await fetch(`${API_BASE}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Export failed" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }

  // Download the PDF blob
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;

  // Extract filename from Content-Disposition header, or use a default
  const disposition = res.headers.get("Content-Disposition");
  const match = disposition?.match(/filename="(.+)"/);
  a.download = match?.[1] ?? "rag_chat_export.pdf";

  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
