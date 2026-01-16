import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import os

# NOT: API Bilgileri asla kodun içinde açık tutulmaz. 
# Kullanıcıdan .env veya güvenli giriş istenir.

class BinanceBot:
    def __init__(self, symbol='BTC/USDT', leveraged=25):
        self.symbol = symbol
        self.leverage = leveraged
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'} # Futures (Vadeli) işlemler için
        })
        self.is_running = False
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("bot_log.txt", "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def check_signals(self, timeframe='4h'):
        """Analiz motorundaki champion sinyalini kontrol eder (Örn: 4h ADX)"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
            
            # ADX Hesapla (Champion Strateji)
            adx = df.ta.adx(length=14)
            current_adx = adx['ADX_14'].iloc[-1]
            
            # Basit Buy Sinyali (Kaba taslak)
            if current_adx > 25 and df['close'].iloc[-1] > df['close'].iloc[-2]:
                return "BUY"
            return "WAIT"
        except Exception as e:
            self.log(f"Sinyal hatası: {e}")
            return "ERROR"

    def run_dry_mode(self):
        """Gerçek para kullanmadan, canlı veride test modu"""
        self.log(f"Bot DIY MODDA (Simülasyon) Başlatıldı. Sembol: {self.symbol}")
        self.is_running = True
        try:
            while self.is_running:
                signal = self.check_signals()
                self.log(f"Mevcut Sinyal: {signal}")
                # 4 saatlik periyot olduğu için her mum başında kontrol yeterli
                # Test için 10 saniyede bir kontrol edelim
                time.sleep(10) 
        except KeyboardInterrupt:
            self.log("Bot durduruluyor...")
            self.is_running = False

if __name__ == "__main__":
    # Bu sadece bir taslak. Canlı işlem için API Key gerekecek.
    bot = BinanceBot()
    # bot.run_dry_mode() # Test etmek istersen açabilirsin
