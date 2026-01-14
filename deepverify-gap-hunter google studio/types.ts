
export interface TechTopic {
  name: string;
  interest: number; // 1-100
  competition: number; // 1-100
  growth: string;
  description: string;
  nicheScore: number;
}

export interface AnalysisResult {
  report: string;
  topics: TechTopic[];
  sources: Array<{
    title: string;
    uri: string;
  }>;
}

export enum AnalysisStatus {
  IDLE = 'IDLE',
  LOADING = 'LOADING',
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR'
}
