import platform
# Comprehensive Platform Mock to bypass Windows/WMI hangs
platform.system = lambda: "Windows"
platform.win32_ver = lambda: ("10", "10.0.19045", "SP0", "Multiprocessor Free")
platform.release = lambda: "10"
platform.version = lambda: "10.0.19045"

import asyncio
import ccxt.async_support as ccxt
import time
from datetime import datetime

# Genişletilmiş İzlenecek Çiftler (Top 50+ Volüm Odaklı)
SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 
    'AVAX/USDT', 'DOT/USDT', 'LINK/USDT', 'MATIC/USDT', 'LTC/USDT',
    'BCH/USDT', 'SHIB/USDT', 'DOGE/USDT', 'TRX/USDT', 'UNI/USDT',
    'ATOM/USDT', 'ETC/USDT', 'NEAR/USDT', 'ALGO/USDT', 'AAVE/USDT',
    'ICP/USDT', 'FIL/USDT', 'ARB/USDT', 'OP/USDT', 'TIA/USDT',
    'ORDI/USDT', 'SUI/USDT', 'SEI/USDT', 'INJ/USDT', 'RNDR/USDT',
    'STX/USDT', 'GRT/USDT', 'LDO/USDT', 'IMX/USDT', 'APT/USDT',
    'FET/USDT', 'PEPE/USDT', 'FLOKI/USDT', 'BONK/USDT', 'WLD/USDT'
]

import logging
logging.getLogger('ccxt').setLevel(logging.ERROR)

async def fetch_exchange_tickers_optimized(exch, symbols):
    """Borsadan tüm sembolleri tek bir 'fetch_tickers' isteği ile toplu çeker."""
    exch_name = exch.id
    print(f"[{exch_name}] Piyasalar yukleniyor...")
    
    try:
        # Piyasaları bir kez yükle (Hangi sembollerin desteklendiğini bilmek için)
        markets = await exch.load_markets()
        
        # Borsa özelinde sembol dönüşümü (Örn: Kucoin MATIC -> POL)
        valid_symbols = []
        for s in symbols:
            # Kucoin için özel durum: MATIC/USDT artık POL/USDT oldu
            target_s = s
            if exch_name == 'kucoin' and s == 'MATIC/USDT':
                target_s = 'POL/USDT'
            
            if target_s in markets:
                valid_symbols.append(target_s)
        
        if not valid_symbols:
            print(f"  [{exch_name}] Gecerli sembol bulunamadi.")
            return {}

        print(f"[{exch_name}] Toplu tarama basliyor ({len(valid_symbols)}/{len(symbols)} cifte)...")
        
        # fetch_tickers desteği kontrolü ve kullanımı
        if exch.has['fetchTickers']:
            tickers = await asyncio.wait_for(exch.fetch_tickers(valid_symbols), timeout=10.0)
            # Sadece bid/ask olanları filtrele ve orijinal isimlendirmeye geri dön (karşılaştırma için)
            final_tickers = {}
            for s, t in tickers.items():
                if t.get('bid') and t.get('ask'):
                    # Eğer biz sembolü değiştirdiysek (POL -> MATIC), geri çevir ki karşılaştırma motoru anlasın
                    orig_s = s
                    if exch_name == 'kucoin' and s == 'POL/USDT':
                        orig_s = 'MATIC/USDT'
                    final_tickers[orig_s] = t
            
            print(f"  [{exch_name}] {len(final_tickers)} sembol toplu olarak alindi.")
            return final_tickers
        else:
            # Desteği yoksa (nadir), mecburen tek tek ama hızlıca tara
            print(f"  [{exch_name}] fetchTickers desteklenmiyor. Sıralı taramaya geçiliyor...")
            results = {}
            for symbol in symbols:
                try:
                    ticker = await asyncio.wait_for(exch.fetch_ticker(symbol), timeout=3.0)
                    if ticker and ticker.get('bid') and ticker.get('ask'):
                        results[symbol] = ticker
                except:
                    continue
            return results
    except Exception as e:
        print(f"  [{exch_name}] Kritik Hata: {type(e).__name__} - {str(e)}")
        return {}

async def get_arbitrage_data_async(provided_exchanges=None):
    """
    Borsalardan verileri toplu çeker ve fırsatları hesaplar.
    provided_exchanges: Eğer dışarıdan (bridge_server) persist instance'lar gelirse onları kullanır.
    """
    exchange_names = ['gateio', 'bybit', 'kucoin'] # Binance yerine Gate.io (Amerika IP engeli yok)
    
    # Instance yönetimi
    if provided_exchanges:
        exchanges = provided_exchanges
    else:
        exchanges = {name: getattr(ccxt, name)() for name in exchange_names}
    
    try:
        # Tüm borsaları paralel tara
        tasks = [fetch_exchange_tickers_optimized(exchanges[name], SYMBOLS) for name in exchange_names if name in exchanges]
        raw_results = await asyncio.gather(*tasks)
        
        # Verileri birleştir: {symbol: {exch_name: ticker}}
        data = {}
        for i, ex_name in enumerate([n for n in exchange_names if n in exchanges]):
            tickers = raw_results[i]
            for symbol, ticker in tickers.items():
                if symbol not in data: data[symbol] = {}
                data[symbol][ex_name] = ticker
                
        final_results = []
        for symbol, tickers in data.items():
            ex_list = list(tickers.keys())
            if len(ex_list) < 2: continue
            
            # Tüm kombinasyonları incele
            for i in range(len(ex_list)):
                for j in range(len(ex_list)):
                    if i == j: continue
                    
                    ex1_name = ex_list[i]
                    ex2_name = ex_list[j]
                    
                    ex1 = tickers[ex1_name]
                    ex2 = tickers[ex2_name]
                    
                    # Formül: ex2'de sat (bid), ex1'de al (ask)
                    profit = ex2['bid'] - ex1['ask']
                    pct = (profit / ex1['ask']) * 100
                    
                    if pct > 0.05: # %0.05 altı gürültüdür
                        final_results.append({
                            "symbol": symbol,
                            "spread_pct": round(pct, 2),
                            "buy_at": ex1_name.capitalize(),
                            "sell_at": ex2_name.capitalize(),
                            "buy_price": ex1['ask'],
                            "sell_price": ex2['bid'],
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })

        # En iyi 20 fırsatı dön
        return sorted(final_results, key=lambda x: x['spread_pct'], reverse=True)[:20]
        
    finally:
        # Sadece biz oluşturduysak kapat
        if not provided_exchanges:
            for exch in exchanges.values():
                await exch.close()

def get_arbitrage_data():
    """Sync wrapper."""
    try:
        return asyncio.run(get_arbitrage_data_async())
    except Exception as e:
        print(f"Arbitrage Error: {e}")
        return []

if __name__ == "__main__":
    print("--- MEGA ARBITRAJ MOTORU TESTİ (40+ TOKEN) ---")
    start = time.time()
    data = get_arbitrage_data()
    end = time.time()
    for row in data:
        print(f"[{row['timestamp']}] {row['symbol']}: %{row['spread_pct']} ({row['buy_at']} -> {row['sell_at']})")
    print(f"\nSüre: {end - start:.2f} saniye. Fırsat: {len(data)}")

