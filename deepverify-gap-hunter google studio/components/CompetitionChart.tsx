
import React from 'react';
import { 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  ZAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell,
  Label
} from 'recharts';
import { TechTopic } from '../types';

interface Props {
  topics: TechTopic[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-slate-800 border border-slate-700 p-3 rounded-lg shadow-xl text-sm">
        <p className="font-bold text-white mb-1">{data.name}</p>
        <p className="text-blue-400">İlgi: %{data.interest}</p>
        <p className="text-red-400">Rekabet: %{data.competition}</p>
        <p className="text-emerald-400 mt-1">Niş Skoru: {data.nicheScore}/100</p>
      </div>
    );
  }
  return null;
};

export const CompetitionChart: React.FC<Props> = ({ topics }) => {
  return (
    <div className="w-full h-[400px] mt-8 bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
      <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
        <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
        İlgi vs. Rekabet Matrisi
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <XAxis 
            type="number" 
            dataKey="interest" 
            name="İlgi" 
            unit="%" 
            stroke="#94a3b8"
            domain={[0, 100]}
          >
            <Label value="Pazar İlgisi (%)" offset={-10} position="insideBottom" fill="#94a3b8" />
          </XAxis>
          <YAxis 
            type="number" 
            dataKey="competition" 
            name="Rekabet" 
            unit="%" 
            stroke="#94a3b8"
            domain={[0, 100]}
          >
            <Label value="Rekabet Düzeyi (%)" angle={-90} position="insideLeft" fill="#94a3b8" />
          </YAxis>
          <ZAxis type="number" dataKey="nicheScore" range={[100, 1000]} name="Niş Skoru" />
          <Tooltip content={<CustomTooltip />} />
          <Scatter name="Teknoloji Konuları" data={topics}>
            {topics.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.nicheScore > 70 ? '#10b981' : entry.nicheScore > 40 ? '#3b82f6' : '#ef4444'} 
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="mt-4 flex justify-center gap-6 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
          <span>Yüksek Niş Fırsatı (Mavi Okyanus)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span>Dengeli Pazar</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span>Doymuş Pazar</span>
        </div>
      </div>
    </div>
  );
};
