import React, { useState, useEffect } from 'react';
import { 
  X, 
  CheckCircle, 
  AlertTriangle, 
  FileText, 
  RefreshCw, 
  History, 
  Cpu, 
  Save, 
  Trash2,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';
import { Expense, ReviewUpdateRequest } from '../types';
import { updateExpenseReview, retryExtraction, getDocumentFileUrl } from '../api';

const FREELANCE_CATEGORIES = [
  'Software & SaaS',
  'Office Supplies',
  'Hardware & Equipment',
  'Travel & Lodging',
  'Meals & Entertainment',
  'Professional Services',
  'Utilities',
  'Other',
];

interface ReviewModalProps {
  expense: Expense;
  onClose: () => void;
  onSaved: (updated: Expense) => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({ expense, onClose, onSaved }) => {
  const [formData, setFormData] = useState<ReviewUpdateRequest>({
    merchant: expense.merchant || '',
    document_type: expense.document_type || 'receipt',
    invoice_number: expense.invoice_number || '',
    transaction_date: expense.transaction_date || '',
    currency: expense.currency || 'USD',
    subtotal: expense.subtotal !== null ? expense.subtotal : undefined,
    tax: expense.tax !== null ? expense.tax : undefined,
    total: expense.total !== null ? expense.total : undefined,
    category: expense.category || 'Other',
    payment_method: expense.payment_method || '',
    description: expense.description || '',
    status: expense.status,
  });

  const [saving, setSaving] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showAuditTrail, setShowAuditTrail] = useState(false);

  // Live Math Reconciliation check
  const sub = formData.subtotal !== undefined && formData.subtotal !== null ? Number(formData.subtotal) : null;
  const tx = formData.tax !== undefined && formData.tax !== null ? Number(formData.tax) : null;
  const tot = formData.total !== undefined && formData.total !== null ? Number(formData.total) : null;

  let liveMismatch = false;
  let liveDelta = 0;
  if (tot !== null && sub !== null && tx !== null) {
    const calc = Number((sub + tx).toFixed(2));
    liveDelta = Number((tot - calc).toFixed(2));
    if (Math.abs(liveDelta) > 0.05) {
      liveMismatch = true;
    }
  }

  const handleSave = async (confirmedStatus: 'confirmed' | 'awaiting_review' | 'rejected') => {
    setSaving(true);
    setErrorMsg(null);
    try {
      const payload: ReviewUpdateRequest = {
        ...formData,
        merchant: formData.merchant ? formData.merchant.trim() : null,
        invoice_number: formData.invoice_number ? formData.invoice_number.trim() : null,
        transaction_date: formData.transaction_date ? formData.transaction_date.trim() : null,
        subtotal: sub !== null && !isNaN(sub) ? sub : null,
        tax: tx !== null && !isNaN(tx) ? tx : null,
        total: tot !== null && !isNaN(tot) ? tot : null,
        status: confirmedStatus,
      };

      const res = await updateExpenseReview(expense.id, payload);
      onSaved(res);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save edits.');
    } finally {
      setSaving(false);
    }
  };

  const handleRetry = async () => {
    setRetrying(true);
    setErrorMsg(null);
    try {
      const res = await retryExtraction(expense.id);
      onSaved(res);
      setFormData({
        merchant: res.merchant || '',
        document_type: res.document_type || 'receipt',
        invoice_number: res.invoice_number || '',
        transaction_date: res.transaction_date || '',
        currency: res.currency || 'USD',
        subtotal: res.subtotal !== null ? res.subtotal : undefined,
        tax: res.tax !== null ? res.tax : undefined,
        total: res.total !== null ? res.total : undefined,
        category: res.category || 'Other',
        payment_method: res.payment_method || '',
        description: res.description || '',
        status: res.status,
      });
    } catch (err: any) {
      setErrorMsg(err.message || 'Retry failed.');
    } finally {
      setRetrying(false);
    }
  };

  const isImage = expense.mime_type.startsWith('image/');
  const isPdf = expense.mime_type === 'application/pdf';
  const fileUrl = getDocumentFileUrl(expense.id);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-2xl max-w-5xl w-full max-h-[92vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-3">
            <span className={`w-3 h-3 rounded-full ${
              expense.status === 'confirmed' ? 'bg-emerald-500' : 'bg-amber-500'
            }`} />
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center">
                Review & Confirm Document
                <span className="ml-2 text-xs font-mono font-normal text-slate-500">
                  [{expense.source_filename}]
                </span>
              </h2>
              <div className="flex items-center space-x-2 text-xs text-slate-500 mt-0.5">
                <Cpu className="w-3.5 h-3.5 text-indigo-500" />
                <span>Extracted with: <strong className="text-slate-700">{expense.extraction_mode}</strong></span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 rounded-lg p-1.5 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body: Split Screen */}
        <div className="flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
          {/* Left Column: Source Document Evidence */}
          <div className="p-6 bg-slate-50/50 flex flex-col space-y-4 overflow-y-auto max-h-[70vh]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center">
                <FileText className="w-3.5 h-3.5 mr-1 text-slate-500" /> Source Evidence
              </span>
              <button
                onClick={handleRetry}
                disabled={retrying}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
              >
                <RefreshCw className={`w-3 h-3 mr-1 ${retrying ? 'animate-spin' : ''}`} />
                Re-extract with AI
              </button>
            </div>

            {/* Document Preview (Image, PDF or OCR Text) */}
            <div className="border border-slate-200 rounded-xl bg-white overflow-hidden shadow-xs flex-1 min-h-[220px]">
              {isImage ? (
                <div className="p-2 flex items-center justify-center bg-slate-100">
                  <img
                    src={fileUrl}
                    alt={expense.source_filename}
                    className="max-h-80 w-auto object-contain rounded"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                </div>
              ) : isPdf ? (
                <div className="p-4 text-center">
                  <FileText className="w-12 h-12 text-slate-400 mx-auto mb-2" />
                  <p className="text-xs font-medium text-slate-700 mb-2">PDF Document Attached</p>
                  <a
                    href={fileUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-block text-xs text-emerald-600 hover:underline font-semibold"
                  >
                    Open PDF in new tab
                  </a>
                </div>
              ) : null}

              {/* Extracted OCR Text view */}
              <div className="p-4 border-t border-slate-100 bg-slate-900 text-slate-200">
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                  Extracted Document Text
                </span>
                <pre className="font-mono text-xs whitespace-pre-wrap leading-relaxed max-h-56 overflow-y-auto text-emerald-400/90 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  {expense.raw_ocr_text || '(No OCR text extracted)'}
                </pre>
              </div>
            </div>

            {/* Warnings Alert */}
            {expense.warnings && expense.warnings.length > 0 && (
              <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
                <div className="flex items-center font-semibold">
                  <AlertTriangle className="w-4 h-4 mr-1 text-amber-600" />
                  Extraction & Reconciliation Warnings:
                </div>
                <ul className="list-disc pl-5 space-y-0.5 text-amber-800">
                  {expense.warnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Right Column: Editable Financial Form */}
          <div className="p-6 space-y-5 overflow-y-auto max-h-[70vh]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Extracted Fields (Editable)
              </span>
              <span className="text-xs text-slate-400">Review and confirm below</span>
            </div>

            {/* Math Discrepancy Warning Banner */}
            {liveMismatch && (
              <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start space-x-2.5">
                <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <div>
                  <strong className="font-semibold text-rose-900">Reconciliation Mismatch:</strong> Subtotal ({sub?.toFixed(2)}) + Tax ({tx?.toFixed(2)}) = {(Number(sub) + Number(tx)).toFixed(2)}, which does not match Total ({tot?.toFixed(2)}). Discrepancy of {Math.abs(liveDelta).toFixed(2)}. Please verify before confirming!
                </div>
              </div>
            )}

            {/* Form Fields */}
            <div className="space-y-4 text-xs">
              {/* Merchant / Vendor */}
              <div>
                <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Merchant / Vendor Name
                </label>
                <input
                  type="text"
                  value={formData.merchant || ''}
                  onChange={(e) => setFormData({ ...formData, merchant: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 font-medium focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  placeholder="e.g. Starbucks, AWS, Staples"
                />
              </div>

              {/* Date & Document Type */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Date (YYYY-MM-DD)
                  </label>
                  <input
                    type="date"
                    value={formData.transaction_date || ''}
                    onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Document Type
                  </label>
                  <select
                    value={formData.document_type || 'receipt'}
                    onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
                  >
                    <option value="receipt">Receipt</option>
                    <option value="invoice">Invoice</option>
                    <option value="other">Other / Proof of Payment</option>
                  </select>
                </div>
              </div>

              {/* Amounts Grid: Currency, Subtotal, Tax, Total */}
              <div className="grid grid-cols-4 gap-2.5 bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div>
                  <label className="block font-semibold text-slate-600 uppercase text-[10px] tracking-wider mb-1">
                    Currency
                  </label>
                  <input
                    type="text"
                    value={formData.currency || 'USD'}
                    onChange={(e) => setFormData({ ...formData, currency: e.target.value.toUpperCase() })}
                    className="w-full px-2 py-1.5 rounded-md border border-slate-200 font-bold text-center text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white uppercase"
                    maxLength={3}
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-600 uppercase text-[10px] tracking-wider mb-1">
                    Subtotal
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.subtotal ?? ''}
                    onChange={(e) => setFormData({ ...formData, subtotal: e.target.value !== '' ? parseFloat(e.target.value) : undefined })}
                    className="w-full px-2 py-1.5 rounded-md border border-slate-200 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-600 uppercase text-[10px] tracking-wider mb-1">
                    Tax / VAT
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.tax ?? ''}
                    onChange={(e) => setFormData({ ...formData, tax: e.target.value !== '' ? parseFloat(e.target.value) : undefined })}
                    className="w-full px-2 py-1.5 rounded-md border border-slate-200 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-emerald-800 uppercase text-[10px] tracking-wider mb-1">
                    Total
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.total ?? ''}
                    onChange={(e) => setFormData({ ...formData, total: e.target.value !== '' ? parseFloat(e.target.value) : undefined })}
                    className="w-full px-2 py-1.5 rounded-md border-2 border-emerald-400 font-mono font-bold text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white text-emerald-900"
                    placeholder="0.00"
                  />
                </div>
              </div>

              {/* Category & Invoice Number */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Freelance Tax Category
                  </label>
                  <select
                    value={formData.category || 'Other'}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
                  >
                    {FREELANCE_CATEGORIES.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Invoice / Order Ref #
                  </label>
                  <input
                    type="text"
                    value={formData.invoice_number || ''}
                    onChange={(e) => setFormData({ ...formData, invoice_number: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                    placeholder="e.g. INV-2026-01"
                  />
                </div>
              </div>

              {/* Payment Method & Description */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Payment Method
                  </label>
                  <input
                    type="text"
                    value={formData.payment_method || ''}
                    onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                    placeholder="e.g. Visa 4102, Cash"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Description / Client Note
                  </label>
                  <input
                    type="text"
                    value={formData.description || ''}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                    placeholder="Brief expense description"
                  />
                </div>
              </div>

              {/* Audit Trail Accordion */}
              <div className="border border-slate-200 rounded-xl overflow-hidden mt-4">
                <button
                  type="button"
                  onClick={() => setShowAuditTrail(!showAuditTrail)}
                  className="w-full px-4 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left text-xs font-semibold text-slate-700"
                >
                  <span className="flex items-center">
                    <History className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
                    Audit Trail & Lineage History
                  </span>
                  {showAuditTrail ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {showAuditTrail && (
                  <div className="p-4 bg-white space-y-3 text-xs border-t border-slate-200 font-mono">
                    <div>
                      <span className="font-semibold text-slate-700 block mb-1">User Edits Recorded:</span>
                      {Object.keys(expense.user_edits || {}).length > 0 ? (
                        <pre className="bg-slate-50 p-2 rounded text-[11px] overflow-x-auto text-slate-700">
                          {JSON.stringify(expense.user_edits, null, 2)}
                        </pre>
                      ) : (
                        <p className="text-slate-400 italic text-[11px]">No manual edits made yet.</p>
                      )}
                    </div>

                    <div>
                      <span className="font-semibold text-slate-700 block mb-1">Raw Model Output:</span>
                      <pre className="bg-slate-900 text-emerald-400 p-2 rounded text-[11px] overflow-x-auto">
                        {expense.raw_model_response || '{}'}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleSave('rejected')}
              disabled={saving}
              className="px-3.5 py-2 rounded-lg text-rose-600 hover:bg-rose-50 text-xs font-semibold transition-colors flex items-center"
            >
              <Trash2 className="w-3.5 h-3.5 mr-1.5" />
              Reject Document
            </button>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
            <button
              onClick={() => handleSave('awaiting_review')}
              disabled={saving}
              className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 text-xs font-semibold transition-colors"
            >
              Save as Draft
            </button>
            <button
              onClick={() => handleSave('confirmed')}
              disabled={saving}
              className="px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors flex items-center shadow-xs"
            >
              {saving ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle className="w-3.5 h-3.5 mr-1.5" />
                  Confirm & Approve Record
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
