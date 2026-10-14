import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  Trash2, 
  Edit3, 
  CheckCircle, 
  AlertCircle, 
  ArrowUpDown, 
  Calendar, 
  FileText, 
  Download,
  AlertTriangle,
  RotateCcw
} from 'lucide-react';
import { Expense } from '../types';
import { deleteExpense, getExportCsvUrl } from '../api';

const FREELANCE_CATEGORIES = [
  'All',
  'Software & SaaS',
  'Office Supplies',
  'Hardware & Equipment',
  'Travel & Lodging',
  'Meals & Entertainment',
  'Professional Services',
  'Utilities',
  'Other',
];

interface ExpenseLedgerProps {
  expenses: Expense[];
  onSelectExpenseForReview: (expense: Expense) => void;
  onRefreshData: () => Promise<void>;
  initialStatusFilter?: string;
}

export const ExpenseLedger: React.FC<ExpenseLedgerProps> = ({
  expenses,
  onSelectExpenseForReview,
  onRefreshData,
  initialStatusFilter = 'all',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState(initialStatusFilter);
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [currencyFilter, setCurrencyFilter] = useState('All');
  const [sortBy, setSortBy] = useState<'date' | 'total' | 'merchant'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this expense and its local document file?')) {
      return;
    }
    setDeletingId(id);
    try {
      await deleteExpense(id);
      await onRefreshData();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  // Unique currencies present in dataset
  const availableCurrencies = useMemo(() => {
    const set = new Set<string>();
    expenses.forEach((e) => e.currency && set.add(e.currency));
    return ['All', ...Array.from(set)];
  }, [expenses]);

  // Filter & Sort
  const filteredExpenses = useMemo(() => {
    return expenses
      .filter((item) => {
        // Search
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchMerchant = item.merchant?.toLowerCase().includes(q) || false;
          const matchDesc = item.description?.toLowerCase().includes(q) || false;
          const matchInv = item.invoice_number?.toLowerCase().includes(q) || false;
          const matchFile = item.source_filename.toLowerCase().includes(q);
          if (!matchMerchant && !matchDesc && !matchInv && !matchFile) return false;
        }

        // Status
        if (statusFilter !== 'all' && item.status !== statusFilter) return false;

        // Category
        if (categoryFilter !== 'All' && item.category !== categoryFilter) return false;

        // Currency
        if (currencyFilter !== 'All' && item.currency !== currencyFilter) return false;

        return true;
      })
      .sort((a, b) => {
        let valA: any = a.transaction_date || '';
        let valB: any = b.transaction_date || '';

        if (sortBy === 'total') {
          valA = a.total ?? -999999;
          valB = b.total ?? -999999;
        } else if (sortBy === 'merchant') {
          valA = (a.merchant || '').toLowerCase();
          valB = (b.merchant || '').toLowerCase();
        }

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
  }, [expenses, searchQuery, statusFilter, categoryFilter, currencyFilter, sortBy, sortOrder]);

  // Paginated records
  const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage) || 1;
  const paginatedExpenses = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredExpenses.slice(start, start + itemsPerPage);
  }, [filteredExpenses, currentPage]);

  const toggleSort = (column: 'date' | 'total' | 'merchant') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
    setCategoryFilter('All');
    setCurrencyFilter('All');
    setCurrentPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Expense Ledger</h1>
          <p className="text-sm text-slate-500">
            Search, filter, verify, and export all recorded freelance expenses.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <a
            href={getExportCsvUrl(statusFilter, currencyFilter)}
            download="pocketledger_expenses.csv"
            className="px-3.5 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-colors flex items-center shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" />
            Export Filtered CSV
          </a>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
          {/* Search */}
          <div className="lg:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Search vendor, description, invoice #..."
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800 text-xs"
            />
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800 bg-white"
            >
              <option value="all">All Statuses</option>
              <option value="awaiting_review">Awaiting Review</option>
              <option value="confirmed">Confirmed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800 bg-white"
            >
              {FREELANCE_CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c === 'All' ? 'All Categories' : c}
                </option>
              ))}
            </select>
          </div>

          {/* Currency Filter */}
          <div>
            <select
              value={currencyFilter}
              onChange={(e) => {
                setCurrencyFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800 bg-white"
            >
              {availableCurrencies.map((c) => (
                <option key={c} value={c}>
                  {c === 'All' ? 'All Currencies' : c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Active Filter Chips & Reset */}
        {(searchQuery || statusFilter !== 'all' || categoryFilter !== 'All' || currencyFilter !== 'All') && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
            <span className="text-slate-500">
              Showing {filteredExpenses.length} of {expenses.length} records
            </span>
            <button
              onClick={handleResetFilters}
              className="text-emerald-600 hover:text-emerald-700 font-medium flex items-center"
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              Reset all filters
            </button>
          </div>
        )}
      </div>

      {/* Financial Records Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th 
                  onClick={() => toggleSort('date')}
                  className="px-5 py-3 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center space-x-1">
                    <span>Date</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th 
                  onClick={() => toggleSort('merchant')}
                  className="px-5 py-3 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center space-x-1">
                    <span>Merchant / Vendor</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="px-5 py-3">Category</th>
                <th className="px-5 py-3">Math Check</th>
                <th 
                  onClick={() => toggleSort('total')}
                  className="px-5 py-3 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center space-x-1">
                    <span>Total Amount</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="px-5 py-3">Mode</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedExpenses.length > 0 ? (
                paginatedExpenses.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => onSelectExpenseForReview(item)}
                    className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                  >
                    {/* Date */}
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs text-slate-500 font-mono">
                      {item.transaction_date || (
                        <span className="text-amber-600 italic">Needs date</span>
                      )}
                    </td>

                    {/* Merchant */}
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-slate-900 text-xs">
                        {item.merchant || <span className="text-slate-400 italic">Unknown Vendor</span>}
                      </div>
                      {item.invoice_number && (
                        <div className="text-[11px] text-slate-400 font-mono">
                          Ref: {item.invoice_number}
                        </div>
                      )}
                    </td>

                    {/* Category */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded text-xs bg-slate-100 text-slate-700 font-medium">
                        {item.category}
                      </span>
                    </td>

                    {/* Math Reconciliation */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      {item.reconciliation_status === 'reconciled' ? (
                        <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <CheckCircle className="w-3 h-3 mr-1 text-emerald-500" /> Reconciled
                        </span>
                      ) : item.reconciliation_status === 'mismatch' ? (
                        <span 
                          className="inline-flex items-center text-[11px] font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200"
                          title="Subtotal + Tax != Total"
                        >
                          <AlertTriangle className="w-3 h-3 mr-1 text-rose-500" /> Discrepancy
                        </span>
                      ) : (
                        <span className="text-[11px] text-slate-400">Unverified</span>
                      )}
                    </td>

                    {/* Total Amount */}
                    <td className="px-5 py-3.5 whitespace-nowrap font-mono font-bold text-xs text-slate-900">
                      {item.currency} {item.total !== null ? item.total.toFixed(2) : '--'}
                    </td>

                    {/* Extraction Mode */}
                    <td className="px-5 py-3.5 whitespace-nowrap text-[11px] text-slate-500">
                      <span className={`px-1.5 py-0.5 rounded font-mono ${
                        item.extraction_mode.includes('gemma')
                          ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}>
                        {item.extraction_mode.includes('gemma') ? 'Gemma 2B' : 'Fallback'}
                      </span>
                    </td>

                    {/* Status */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-0.5 text-[11px] font-semibold rounded-full ${
                        item.status === 'confirmed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : item.status === 'awaiting_review'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}>
                        {item.status === 'awaiting_review' ? 'Needs Review' : item.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="px-5 py-3.5 text-right whitespace-nowrap text-xs">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectExpenseForReview(item);
                          }}
                          className="p-1 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                          title="Review / Edit"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          disabled={deletingId === item.id}
                          className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-xs text-slate-400">
                    No expense records matching the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Toolbar */}
        {totalPages > 1 && (
          <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
            <span>
              Page {currentPage} of {totalPages} ({filteredExpenses.length} total)
            </span>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-2.5 py-1 rounded border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-2.5 py-1 rounded border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
