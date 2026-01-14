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
            contents: [{ text: prompt }]
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
