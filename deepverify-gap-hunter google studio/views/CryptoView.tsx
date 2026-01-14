
import React, { useEffect, useState } from 'react';

interface BotInfo {
    id: number;
    name: string;
    strategy: string;
    balance: number;
    pnl: number;
    active_trade: any;
}

interface BotStatus {
    active: boolean;
    total_pnl: number;
    global_balance: number;
    bot_count: number;
    last_update: string;
}

interface Trade {
    Bot: string;
    Date: string;
    Side: string;
    Entry: number;
    Exit: number;
    PnL: number;
    Balance: number;
}

export const CryptoView: React.FC = () => {
    const [status, setStatus] = useState<BotStatus | null>(null);
    const [bots, setBots] = useState<BotInfo[]>([]);
    const [logs, setLogs] = useState<string[]>([]);
    const [history, setHistory] = useState<Trade[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            // Fetch Status
            const resStatus = await fetch('http://localhost:8001/status');
            const dataStatus = await resStatus.json();
            setStatus(dataStatus);

            // Fetch Bots
            const resBots = await fetch('http://localhost:8001/bots');
            const dataBots = await resBots.json();
            setBots(dataBots.bots || []);

            // Fetch Logs
            const resLogs = await fetch('http://localhost:8001/logs');
            const dataLogs = await resLogs.json();
            setLogs(dataLogs.logs || []);

            // Fetch History
            const resHistory = await fetch('http://localhost:8001/history');
            const dataHistory = await resHistory.json();
            setHistory(dataHistory.trades || []);

            setLoading(false);
        } catch (e) {
            console.error("Bridge API Error", e);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-bl-full transition-transform group-hover:scale-110"></div>
                    <div>
                        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">Global PnL (Toplam)</p>
                        <h2 className={`text-4xl font-bold mt-2 ${status && status.total_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                            {status ? `${status.total_pnl.toFixed(2)}$` : "..."}
                        </h2>
                    </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-bl-full transition-transform group-hover:scale-110"></div>
                    <div>
                        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">Global Bakiye</p>
                        <h2 className="text-4xl font-bold text-white mt-2">
                            {status ? `${status.global_balance.toFixed(2)}$` : "..."}
                        </h2>
                    </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-bl-full transition-transform group-hover:scale-110"></div>
                    <div>
                        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">Müfreze Durumu</p>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                            </span>
                            <h2 className="text-xl font-bold text-emerald-400">4 BOT AKTİF</h2>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bots Quadrant Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {bots.map((bot) => (
                    <div key={bot.id} className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl relative overflow-hidden backdrop-blur-sm">
                        <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-white">{bot.name}</h4>
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${bot.active_trade ? "bg-blue-500 text-white" : "bg-slate-800 text-slate-500"}`}>
                                {bot.active_trade ? bot.active_trade.side : "NÖBETTE"}
                            </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mb-3">{bot.strategy}</p>
                        <div className="flex justify-between items-end">
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase">PnL</p>
                                <p className={`text-sm font-bold ${bot.pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                                    {bot.pnl >= 0 ? "+" : ""}{bot.pnl.toFixed(2)}$
                                </p>
                            </div>
                            <div className="text-right">
                                <p className="text-[10px] text-slate-500 uppercase">Bakiye</p>
                                <p className="text-sm font-bold text-white">{bot.balance.toFixed(2)}$</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* History Table */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-md">
                <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-800/20">
                    <h3 className="font-bold text-white flex items-center gap-2">
                        <span className="text-blue-400">📜</span> Son İşlemler (Canlı Geçmiş)
                    </h3>
                    <span className="text-[10px] text-slate-500 font-mono">SQLITE + REALTIME</span>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-800/30 text-slate-400 text-[10px] uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-3 font-bold">Bot</th>
                                <th className="px-6 py-3 font-bold">Tarih</th>
                                <th className="px-6 py-3 font-bold">Yön</th>
                                <th className="px-6 py-3 font-bold">Giriş</th>
                                <th className="px-6 py-3 font-bold">Çıkış</th>
                                <th className="px-6 py-3 font-bold">PnL</th>
                                <th className="px-6 py-3 font-bold">Bakiye</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50 text-slate-300">
                            {history.length > 0 ? history.map((trade, i) => (
                                <tr key={i} className="hover:bg-slate-800/30 transition-colors group">
                                    <td className="px-6 py-3 font-medium text-blue-400/80">{trade.Bot}</td>
                                    <td className="px-6 py-3 text-slate-500 text-xs font-mono">{trade.Date}</td>
                                    <td className="px-6 py-3">
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${trade.Side === 'LONG' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                            {trade.Side}
                                        </span>
                                    </td>
                                    <td className="px-6 py-3 font-mono">{trade.Entry.toFixed(2)}</td>
                                    <td className="px-6 py-3 font-mono">{trade.Exit.toFixed(2)}</td>
                                    <td className={`px-6 py-3 font-bold ${trade.PnL >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                                        {trade.PnL >= 0 ? "+" : ""}{trade.PnL.toFixed(2)}$
                                    </td>
                                    <td className="px-6 py-3 text-white font-bold">{trade.Balance.toFixed(2)}$</td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan={7} className="px-6 py-10 text-center text-slate-600 italic">
                                        Henüz işlem kaydı bulunamadı.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[500px]">
                {/* Sol: Terminal Log */}
                <div className="lg:col-span-2 bg-[#0B1120] border border-slate-800 rounded-2xl p-4 flex flex-col font-mono text-xs overflow-hidden shadow-inner shadow-black/50">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-800/50">
                        <span className="text-slate-500 font-bold">QUADRANT COMMAND CENTER</span>
                        <div className="flex gap-1.5">
                            <div className="w-2.5 h-2.5 rounded-full bg-red-500/20"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-green-500/20"></div>
                        </div>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-1 pr-2" id="log-container">
                        {logs.slice().reverse().map((log, i) => (
                            <div key={i} className={`break-words ${log.includes('Hata') ? 'text-red-400' : log.includes('KAPANDI') ? 'text-emerald-400 font-bold' : log.includes('GIRILDI') ? 'text-blue-400 font-bold' : 'text-slate-400'}`}>
                                <span className="opacity-30 mr-2">{logs.length - i}</span>
                                {log}
                            </div>
                        ))}
                        {logs.length === 0 && <div className="text-slate-600 italic">Veri bekleniyor...</div>}
                    </div>
                </div>

                {/* Sağ: Quick Stats */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-4">🛡️ Risk Kontrolü</h3>
                    <div className="space-y-4">
                        <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                            <p className="text-[10px] text-slate-500 uppercase font-bold">Aktif Koruma</p>
                            <p className="text-xs text-slate-300 mt-1">Sistem tüm botlar için Trailing Stop ve %2 Stop-Loss limitlerini takip ediyor.</p>
                        </div>
                        <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                            <p className="text-[10px] text-slate-500 uppercase font-bold">Kaldıraç</p>
                            <p className="text-xs text-slate-300 mt-1">Tüm botlar 50x izole kaldıraç ile işlem yapıyor.</p>
                        </div>
                    </div>
                    <div className="mt-auto pt-6 border-t border-slate-800">
                        <p className="text-[10px] text-slate-500 uppercase mb-2">Sistem Zamanı</p>
                        <p className="text-sm font-bold text-white">{status?.last_update || "..."}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
