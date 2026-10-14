import React, { useState, useMemo } from 'react';
import { 
  FileSpreadsheet, 
  Download, 
  ShieldCheck, 
  AlertCircle, 
  TrendingUp, 
  Calendar,
  CheckCircle,
  FileText
} from 'lucide-react';
import { Expense } from '../types';
import { getExportCsvUrl, getExportSummaryCsvUrl } from '../api';

interface ReportsViewProps {
  expenses: Expense[];
}

export const ReportsView: React.FC<ReportsViewProps> = ({ expenses }) => {
  const [selectedCurrency, setSelectedCurrency] = useState('All');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  // Currencies present
  const availableCurrencies = useMemo(() => {
    const set = new Set<string>();
    expenses.forEach((e) => e.currency && set.add(e.currency));
    return ['All', ...Array.from(set)];
  }, [expenses]);

  // Confirmed expenses
  const confirmed = useMemo(() => {
    return expenses.filter((e) => e.status === 'confirmed');
  }, [expenses]);

  // Aggregated totals segregated strictly by currency
  const currencyTotals = useMemo(() => {
    const totals: Record<string, { count: number; sum: number }> = {};
    confirmed.forEach((e) => {
      if (e.total === null) return;
      const c = e.currency || 'USD';
      if (!totals[c]) totals[c] = { count: 0, sum: 0 };
      totals[c].count += 1;
      totals[c].sum += e.total;
    });
    return totals;
  }, [confirmed]);

  // Grouped by (Month, Category, Currency)
  const monthlyCategorySummary = useMemo(() => {
    const groups: Record<string, { month: string; category: string; currency: string; count: number; total: number }> = {};

    confirmed.forEach((e) => {
      if (e.total === null) return;
      if (selectedCurrency !== 'All' && e.currency !== selectedCurrency) return;

      const rawDate = e.transaction_date || 'Unknown';
      const month = rawDate.length >= 7 && rawDate.includes('-') ? rawDate.slice(0, 7) : 'Unknown';
      const cat = e.category || 'Other';
      const curr = e.currency || 'USD';

      const key = `${month}__${cat}__${curr}`;
      if (!groups[key]) {
        groups[key] = { month, category: cat, currency: curr, count: 0, total: 0 };
      }
      groups[key].count += 1;
      groups[key].total += e.total;
    });

    return Object.values(groups).sort((a, b) => (a.month < b.month ? 1 : -1));
  }, [confirmed, selectedCurrency]);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Reports & Tax Export</h1>
        <p className="text-sm text-slate-500">
          Clean, injection-safe CSV exports designed for freelance tax preparation and accountant review.
        </p>
      </div>

      {/* Export Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Full Ledger CSV */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between space-y-4">
          <div>
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Detailed Expense Ledger CSV</h3>
            <p className="text-xs text-slate-500 mt-1">
              Complete transaction log with merchant names, normalized dates, categories, invoice IDs, payment methods, and math reconciliation status.
            </p>
          </div>

          <div className="pt-2">
            <a
              href={getExportCsvUrl('confirmed', selectedCurrency)}
              download="pocketledger_confirmed_expenses.csv"
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold inline-flex items-center justify-center shadow-xs transition-colors"
            >
              <Download className="w-4 h-4 mr-2 text-emerald-400" />
              Download Confirmed Expenses CSV
            </a>
          </div>
        </div>

        {/* Grouped Summary CSV */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between space-y-4">
          <div>
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Monthly Tax Category Summary</h3>
            <p className="text-xs text-slate-500 mt-1">
              Summarized schedule of expenses grouped by year-month, tax category, and currency. Ideal for quarterly self-employment taxes (Schedule C / VAT).
            </p>
          </div>

          <div className="pt-2">
            <a
              href={getExportSummaryCsvUrl()}
              download="pocketledger_monthly_summary.csv"
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold inline-flex items-center justify-center shadow-xs transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Monthly Summary CSV
            </a>
          </div>
        </div>
      </div>

      {/* Strict Currency Separation Totals */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Total Confirmed Spending by Currency</h3>
            <p className="text-xs text-slate-500">
              PocketLedger enforces strict currency segregation. Multi-currency totals are never combined into arbitrary sums.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {Object.keys(currencyTotals).length > 0 ? (
            Object.entries(currencyTotals).map(([curr, data]) => (
              <div key={curr} className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-xs font-semibold text-slate-500 uppercase">{curr} Total</span>
                <div className="text-xl font-bold text-slate-900 mt-1">
                  {curr === 'USD' ? '$' : curr === 'EUR' ? '€' : curr === 'GBP' ? '£' : `${curr} `}
                  {data.sum.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">{data.count} confirmed receipts</p>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-400 py-4 col-span-3">No confirmed transactions recorded yet.</p>
          )}
        </div>
      </div>

      {/* Monthly Category Schedule Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Monthly Tax Summary Table</h3>
            <p className="text-xs text-slate-500">Breakdown ready for freelance tax reporting</p>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-500 font-medium">Filter Currency:</span>
            <select
              value={selectedCurrency}
              onChange={(e) => setSelectedCurrency(e.target.value)}
              className="px-2.5 py-1 rounded-md border border-slate-200 bg-white text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              {availableCurrencies.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Month (YYYY-MM)</th>
                <th className="px-5 py-3">Expense Category</th>
                <th className="px-5 py-3">Currency</th>
                <th className="px-5 py-3">Receipt Count</th>
                <th className="px-5 py-3 text-right">Total Subtotal</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {monthlyCategorySummary.length > 0 ? (
                monthlyCategorySummary.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50">
                    <td className="px-5 py-3 text-xs font-mono font-semibold text-slate-800">
                      {row.month}
                    </td>
                    <td className="px-5 py-3 text-xs font-medium text-slate-900">
                      {row.category}
                    </td>
                    <td className="px-5 py-3 text-xs font-mono text-slate-500">
                      {row.currency}
                    </td>
                    <td className="px-5 py-3 text-xs text-slate-600">
                      {row.count} document{row.count > 1 ? 's' : ''}
                    </td>
                    <td className="px-5 py-3 text-xs font-mono font-bold text-slate-900 text-right">
                      {row.total.toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-5 py-8 text-center text-xs text-slate-400">
                    No confirmed records matching the selected currency.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CSV Security Notice */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-800">Spreadsheet Security & Formula Injection Defense:</strong>
          <p className="mt-1">
            All CSV exports are sanitized against formula injection. Any fields or descriptions starting with spreadsheet formula triggers (such as <code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">=</code>, <code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">+</code>, <code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">-</code>, <code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">@</code>, or tab characters) are automatically escaped with a leading single quote (<code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">'</code>) to prevent malicious code execution in Microsoft Excel, Google Sheets, and LibreOffice.
          </p>
        </div>
      </div>
    </div>
  );
};
