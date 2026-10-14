import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { DocumentInbox } from './components/DocumentInbox';
import { ExpenseLedger } from './components/ExpenseLedger';
import { ReportsView } from './components/ReportsView';
import { SettingsPrivacy } from './components/SettingsPrivacy';
import { PricingView } from './components/PricingView';
import { ReviewModal } from './components/ReviewModal';
import { Expense, SystemStatus, DashboardSummary } from './types';
import { fetchSystemStatus, fetchDashboard, fetchExpenses, seedDemoWorkspace } from './api';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [initialLedgerFilter, setInitialLedgerFilter] = useState<string>('all');
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [dashboardSummary, setDashboardSummary] = useState<DashboardSummary | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [reviewingExpense, setReviewingExpense] = useState<Expense | null>(null);

  // Load all core data
  const loadData = useCallback(async () => {
    try {
      const [status, dash, list] = await Promise.all([
        fetchSystemStatus().catch(() => null),
        fetchDashboard().catch(() => null),
        fetchExpenses().catch(() => []),
      ]);
      setSystemStatus(status);
      setDashboardSummary(dash);
      setExpenses(list);
    } catch (err) {
      console.error('Error loading PocketLedger data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Navigate with optional filter
  const handleNavigateTab = (tab: string, filter?: string) => {
    if (tab === 'ledger' && filter) {
      setInitialLedgerFilter(filter);
    } else {
      setInitialLedgerFilter('all');
    }
    setCurrentTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSeedDemo = async () => {
    try {
      await seedDemoWorkspace();
      await loadData();
      setCurrentTab('dashboard');
    } catch (err: any) {
      alert(`Seeding demo workspace failed: ${err.message}`);
    }
  };

  const handleUploadSuccess = async (uploaded: Expense[]) => {
    await loadData();
    if (uploaded.length === 1) {
      setReviewingExpense(uploaded[0]);
    } else {
      handleNavigateTab('ledger', 'awaiting_review');
    }
  };

  const handleExpenseSaved = async (updated: Expense) => {
    setExpenses((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
    // Refresh dashboard stats
    const dash = await fetchDashboard().catch(() => null);
    if (dash) setDashboardSummary(dash);
  };

  const awaitingReviewCount = dashboardSummary?.awaiting_review_count || 0;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-900 font-sans">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={(tab) => handleNavigateTab(tab)}
        status={systemStatus}
        awaitingReviewCount={awaitingReviewCount}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {currentTab === 'dashboard' && (
          <DashboardView
            summary={dashboardSummary}
            onNavigateTab={handleNavigateTab}
            onSelectExpenseForReview={(exp) => setReviewingExpense(exp)}
            onSeedDemo={handleSeedDemo}
            loading={loading}
          />
        )}

        {currentTab === 'inbox' && (
          <DocumentInbox
            onUploadSuccess={handleUploadSuccess}
            onNavigateTab={handleNavigateTab}
          />
        )}

        {currentTab === 'ledger' && (
          <ExpenseLedger
            expenses={expenses}
            onSelectExpenseForReview={(exp) => setReviewingExpense(exp)}
            onRefreshData={loadData}
            initialStatusFilter={initialLedgerFilter}
          />
        )}

        {currentTab === 'reports' && (
          <ReportsView expenses={expenses} />
        )}

        {currentTab === 'pricing' && (
          <PricingView />
        )}

        {currentTab === 'settings' && (
          <SettingsPrivacy
            status={systemStatus}
            onRefreshAll={loadData}
          />
        )}
      </main>

      {/* Modal Review Screen */}
      {reviewingExpense && (
        <ReviewModal
          expense={reviewingExpense}
          onClose={() => setReviewingExpense(null)}
          onSaved={handleExpenseSaved}
        />
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-800">PocketLedger AI</span>
            <span>—</span>
            <span>Hacktoberfest Side Hustle Challenge</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center text-emerald-700 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5" />
              100% On-Device Inference
            </span>
            <span>•</span>
            <span className="font-mono text-slate-400">Powered by Gemma 2B & Ollama</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
