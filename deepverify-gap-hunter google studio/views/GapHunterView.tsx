
import React, { useState } from 'react';
import { analyzeTurkishTechMarket, generateBlueprint } from '../services/geminiService';
import { AnalysisResult, AnalysisStatus } from '../types';
import { CompetitionChart } from '../components/CompetitionChart';
import { GapScoreCard } from '../components/GapScoreCard';
import { BlueprintModal } from '../components/BlueprintModal';

export const GapHunterView: React.FC = () => {
    const [status, setStatus] = useState<AnalysisStatus>(AnalysisStatus.IDLE);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Blueprint State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [blueprintContent, setBlueprintContent] = useState("");
    const [blueprintTitle, setBlueprintTitle] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    const handleStartAnalysis = async (category: string = "Teknoloji") => {
        setStatus(AnalysisStatus.LOADING);
        setError(null);
        try {
            const data = await analyzeTurkishTechMarket(category);
            setResult(data);
            setStatus(AnalysisStatus.SUCCESS);
        } catch (err: any) {
            setError(err.message || "Analiz sırasında bir hata oluştu.");
            setStatus(AnalysisStatus.ERROR);
        }
    };

    const handleGenerate = async (topicName: string, type: 'VIDEO' | 'CODE') => {
        setIsModalOpen(true);
        setIsGenerating(true);
        setBlueprintTitle(type === 'VIDEO' ? `${topicName} - Video Senaryosu` : `${topicName} - Kod Başlangıç Kiti`);
        setBlueprintContent("");

        try {
            const content = await generateBlueprint(topicName, type);
            setBlueprintContent(content);
        } catch (e: any) {
            setBlueprintContent("Hata oluştu: " + e.message);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="animate-in fade-in duration-500">
            <BlueprintModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={blueprintTitle}
                content={blueprintContent}
                isLoading={isGenerating}
            />

            {status === AnalysisStatus.IDLE && (
                <div className="flex flex-col items-center justify-center py-24 text-center">
                    <div className="w-24 h-24 bg-gradient-to-tr from-blue-500/20 to-indigo-500/20 rounded-full flex items-center justify-center mb-8 ring-1 ring-blue-500/30 shadow-[0_0_50px_-12px_rgba(59,130,246,0.5)]">
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white tracking-tight">
                        Pazardaki <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Gizli Fırsatları</span> Yakala
                    </h2>
                    <p className="text-slate-400 text-lg max-w-2xl mb-12 leading-relaxed">
                        Google'ın gerçek zamanlı arama verilerini kullanarak, yüksek talep gören ancak henüz yeterince kaliteli içeriğin olmadığı "boşlukları" (content gaps) saniyeler içinde tespit et.
                    </p>

                    <div className="w-full max-w-md bg-slate-800/50 p-2 rounded-2xl border border-slate-700 shadow-xl flex gap-2">
                        <input
                            type="text"
                            placeholder="Hangi alanda fırsat arıyorsun? (Örn: Yapay Zeka, Kripto, Sağlık)"
                            className="flex-1 bg-transparent border-none text-white placeholder-slate-500 px-4 focus:ring-0 text-lg"
                            onKeyDown={(e) => e.key === 'Enter' && handleStartAnalysis((e.target as HTMLInputElement).value)}
                            id="categoryInput"
                        />
                        <button
                            onClick={() => {
                                const input = document.getElementById('categoryInput') as HTMLInputElement;
                                handleStartAnalysis(input.value || "Teknoloji");
                            }}
                            disabled={status === AnalysisStatus.LOADING}
                            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-95 whitespace-nowrap"
                        >
                            🚀 TARA
                        </button>
                    </div>

                    <div className="mt-8 flex gap-4 text-sm text-slate-500">
                        <span className="flex items-center gap-1">✨ Trend Analizi</span>
                        <span className="flex items-center gap-1">•</span>
                        <span className="flex items-center gap-1">📊 Rekabet Ölçümü</span>
                        <span className="flex items-center gap-1">•</span>
                        <span className="flex items-center gap-1">💡 İçerik Stratejisi</span>
                    </div>
                </div>
            )}

            {status === AnalysisStatus.ERROR && (
                <div className="max-w-2xl mx-auto bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center backdrop-blur-sm">
                    <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-red-500">⚠️</div>
                    <h3 className="text-xl font-bold text-white mb-2">Analiz Tamamlanamadı</h3>
                    <p className="text-red-300 mb-6">{error}</p>
                    <button
                        onClick={() => setStatus(AnalysisStatus.IDLE)}
                        className="px-6 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg font-medium transition-colors"
                    >
                        Tekrar Dene
                    </button>
                </div>
            )}

            {status === AnalysisStatus.LOADING && (
                <div className="max-w-4xl mx-auto text-center py-20">
                    <div className="relative w-24 h-24 mx-auto mb-8">
                        <div className="absolute inset-0 border-4 border-slate-800 rounded-full"></div>
                        <div className="absolute inset-0 border-4 border-t-blue-500 border-r-emerald-500 border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">Pazar Taranıyor...</h3>
                    <p className="text-slate-400">Google Search verileri analiz ediliyor, rekabet ölçülüyor.</p>
                </div>
            )}

            {status === AnalysisStatus.SUCCESS && result && (
                <div className="space-y-16 animate-in fade-in slide-in-from-bottom-4 duration-700">

                    {/* Hero Section of Results */}
                    <div className="flex flex-col md:flex-row gap-8 items-start">
                        <div className="flex-1">
                            <h2 className="text-3xl font-bold text-white mb-6">
                                Bulunan <span className="text-emerald-400">En İyi Fırsatlar</span>
                            </h2>
                            <p className="text-slate-400 leading-relaxed mb-8">
                                Yapay zeka analizine göre, aşağıdaki konular şu anda yüksek aranma hacmine sahip olmasına rağmen içerik bakımından zayıf kalmış durumda. Bu "boşluklara" odaklanarak hızlı yükseliş yakalayabilirsin.
                            </p>
                            <div className="flex gap-4">
                                <button onClick={() => setStatus(AnalysisStatus.IDLE)} className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors">
                                    ← Yeni Arama Yap
                                </button>
                            </div>
                        </div>

                        {/* Visual Chart */}
                        <div className="flex-1 w-full bg-slate-900/50 rounded-2xl border border-slate-800/50 p-1">
                            <CompetitionChart topics={result.topics} />
                        </div>
                    </div>

                    {/* Gap Score Cards - The Meat of the App */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {result.topics.map((topic, i) => (
                            <div key={i} className="group relative">
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-2xl opacity-20 group-hover:opacity-100 transition duration-500 blur"></div>
                                <div className="relative bg-slate-900 border border-slate-800 p-6 rounded-2xl h-full flex flex-col">

                                    <div className="flex justify-between items-start mb-6">
                                        <h3 className="text-xl font-bold text-white line-clamp-2 min-h-[3.5rem] group-hover:text-blue-400 transition-colors">
                                            {topic.name}
                                        </h3>
                                        <GapScoreCard
                                            score={topic.nicheScore}
                                            interest={topic.interest}
                                            competition={topic.competition}
                                        />
                                    </div>

                                    <div className="mb-6 flex-1">
                                        <p className="text-slate-400 text-sm leading-relaxed mb-4">
                                            {topic.description}
                                        </p>
                                        <div className="flex items-center gap-2 p-3 bg-slate-800/50 rounded-lg border border-slate-800">
                                            <span className="text-emerald-400 text-lg">📈</span>
                                            <div>
                                                <p className="text-[10px] text-slate-500 uppercase font-bold">Büyüme Tahmini</p>
                                                <p className="text-white font-bold">{topic.growth}</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-slate-800">
                                        <button
                                            onClick={() => handleGenerate(topic.name, 'CODE')}
                                            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                                        >
                                            💻 Kod Üret
                                        </button>
                                        <button
                                            onClick={() => handleGenerate(topic.name, 'VIDEO')}
                                            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                                        >
                                            🎬 Senaryo
                                        </button>
                                    </div>

                                </div>
                            </div>
                        ))}
                    </div>

                    {/* AI Report Text */}
                    <div className="bg-slate-900/40 p-10 rounded-3xl border border-slate-800/60 backdrop-blur-sm">
                        <h2 className="text-2xl font-bold mb-8 flex items-center gap-3 text-white">
                            <span className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400">📄</span>
                            Detaylı Pazar Analizi
                        </h2>
                        <div className="prose prose-invert prose-lg max-w-none prose-p:text-slate-300 prose-headings:text-white prose-strong:text-blue-400 prose-li:text-slate-300 whitespace-pre-line leading-relaxed">
                            {result.report}
                        </div>
                    </div>

                    {/* Footer Sources */}
                    {result.sources.length > 0 && (
                        <div className="border-t border-slate-800 pt-8">
                            <p className="text-sm text-slate-500 mb-4">Analiz için kullanılan canlı veri kaynakları:</p>
                            <div className="flex flex-wrap gap-3">
                                {result.sources.map((source, i) => (
                                    <a key={i} href={source.uri} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 text-xs text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
                                        🔗 {source.title}
                                    </a>
                                ))}
                            </div>
                        </div>
                    )}

                </div>
            )}
        </div>
    );
};
