import pandas as pd
import pandas_ta as ta
import numpy as np
import os
import itertools
from datetime import datetime
import time
import sys

import multiprocessing as mp
from functools import partial

# Saf Gerçeklik ve Tam Dürüstlük Motoru - v9.1 (Turbo Mega Analiz)
class UltimateMegaAnalyzerV9:
    def __init__(self, timeframes=['5m', '15m', '30m', '1h', '4h']):
        self.timeframes = timeframes
        self.leverages = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        self.initial_balance = 250
        self.margin_per_trade = 100
        
    def prepare_data(self, csv_file):
        if not os.path.exists(csv_file): return None, None
        df = pd.read_csv(csv_file)
        if df.empty: return None, None
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # --- 25 İndikatör (Tam Set) ---
        try:
            df.ta.rsi(append=True)
            df.ta.macd(append=True)
            df.ta.adx(append=True)
            df.ta.stoch(append=True)
            df.ta.willr(append=True)
            df.ta.supertrend(append=True)
            df.ta.ema(length=20, append=True)
            df.ta.ema(length=50, append=True)
            df.ta.psar(append=True)
            df.ta.fisher(append=True)
            df.ta.vortex(append=True)
            df.ta.hma(length=20, append=True)
            df.ta.er(append=True)
            df.ta.ao(append=True)
            df.ta.chop(append=True)
            df.ta.mfi(append=True)
            df.ta.cci(append=True)
            df.ta.mom(append=True)
            df.ta.obv(append=True)
            df.ta.bbands(append=True)
            df.ta.dpo(append=True)
            df.ta.cmo(append=True)
            df.ta.ppo(append=True)
            df.ta.uo(append=True)
            df.ta.tsi(append=True)
        except: pass

        df.fillna(method='ffill', inplace=True)
        cols = df.columns.tolist()
        def get_col(prefix):
            match = [c for c in cols if c.lower().startswith(prefix.lower())]
            return match[0] if match else None

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

def worker_task(combo_indices, close_arr, sig_vals, leverage, initial_balance, margin_per_trade):
    l_active = np.all(sig_vals[:, [idx*2 for idx in combo_indices]], axis=1)
    s_active = np.all(sig_vals[:, [idx*2+1 for idx in combo_indices]], axis=1)
    
    balance = initial_balance
    active_trade = None
    trades, wins = 0, 0
    
    for i in range(len(close_arr)-1):
        curr = close_arr[i+1]
        if active_trade:
            side, entry, peak = active_trade['side'], active_trade['entry'], active_trade['peak']
            if side == 'LONG':
                peak = max(peak, curr)
                pnl_pct = (curr - entry) / entry
                is_stop = curr <= entry * 0.98 or (pnl_pct >= 0.01 and curr < peak * 0.995)
            else:
                peak = min(peak, curr)
                pnl_pct = (entry - curr) / entry
                is_stop = curr >= entry * 1.02 or (pnl_pct >= 0.01 and curr > peak * 1.005)

            if is_stop:
                balance += pnl_pct * leverage * margin_per_trade
                if pnl_pct > 0: wins += 1
                active_trade = None
                if balance <= 10: balance = 0; break
        else:
            if l_active[i]:
                active_trade = {'side': 'LONG', 'entry': close_arr[i], 'peak': close_arr[i]}
                trades += 1
            elif s_active[i]:
                active_trade = {'side': 'SHORT', 'entry': close_arr[i], 'peak': close_arr[i]}
                trades += 1
                
    return (balance, (wins/trades*100) if trades > 0 else 0, trades)

class UltimateMegaAnalyzerV9:
    def __init__(self, timeframes=['5m', '15m', '30m', '1h', '4h']):
        self.timeframes = timeframes
        self.leverages = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        self.initial_balance = 250
        self.margin_per_trade = 100

    def prepare_data(self, csv_file):
        if not os.path.exists(csv_file): return None, None
        df = pd.read_csv(csv_file)
        if df.empty: return None, None
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        try:
            df.ta.rsi(append=True); df.ta.macd(append=True); df.ta.adx(append=True)
            df.ta.stoch(append=True); df.ta.willr(append=True); df.ta.supertrend(append=True)
            df.ta.ema(length=20, append=True); df.ta.ema(length=50, append=True)
            df.ta.psar(append=True); df.ta.fisher(append=True); df.ta.vortex(append=True)
            df.ta.hma(length=20, append=True); df.ta.er(append=True); df.ta.ao(append=True)
            df.ta.chop(append=True); df.ta.mfi(append=True); df.ta.cci(append=True)
            df.ta.mom(append=True); df.ta.obv(append=True); df.ta.bbands(append=True)
            df.ta.dpo(append=True); df.ta.cmo(append=True); df.ta.ppo(append=True)
            df.ta.uo(append=True); df.ta.tsi(append=True)
        except: pass
        df.fillna(method='ffill', inplace=True)
        cols = df.columns.tolist()
        def get_col(prefix):
            match = [c for c in cols if c.lower().startswith(prefix.lower())]
            return match[0] if match else None
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

    def run(self):
        print(f"--- TURBO MEGA ANALIZ V9.1 BASLATILDI (PID: {os.getpid()}) ---")
        for tf in self.timeframes:
            csv_path = f"btc_usdt_{tf}.csv"
            close, sig_df = self.prepare_data(csv_path)
            if close is None: continue
            
            indicators = [c.replace('L_', '') for c in sig_df.columns if c.startswith('L_')]
            close_arr = close.to_numpy()
            sig_vals = sig_df.to_numpy()
            
            print(f"\n>>> ZAMAN DILIMI: {tf.upper()} | Indikator Sayısı: {len(indicators)}")
            
            for r in range(1, len(indicators) + 1):
                combos = list(itertools.combinations(range(len(indicators)), r))
                print(f"  {r}-li kombinasyonlar ({len(combos)} adet) isleniyor...")
                
                all_res = []
                # Paralel isleme: Her kaldıraç ve kombinasyon ikilisi icin
                with mp.Pool(mp.cpu_count()) as pool:
                    for lev in self.leverages:
                        func = partial(worker_task, close_arr=close_arr, sig_vals=sig_vals, 
                                       leverage=lev, initial_balance=self.initial_balance, 
                                       margin_per_trade=self.margin_per_trade)
                        results = pool.map(func, combos)
                        
                        for idx, (bal, wr, t) in enumerate(results):
                            if t > 5 and bal > 1000:
                                combo_names = "+".join([indicators[i] for i in combos[idx]])
                                all_res.append({'TF': tf, 'Combo': combo_names, 'Lev': lev, 'Final_$': round(bal, 2), 'Trades': t})
                    
                if all_res:
                    self.save_report(all_res, f"V9_TF_{tf}_R_{r}")

    def save_report(self, results, tag):
        df = pd.DataFrame(results)
        top = df.sort_values(by='Final_$', ascending=False).head(50)
        with open("sampiyonlar_v9.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- {tag} ---\n")
            f.write(top.to_string(index=False) + "\n")

if __name__ == "__main__":
    # Windows'ta multiprocessing için gerekli
    mp.freeze_support()
    analyzer = UltimateMegaAnalyzerV9()
    analyzer.run()
