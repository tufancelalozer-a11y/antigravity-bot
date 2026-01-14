import React, { useState } from 'react';

interface Video {
    title: string;
    url: string;
    id: string;
}

interface ChannelInfo {
    channel_title: string;
    videos: Video[];
    error?: string;
}

export const CompetitorView: React.FC = () => {
    const [channelUrl, setChannelUrl] = useState('');
    const [sortBy, setSortBy] = useState<'new' | 'popular'>('new');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ChannelInfo | null>(null);
    const [copySuccess, setCopySuccess] = useState(false);

    const handleExtract = async () => {
        if (!channelUrl) return;
        setLoading(true);
        setData(null);
        try {
            const response = await fetch('http://localhost:8001/competitor/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: channelUrl, sort_by: sortBy })
            });
            const result = await response.json();
            setData(result);
        } catch (e) {
            console.error(e);
            setData({ channel_title: '', videos: [], error: 'Bağlantı hatası' });
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        if (!data || !data.videos) return;
        const text = data.videos.map(v => v.url).join('\n');
        navigator.clipboard.writeText(text);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Input Header */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 p-8 rounded-3xl relative overflow-hidden group shadow-2xl shadow-black/50">
                <div className="absolute top-0 right-0 w-64 h-64 bg-orange-600/5 rounded-full -mr-32 -mt-32 blur-3xl group-hover:bg-orange-600/10 transition-colors"></div>

                <div className="relative z-10">
                    <h2 className="text-3xl font-extrabold text-white mb-2">Rakip Analizi & NotebookLM</h2>
                    <p className="text-slate-400 mb-8 max-w-2xl">
                        Herhangi bir YouTube kanalındaki videoları saniyeler içinde dökün ve NotebookLM'e aktararak kendi rakiplerinizin yapay zeka klonunu oluşturun.
                    </p>

                    <div className="flex flex-col md:flex-row gap-6">
                        <div className="flex-1 relative">
                            <input
                                type="text"
                                value={channelUrl}
                                onChange={(e) => setChannelUrl(e.target.value)}
                                placeholder="Kanal Linki veya @KullanıcıAdı"
                                className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-6 py-4 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500/50 transition-all placeholder:text-slate-600 pr-12"
                            />
                            {loading && (
                                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                                    <div className="w-5 h-5 border-2 border-orange-500/20 border-t-orange-500 rounded-full animate-spin"></div>
                                </div>
                            )}
                        </div>

                        {/* Sorting Toggle */}
                        <div className="flex bg-slate-950 border border-slate-700 p-1.5 rounded-2xl self-start">
                            <button
                                onClick={() => setSortBy('new')}
                                className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all ${sortBy === 'new' ? 'bg-slate-800 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                            >
                                🆕 En Yeniler
                            </button>
                            <button
                                onClick={() => setSortBy('popular')}
                                className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all ${sortBy === 'popular' ? 'bg-orange-600 text-white shadow-lg shadow-orange-900/40' : 'text-slate-500 hover:text-slate-300'}`}
                            >
                                🔥 En Popülerler
                            </button>
                        </div>

                        <button
                            onClick={handleExtract}
                            disabled={loading || !channelUrl}
                            className="bg-orange-600 hover:bg-orange-500 disabled:opacity-50 disabled:hover:bg-orange-600 text-white font-bold px-8 py-4 rounded-2xl transition-all shadow-lg shadow-orange-900/40 active:scale-95 whitespace-nowrap"
                        >
                            {loading ? 'Analiz Ediliyor...' : 'Videoları Bul'}
                        </button>
                    </div>
                </div>
            </div>

            {data && !data.error && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[600px]">
                    <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-3xl p-6 overflow-hidden flex flex-col shadow-xl">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                📺 {data.channel_title} <span className="text-slate-500 text-sm font-normal">({data.videos.length} {sortBy === 'popular' ? 'Popüler' : 'Yeni'} Video)</span>
                            </h3>
                            <button
                                onClick={copyToClipboard}
                                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${copySuccess ? 'bg-emerald-500 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
                            >
                                {copySuccess ? '✅ Kopyalandı!' : '📋 NotebookLM İçin Tüm Linkleri Kopyala'}
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto space-y-2 pr-2 custom-scrollbar">
                            {data.videos.map((video, idx) => (
                                <div key={idx} className="flex items-center gap-4 bg-slate-950/50 p-3 rounded-xl border border-white/5 hover:border-white/10 transition-colors group">
                                    <span className="text-xs text-slate-600 font-mono w-4">{idx + 1}</span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-slate-200 truncate">{video.title}</p>
                                        <p className="text-[10px] text-slate-500 truncate">{video.url}</p>
                                    </div>
                                    <a
                                        href={video.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white"
                                    >
                                        🔗
                                    </a>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-slate-900 border border-orange-900/20 rounded-3xl p-8 flex flex-col shadow-xl relative overflow-hidden">
                        <div className="absolute -bottom-16 -right-16 w-48 h-48 bg-orange-600/5 rounded-full blur-3xl"></div>
                        <h4 className="text-orange-500 font-bold uppercase tracking-widest text-xs mb-4">NotebookLM Aktarım Rehberi</h4>

                        <div className="space-y-6 relative z-10">
                            <div className="flex gap-4">
                                <div className="w-8 h-8 rounded-lg bg-orange-600/20 text-orange-500 flex items-center justify-center font-bold flex-shrink-0">1</div>
                                <p className="text-sm text-slate-300 leading-relaxed">Yukarıdaki <b>Kopyala</b> butonuyla tüm linkleri hafızaya alın.</p>
                            </div>
                            <div className="flex gap-4">
                                <div className="w-8 h-8 rounded-lg bg-orange-600/20 text-orange-500 flex items-center justify-center font-bold flex-shrink-0">2</div>
                                <p className="text-sm text-slate-300 leading-relaxed">Google <b>NotebookLM</b> sitesini açın ve yeni bir defter oluşturun.</p>
                            </div>
                            <div className="flex gap-4">
                                <div className="w-8 h-8 rounded-lg bg-orange-600/20 text-orange-500 flex items-center justify-center font-bold flex-shrink-0">3</div>
                                <p className="text-sm text-slate-300 leading-relaxed"><b>WebSync</b> veya <b>NotebookLMorter</b> eklentisini kullanarak kopyaladığınız linkleri tek tıkla topluca yükleyin.</p>
                            </div>

                            <div className="mt-8 p-4 bg-orange-600/10 rounded-2xl border border-orange-600/20">
                                <p className="text-xs text-orange-400 leading-relaxed">
                                    💡 <b>İpucu:</b> Kanal klonlandığında yapay zekaya "Bu kanal sahibinin en sık kullandığı 5 kurgu tekniği nedir?" diye sormayı deneyin.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {data?.error && (
                <div className="bg-rose-500/10 border border-rose-500/20 p-6 rounded-3xl text-rose-400 font-bold text-center">
                    ❌ Hata: {data.error}
                </div>
            )}
        </div>
    );
};
