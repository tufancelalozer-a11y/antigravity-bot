import ccxt
import pandas as pd
import os
from datetime import datetime, timedelta

def download_data(symbol='BTC/USDT', timeframe='1h', days=365):
    filename = f"{symbol.replace('/', '_').lower()}_{timeframe}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    if os.path.exists(filepath):
        print(f"{filename} zaten mevcut, atlanıyor.")
        return filepath

    print(f"\n{symbol} için son {days} günlük {timeframe} verisi indiriliyor...")
    exchange = ccxt.binance()
    since = exchange.parse8601((datetime.now() - timedelta(days=days)).isoformat())
    
    all_ohlcv = []
    while since < exchange.milliseconds():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            if not ohlcv: break
            since = ohlcv[-1][0] + 1
            all_ohlcv += ohlcv
            print(f"{len(all_ohlcv)} satır çekildi...", end='\r')
        except Exception as e:
            print(f"\nHata: {e}")
            break
            
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.to_csv(filepath, index=False)
    print(f"\nKaydedildi: {filepath}")
    return filepath

if __name__ == "__main__":
    timeframes = ['5m', '15m', '1h', '4h'] # Temel zaman dilimleri
    for tf in timeframes:
        download_data(symbol='BTC/USDT', timeframe=tf, days=365)
