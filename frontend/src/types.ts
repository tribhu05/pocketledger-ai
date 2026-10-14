export interface Expense {
  id: string;
  source_filename: string;
  stored_filename: string;
  mime_type: string;
  file_size_bytes: number;
  merchant: string | null;
  document_type: string;
  invoice_number: string | null;
  transaction_date: string | null;
  raw_date: string | null;
  currency: string;
  subtotal: number | null;
  tax: number | null;
  total: number | null;
  category: string;
  payment_method: string | null;
  description: string | null;
  status: 'awaiting_review' | 'confirmed' | 'rejected';
  reconciliation_status: 'reconciled' | 'mismatch' | 'unverified';
  reconciliation_delta: number | null;
  extraction_mode: string;
  warnings: string[];
  raw_ocr_text: string | null;
  raw_model_response: string | null;
  user_edits: Record<string, any>;
  created_at: string | null;
  updated_at: string | null;
}

export interface SystemStatus {
  app_name: string;
  version: string;
  environment: string;
  ollama_connected: boolean;
  ollama_url: string;
  gemma_model: string;
  gemma_available: boolean;
  ocr_available: boolean;
  ocr_engine: string;
  ocr_binary_path: string | null;
  database_connected: boolean;
  current_mode: 'gemma2_local' | 'deterministic_fallback' | string;
}

export interface DashboardSummary {
  total_expenses_by_currency: Record<string, number>;
  receipts_count: number;
  awaiting_review_count: number;
  confirmed_count: number;
  rejected_count: number;
  category_breakdown: Array<{ category: string; count: number; amount: number }>;
  monthly_trend: Array<{ month: string; count: number; amount: number }>;
  recent_transactions: Expense[];
}

export interface ReviewUpdateRequest {
  merchant?: string | null;
  document_type?: string;
  invoice_number?: string | null;
  transaction_date?: string | null;
  currency?: string;
  subtotal?: number | null;
  tax?: number | null;
  total?: number | null;
  category?: string;
  payment_method?: string | null;
  description?: string | null;
  status: 'awaiting_review' | 'confirmed' | 'rejected';
}

export interface BenchmarkResult {
  model_name: string;
  gemma_available: boolean;
  corpus_size: number;
  timestamp: string;
  fallback: {
    total_time_ms: number;
    avg_time_ms: number;
    field_accuracy: Record<string, number>;
    cases: any[];
  };
  gemma: {
    total_time_ms?: number;
    avg_time_ms?: number;
    field_accuracy?: Record<string, number>;
    cases?: any[];
    status?: string;
  };
}
