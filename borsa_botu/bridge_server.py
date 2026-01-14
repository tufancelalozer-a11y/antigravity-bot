from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import asyncio
from contextlib import asynccontextmanager
import time
import platform

# --- Comprehensive Platform Mock (Windows Hang Fix) ---
platform.system = lambda: "Windows"
platform.win32_ver = lambda: ("10", "10.0.19045", "SP0", "Multiprocessor Free")
platform.release = lambda: "10"
platform.version = lambda: "10.0.19045"

from database_manager import DatabaseManager
from youtube_extractor import extract_channel_videos
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "quadrant_state.json")

def save_state():
    """Sistem durumunu diske kaydeder."""
    try:
        # Sadece kalıcı olması gereken verileri seç
        persistent_data = {
            "status": SYSTEM_STATE["status"],
            "bots": SYSTEM_STATE["bots"]
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(persistent_data, f, indent=4)
    except Exception as e:
        print(f"Error saving state: {e}")

def load_state():
    """Sistem durumunu diskten yükler."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                SYSTEM_STATE["status"] = data.get("status", SYSTEM_STATE["status"])
                # Bot ayarlarını koru ama durumları (balance, pnl, active_trade) diskten al
                if "bots" in data:
                    for i, saved_bot in enumerate(data["bots"]):
                        if i < len(SYSTEM_STATE["bots"]):
                            SYSTEM_STATE["bots"][i].update({
                                "balance": saved_bot.get("balance", 250.0),
                                "pnl": saved_bot.get("pnl", 0.0),
                                "active_trade": saved_bot.get("active_trade"),
                                "active": saved_bot.get("active", False)
                            })
            return True
        except Exception as e:
            print(f"Error loading state: {e}")
    return False

# --- Global System State (Ana Gemi Belleği) ---
SYSTEM_STATE = {
    "status": {
        "active": True,
        "total_pnl": 0.0,
        "global_balance": 1000.0, # 4 bot için 250*4
    },
    "bots": [
        {
            "id": 1, "name": "Quadrans-A", "active": False, "balance": 250.0, "pnl": 0.0,
            "strategy": "5m STOCH+HMA", "active_trade": None, "settings": {"sl": 0.02, "ts_trigger": 0.01, "ts_offset": 0.005}
        },
        {
            "id": 2, "name": "Quadrans-B", "active": False, "balance": 250.0, "pnl": 0.0,
            "strategy": "15m WILLR+ER", "active_trade": None, "settings": {"sl": 0.02, "ts_trigger": 0.01, "ts_offset": 0.005}
        },
        {
            "id": 3, "name": "Quadrans-C", "active": False, "balance": 250.0, "pnl": 0.0,
            "strategy": "1h ADX+VORTEX", "active_trade": None, "settings": {"sl": 0.03, "ts_trigger": 0.015, "ts_offset": 0.007}
        },
        {
            "id": 4, "name": "Quadrans-D", "active": False, "balance": 250.0, "pnl": 0.0,
            "strategy": "4h RSI+MACD", "active_trade": None, "settings": {"sl": 0.04, "ts_trigger": 0.02, "ts_offset": 0.01}
        }
    ],
    "arbitrage": [],
    "logs": ["Mothership Quadrant Sistemi baslatiliyor..."],
    "last_update": 0
}

# Açılışta eski durumu yükle
load_state()

db = DatabaseManager()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "borsa_gunlugu.txt")
CSV_FILE = os.path.join(BASE_DIR, "sampiyon_islemler.csv")
HISTORY_CSV = os.path.join(BASE_DIR, "sampiyon_islemler_history.csv")

# --- Workers (Arka Plan Isçileri) ---

def log_message(msg):
    """Hem bellege hem de dosyaya log yazar."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted_msg = f"[{timestamp}] {msg}"
    # Belleğe ekle (En son 50 taneyi tut)
    SYSTEM_STATE["logs"].append(formatted_msg)
    if len(SYSTEM_STATE["logs"]) > 50:
        SYSTEM_STATE["logs"].pop(0)
    
    # Dosyaya ekle
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except:
        pass

async def arbitrage_worker(persistent_exchanges):
    """Borsalari tarayip bellegi günceller. Kalici baglantilari kullanir."""
    from arbitraj_motoru import get_arbitrage_data_async
    while True:
        try:
            data = await get_arbitrage_data_async(provided_exchanges=persistent_exchanges)
            SYSTEM_STATE["arbitrage"] = data
            SYSTEM_STATE["last_update"] = time.time()
        except Exception as e:
            log_message(f"Worker Error (Arbitrage): {e}")
        await asyncio.sleep(15)

async def metrics_worker():
    """Veritabanini ve metrikleri günceller."""
    while True:
        try:
            # CSV'den verileri veritabanına taşı
            db.sync_from_csv(CSV_FILE)
            if os.path.exists(HISTORY_CSV):
                db.sync_from_csv(HISTORY_CSV)
        except Exception as e:
            log_message(f"Worker Error (Metrics): {e}")
        await asyncio.sleep(60)

async def log_worker():
    """Log dosyasini takip eder."""
    while True:
        await asyncio.sleep(60)

async def virtual_trader_worker():
    """Quadrant Engine: 4 bot'u aynı anda yöneten profesyonel risk motoru."""
    import ccxt.async_support as ccxt_async
    import pandas as pd
    import pandas_ta as ta
    from database_manager import DatabaseManager
    from datetime import datetime
    
    db = DatabaseManager()
    exch = ccxt_async.binance()
    symbol = 'BTC/USDT'
    margin = 100.0
    leverage = 50
    
    log_message("⚔️ KRIPTO KULE: Quadrant Müfrezesi Mevzileniyor (4'lü Bot Aktif)")
    
    while True:
        try:
            # Tüm gerekli timeframe'leri belirle
            timeframes = list(set([b["strategy"].split(" ")[0] for b in SYSTEM_STATE["bots"]]))
            ohlcv_data = {}
            
            for tf in timeframes:
                ohlcv = await exch.fetch_ohlcv(symbol, timeframe=tf, limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                # Teknik Göstergeler
                df.ta.stoch(append=True); df.ta.hma(append=True); df.ta.willr(append=True); 
                df.ta.er(append=True); df.ta.adx(append=True); df.ta.vortex(append=True);
                df.ta.rsi(append=True); df.ta.macd(append=True)
                ohlcv_data[tf] = df

            # 4 Bot'u Döngüye Al
            for bot in SYSTEM_STATE["bots"]:
                tf = bot["strategy"].split(" ")[0]
                df = ohlcv_data.get(tf)
                if df is None: continue
                
                curr_price = df['close'].iloc[-1]
                active = bot.get("active_trade")
                
                # Sinyal Hesaplama
                signal = "WAIT"
                if "STOCH" in bot["strategy"]:
                    if 'STOCHk_14_3_3' in df.columns and df['STOCHk_14_3_3'].iloc[-1] < 20: signal = "LONG"
                    elif 'STOCHk_14_3_3' in df.columns and df['STOCHk_14_3_3'].iloc[-1] > 80: signal = "SHORT"
                elif "WILLR" in bot["strategy"]:
                    if 'WILLR_14' in df.columns and df['WILLR_14'].iloc[-1] < -80: signal = "LONG"
                    elif 'WILLR_14' in df.columns and df['WILLR_14'].iloc[-1] > -20: signal = "SHORT"
                elif "ADX" in bot["strategy"]:
                    if 'ADX_14' in df.columns and df['ADX_14'].iloc[-1] > 25:
                        signal = "LONG" if df['close'].iloc[-1] > df['close'].iloc[-2] else "SHORT"
                elif "RSI" in bot["strategy"]:
                    if 'RSI_14' in df.columns and df['RSI_14'].iloc[-1] < 30: signal = "LONG"
                    elif 'RSI_14' in df.columns and df['RSI_14'].iloc[-1] > 70: signal = "SHORT"

                if not active:
                    if signal in ["LONG", "SHORT"]:
                        bot["active_trade"] = {
                            "side": signal, "entry": curr_price, "peak": curr_price,
                            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        save_state() # İşlem açıldığında kaydet
                        log_message(f"🚀 [{bot['name']}] {signal} GIRILDI @ {curr_price}")
                else:
                    # PROFESYONEL RISK YÖNETİMİ
                    entry = active["entry"]
                    peak = active["peak"]
                    side = active["side"]
                    settings = bot["settings"]
                    
                    pnl_raw = (curr_price - entry) / entry if side == "LONG" else (entry - curr_price) / entry
                    
                    if side == "LONG": active["peak"] = max(peak, curr_price)
                    else: active["peak"] = min(peak, curr_price)
                    
                    is_exit = False
                    reason = ""
                    
                    if pnl_raw <= -settings["sl"]: 
                        is_exit = True; reason = "Stop Loss"
                    elif pnl_raw >= settings["ts_trigger"]:
                        ts_check = (active["peak"] - curr_price) / active["peak"] if side == "LONG" else (curr_price - active["peak"]) / active["peak"]
                        if ts_check >= settings["ts_offset"]:
                            is_exit = True; reason = "Trailing Stop"
                    elif (side == "LONG" and signal == "SHORT") or (side == "SHORT" and signal == "LONG"):
                        is_exit = True; reason = "Ters Sinyal"
                    elif bot.get("_manual_exit"):
                        is_exit = True; reason = "Manuel Kapatma"
                        bot["_manual_exit"] = False # Reset flag
                    
                    if is_exit:
                        profit = pnl_raw * leverage * margin
                        bot["balance"] += profit
                        bot["pnl"] += profit
                        SYSTEM_STATE["status"]["total_pnl"] += profit
                        
                        try:
                            # Bot ismi ve tüm detaylarla veritabanına işle
                            db.log_virtual_trade(
                                bot_name=bot["name"],
                                entry_time=active["start_time"],
                                exit_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                side=side, entry_price=entry, exit_price=curr_price,
                                pnl=profit, balance=bot["balance"]
                            )
                        except Exception as e:
                            log_message(f"İşlem Kayıt Hatası: {e}")
                        bot["active_trade"] = None
                        save_state() # İşlem kapandığında kaydet
                        log_message(f"🏁 [{bot['name']}] {side} KAPANDI ({reason}) | PnL: {round(profit,2)}$")
            
            # Periyodik kaydet (Her döngüde bir kez pnl/balance güncelliği için)
            save_state()

        except Exception as e:
            log_message(f"⚠️ Quadrant Engine Hata: {str(e)}")
            
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Borsa Persist Baglantilarini Kur
    import ccxt.async_support as ccxt
    persistent_exchanges = {
        'binance': ccxt.binance(),
        'bybit': ccxt.bybit(),
        'kucoin': ccxt.kucoin()
    }
    
    workers = [
        asyncio.create_task(arbitrage_worker(persistent_exchanges)),
        asyncio.create_task(metrics_worker()),
        asyncio.create_task(log_worker()),
        asyncio.create_task(virtual_trader_worker())
    ]
    print(f"Mothership V2: Quadrant Bot ve Arbitraj motorlari ateslendi.")
    SYSTEM_STATE["logs"].append("🎮 Quadrant Sistemi Hazir: 4 Bot Nöbette.")
    
    yield
    # Shutdown: Motorlari durdur ve baglantilari kapat
    for worker in workers:
        worker.cancel()
    for exch in persistent_exchanges.values():
        await exch.close()

app = FastAPI(title="Ana Gemi Bridge V2", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Ana sayfa karsilama ve API dokumantasyonu."""
    return {
        "message": "Mothership V2: Quadrant Bot Sistemi Hazir!",
        "version": "2.0.0",
        "endpoints": {
            "status": "/status - Genel sistem ozeti",
            "bots": "/bots - Botlarin anlik durumlari",
            "logs": "/logs - Sistem gunlukleri",
            "arbitrage": "/arbitrage - Arbitraj firsatlari",
            "history": "/history - Islem gecmisi (DB)",
            "control": "/control/status - Detayli kontrol verisi"
        },
        "health": "Live"
    }

@app.get("/status")
async def get_status():
    """Anlik sistem ozetini doner."""
    return {
        "active": SYSTEM_STATE["status"]["active"],
        "total_pnl": round(SYSTEM_STATE["status"]["total_pnl"], 2),
        "global_balance": round(SYSTEM_STATE["status"]["global_balance"], 2),
        "bot_count": len(SYSTEM_STATE["bots"]),
        "last_update": time.strftime("%H:%M:%S")
    }

@app.get("/bots")
async def get_bots():
    """Bireysel bot durumlarini döner."""
    return {"bots": SYSTEM_STATE["bots"]}

@app.get("/history")
async def get_history():
    """İşlem geçmişini veritabanından döner."""
    metrics = db.get_metrics()
    return {"trades": metrics["trades"], "total_pnl": metrics["total_pnl"], "balance": metrics["balance"]}

@app.get("/arbitrage")
async def get_arbitrage():
    """Anlik arbitraj verisini döner (Sifir bekleme)."""
    return {"data": SYSTEM_STATE["arbitrage"], "last_update": SYSTEM_STATE["last_update"]}

@app.get("/logs")
async def get_logs():
    """Anlik log verisini döner."""
    return {"logs": SYSTEM_STATE["logs"]}

@app.post("/competitor/extract")
async def post_competitor_extract(data: dict):
    """Kanal linkinden video listesini ceker."""
    url = data.get("url")
    sort_by = data.get("sort_by", "new")
    if not url:
        return {"error": "URL gerekli"}
    
    SYSTEM_STATE["logs"].append(f"🔍 Kanal Analizi Baslatildi ({sort_by}): {url}")
    result = await extract_channel_videos(url, sort_by=sort_by)
    return result

# --- Yeni Kontrol Endpoint'leri ---

@app.post("/control/sell")
async def manual_sell(data: dict):
    """Belirtilen botun aktif islemini manuel kapatir."""
    bot_id = data.get("bot_id")
    bot = next((b for b in SYSTEM_STATE["bots"] if b["id"] == bot_id), None)
    
    if not bot:
        return {"error": "Bot bulunamadi"}
    
    if not bot["active_trade"]:
        return {"error": "Aktif islem yok"}
    
    # Islem kapatma tetikleyicisi (Bir sonraki cycle beklememek için burada da yapabiliriz ama worker'da 'should_exit' flag'i yok)
    # Bu yüzden botun active_trade bilgisini worker'a 'kapat' emri verecek şekilde işaretlememiz lazım.
    # Şimdilik direkt burada kapatıp loglayalım (Worker bir sonraki döngüde active_trade'i None görecek).
    
    bot["_manual_exit"] = True # Worker'a sinyal gönder
    log_message(f"🚨 [{bot['name']}] MANUEL KAPATMA EMRI VERILDI!")
    return {"status": "success", "message": f"{bot['name']} icin kapatma emri iletildi."}

@app.post("/control/reset")
async def reset_system():
    """Tüm sistemi fabrika ayarlarına döndürür."""
    global SYSTEM_STATE
    SYSTEM_STATE["status"]["total_pnl"] = 0.0
    SYSTEM_STATE["status"]["global_balance"] = 1000.0
    
    for bot in SYSTEM_STATE["bots"]:
        bot["balance"] = 250.0
        bot["pnl"] = 0.0
        bot["active_trade"] = None
        bot["active"] = False
        bot["_manual_exit"] = False
        
    SYSTEM_STATE["logs"].append("🧹 SISTEM SIFIRLANDI: Tum bakiyeler 250$ yapildi.")
    save_state()
    return {"status": "success", "message": "Sistem sifirlandi."}

@app.get("/dashboard")
async def get_dashboard():
    """Görsel takip paneli (HTML)."""
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mothership Quadrant Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0a0b10;
                --card-bg: #151921;
                --accent: #4f46e5;
                --green: #10b981;
                --red: #ef4444;
                --text: #e2e8f0;
                --text-dim: #94a3b8;
            }
            body {
                background: var(--bg);
                color: var(--text);
                font-family: 'Inter', sans-serif;
                margin: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            header {
                padding: 2rem;
                background: linear-gradient(to right, #1e1b4b, #0a0b10);
                border-bottom: 1px solid #1e293b;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .logo {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.5rem;
                font-weight: bold;
                letter-spacing: 2px;
                color: var(--accent);
                text-transform: uppercase;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                width: 100%;
                box-sizing: border-box;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            .stat-card {
                background: var(--card-bg);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #1e293b;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .stat-label { color: var(--text-dim); font-size: 0.875rem; margin-bottom: 0.5rem; }
            .stat-value { font-size: 1.5rem; font-weight: bold; font-family: 'Orbitron', sans-serif; }
            .stat-value.green { color: var(--green); }
            .stat-value.red { color: var(--red); }

            .bots-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            .bot-card {
                background: var(--card-bg);
                border-radius: 12px;
                border: 1px solid #1e293b;
                overflow: hidden;
                transition: transform 0.2s;
            }
            .bot-card:hover { transform: translateY(-4px); }
            .bot-header {
                padding: 1rem;
                background: #1e293b;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .bot-name { font-weight: bold; font-family: 'Orbitron', sans-serif; }
            .bot-status {
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                text-transform: uppercase;
                background: #0f172a;
            }
            .bot-status.long { color: var(--green); border: 1px solid var(--green); }
            .bot-status.short { color: var(--red); border: 1px solid var(--red); }
            .bot-status.wait { color: var(--text-dim); border: 1px solid var(--text-dim); }
            .bot-body { padding: 1rem; }
            .bot-info { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
            .bot-info span:first-child { color: var(--text-dim); }

            .logs-container {
                background: #0f172a;
                border-radius: 12px;
                padding: 1.5rem;
                font-family: 'Courier New', Courier, monospace;
                height: 300px;
                overflow-y: auto;
                border: 1px solid #1e293b;
            }
            .log-line { margin-bottom: 0.5rem; font-size: 0.9rem; border-bottom: 1px solid #1e293b22; padding-bottom: 2px; }

            .actions { margin-top: 2rem; display: flex; gap: 1rem; }
            button {
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                font-weight: bold;
                transition: opacity 0.2s;
            }
            .btn-reset { background: var(--red); color: white; }
            button:hover { opacity: 0.8; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">Mothership V2 Dashboard</div>
            <div id="last-update" style="color: var(--text-dim)">Yükleniyor...</div>
        </header>

        <div class="container">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">GLOBAL PNL (TOPLAM)</div>
                    <div id="total-pnl" class="stat-value">0.00$</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">GLOBAL BAKİYE</div>
                    <div id="global-balance" class="stat-value">1000.00$</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">MÜFREZE DURUMU</div>
                    <div id="bot-count" class="stat-value" style="color: var(--accent)">4 BOT AKTİF</div>
                </div>
            </div>

            <div class="bots-grid" id="bots-container">
                <!-- Bot Kartları Buraya Gelecek -->
            </div>

            <h2 style="font-family: 'Orbitron'; font-size: 1.2rem; margin-top: 3rem;">KOMUT MERKEZİ GÜNLÜĞÜ</h2>
            <div class="logs-container" id="logs-container">
                <!-- Loglar Buraya Gelecek -->
            </div>

            <div class="actions">
                <button class="btn-reset" onclick="resetSystem()">SİSTEMİ SIFIRLA</button>
            </div>
        </div>

        <script>
            async function fetchData() {
                try {
                    const [statusRes, botsRes, logsRes] = await Promise.all([
                        fetch('/status'),
                        fetch('/bots'),
                        fetch('/logs')
                    ]);
                    const status = await statusRes.json();
                    const bots = await botsRes.json();
                    const logs = await logsRes.json();

                    // Üst Paneller
                    document.getElementById('total-pnl').innerText = status.total_pnl + '$';
                    document.getElementById('total-pnl').className = 'stat-value ' + (status.total_pnl >= 0 ? 'green' : 'red');
                    document.getElementById('global-balance').innerText = status.global_balance + '$';
                    document.getElementById('last-update').innerText = 'Son Güncelleme: ' + status.last_update;

                    // Bot Kartları
                    const container = document.getElementById('bots-container');
                    container.innerHTML = '';
                    bots.bots.forEach(bot => {
                        const tradeStatus = bot.active_trade ? bot.active_trade.side : 'WAIT';
                        const card = `
                            <div class="bot-card">
                                <div class="bot-header">
                                    <span class="bot-name">${bot.name}</span>
                                    <span class="bot-status ${tradeStatus.toLowerCase()}">${tradeStatus}</span>
                                </div>
                                <div class="bot-body">
                                    <div class="bot-info"><span>Strateji:</span> <span>${bot.strategy}</span></div>
                                    <div class="bot-info"><span>PnL:</span> <span class="${bot.pnl >= 0 ? 'green' : 'red'}">${bot.pnl.toFixed(2)}$</span></div>
                                    <div class="bot-info"><span>Bakiye:</span> <span>${bot.balance.toFixed(2)}$</span></div>
                                    <div class="bot-info"><span>Son İşlem:</span> <span>${bot.active_trade ? bot.active_trade.start_time.split(' ')[1] : 'Yok'}</span></div>
                                </div>
                            </div>
                        `;
                        container.innerHTML += card;
                    });

                    // Loglar
                    const logBox = document.getElementById('logs-container');
                    const isAtBottom = logBox.scrollHeight - logBox.clientHeight <= logBox.scrollTop + 1;
                    logBox.innerHTML = logs.logs.map(l => `<div class="log-line">${l}</div>`).join('');
                    if (isAtBottom) logBox.scrollTop = logBox.scrollHeight;

                } catch (e) { console.error(e); }
            }

            async function resetSystem() {
                if(confirm('TÜM bakiyeleri ve PnL verilerini sıfırlamak istediğine emin misin?')) {
                    await fetch('/control/reset', { method: 'POST' });
                    fetchData();
                }
            }

            setInterval(fetchData, 3000);
            fetchData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/control/status")
async def full_status():
    """Tum botlarin detayli durumunu doner."""
    return {
        "global": SYSTEM_STATE["status"],
        "bots": SYSTEM_STATE["bots"]
    }

if __name__ == "__main__":
    # Zombie python süreçlerini temizle (Sadece ana scriptte)
    os.system('taskkill /f /im uvicorn.exe /t >nul 2>&1')
    uvicorn.run(app, host="0.0.0.0", port=8001)
