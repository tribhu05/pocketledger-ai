import React from 'react';
import { 
  Receipt, 
  LayoutDashboard, 
  UploadCloud, 
  TableProperties, 
  FileSpreadsheet, 
  ShieldCheck, 
  Sparkles,
  Cpu,
  AlertTriangle,
  CreditCard
} from 'lucide-react';
import { SystemStatus } from '../types';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  status: SystemStatus | null;
  awaitingReviewCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  status,
  awaitingReviewCount,
}) => {
  const isGemmaActive = status?.current_mode === 'gemma2_local';

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-30 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Tagline */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Receipt className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">PocketLedger</span>
                <span className="px-1.5 py-0.5 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  AI
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Your receipts. Your records. Your data stays yours.
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            <button
              onClick={() => setCurrentTab('dashboard')}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'dashboard'
                  ? 'bg-slate-800 text-white border-b-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <LayoutDashboard className="w-4 h-4 mr-1.5" />
              Dashboard
            </button>

            <button
              onClick={() => setCurrentTab('inbox')}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'inbox'
                  ? 'bg-slate-800 text-white border-b-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <UploadCloud className="w-4 h-4 mr-1.5" />
              Inbox & Upload
            </button>

            <button
              onClick={() => setCurrentTab('ledger')}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors relative ${
                currentTab === 'ledger'
                  ? 'bg-slate-800 text-white border-b-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <TableProperties className="w-4 h-4 mr-1.5" />
              Ledger
              {awaitingReviewCount > 0 && (
                <span className="ml-2 px-1.5 py-0.2 text-xs font-semibold rounded-full bg-amber-500 text-slate-950">
                  {awaitingReviewCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setCurrentTab('reports')}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'reports'
                  ? 'bg-slate-800 text-white border-b-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <FileSpreadsheet className="w-4 h-4 mr-1.5" />
              Reports & CSV
            </button>

            <button
              onClick={() => setCurrentTab('pricing')}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'pricing'
                  ? 'bg-slate-800 text-white border-b-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <CreditCard className="w-4 h-4 mr-1.5" />
              Pricing & Side Hustle
            </button>

            <button
              onClick={() => setCurrentTab('settings')}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'settings'
                  ? 'bg-slate-800 text-white border-b-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-4 h-4 mr-1.5" />
              Privacy & Status
            </button>
          </nav>

          {/* System Status Pill */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setCurrentTab('settings')}
              className="flex items-center space-x-2 px-2.5 py-1.5 rounded-full bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs transition-colors"
              title="Click to view full privacy and model status"
            >
              <span className={`w-2 h-2 rounded-full ${isGemmaActive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="font-medium text-slate-200">
                {isGemmaActive ? 'Gemma 2B Local' : 'Local Fallback'}
              </span>
              <span className="text-slate-500">|</span>
              <span className="text-emerald-400 font-medium">100% On-Device</span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile navigation bar */}
      <div className="md:hidden flex overflow-x-auto py-2 px-4 space-x-2 bg-slate-950 border-t border-slate-800">
        {['dashboard', 'inbox', 'ledger', 'reports', 'pricing', 'settings'].map((tab) => (
          <button
            key={tab}
            onClick={() => setCurrentTab(tab)}
            className={`px-3 py-1 rounded text-xs font-medium whitespace-nowrap capitalize ${
              currentTab === tab ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab}
            {tab === 'ledger' && awaitingReviewCount > 0 && ` (${awaitingReviewCount})`}
          </button>
        ))}
      </div>
    </header>
  );
};
