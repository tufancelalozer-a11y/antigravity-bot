
import fs from 'fs';
import https from 'https';

// Read API Key from .env.local manually to be dependency-free regarding dotenv
let apiKey = "";
try {
    const envFile = fs.readFileSync('.env.local', 'utf8');
    const match = envFile.match(/VITE_GEMINI_API_KEY=(.*)/);
    if (match) {
        apiKey = match[1].trim();
    }
} catch (e) {
    console.error("Could not read .env.local");
}

if (!apiKey) {
    console.error("API Key not found!");
    process.exit(1);
}

const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

https.get(url, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        try {
            const json = JSON.parse(data);
            if (json.error) {
                console.error("API Error:", json.error);
            } else if (json.models) {
                console.log("Available Models:");
                json.models.forEach(m => {
                    // Filter for 'generateContent' supported models
                    if (m.supportedGenerationMethods && m.supportedGenerationMethods.includes('generateContent')) {
                        console.log(`- ${m.name} (${m.displayName})`);
                    }
                });
            } else {
                console.log("No models found or unexpected format:", data);
            }
        } catch (e) {
            console.error("Parse error:", e);
            console.log("Raw data:", data);
        }
    });
}).on('error', (e) => {
    console.error("Request error:", e);
});
