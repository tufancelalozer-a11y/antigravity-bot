import pandas as pd
import pandas_ta as ta
import numpy as np
import os
from datetime import datetime

# Nihai Şampiyonun İşlem Geçmişini Raporlayan Motor
class ChampionTradeLogger:
    def __init__(self, tf='15m', combo=['WILLR', 'ER'], leverage=50):
        self.tf = tf
        self.combo = combo
        self.leverage = leverage
        self.initial_balance = 250
        self.margin_per_trade = 100
        
    def prepare_data(self):
        csv_path = f"btc_usdt_{self.tf}.csv"
        if not os.path.exists(csv_path): return None, None
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Sadece şampiyonun indikatörleri
        df.ta.willr(append=True)
        df.ta.er(length=10, append=True)
        df.fillna(method='ffill', inplace=True)
        
        # Sinyaller
        l_cond = (df['WILLR_14'] < -80) & (df['ER_10'] > 0.5)
        s_cond = (df['WILLR_14'] > -20) & (df['ER_10'] > 0.5)
        
        sig_df = pd.DataFrame(index=df.index)
        sig_df['L'] = l_cond.astype(int)
        sig_df['S'] = s_cond.astype(int)
        return df['close'], sig_df

    def log_trades(self):
        close, sig_df = self.prepare_data()
        if close is None: return
        
        prices = close.to_numpy()
        times = sig_df.index.tolist()
        l_active = sig_df['L'].to_numpy()
        s_active = sig_df['S'].to_numpy()
        
        balance = self.initial_balance
        active_trade = None
        trade_logs = []
        
        for i in range(len(prices)-1):
            curr = prices[i+1]
            t_now = times[i+1]
            
            if active_trade:
                side, entry, peak, t_entry = active_trade['side'], active_trade['entry'], active_trade['peak'], active_trade['time']
                if side == 'LONG':
                    active_trade['peak'] = max(peak, curr)
                    pnl_pct = (curr - entry) / entry
                    is_stop = curr <= entry * 0.98 or (pnl_pct >= 0.01 and curr < active_trade['peak'] * 0.995)
                else:
                    active_trade['peak'] = min(peak, curr)
                    pnl_pct = (entry - curr) / entry
                    is_stop = curr >= entry * 1.02 or (pnl_pct >= 0.01 and curr > active_trade['peak'] * 1.005)

                if is_stop:
                    pnl_dollars = pnl_pct * self.leverage * self.margin_per_trade
                    balance += pnl_dollars
                    trade_logs.append({
                        'Giriş Zamanı': t_entry,
                        'Çıkış Zamanı': t_now,
                        'Yön': side,
                        'Giriş Fiyatı': round(entry, 2),
                        'Çıkış Fiyatı': round(curr, 2),
                        'PnL ($)': round(pnl_dollars, 2),
                        'Bakiye ($)': round(balance, 2)
                    })
                    active_trade = None
                    if balance <= 10: break
            else:
                if l_active[i]:
                    active_trade = {'side': 'LONG', 'entry': prices[i], 'peak': prices[i], 'time': times[i]}
                elif s_active[i]:
                    active_trade = {'side': 'SHORT', 'entry': prices[i], 'peak': prices[i], 'time': times[i]}
                    
        res_df = pd.DataFrame(trade_logs)
        res_df.to_csv("sampiyon_islemler.csv", index=False)
        print(f"--- Şampiyon ({self.tf} {self.combo}) İşlem Raporu Hazır ---")
        print(f"Toplam İşlem: {len(res_df)}")
        print(f"Nihai Bakiye: {round(balance, 2)}$")
        print("\nSon 10 İşlem:")
        print(res_df.tail(10).to_string(index=False))

if __name__ == "__main__":
    logger = ChampionTradeLogger()
    logger.log_trades()
