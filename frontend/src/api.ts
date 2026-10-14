import { Expense, SystemStatus, DashboardSummary, ReviewUpdateRequest, BenchmarkResult } from './types';

const API_BASE = '/api';

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error(`Status check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDashboard(): Promise<DashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error(`Failed to load dashboard: ${res.statusText}`);
  return res.json();
}

export async function fetchExpenses(params?: {
  search?: string;
  status?: string;
  category?: string;
  currency?: string;
  sort_by?: string;
  order?: string;
}): Promise<Expense[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.status && params.status !== 'all') query.set('status', params.status);
  if (params?.category && params.category !== 'all') query.set('category', params.category);
  if (params?.currency && params.currency !== 'all') query.set('currency', params.currency);
  if (params?.sort_by) query.set('sort_by', params.sort_by);
  if (params?.order) query.set('order', params.order);

  const res = await fetch(`${API_BASE}/documents?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  return res.json();
}

export async function fetchExpense(id: string): Promise<Expense> {
  const res = await fetch(`${API_BASE}/documents/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch document ${id}: ${res.statusText}`);
  return res.json();
}

export async function uploadDocuments(files: File[]): Promise<Expense[]> {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: ${res.statusText}`);
  }
  return res.json();
}

export async function uploadRawText(title: string, rawText: string): Promise<Expense> {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('raw_text', rawText);
  const res = await fetch(`${API_BASE}/documents/upload-raw-text`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Text processing failed: ${res.statusText}`);
  }
  return res.json();
}

export async function updateExpenseReview(id: string, data: ReviewUpdateRequest): Promise<Expense> {
  const res = await fetch(`${API_BASE}/documents/${id}/review`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Review update failed: ${res.statusText}`);
  return res.json();
}

export async function deleteExpense(id: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/documents/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Delete failed: ${res.statusText}`);
  return res.json();
}

export async function retryExtraction(id: string): Promise<Expense> {
  const res = await fetch(`${API_BASE}/documents/${id}/retry`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Retry extraction failed: ${res.statusText}`);
  return res.json();
}

export async function resetAllData(): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/reset-data`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Reset failed: ${res.statusText}`);
  return res.json();
}

export async function seedDemoWorkspace(): Promise<{ success: boolean; count: number; message: string }> {
  const res = await fetch(`${API_BASE}/demo/seed`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Seeding demo failed: ${res.statusText}`);
  return res.json();
}

export async function fetchBenchmark(): Promise<BenchmarkResult> {
  const res = await fetch(`${API_BASE}/benchmark`);
  if (!res.ok) throw new Error(`Benchmark failed: ${res.statusText}`);
  return res.json();
}

export function getDocumentFileUrl(id: string): string {
  return `${API_BASE}/documents/${id}/file`;
}

export function getExportCsvUrl(status?: string, currency?: string): string {
  const query = new URLSearchParams();
  if (status && status !== 'all') query.set('status', status);
  if (currency && currency !== 'all') query.set('currency', currency);
  return `${API_BASE}/export/csv?${query.toString()}`;
}

export function getExportSummaryCsvUrl(): string {
  return `${API_BASE}/export/summary-csv`;
}
