
import React, { useEffect, useState } from 'react';

interface ArbitrageOpp {
    symbol: string;
    binance_price: number; // For backward compatibility/avg display
    kraken_price: number; // For backward compatibility/avg display
    spread_usd: number;
    spread_pct: number;
    buy_at: string;
    sell_at: string;
    buy_price: number;
    sell_price: number;
    timestamp: string;
}

export const ArbitrageView: React.FC = () => {
    const [opps, setOpps] = useState<ArbitrageOpp[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchArbitrage = async () => {
        try {
            setLoading(true);
            const res = await fetch('http://127.0.0.1:8001/arbitrage');
            if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);

            const json = await res.json();

            if (json.error) {
                setError(`API Hatası: ${json.error}`);
            } else {
                setOpps(json.data || []);
                setError(null);
            }
        } catch (e: any) {
            console.error("Fetch Error:", e);
            setError(`Bağlantı Hatası: ${e.message}`);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchArbitrage();
        const interval = setInterval(fetchArbitrage, 15000); // Higher interval for multi-scan
        return () => clearInterval(interval);
    }, []);

    const safeFix = (val: number | undefined | null, precision = 2) => {
        if (typeof val !== 'number') return "0.00";
        return val.toFixed(precision);
    };

    return (
        <div className="animate-in fade-in duration-500 pb-20">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                        ⚡ Arbitraj Hub
                        <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded-lg border border-blue-500/30">MULTI-EXCHANGE</span>
                    </h2>
                    <p className="text-slate-400 mt-2">Binance, Kraken ve Bybit arasındaki en kârlı {opps.length} fırsat listeleniyor.</p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="text-right hidden sm:block">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Son Tarama</p>
                        <p className="text-xs text-slate-300 font-mono">{opps.length > 0 ? opps[0].timestamp : '--:--:--'}</p>
                    </div>
                    <button
                        onClick={fetchArbitrage}
                        disabled={loading}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all ${loading ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 active:scale-95'}`}
                    >
                        {loading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                Taranıyor...
                            </>
                        ) : '🔄 Şimdi Tara'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl text-red-400 mb-6 flex items-center gap-3">
                    <span className="text-xl">⚠️</span>
                    <div>
                        <p className="font-bold">Bağlantı Sorunu</p>
                        <p className="text-sm opacity-80">{error}</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {opps.map((opp, i) => (
                    <div key={i} className={`group relative p-5 rounded-2xl border transition-all duration-300 hover:translate-y-[-4px] ${opp.spread_pct > 0.5 ? 'bg-emerald-950/20 border-emerald-500/40 shadow-xl shadow-emerald-950/10' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'}`}>

                        <div className="flex justify-between items-start mb-5">
                            <div>
                                <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">{opp.symbol.split('/')[0]}<span className="text-slate-500 text-sm">/USDT</span></h3>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-[9px] px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded-md font-bold uppercase tracking-tighter">Spot</span>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className={`inline-block px-2 py-1 rounded-lg font-bold text-sm ${opp.spread_pct > 0.5 ? 'bg-emerald-500 text-white' : 'bg-slate-800 text-emerald-400'}`}>
                                    %{safeFix(opp.spread_pct)}
                                </div>
                                <p className="text-[10px] font-mono mt-1 text-slate-500">${safeFix(opp.spread_usd, 4)}</p>
                            </div>
                        </div>

                        <div className="space-y-3 bg-black/30 p-4 rounded-xl border border-white/5">
                            <div className="flex justify-between items-center text-xs">
                                <div className="flex flex-col">
                                    <span className="text-slate-500 font-bold uppercase text-[9px]">ALIŞ</span>
                                    <span className="text-white font-bold">{opp.buy_at}</span>
                                </div>
                                <span className="text-white font-mono font-bold">{safeFix(opp.buy_price, opp.buy_price < 1 ? 4 : 2)}$</span>
                            </div>

                            <div className="relative h-4 flex items-center justify-center">
                                <div className="absolute w-full h-px bg-slate-800"></div>
                                <div className="relative bg-slate-900 px-2 text-[10px] text-slate-600 font-bold">&gt;&gt;&gt;</div>
                            </div>

                            <div className="flex justify-between items-center text-xs">
                                <div className="flex flex-col">
                                    <span className="text-slate-500 font-bold uppercase text-[9px]">SATIŞ</span>
                                    <span className="text-emerald-400 font-bold">{opp.sell_at}</span>
                                </div>
                                <span className="text-emerald-400 font-mono font-bold">{safeFix(opp.sell_price, opp.sell_price < 1 ? 4 : 2)}$</span>
                            </div>
                        </div>

                        {opp.spread_pct > 0.5 && (
                            <div className="mt-4 flex items-center justify-center gap-2 text-emerald-400">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                <span className="text-[10px] font-bold uppercase tracking-widest">Aktif Fırsat</span>
                            </div>
                        )}
                    </div>
                ))}

                {!loading && opps.length === 0 && !error && (
                    <div className="col-span-full py-20 text-center bg-slate-900/40 border border-dashed border-slate-700 rounded-3xl">
                        <div className="text-4xl mb-4">🔍</div>
                        <h3 className="text-white font-bold text-lg">Şu an kârlı fark bulunamadı</h3>
                        <p className="text-slate-500 text-sm mt-1">Piyasalar durgun. Otomatik tarama devam ediyor...</p>
                    </div>
                )}
            </div>

            <div className="mt-12 p-6 bg-blue-600/5 border border-blue-500/20 rounded-2xl flex items-start gap-4">
                <div className="w-10 h-10 bg-blue-600/20 rounded-full flex items-center justify-center text-blue-400 shrink-0">ℹ️</div>
                <div>
                    <h4 className="text-blue-400 font-bold">Ölçeklendirme Notu</h4>
                    <p className="text-slate-400 text-sm mt-1 leading-relaxed">
                        Sistem şu an 3 ana borsa ve en popüler 15 parite üzerinde **paralel** tarama yapmaktadır.
                        Tüm borsalar ve binlerce parite eklendiğinde sistem tıkandığı için, sadece hacmi yüksek ve kâr ihtimali olan "Altın Liste"ye odaklanıyoruz.
                    </p>
                </div>
            </div>
        </div>
    );
};
