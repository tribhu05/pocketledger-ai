import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  RefreshCw, 
  FileCode, 
  X, 
  ArrowRight,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { Expense } from '../types';
import { uploadDocuments, uploadRawText } from '../api';

interface DocumentInboxProps {
  onUploadSuccess: (expenses: Expense[]) => void;
  onNavigateTab: (tab: string) => void;
}

export const DocumentInbox: React.FC<DocumentInboxProps> = ({ onUploadSuccess, onNavigateTab }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Raw text tab
  const [activeTab, setActiveTab] = useState<'files' | 'raw_text'>('files');
  const [rawTitle, setRawTitle] = useState('Manual Receipt');
  const [rawText, setRawText] = useState('');
  const [processingText, setProcessingText] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFiles = (files: FileList | File[]) => {
    const validExts = ['.jpg', '.jpeg', '.png', '.webp', '.pdf'];
    const valid: File[] = [];
    const errors: string[] = [];

    Array.from(files).forEach((f) => {
      const ext = '.' + f.name.split('.').pop()?.toLowerCase();
      if (!validExts.includes(ext)) {
        errors.push(`"${f.name}" has unsupported format. Use PNG, JPG, or PDF.`);
        return;
      }
      if (f.size > 15 * 1024 * 1024) {
        errors.push(`"${f.name}" exceeds 15 MB limit.`);
        return;
      }
      valid.push(f);
    });

    if (errors.length > 0) {
      setUploadError(errors.join(' '));
    } else {
      setUploadError(null);
    }

    setSelectedFiles((prev) => [...prev, ...valid]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateFiles(e.target.files);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleStartProcessing = async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);
    setUploadError(null);
    setUploadProgress(`Extracting data with local Gemma AI model... (0 / ${selectedFiles.length})`);

    try {
      const results = await uploadDocuments(selectedFiles);
      setUploadProgress(`Extracted ${results.length} documents successfully!`);
      setSelectedFiles([]);
      onUploadSuccess(results);
    } catch (err: any) {
      setUploadError(err.message || 'Processing failed. Please check backend connection.');
    } finally {
      setUploading(false);
    }
  };

  const handleProcessRawText = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawText.trim()) return;

    setProcessingText(true);
    setUploadError(null);

    try {
      const res = await uploadRawText(rawTitle, rawText);
      setRawText('');
      onUploadSuccess([res]);
    } catch (err: any) {
      setUploadError(err.message || 'Extraction failed.');
    } finally {
      setProcessingText(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Document Inbox</h1>
        <p className="text-sm text-slate-500">
          Upload receipt scans, invoice PDFs, or paste raw text. Documents are processed locally on your hardware.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('files')}
          className={`py-2 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center ${
            activeTab === 'files'
              ? 'border-emerald-600 text-emerald-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <UploadCloud className="w-4 h-4 mr-2" />
          File Upload (Images & PDFs)
        </button>
        <button
          onClick={() => setActiveTab('raw_text')}
          className={`py-2 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center ${
            activeTab === 'raw_text'
              ? 'border-emerald-600 text-emerald-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileCode className="w-4 h-4 mr-2" />
          Paste Receipt Text
        </button>
      </div>

      {uploadError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-rose-900">Upload / Processing Error</h4>
            <p className="text-xs text-rose-700 mt-1">{uploadError}</p>
          </div>
          <button onClick={() => setUploadError(null)} className="text-rose-500 hover:text-rose-700">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {activeTab === 'files' ? (
        <div className="space-y-6">
          {/* Dropzone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
              dragActive
                ? 'border-emerald-500 bg-emerald-50/50'
                : 'border-slate-300 hover:border-slate-400 bg-white'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.webp,.pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="w-14 h-14 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center mx-auto text-slate-600 mb-4">
              <UploadCloud className="w-7 h-7" />
            </div>
            <h3 className="text-base font-semibold text-slate-900 mb-1">
              Drag and drop receipts or invoices here
            </h3>
            <p className="text-xs text-slate-500 mb-3">
              Supports PDF, PNG, JPG, JPEG, WEBP (Max 15 MB per file)
            </p>
            <span className="inline-flex items-center text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200">
              Select files from computer
            </span>
          </div>

          {/* Selected Files Staging List */}
          {selectedFiles.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Files staged for extraction ({selectedFiles.length})
                </span>
                <button
                  onClick={() => setSelectedFiles([])}
                  className="text-xs text-rose-600 hover:text-rose-700 font-medium"
                >
                  Clear all
                </button>
              </div>

              <div className="divide-y divide-slate-100 max-h-60 overflow-y-auto">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="py-2.5 flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-3 truncate">
                      <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                      <span className="font-medium text-slate-800 truncate">{file.name}</span>
                      <span className="text-slate-400">({(file.size / 1024).toFixed(0)} KB)</span>
                    </div>
                    <button
                      onClick={() => removeFile(idx)}
                      className="text-slate-400 hover:text-rose-600 transition-colors ml-2"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  onClick={handleStartProcessing}
                  disabled={uploading}
                  className="px-6 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm transition-colors flex items-center disabled:opacity-60 shadow-sm"
                >
                  {uploading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Extracting with Gemma AI...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Process {selectedFiles.length} Document{selectedFiles.length > 1 ? 's' : ''}
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Raw Text Processing Form */
        <form onSubmit={handleProcessRawText} className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Document Reference Title
            </label>
            <input
              type="text"
              value={rawTitle}
              onChange={(e) => setRawTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="e.g. Starbucks Client Meeting"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Pasted Receipt / Invoice Text
            </label>
            <textarea
              rows={8}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder={`Paste any text snippet, e.g.:\nACME CLOUD HOSTING INC\nInvoice #INV-2026-992\nDate: 2026-09-14\nSubtotal: $45.00\nSales Tax (8%): $3.60\nTotal Due: $48.60\nPaid with Visa 4112`}
              required
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={processingText}
              className="px-6 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm transition-colors flex items-center disabled:opacity-60 shadow-sm"
            >
              {processingText ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Running Gemma 2B Inference...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2 text-emerald-400" />
                  Extract & Structure Text
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Privacy Callout */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-center space-x-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <p>
          <strong className="text-slate-800">Local Security Guarantee:</strong> All files uploaded here are stored in your project's local <code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">uploads/</code> folder and analyzed exclusively through your local Ollama instance. No document text or metadata is ever transmitted over the Internet.
        </p>
      </div>
    </div>
  );
};
