
import React from 'react';

interface BlueprintModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    content: string;
    isLoading: boolean;
}

export const BlueprintModal: React.FC<BlueprintModalProps> = ({
    isOpen,
    onClose,
    title,
    content,
    isLoading
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            ></div>

            {/* Modal Content */}
            <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-900">
                    <div>
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <span className="text-blue-400">⚡</span>
                            {isLoading ? 'Blueprint Hazırlanıyor...' : 'AI Blueprint'}
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">
                            {isLoading ? 'Google AI sunucularında içerik üretiliyor.' : title}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Body */}
                <div className="flex-1 overflow-y-auto p-6 bg-[#0B1120]">
                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center h-64 space-y-4">
                            <div className="relative w-16 h-16">
                                <div className="absolute inset-0 border-4 border-slate-800 rounded-full"></div>
                                <div className="absolute inset-0 border-4 border-t-blue-500 border-r-purple-500 border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                            </div>
                            <p className="text-slate-400 animate-pulse">Kod ve strateji yazılıyor...</p>
                        </div>
                    ) : (
                        <div className="prose prose-invert max-w-none prose-pre:bg-slate-800 prose-pre:border prose-pre:border-slate-700">
                            <div className="whitespace-pre-wrap font-mono text-sm text-slate-300">
                                {content}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                {!isLoading && (
                    <div className="p-4 border-t border-slate-800 bg-slate-900 flex justify-end gap-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-slate-300 hover:text-white font-medium transition-colors"
                        >
                            Kapat
                        </button>
                        <button
                            onClick={() => navigator.clipboard.writeText(content)}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-95 flex items-center gap-2"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                            </svg>
                            Kopyala
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};
