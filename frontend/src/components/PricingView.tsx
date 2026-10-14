import React, { useState } from 'react';
import { 
  CreditCard, 
  Check, 
  HelpCircle, 
  MessageSquare, 
  Send, 
  Sparkles, 
  ShieldCheck,
  Clock,
  Layers
} from 'lucide-react';

export const PricingView: React.FC = () => {
  const [feedback, setFeedback] = useState({
    currentMethod: 'Spreadsheets manually',
    timeSpent: '15-30 minutes',
    whatFailed: '',
    wouldPay: 'Maybe - depends on automated desktop watcher',
    neededFeatures: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmitFeedback = (e: React.FormEvent) => {
    e.preventDefault();
    // Saves feedback to local storage for honest validation without collecting financial data
    const existing = JSON.parse(localStorage.getItem('pocketledger_feedback') || '[]');
    existing.push({ ...feedback, timestamp: new Date().toISOString() });
    localStorage.setItem('pocketledger_feedback', JSON.stringify(existing));
    setSubmitted(true);
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-12">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 uppercase tracking-wider">
          Side Hustle Business Model Experiment
        </span>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Transparent, Honest Pricing
        </h1>
        <p className="text-sm text-slate-500">
          PocketLedger AI is 100% open-source and free to run locally. Below is our proposed commercial roadmap for the Hacktoberfest Side Hustle challenge.
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tier 1: Free Open-Source */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold text-slate-500 uppercase">Community</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">Active</span>
            </div>
            <div>
              <div className="text-3xl font-black text-slate-900">$0</div>
              <p className="text-xs text-slate-500">Free forever, open-source (MIT)</p>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Local Gemma 2B inference</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Deterministic math reconciliation</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Unlimited receipts & invoices</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Local SQLite storage</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Formula-safe CSV export</li>
            </ul>
          </div>
          <button
            disabled
            className="w-full py-2.5 rounded-lg bg-slate-100 text-slate-500 font-semibold text-xs cursor-default"
          >
            Currently Installed
          </button>
        </div>

        {/* Tier 2: Solo Desktop (Proposed) */}
        <div className="bg-white border-2 border-emerald-500 rounded-2xl p-6 shadow-md flex flex-col justify-between space-y-6 relative">
          <div className="absolute -top-3 right-6 bg-emerald-600 text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
            Proposed Concept
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold text-emerald-700 uppercase">Solo Freelancer</span>
            </div>
            <div>
              <div className="text-3xl font-black text-slate-900">$29</div>
              <p className="text-xs text-slate-500">Proposed one-time lifetime license</p>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Everything in Free</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Single-click native desktop installer (.exe / .dmg)</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Automatic folder watcher (auto-scans drop folder)</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Custom tax category rules</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Priority GitHub issue triage</li>
            </ul>
          </div>
          <button
            onClick={() => {
              const el = document.getElementById('feedback-form');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-colors shadow-xs"
          >
            Vote for Solo Desktop
          </button>
        </div>

        {/* Tier 3: Freelancer Pro (Proposed) */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold text-slate-500 uppercase">Freelancer Pro</span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">Roadmap</span>
            </div>
            <div>
              <div className="text-3xl font-black text-slate-900">$9 <span className="text-xs font-normal text-slate-500">/ month</span></div>
              <p className="text-xs text-slate-500">Proposed subscription</p>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Everything in Solo</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Multi-client workspace segregation</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Reimbursable client expense tagging</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Auto-generated client PDF invoice attachments</li>
              <li className="flex items-center"><Check className="w-4 h-4 text-emerald-500 mr-2 shrink-0" /> Encrypted local backup to USB or WebDAV</li>
            </ul>
          </div>
          <button
            onClick={() => {
              const el = document.getElementById('feedback-form');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="w-full py-2.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold text-xs transition-colors"
          >
            Request Multi-Client Pro
          </button>
        </div>
      </div>

      {/* Honest Pricing Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-800">Commercial Honesty & Validation Rule:</strong>
          <p className="mt-1">
            This page represents a transparent pricing experiment for the Hacktoberfest Side Hustle theme. We do not implement fake payment buttons, nor do we fabricate paying customers or revenue. If you are a freelancer testing PocketLedger, please share your honest thoughts in the validation form below.
          </p>
        </div>
      </div>

      {/* Freelancer Validation Feedback Form */}
      <div id="feedback-form" className="bg-white border border-slate-200 rounded-2xl p-8 shadow-xs space-y-6">
        <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Freelancer Validation Survey</h3>
            <p className="text-xs text-slate-500">
              Help us understand if this solves a real problem. No sensitive receipt data is collected.
            </p>
          </div>
        </div>

        {submitted ? (
          <div className="p-6 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-center space-y-2">
            <Sparkles className="w-8 h-8 text-emerald-600 mx-auto" />
            <h4 className="font-bold text-sm">Thank you for your feedback!</h4>
            <p className="text-xs text-emerald-700">
              Your response has been saved to your local survey log. As an open-source project, your candid thoughts directly shape what we build next.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmitFeedback} className="space-y-4 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  How do you currently organize receipts?
                </label>
                <select
                  value={feedback.currentMethod}
                  onChange={(e) => setFeedback({ ...feedback, currentMethod: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="Spreadsheets manually">Spreadsheets manually (Excel / Google Sheets)</option>
                  <option value="Shoebox / physical folder">Shoebox or folder until tax season</option>
                  <option value="Cloud accounting software">Cloud accounting (QuickBooks / Xero / FreshBooks)</option>
                  <option value="Email search when needed">Email search when accountant asks</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  How much time did you spend testing PocketLedger?
                </label>
                <select
                  value={feedback.timeSpent}
                  onChange={(e) => setFeedback({ ...feedback, timeSpent: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="Under 5 minutes">Under 5 minutes (quick glance)</option>
                  <option value="5-15 minutes">5–15 minutes (tested sample documents)</option>
                  <option value="15-30 minutes">15–30 minutes (tested real invoices)</option>
                  <option value="Over 30 minutes">Over 30 minutes (full workflow test)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Would you pay for a standalone offline desktop version?
                </label>
                <select
                  value={feedback.wouldPay}
                  onChange={(e) => setFeedback({ ...feedback, wouldPay: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="Yes - $29 one-time purchase">Yes — $29 one-time purchase is very reasonable</option>
                  <option value="Yes - $9/month with client features">Yes — $9/month if it handles multiple clients</option>
                  <option value="Maybe - depends on automated desktop watcher">Maybe — depends on automated folder watcher</option>
                  <option value="No - I only use free tools">No — I only use free/open-source tools</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  What was missing or what failed during your test?
                </label>
                <input
                  type="text"
                  value={feedback.whatFailed}
                  onChange={(e) => setFeedback({ ...feedback, whatFailed: e.target.value })}
                  placeholder="e.g. OCR struggled on crumpled receipt, needed faster inference..."
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                What critical feature would you need before adopting PocketLedger for your business?
              </label>
              <textarea
                rows={3}
                value={feedback.neededFeatures}
                onChange={(e) => setFeedback({ ...feedback, neededFeatures: e.target.value })}
                placeholder="e.g. Client-specific export, automated email forwarding watcher, native desktop tray..."
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                className="px-6 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition-colors flex items-center shadow-xs"
              >
                <Send className="w-3.5 h-3.5 mr-2 text-emerald-400" />
                Submit Feedback
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
