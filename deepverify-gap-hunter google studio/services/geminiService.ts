
import { AnalysisResult, TechTopic } from "../types";

export const analyzeTurkishTechMarket = async (category: string = "Teknoloji"): Promise<AnalysisResult> => {
  try {
    const response = await fetch("/.netlify/functions/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Sunucu hatası");
    }

    const { fullText, sources } = await response.json();

    // Extract JSON data
    const dataMatch = fullText.match(/DATA_START\s*([\s\S]*?)\s*DATA_END/);
    let topics: TechTopic[] = [];
    let cleanReport = fullText.replace(/DATA_START[\s\S]*DATA_END/, "").trim();

    if (dataMatch && dataMatch[1]) {
      try {
        const jsonStr = dataMatch[1].replace(/```json/g, "").replace(/```/g, "").trim();
        topics = JSON.parse(jsonStr);
      } catch (e) {
        console.error("JSON parsing error", e);
        cleanReport += "\n\n(Not: Veri görselleştirme için JSON ayrıştırılamadı, lütfen tekrar deneyin.)";
      }
    }

    return {
      report: cleanReport,
      topics,
      sources,
    };
  } catch (error: any) {
    console.error("Frontend Service Error:", error);
    throw new Error(error.message || "Analiz başarısız oldu.");
  }
};

export const generateBlueprint = async (topicName: string, type: 'VIDEO' | 'CODE'): Promise<string> => {
  try {
    const response = await fetch("/.netlify/functions/blueprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topicName, type }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "İçerik üretilemedi.");
    }

    const result = await response.json();
    return result.text || "İçerik üretilemedi.";
  } catch (e: any) {
    console.error("Blueprint Gen Error", e);
    throw new Error("İçerik üretilemedi: " + e.message);
  }
};

