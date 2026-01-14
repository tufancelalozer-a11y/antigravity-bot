import { Handler } from "@netlify/functions";
import { GoogleGenAI } from "@google/genai";

export const handler: Handler = async (event, context) => {
    // Only allow POST requests
    if (event.httpMethod !== "POST") {
        return { statusCode: 405, body: "Method Not Allowed" };
    }

    const API_KEY = process.env.VITE_GEMINI_API_KEY;
    if (!API_KEY) {
        return {
            statusCode: 500,
            body: JSON.stringify({ error: "API Key not configured on server." })
        };
    }

    const { category = "Teknoloji" } = JSON.parse(event.body || "{}");

    const ai = new GoogleGenAI({ apiKey: API_KEY });

    const prompt = `
    Sen "Gap Hunter" (Boşluk Avcısı) adında uzman bir analistsin. 
    Görevin: Türkiye pazarında "${category}" kategorisindeki İÇERİK AÇIKLARINI (Content Gaps) bulmak.
    
    Yöntem:
    1. Google Search verilerini kullanarak şu an trend olan veya "Nasıl yapılır", "Nedir" şeklinde çok aratılan konuları bul.
    2. Bu konuları YouTube ve web içeriği yoğunluğu ile karşılaştır.
    3. ARANMA HACMİ YÜKSEK ama KALİTELİ İÇERİK SAYISI AZ olan konuları tespit et.
    
    Her bir konu için şu hesaplamayı yap:
    - **Interest (İlgi):** 0-100 arası (Google Trends/Search hacmine dayalı tahmin)
    - **Competition (Rekabet):** 0-100 arası (Mevcut içerik yoğunluğu)
    - **Gap Score (Fırsat Puanı):** (Interest * 1.5) - Competition. (Eğer sonuç negatifse 0 yap). Bu puan fırsatın büyüklüğünü gösterir.
    
    Çıktı Formatı:
    Analizini önce özetle, ardından TAM OLARAK aşağıdaki JSON formatında "DATA_START" ve "DATA_END" etiketleri arasına veriyi koy.
    
    Raporun içinde şunlara değin:
    - Neden bu konuların seçildiğini kanıtla.
    - Hangi anahtar kelimelerin odaklanılması gerektiğini belirt.
    
    JSON FORMATI:
    DATA_START
    [
      {
        "name": "Konu Başlığı",
        "interest": 85,
        "competition": 20,
        "growth": "%200",
        "description": "Neden fırsat olduğu ve ne tür içerik üretilmesi gerektiği hakkında kısa stratejik tavsiye.",
        "nicheScore": 95
      }
    ]
    DATA_END
  `;

    try {
        const response = await ai.models.generateContent({
            model: "gemini-1.5-flash",
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
            config: {
                tools: [{ type: 'google_search' } as any]
            }
        });

        const fullText = response.text || "";

        // Extract sources from grounding metadata if available
        const groundingMetadata = response.candidates?.[0]?.groundingMetadata;
        const sources = groundingMetadata?.groundingChunks
            ?.filter((chunk: any) => chunk.web)
            ?.map((chunk: any) => ({
                title: chunk.web.title || "Google Search Kaynağı",
                uri: chunk.web.uri,
            })) || [];

        return {
            statusCode: 200,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                fullText,
                sources
            }),
        };
    } catch (error: any) {
        console.error("Gemini API Error:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message || "Analiz başarısız oldu." }),
        };
    }
};
