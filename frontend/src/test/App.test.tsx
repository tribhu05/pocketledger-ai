import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import App from '../App';
import * as api from '../api';
import { Expense, SystemStatus, DashboardSummary } from '../types';

const mockSystemStatus: SystemStatus = {
  app_name: 'PocketLedger AI',
  version: '1.0.0',
  environment: 'local',
  ollama_connected: true,
  ollama_url: 'http://localhost:11434',
  gemma_model: 'gemma2:2b',
  gemma_available: true,
  ocr_available: true,
  ocr_engine: 'tesseract',
  ocr_binary_path: '/usr/bin/tesseract',
  database_connected: true,
  current_mode: 'gemma2_local',
};

const mockExpense: Expense = {
  id: 'exp-1',
  source_filename: 'starbucks-receipt.png',
  stored_filename: '123_starbucks-receipt.png',
  mime_type: 'image/png',
  file_size_bytes: 12040,
  merchant: 'Starbucks Coffee',
  document_type: 'receipt',
  invoice_number: 'SB-991',
  transaction_date: '2026-10-02',
  raw_date: '10/02/2026',
  currency: 'USD',
  subtotal: 13.50,
  tax: 1.35,
  total: 14.85,
  category: 'Meals & Entertainment',
  payment_method: 'Mastercard 9921',
  description: 'Client coffee meeting',
  status: 'confirmed',
  reconciliation_status: 'reconciled',
  reconciliation_delta: 0.0,
  extraction_mode: 'gemma2:2b',
  warnings: [],
  raw_ocr_text: 'STARBUCKS #102\nTotal: $14.85',
  raw_model_response: '{"total": 14.85}',
  user_edits: {},
  created_at: '2026-10-02T10:00:00Z',
  updated_at: '2026-10-02T10:00:00Z',
};

const mockDashboard: DashboardSummary = {
  total_expenses_by_currency: { USD: 14.85 },
  receipts_count: 1,
  awaiting_review_count: 0,
  confirmed_count: 1,
  rejected_count: 0,
  category_breakdown: [{ category: 'Meals & Entertainment', count: 1, amount: 14.85 }],
  monthly_trend: [{ month: '2026-10', count: 1, amount: 14.85 }],
  recent_transactions: [mockExpense],
};

describe('PocketLedger AI Frontend Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(api, 'fetchSystemStatus').mockResolvedValue(mockSystemStatus);
    vi.spyOn(api, 'fetchDashboard').mockResolvedValue(mockDashboard);
    vi.spyOn(api, 'fetchExpenses').mockResolvedValue([mockExpense]);
  });

  it('renders navbar and displays live on-device Gemma status', async () => {
    render(<App />);

    expect(await screen.findByText('PocketLedger')).toBeInTheDocument();
    const deviceBadges = await screen.findAllByText(/100% On-Device/i);
    expect(deviceBadges.length).toBeGreaterThanOrEqual(1);
  });

  it('renders dashboard with confirmed expense metrics', async () => {
    render(<App />);

    expect(await screen.findByText('Financial Overview')).toBeInTheDocument();
    const categories = await screen.findAllByText('Meals & Entertainment');
    expect(categories.length).toBeGreaterThanOrEqual(1);

    const amounts = await screen.findAllByText('$14.85');
    expect(amounts.length).toBeGreaterThanOrEqual(1);
  });

  it('navigates to ledger and filters by search query', async () => {
    render(<App />);

    const ledgerTabs = await screen.findAllByRole('button', { name: /Ledger/i });
    fireEvent.click(ledgerTabs[0]);

    expect(await screen.findByText('Expense Ledger')).toBeInTheDocument();
    expect(screen.getByText('Starbucks Coffee')).toBeInTheDocument();

    // Type query
    const searchInput = screen.getByPlaceholderText(/Search vendor, description/i);
    fireEvent.change(searchInput, { target: { value: 'Nonexistent' } });

    expect(screen.getByText(/No expense records matching the current filters/i)).toBeInTheDocument();
  });

  it('navigates to reports view and verifies CSV export links', async () => {
    render(<App />);

    const reportsTabs = await screen.findAllByRole('button', { name: /Reports & CSV/i });
    fireEvent.click(reportsTabs[0]);

    expect(await screen.findByText('Reports & Tax Export')).toBeInTheDocument();
    expect(screen.getByText('Download Confirmed Expenses CSV')).toBeInTheDocument();
    expect(screen.getByText('Download Monthly Summary CSV')).toBeInTheDocument();
  });

  it('navigates to pricing and displays honest side hustle experiment', async () => {
    render(<App />);

    const pricingTabs = await screen.findAllByRole('button', { name: /Pricing & Side Hustle/i });
    fireEvent.click(pricingTabs[0]);

    expect(await screen.findByText('Transparent, Honest Pricing')).toBeInTheDocument();
    expect(screen.getByText('Solo Freelancer')).toBeInTheDocument();
    expect(screen.getByText('Freelancer Validation Survey')).toBeInTheDocument();
  });

  it('opens review modal and displays editable financial fields', async () => {
    render(<App />);

    // Click Review on the recent transaction from dashboard
    const reviewButtons = await screen.findAllByRole('button', { name: /Review/i });
    fireEvent.click(reviewButtons[0]);

    expect(await screen.findByText(/Review & Confirm Document/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Starbucks Coffee')).toBeInTheDocument();
    expect(screen.getByDisplayValue('14.85')).toBeInTheDocument();
  });
});
