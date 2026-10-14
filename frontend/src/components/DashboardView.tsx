import React from 'react';
import { 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  Receipt, 
  FileText, 
  ArrowRight, 
  AlertCircle,
  Database,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { DashboardSummary, Expense } from '../types';

interface DashboardViewProps {
  summary: DashboardSummary | null;
  onNavigateTab: (tab: string, filter?: string) => void;
  onSelectExpenseForReview: (expense: Expense) => void;
  onSeedDemo: () => Promise<void>;
  loading: boolean;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  summary,
  onNavigateTab,
  onSelectExpenseForReview,
  onSeedDemo,
  loading,
}) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center space-y-3 text-slate-500">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium">Loading ledger data...</p>
        </div>
      </div>
    );
  }

  const currencies = Object.keys(summary?.total_expenses_by_currency || {});
  const isEmpty = (summary?.receipts_count || 0) === 0;

  if (isEmpty) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-8 sm:p-12 text-center shadow-sm">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto text-emerald-600 mb-6">
            <Receipt className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Welcome to PocketLedger AI</h2>
          <p className="text-slate-600 max-w-lg mx-auto mb-8">
            Your private expense assistant. Drop messy receipt images or invoice PDFs to automatically extract vendor names, line totals, taxes, and dates using local Gemma open-weight AI.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => onNavigateTab('inbox')}
              className="w-full sm:w-auto px-6 py-3 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition-colors flex items-center justify-center shadow-sm"
            >
              <Receipt className="w-4 h-4 mr-2" />
              Upload Receipts or PDFs
            </button>
            <button
              onClick={onSeedDemo}
              className="w-full sm:w-auto px-6 py-3 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 font-medium hover:bg-emerald-100 transition-colors flex items-center justify-center"
            >
              <Sparkles className="w-4 h-4 mr-2 text-emerald-600" />
              Load Synthetic Demo Workspace
            </button>
          </div>

          <div className="mt-12 pt-8 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <ShieldCheck className="w-5 h-5 text-emerald-600 mb-2" />
              <h4 className="font-semibold text-slate-900 text-sm mb-1">100% On-Device Privacy</h4>
              <p className="text-xs text-slate-500">
                Documents stay strictly on your local machine. No external cloud AI APIs see your financial data.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <TrendingUp className="w-5 h-5 text-indigo-600 mb-2" />
              <h4 className="font-semibold text-slate-900 text-sm mb-1">Deterministic Math Check</h4>
              <p className="text-xs text-slate-500">
                Guaranteed math verification: flags mismatching subtotals and taxes before you save.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <Database className="w-5 h-5 text-amber-600 mb-2" />
              <h4 className="font-semibold text-slate-900 text-sm mb-1">Full Audit History</h4>
              <p className="text-xs text-slate-500">
                Every field change and raw model output is preserved for accurate, reviewable accounting.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Top Banner / Summary Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Financial Overview</h1>
          <p className="text-sm text-slate-500">
            Summary of confirmed freelance expenses, review backlog, and monthly trends.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigateTab('inbox')}
            className="px-4 py-2 rounded-lg bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition-colors shadow-sm flex items-center"
          >
            <Receipt className="w-4 h-4 mr-2" />
            Add Receipts
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Spend */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Confirmed Spend</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            {currencies.length > 0 ? (
              <div className="space-y-1">
                {currencies.map((c) => (
                  <div key={c} className="flex items-baseline justify-between">
                    <span className="text-xl font-bold text-slate-900">
                      {c === 'USD' ? '$' : c === 'EUR' ? '€' : c === 'GBP' ? '£' : `${c} `}
                      {summary?.total_expenses_by_currency[c].toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                    <span className="text-xs font-semibold text-slate-400">{c}</span>
                  </div>
                ))}
              </div>
            ) : (
              <span className="text-xl font-bold text-slate-900">$0.00</span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-2">Segregated by currency (never merged)</p>
        </div>

        {/* Total Documents */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Processed Records</span>
            <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{summary?.receipts_count || 0}</span>
            <span className="text-xs text-slate-500 font-medium">total documents</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Stored securely in local SQLite</p>
        </div>

        {/* Awaiting Review */}
        <div 
          onClick={() => (summary?.awaiting_review_count || 0) > 0 && onNavigateTab('ledger', 'awaiting_review')}
          className={`bg-white border rounded-xl p-5 shadow-xs transition-all ${
            (summary?.awaiting_review_count || 0) > 0
              ? 'border-amber-300 hover:border-amber-400 cursor-pointer bg-amber-50/20'
              : 'border-slate-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Needs Review</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{summary?.awaiting_review_count || 0}</span>
            {(summary?.awaiting_review_count || 0) > 0 && (
              <span className="text-xs font-semibold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full flex items-center">
                Action required <ArrowRight className="w-3 h-3 ml-1" />
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-2">Uncertain or mismatched totals</p>
        </div>

        {/* Confirmed Records */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Confirmed Records</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{summary?.confirmed_count || 0}</span>
            <span className="text-xs font-medium text-emerald-600">Verified by user</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Ready for CSV export & taxes</p>
        </div>
      </div>

      {/* Charts & Breakdown Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown (2 cols) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-base font-semibold text-slate-900">Expenses by Category</h3>
              <p className="text-xs text-slate-500">Confirmed spending categorized for freelancer tax deductions</p>
            </div>
          </div>

          <div className="space-y-4">
            {summary?.category_breakdown && summary.category_breakdown.length > 0 ? (
              summary.category_breakdown.map((item) => {
                const maxAmount = Math.max(...summary.category_breakdown.map((x) => x.amount), 1);
                const pct = Math.round((item.amount / maxAmount) * 100);
                return (
                  <div key={item.category} className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-slate-700">{item.category}</span>
                      <div className="space-x-2">
                        <span className="text-slate-400">{item.count} items</span>
                        <span className="font-semibold text-slate-900">${item.amount.toFixed(2)}</span>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-xs text-slate-400 text-center py-6">No confirmed expenses yet.</p>
            )}
          </div>
        </div>

        {/* Monthly Trend (1 col) */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <h3 className="text-base font-semibold text-slate-900 mb-1">Monthly Spending</h3>
          <p className="text-xs text-slate-500 mb-5">Historical expense volume</p>

          <div className="space-y-3">
            {summary?.monthly_trend && summary.monthly_trend.length > 0 ? (
              summary.monthly_trend.map((m) => (
                <div key={m.month} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <div>
                    <span className="text-xs font-semibold text-slate-800">{m.month}</span>
                    <p className="text-[10px] text-slate-400">{m.count} confirmed receipts</p>
                  </div>
                  <span className="text-sm font-bold text-slate-900">${m.amount.toFixed(2)}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 text-center py-6">No monthly history yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Recent Receipts</h3>
            <p className="text-xs text-slate-500">Latest imported financial records</p>
          </div>
          <button
            onClick={() => onNavigateTab('ledger')}
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center"
          >
            View all records <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Merchant</th>
                <th className="px-5 py-3">Category</th>
                <th className="px-5 py-3">Reconciliation</th>
                <th className="px-5 py-3">Total</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {summary?.recent_transactions && summary.recent_transactions.length > 0 ? (
                summary.recent_transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs text-slate-500 font-mono">
                      {tx.transaction_date || 'Undated'}
                    </td>
                    <td className="px-5 py-3.5 font-medium text-slate-900">
                      {tx.merchant || <span className="text-slate-400 italic">Unknown Vendor</span>}
                    </td>
                    <td className="px-5 py-3.5 text-xs text-slate-600">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {tx.category}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      {tx.reconciliation_status === 'reconciled' ? (
                        <span className="inline-flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <CheckCircle className="w-3 h-3 mr-1 text-emerald-500" /> Matched
                        </span>
                      ) : tx.reconciliation_status === 'mismatch' ? (
                        <span className="inline-flex items-center text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                          <AlertCircle className="w-3 h-3 mr-1 text-amber-500" /> Discrepancy
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">Unverified</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 font-semibold text-slate-900 whitespace-nowrap">
                      {tx.currency} {tx.total !== null ? tx.total.toFixed(2) : '--'}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${
                        tx.status === 'confirmed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : tx.status === 'awaiting_review'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}>
                        {tx.status === 'awaiting_review' ? 'Needs Review' : tx.status}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right whitespace-nowrap">
                      <button
                        onClick={() => onSelectExpenseForReview(tx)}
                        className="text-xs font-medium px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 transition-colors"
                      >
                        Review
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center text-xs text-slate-400">
                    No transactions to display.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
