import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Database, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Trash2, 
  RefreshCw, 
  Sparkles,
  BarChart2,
  ExternalLink,
  HelpCircle,
  HardDrive
} from 'lucide-react';
import { SystemStatus, BenchmarkResult } from '../types';
import { resetAllData, seedDemoWorkspace, fetchBenchmark, fetchSystemStatus } from '../api';

interface SettingsPrivacyProps {
  status: SystemStatus | null;
  onRefreshAll: () => Promise<void>;
}

export const SettingsPrivacy: React.FC<SettingsPrivacyProps> = ({ status, onRefreshAll }) => {
  const [resetting, setResetting] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [benchmarking, setBenchmarking] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkResult | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const handleResetData = async () => {
    if (!window.confirm('CAUTION: This will permanently wipe all expense records and delete all uploaded documents from your local disk. Are you sure?')) {
      return;
    }
    setResetting(true);
    setActionMessage(null);
    try {
      const res = await resetAllData();
      setActionMessage(res.message);
      await onRefreshAll();
    } catch (err: any) {
      alert(`Wipe failed: ${err.message}`);
    } finally {
      setResetting(false);
    }
  };

  const handleSeedDemo = async () => {
    setSeeding(true);
    setActionMessage(null);
    try {
      const res = await seedDemoWorkspace();
      setActionMessage(res.message);
      await onRefreshAll();
    } catch (err: any) {
      alert(`Seeding failed: ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  const handleRunBenchmark = async () => {
    setBenchmarking(true);
    setActionMessage('Running live inference benchmark on synthetic corpus (Gemma 2B vs Fallback)... This takes ~30-40s on local CPU.');
    try {
      const res = await fetchBenchmark();
      setBenchmarkResult(res);
      setActionMessage('Benchmark completed successfully!');
    } catch (err: any) {
      alert(`Benchmark failed: ${err.message}`);
      setActionMessage(null);
    } finally {
      setBenchmarking(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Status & Privacy Settings</h1>
        <p className="text-sm text-slate-500">
          Hardware runtime verification, model configuration, privacy guarantees, and testing utilities.
        </p>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-emerald-600 hover:text-emerald-900 font-bold ml-2">
            ×
          </button>
        </div>
      )}

      {/* Real-time System Status Panel */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center text-slate-700">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Runtime & Model Status</h3>
              <p className="text-xs text-slate-500">Live checks on local inference and extraction engines</p>
            </div>
          </div>
          <button
            onClick={() => onRefreshAll()}
            className="text-xs text-slate-500 hover:text-slate-800 flex items-center"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh Status
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Gemma 2B Status */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-500 uppercase">AI Model</span>
              {status?.gemma_available ? (
                <CheckCircle className="w-4 h-4 text-emerald-600" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-600" />
              )}
            </div>
            <div className="font-bold text-sm text-slate-900 font-mono">
              {status?.gemma_model || 'gemma2:2b'}
            </div>
            <p className="text-[11px] text-slate-500">
              {status?.gemma_available ? 'Ready for local inference' : 'Unavailable (Fallback active)'}
            </p>
          </div>

          {/* Ollama Service */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-500 uppercase">Ollama Runtime</span>
              {status?.ollama_connected ? (
                <CheckCircle className="w-4 h-4 text-emerald-600" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-rose-600" />
              )}
            </div>
            <div className="font-bold text-sm text-slate-900 font-mono">
              {status?.ollama_url || 'http://localhost:11434'}
            </div>
            <p className="text-[11px] text-slate-500">
              {status?.ollama_connected ? 'Connected on local port' : 'Server not responding'}
            </p>
          </div>

          {/* OCR Engine */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-500 uppercase">OCR / PDF Engine</span>
              {status?.ocr_available ? (
                <CheckCircle className="w-4 h-4 text-emerald-600" />
              ) : (
                <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">Digital PDF</span>
              )}
            </div>
            <div className="font-bold text-sm text-slate-900 capitalize">
              {status?.ocr_available ? 'Tesseract OCR' : 'PDF Native Text'}
            </div>
            <p className="text-[11px] text-slate-500">
              {status?.ocr_available ? 'Image OCR active' : 'PDFs supported; install OCR for photos'}
            </p>
          </div>

          {/* Database */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-500 uppercase">Local Database</span>
              <CheckCircle className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="font-bold text-sm text-slate-900 font-mono">
              pocketledger.db
            </div>
            <p className="text-[11px] text-slate-500">
              SQLite (Persistent, zero cloud)
            </p>
          </div>
        </div>
      </div>

      {/* Model Accuracy & Latency Benchmark Panel */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center">
              <BarChart2 className="w-5 h-5 mr-2 text-indigo-600" />
              On-Device Benchmark & Model Evaluation
            </h3>
            <p className="text-xs text-slate-500">
              Measures field-level extraction accuracy and latency on the synthetic receipt corpus without fabricated numbers.
            </p>
          </div>
          <button
            onClick={handleRunBenchmark}
            disabled={benchmarking}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center transition-colors disabled:opacity-60 shadow-xs"
          >
            {benchmarking ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                Measuring Benchmark...
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                Run Live Benchmark
              </>
            )}
          </button>
        </div>

        {benchmarkResult ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Gemma Stats */}
              <div className="p-4 rounded-xl bg-indigo-50/50 border border-indigo-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-indigo-900 uppercase">Gemma 2B (Local Open-Weight)</span>
                  <span className="text-xs font-mono font-semibold text-indigo-700">
                    Avg: {benchmarkResult.gemma.avg_time_ms ? `${(benchmarkResult.gemma.avg_time_ms / 1000).toFixed(1)}s` : 'N/A'}
                  </span>
                </div>
                {benchmarkResult.gemma.field_accuracy ? (
                  <div className="space-y-1.5 text-xs">
                    {Object.entries(benchmarkResult.gemma.field_accuracy).map(([f, acc]) => (
                      <div key={f} className="flex justify-between items-center">
                        <span className="text-slate-600 capitalize">{f.replace('_', ' ')}:</span>
                        <span className="font-bold text-slate-900 font-mono">{acc}%</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">{benchmarkResult.gemma.status || 'Offline'}</p>
                )}
              </div>

              {/* Fallback Stats */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-700 uppercase">Deterministic Fallback</span>
                  <span className="text-xs font-mono font-semibold text-slate-600">
                    Avg: {benchmarkResult.fallback.avg_time_ms} ms
                  </span>
                </div>
                <div className="space-y-1.5 text-xs">
                  {Object.entries(benchmarkResult.fallback.field_accuracy).map(([f, acc]) => (
                    <div key={f} className="flex justify-between items-center">
                      <span className="text-slate-600 capitalize">{f.replace('_', ' ')}:</span>
                      <span className="font-bold text-slate-900 font-mono">{acc}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-slate-50 text-center space-y-2 border border-slate-200/60">
            <p className="text-xs text-slate-600">
              Click <strong>Run Live Benchmark</strong> to run evaluation across all 8 synthetic receipts in real-time.
            </p>
            <p className="text-[11px] text-slate-400">
              Verified test corpus: AWS Cloud Invoice (PDF), Starbucks (PNG), GitHub Pro (PDF), Staples (JPG), Hetzner (EUR PDF), Heathrow Express (GBP PNG), Bistro Mismatch (PNG), Illegible Taxi (PNG).
            </p>
          </div>
        )}
      </div>

      {/* Privacy Architecture & Threat Model */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center">
          <ShieldCheck className="w-5 h-5 mr-2 text-emerald-600" />
          Privacy-First Architecture & Threat Model
        </h3>
        <div className="text-xs text-slate-600 space-y-2.5 leading-relaxed">
          <p>
            <strong>The Core Freelance Privacy Problem:</strong> Existing AI receipt scanners require uploading invoices containing client identities, credit card hints, billing addresses, and financial amounts to third-party cloud servers.
          </p>
          <p>
            <strong>How PocketLedger Solves It:</strong>
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Zero Remote Inference:</strong> The primary model is Google’s open-weight Gemma 2B running locally via Ollama. No tokens leave your machine.</li>
            <li><strong>No Tracking or Telemetry:</strong> Financial values, filenames, and extracted text are never logged or transmitted.</li>
            <li><strong>Safe Storage:</strong> Files are stored in the local <code className="bg-slate-100 px-1 py-0.5 rounded">uploads/</code> directory and persisted in SQLite.</li>
            <li><strong>Path Traversal Defense:</strong> All file serving validates resolved paths against the upload directory boundary.</li>
            <li><strong>Formula Injection Defense:</strong> All CSV exports prepend single quotes to formula characters (<code className="bg-slate-100 px-1 py-0.5 rounded">=, +, -, @</code>) to protect spreadsheets.</li>
          </ul>
        </div>
      </div>

      {/* Troubleshooting Guide */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center">
          <HelpCircle className="w-5 h-5 mr-2 text-indigo-600" />
          Setup & Troubleshooting Guide
        </h3>
        <div className="divide-y divide-slate-100 text-xs">
          <div className="py-3 space-y-1">
            <h4 className="font-semibold text-slate-800">1. How to run Ollama and Gemma 2B locally</h4>
            <p className="text-slate-600">
              Run <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono">ollama pull gemma2:2b</code> in your terminal. Ensure the Ollama background daemon is running (<code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono">ollama serve</code>). PocketLedger will auto-detect it on port 11434.
            </p>
          </div>

          <div className="py-3 space-y-1">
            <h4 className="font-semibold text-slate-800">2. How Tesseract OCR is configured</h4>
            <p className="text-slate-600">
              For invoice PDFs, PocketLedger extracts text directly without needing Tesseract. For photo receipts, install Tesseract OCR (Windows: <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono">winget install UB-Mannheim.TesseractOCR</code>; macOS: <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono">brew install tesseract</code>; Linux: <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono">sudo apt install tesseract-ocr</code>).
            </p>
          </div>

          <div className="py-3 space-y-1">
            <h4 className="font-semibold text-slate-800">3. Deterministic Local Fallback</h4>
            <p className="text-slate-600">
              If Ollama is stopped or unavailable on a machine with limited memory, PocketLedger switches to the built-in deterministic heuristic parser. It is clearly labeled on every record so you always know which engine handled your data.
            </p>
          </div>
        </div>
      </div>

      {/* Danger Zone & Data Management */}
      <div className="bg-white border border-rose-200 rounded-xl p-6 shadow-xs space-y-4">
        <h3 className="text-base font-bold text-rose-900 flex items-center">
          <Trash2 className="w-5 h-5 mr-2 text-rose-600" />
          Data Management & Permanent Deletion
        </h3>
        <p className="text-xs text-slate-600">
          Manage your local test workspace or permanently delete all data to exercise complete privacy control.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <button
            onClick={handleSeedDemo}
            disabled={seeding}
            className="px-4 py-2.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 text-xs font-semibold flex items-center transition-colors disabled:opacity-60"
          >
            {seeding ? (
              <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-emerald-600" />
            )}
            Seed Synthetic Demo Receipts
          </button>

          <button
            onClick={handleResetData}
            disabled={resetting}
            className="px-4 py-2.5 rounded-lg bg-rose-50 text-rose-800 border border-rose-200 hover:bg-rose-100 text-xs font-semibold flex items-center transition-colors disabled:opacity-60"
          >
            {resetting ? (
              <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
            ) : (
              <Trash2 className="w-3.5 h-3.5 mr-1.5 text-rose-600" />
            )}
            Wipe All Records & Files
          </button>
        </div>
      </div>
    </div>
  );
};
