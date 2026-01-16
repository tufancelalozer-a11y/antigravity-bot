import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import threading
import sys

class CryptoStrategyBot:
    def __init__(self, name, symbol, timeframe, leverage=50):
        self.name = name
        self.symbol = symbol
        self.timeframe = timeframe
        self.leverage = leverage
        self.balance = 250.0  # Başlangıç sanal kasası
        self.margin_per_trade = 100.0
        self.exchange = ccxt.binance({'options': {'defaultType': 'future'}})
        self.active_trade = None
        self.history = []

    def log(self, msg):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{now}] [{self.name}] {msg}"
        print(log_line)
        try:
            with open("borsa_gunlugu.txt", "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except: pass

    def get_data(self):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
            return df
        except Exception as e:
            self.log(f"Veri çekme hatası: {e}")
            return None

    def calculate_signals(self, df):
        if self.name == "4H_TREND_KING":
            # 4h ADX Stratejisi
            adx = df.ta.adx()
            current_adx = adx.iloc[-1]['ADX_14']
            current_close = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            if current_adx > 25:
                if current_close > prev_close: return "LONG"
                if current_close < prev_close: return "SHORT"
                
        elif self.name == "5M_SCALPING_MONSTER":
            # 5m ATR + TRIX Stratejisi
            trix = df.ta.trix()
            current_trix = trix.iloc[-1]['TRIX_30_9']
            current_close = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            if current_trix > 0 and current_close > prev_close:
                return "LONG"
            elif current_trix < 0 and current_close < prev_close:
                return "SHORT"
        return "WAIT"

    def run_cycle(self):
        df = self.get_data()
        if df is None: return

        signal = self.calculate_signals(df)
        price = df['close'].iloc[-1]
        
        # Sadece pozisyon yokken sinyal logla (Kalabalık yapmasın)
        if not self.active_trade:
            self.log(f"Fiyat: {price} | Sinyal: {signal}")

        if signal in ["LONG", "SHORT"] and not self.active_trade:
            self.active_trade = {
                'side': signal,
                'entry_price': price,
                'peak_price': price, # Long için max, Short için min takip edilir
                'start_time': datetime.now()
            }
            self.log(f"🚀 {signal} İŞLEME GİRİLDİ! Fiyat: {price}")

        elif self.active_trade:
            side = self.active_trade['side']
            entry = self.active_trade['entry_price']
            
            if side == "LONG":
                self.active_trade['peak_price'] = max(self.active_trade['peak_price'], price)
                pnl_pct = (price - entry) / entry
                trailing_trigger = price >= entry * 1.01
                trailing_exit = price < self.active_trade['peak_price'] * 0.995 # %0.5 geri çekilme
                stop_loss = price <= entry * 0.98 # %2 stop
            else: # SHORT
                self.active_trade['peak_price'] = min(self.active_trade['peak_price'], price)
                pnl_pct = (entry - price) / entry
                trailing_trigger = price <= entry * 0.99 # %1 kâr (Short için düşüş)
                trailing_exit = price > self.active_trade['peak_price'] * 1.005 # Zirve dipten %0.5 yükseliş
                stop_loss = price >= entry * 1.02 # %2 stop (Short için yükseliş zarardır)
            
            should_exit = False
            exit_reason = ""

            if trailing_trigger and trailing_exit:
                should_exit = True
                exit_reason = "Trailing Stop (Kar Al)"
            elif stop_loss:
                should_exit = True
                exit_reason = "Stop Loss (Zarar)"
            elif (side == "LONG" and signal == "SHORT") or (side == "SHORT" and signal == "LONG"):
                should_exit = True
                exit_reason = "Sinyal Tersine Döndü"

            if should_exit:
                pnl_dollars = pnl_pct * self.leverage * self.margin_per_trade
                self.balance += pnl_dollars
                log_msg = f"🏁 {side} KAPANDI ({exit_reason}) | PnL: {pnl_dollars:.2f}$ | Yeni Bakiye: {self.balance:.2f}$"
                self.log(log_msg)
                
                # CSV Kaydı
                try:
                    with open("sampiyon_islemler.csv", "a", encoding="utf-8") as f:
                        f.write(f"{self.name},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{side},{entry:.4f},{price:.4f},{pnl_dollars:.2f},{self.balance:.2f}\n")
                except: pass
                
                self.active_trade = None

def start_bot(bot):
    while True:
        bot.run_cycle()
        # Periyoda göre bekleme süresi (Scalper için daha sık kontrol)
        sleep_time = 30 if bot.timeframe == '5m' else 300
        time.sleep(sleep_time)

if __name__ == "__main__":
    print("--- MEGA CRYPTO MULTI-BOT SİMÜLASYONU BAŞLADI ---")
    print("Kural: 250$ Başlangıç | 100$ İşlem Başı | GERÇEK VERİ - SANAL PARA\n")
    
    bot1 = CryptoStrategyBot("4H_TREND_KING", "BTC/USDT", "4h", leverage=50)
    bot2 = CryptoStrategyBot("5M_SCALPING_MONSTER", "BTC/USDT", "5m", leverage=50)

    t1 = threading.Thread(target=start_bot, args=(bot1,))
    t2 = threading.Thread(target=start_bot, args=(bot2,))

    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
