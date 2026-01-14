
import React from 'react';

interface GapScoreCardProps {
    score: number;
    interest: number;
    competition: number;
}

export const GapScoreCard: React.FC<GapScoreCardProps> = ({ score, interest, competition }) => {
    // Determine color based on score
    const getColor = (s: number) => {
        if (s >= 80) return "text-emerald-400"; // Excellent
        if (s >= 50) return "text-blue-400";    // Good
        return "text-amber-400";                // Average/Risky
    };

    const getBgColor = (s: number) => {
        if (s >= 80) return "bg-emerald-500";
        if (s >= 50) return "bg-blue-500";
        return "bg-amber-500";
    };

    const getLabel = (s: number) => {
        if (s >= 80) return "💎 MÜKEMMEL FIRSAT";
        if (s >= 50) return "🔥 GÜÇLÜ POTANSİYEL";
        return "⚖️ DENGELİ / RİSKLİ";
    };

    return (
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
            <h4 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">Gap Hunter Skoru</h4>

            <div className="relative w-32 h-32 flex items-center justify-center mb-4">
                {/* Background Circle */}
                <svg className="w-full h-full transform -rotate-90">
                    <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="12"
                        fill="transparent"
                        className="text-slate-800"
                    />
                    {/* Progress Circle */}
                    <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="12"
                        fill="transparent"
                        strokeDasharray={351.86} // 2 * pi * r
                        strokeDashoffset={351.86 - (351.86 * score) / 100}
                        className={`${getColor(score)} transition-all duration-1000 ease-out`}
                        strokeLinecap="round"
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-4xl font-bold ${getColor(score)}`}>{score}</span>
                </div>
            </div>

            <div className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase mb-6 ${getColor(score).replace('text-', 'bg-').replace('400', '500/10')}`}>
                {getLabel(score)}
            </div>

            <div className="w-full space-y-3">
                <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Aranma Hacmi</span>
                    <span className="text-emerald-400 font-bold">%{interest}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Rekabet Yoğunluğu</span>
                    <span className="text-rose-400 font-bold">%{competition}</span>
                </div>
            </div>
        </div>
    );
};
