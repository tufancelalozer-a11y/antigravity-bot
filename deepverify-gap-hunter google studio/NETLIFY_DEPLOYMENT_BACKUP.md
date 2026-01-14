# Netlify Deployment - Complete Backup Documentation

**Tarih:** 2026-01-06  
**Proje:** Deepverify Gap Hunter - Netlify Entegrasyonu  
**Durum:** ✅ Tamamlandı ve Test Edildi

---

## 📋 Özet

Bu dokümantasyon, "Deepverify Gap Hunter" projesinin Netlify'a güvenli bir şekilde deploy edilmesi için yapılan tüm değişiklikleri içerir.

### Yapılan Değişiklikler:
1. ✅ Netlify Serverless Functions oluşturuldu (`analyze.ts`, `blueprint.ts`)
2. ✅ Frontend servisi güvenli API çağrıları için güncellendi
3. ✅ `netlify.toml` konfigürasyon dosyası eklendi
4. ✅ `@google/genai` SDK 1.34.0 sürümüne uyumlu hale getirildi
5. ✅ Build testi başarıyla tamamlandı

---

## 🗂️ Yeni Dosyalar

### 1. `netlify/functions/analyze.ts`

```typescript
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
```

### 2. `netlify/functions/blueprint.ts`

```typescript
import { Handler } from "@netlify/functions";
import { GoogleGenAI } from "@google/genai";

export const handler: Handler = async (event, context) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const API_KEY = process.env.VITE_GEMINI_API_KEY;
  if (!API_KEY) {
    return { statusCode: 500, body: JSON.stringify({ error: "API Key not configured." }) };
  }

  const { topicName, type } = JSON.parse(event.body || "{}");

  const ai = new GoogleGenAI({ apiKey: API_KEY });

  let prompt = "";
  if (type === 'VIDEO') {
    prompt = `
       Konu: "${topicName}"
       Görev: YouTube için viral potansiyeli yüksek, izleyiciyi elde tutan bir video senaryosu yaz.
       
       Format:
       1. **Kanca (0-15sn):** İzleyiciyi şok edecek veya meraklandıracak giriş.
       2. **Giriş:** Sorun/Fırsat tanımı.
       3. **Gelişme:** 3 ana madde halinde derinlemesine inceleme.
       4. **Sonuç & CTA:** İzleyiciyi harekete geçiren kapanış.
       
       Dil: Samimi, enerjik Türkçe.
       `;
  } else {
    prompt = `
       Topic: "${topicName}"
       Task: Create a robust "Starter Kit" code structure for this tech topic.
       
       Output:
       1. **Project Structure:** File tree.
       2. **Key Dependencies:** npm packages needed.
       3. **Core Implementation:** The most critical code snippet (e.g., the main algorithm or component).
       
       Language: English comments, standard code best practices.
       `;
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-1.5-flash",
      contents: prompt
    });
    return {
      statusCode: 200,
      body: JSON.stringify({ text: response.text || "İçerik üretilemedi." }),
    };
  } catch (error: any) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
```

### 3. `netlify.toml`

```toml
[build]
  command = "npm run build"
  publish = "dist"

[functions]
  directory = "netlify/functions"
  node_version = "20"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## 🔄 Değiştirilen Dosyalar

### `services/geminiService.ts`

**Önceki Durum:** API anahtarı frontend'de kullanılıyordu (GÜVENLİK RİSKİ!)  
**Yeni Durum:** Tüm API çağrıları Netlify Functions üzerinden yapılıyor

```typescript
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
```

---

## 🚀 Deployment Adımları

### 1. GitHub'a Push
```bash
git add .
git commit -m "Netlify deployment ready with secure serverless functions"
git push origin main
```

### 2. Netlify'a Bağlan
1. [app.netlify.com](https://app.netlify.com/) adresine git
2. "Add new site" > "Import an existing project" seç
3. GitHub repository'ni seç

### 3. Environment Variables Ayarla (ÖNEMLİ!)
**Netlify Dashboard > Site Settings > Environment variables**

| Key | Value |
|-----|-------|
| `VITE_GEMINI_API_KEY` | `[Senin Gemini API Anahtarın]` |

### 4. Deploy Et
"Deploys" sekmesine git ve "Trigger deploy" butonuna tıkla.

---

## 📊 Ücretsiz Tier Limitleri

### Netlify (Starter Plan)
- ✅ **300 kredi/ay**
- ✅ Her deploy: 15 kredi
- ✅ 10,000 function çağrısı: 3 kredi
- ✅ Aylık ~20 deploy + 100,000+ function çağrısı yapabilirsiniz

### Google AI Studio (Gemini 1.5 Flash)
- ✅ **1,500 istek/gün**
- ✅ 15 istek/dakika
- ✅ 1M token/dakika

**Sonuç:** Gap Hunter için bu limitler fazlasıyla yeterli! 🎉

---

## ⚠️ Önemli Notlar

1. **Kripto Bot İçin Uygun Değil:** Bu yapı 7/24 çalışan botlar için değil, kullanıcı isteği üzerine çalışan web uygulamaları içindir.
2. **API Key Güvenliği:** `.env.local` dosyasını asla GitHub'a pushlama! (`.gitignore`'da zaten var)
3. **Build Testi:** Yerel olarak `npm run build` komutu başarıyla çalıştı ✅

---

## 📁 Proje Yapısı

```
deepverify-gap-hunter/
├── netlify/
│   └── functions/
│       ├── analyze.ts      (Yeni - Gap analizi)
│       └── blueprint.ts    (Yeni - İçerik üretimi)
├── services/
│   └── geminiService.ts    (Güncellendi - Fetch API kullanıyor)
├── netlify.toml            (Yeni - Netlify config)
├── package.json            (@netlify/functions eklendi)
└── .env.local              (API anahtarı - GİZLİ!)
```

---

## 🔗 Faydalı Linkler

- [Netlify Dashboard](https://app.netlify.com/)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)

---

**Son Güncelleme:** 2026-01-06 12:00  
**Durum:** ✅ Production Ready
