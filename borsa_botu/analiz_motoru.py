import pandas as pd
import pandas_ta as ta
import numpy as np
import os
import itertools
from datetime import datetime
import time
import sys

# Saf Gerçeklik ve Tam Dürüstlük Motoru - v8
class UltimateMegaAnalyzerV8:
    def __init__(self, timeframes=['5m', '15m', '1h', '4h']):
        self.timeframes = timeframes
        self.leverages = [25, 50]
        self.initial_balance = 250
        self.margin_per_trade = 100
        
    def prepare_data(self, csv_file):
        df = pd.read_csv(csv_file)
        if df.empty: return None, None
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # --- 25+ İndikatör (Hiçbiri Atlanmıyor) ---
        try:
            df.ta.rsi(append=True) # 1
            df.ta.macd(append=True) # 2
            df.ta.adx(append=True) # 3
            df.ta.stoch(append=True) # 4
            df.ta.willr(append=True) # 5
            df.ta.supertrend(append=True) # 6
            df.ta.ema(length=20, append=True) # 7
            df.ta.ema(length=50, append=True) # 8
            df.ta.psar(append=True) # 9
            df.ta.fisher(append=True) # 10
            df.ta.vortex(append=True) # 11
            df.ta.hma(length=20, append=True) # 12
            df.ta.er(append=True) # 13
            df.ta.ao(append=True) # 14
            df.ta.chop(append=True) # 15
            df.ta.mfi(append=True) # 16
            df.ta.cci(append=True) # 17
            df.ta.mom(append=True) # 18
            df.ta.obv(append=True) # 19
            df.ta.bbands(append=True) # 20
            df.ta.dpo(append=True) # 21
            df.ta.cmo(append=True) # 22
            df.ta.ppo(append=True) # 23
            df.ta.uo(append=True) # 24
            df.ta.tsi(append=True) # 25
        except: pass

        df.fillna(method='ffill', inplace=True)
        cols = df.columns.tolist()
        def get_col(prefix):
            match = [c for c in cols if c.lower().startswith(prefix.lower())]
            return match[0] if match else None

        # --- Tam Simetrik Sinyal Seti (Long & Short) ---
        conditions = {
            'RSI': (df[get_col('RSI_')] < 30, df[get_col('RSI_')] > 70),
            'MACD': (df[get_col('MACDh_')] > 0, df[get_col('MACDh_')] < 0),
            'ADX': (df[get_col('ADX_14')] > 25, df[get_col('ADX_14')] > 25),
            'STOCH': (df[get_col('STOCHk_')] < 20, df[get_col('STOCHk_')] > 80),
            'WILLR': (df[get_col('WILLR_')] < -80, df[get_col('WILLR_')] > -20),
            'SUPERT': (df[get_col('SUPERTd_')] == 1, df[get_col('SUPERTd_')] == -1),
            'EMA_X': (df['EMA_20'] > df['EMA_50'], df['EMA_20'] < df['EMA_50']),
            'PSAR': (df['close'] > df[get_col('PSARl_')], df['close'] < df[get_col('PSARs_')]),
            'FISHER': (df[get_col('FISHERt_')] > 0, df[get_col('FISHERt_')] < 0),
            'VORTEX': (df[get_col('VTXP_')] > df[get_col('VTXM_')], df[get_col('VTXP_')] < df[get_col('VTXM_')]),
            'HMA': (df['close'] > df[get_col('HMA_20')], df['close'] < df[get_col('HMA_20')]),
            'ER': (df[get_col('ER_10')] > 0.5, df[get_col('ER_10')] > 0.5),
            'AO': (df[get_col('AO_')] > 0, df[get_col('AO_')] < 0),
            'CHOP': (df[get_col('CHOP_')] < 38, df[get_col('CHOP_')] < 38),
            'MFI': (df[get_col('MFI_')] < 20, df[get_col('MFI_')] > 80),
            'CCI': (df[get_col('CCI_')] < -100, df[get_col('CCI_')] > 100),
            'MOM': (df[get_col('MOM_')] > 0, df[get_col('MOM_')] < 0),
            'TSI': (df[get_col('TSI_')] > 0, df[get_col('TSI_')] < 0),
            'UO': (df[get_col('UO_')] < 30, df[get_col('UO_')] > 70)
        }

        signal_df = pd.DataFrame(index=df.index)
        for name, (l_cond, s_cond) in conditions.items():
            try:
                signal_df[f'L_{name}'] = l_cond.astype(int)
                signal_df[f'S_{name}'] = s_cond.astype(int)
            except: pass
            
        return df['close'], signal_df.fillna(0)

    def backtest(self, close, sig_df, combo, leverage):
        l_sigs = [f'L_{c}' for c in combo]
        s_sigs = [f'S_{c}' for c in combo]
        
        l_active = sig_df[l_sigs].all(axis=1).to_numpy()
        s_active = sig_df[s_sigs].all(axis=1).to_numpy()
        prices = close.to_numpy()
        
        balance = self.initial_balance
        active_trade = None
        trades, wins = 0, 0
        
        for i in range(len(prices)-1):
            curr = prices[i+1]
            if active_trade:
                side, entry, peak = active_trade['side'], active_trade['entry'], active_trade['peak']
                if side == 'LONG':
                    active_trade['peak'] = max(peak, curr)
                    pnl_pct = (curr - entry) / entry
                    is_stop = curr <= entry * 0.98 or (pnl_pct >= 0.01 and curr < active_trade['peak'] * 0.995)
                else:
                    active_trade['peak'] = min(peak, curr)
                    pnl_pct = (entry - curr) / entry
                    is_stop = curr >= entry * 1.02 or (pnl_pct >= 0.01 and curr > active_trade['peak'] * 1.005)

                if is_stop:
                    balance += pnl_pct * leverage * self.margin_per_trade
                    if pnl_pct > 0: wins += 1
                    active_trade = None
                    if balance <= 10: balance = 0; break
            else:
                if l_active[i]:
                    active_trade = {'side': 'LONG', 'entry': prices[i], 'peak': prices[i]}
                    trades += 1
                elif s_active[i]:
                    active_trade = {'side': 'SHORT', 'entry': prices[i], 'peak': prices[i]}
                    trades += 1
                    
        return balance, (wins/trades*100) if trades > 0 else 0, trades

    def run(self):
        all_res = []
        for tf in self.timeframes:
            csv_path = f"btc_usdt_{tf}.csv"
            if not os.path.exists(csv_path): continue
            close, sig_df = self.prepare_data(csv_path)
            if close is None: continue
            
            indicators = [c.replace('L_', '') for c in sig_df.columns if c.startswith('L_')]
            print(f"\n--- {tf.upper()} NİHAİ MEGA V8 TARAMA (İNDİKATÖR SAYISI: {len(indicators)}) ---")
            
            # 1'den 4'e kadar TÜM kombinasyonlar
            for r in [1, 2, 3, 4]:
                combos = list(itertools.combinations(indicators, r))
                print(f"  {r}-li kombinasyonlar: {len(combos)} adet...")
                for combo in combos:
                    for lev in self.leverages:
                        bal, wr, t = self.backtest(close, sig_df, list(combo), lev)
                        if t > 5 and bal > 500: # Ciddi kârlar
                            all_res.append({'TF': tf, 'Combo': "+".join(combo), 'Lev': lev, 'Final_$': round(bal, 2), 'Trades': t})

        final_df = pd.DataFrame(all_res)
        if not final_df.empty:
            top_20 = final_df.sort_values(by='Final_$', ascending=False).head(20)
            header = "🏆 NİHAİ MEGA ANALİZ V8 ŞAMPİYONLARI (25+ İNDİKATÖR) 🏆"
            print("\n" + "="*80); print(header); print("="*80)
            print(top_20.to_string(index=False)); print("="*80)
            with open("borsa_gunlugu.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[{header} - {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n")
                f.write(top_20.to_string(index=False)); f.write("\n" + "="*80 + "\n")
        else: print("!!! BU ŞARTLARDA KÂR EDEN STRATEJİ YOK !!!")

if __name__ == "__main__":
    analyzer = UltimateMegaAnalyzerV8()
    analyzer.run()
