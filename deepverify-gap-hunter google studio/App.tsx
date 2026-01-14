
import React, { useState } from 'react';
import { GapHunterView } from './views/GapHunterView';
import { CryptoView } from './views/CryptoView';
import { ArbitrageView } from './views/ArbitrageView';
import { CompetitorView } from './views/CompetitorView';

type View = 'HUNTER' | 'CRYPTO' | 'ARBITRAGE' | 'COMPETITOR';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<View>('HUNTER');

  return (
    <div className="flex min-h-screen bg-[#0f172a] text-slate-200 font-sans overflow-hidden">

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col z-20">

        {/* Logo Area */}
        <div className="h-20 flex items-center px-6 border-b border-slate-800 bg-slate-905/50">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center font-bold text-white shadow-lg shadow-blue-900/20 mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white leading-none">
              ANA GEMİ
            </h1>
            <p className="text-[10px] text-blue-400 font-bold tracking-widest uppercase">DeepVerify OS</p>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setCurrentView('HUNTER')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${currentView === 'HUNTER' ? 'bg-blue-600 text-white shadow-blue-900/20 shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white dark:hover:bg-slate-800'}`}
          >
            <span>🏹</span> Gap Hunter
          </button>
          <button
            onClick={() => setCurrentView('CRYPTO')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${currentView === 'CRYPTO' ? 'bg-purple-600 text-white shadow-purple-900/20 shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
          >
            <span>🤖</span> Kripto Kule
          </button>
          <button
            onClick={() => setCurrentView('ARBITRAGE')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${currentView === 'ARBITRAGE' ? 'bg-emerald-600 text-white shadow-emerald-900/20 shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
          >
            <span>⚡</span> Arbitraj
            <span className="ml-auto text-[9px] bg-emerald-500/20 px-1.5 py-0.5 rounded text-emerald-400 font-bold">LIVE</span>
          </button>
          <button
            onClick={() => setCurrentView('COMPETITOR')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${currentView === 'COMPETITOR' ? 'bg-orange-600 text-white shadow-orange-900/20 shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
          >
            <span>🎯</span> Rakip Analizi
          </button>
        </nav>

        {/* Status Footer */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-4 py-3 bg-slate-800/50 rounded-xl border border-slate-800/50">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            <span className="text-xs text-emerald-400 font-bold">Sistem Çevrimiçi</span>
          </div>
        </div>

      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto relative">
        <div className="max-w-7xl mx-auto px-8 py-10">
          {currentView === 'HUNTER' && <GapHunterView />}
          {currentView === 'CRYPTO' && <CryptoView />}
          {currentView === 'ARBITRAGE' && <ArbitrageView />}
          {currentView === 'COMPETITOR' && <CompetitorView />}
        </div>
      </main>

    </div >
  );
};

export default App;
