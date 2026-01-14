import sqlite3
import os
import time

class DatabaseManager:
    def __init__(self, db_path=r"C:\Google Antigravity\borsa_botu\deepverify.db"):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        """Tablolari olusturur."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Islem Tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT,
                start_time TEXT,
                end_time TEXT,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                balance REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sistem Durum Tablosu (Snapshotlar icin)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def sync_from_csv(self, csv_path):
        """CSV'den verileri veritabanina aktarir (Eger henuz yoksa)."""
        import pandas as pd
        if not os.path.exists(csv_path):
            return
            
        try:
            # Turkce basliklara sahip CSV'yi oku
            df = pd.read_csv(csv_path)
            if df.empty:
                return
                
            # SQLite kolon isimlerine map et (Turkce basliklari dusunerek)
            # CSV: Giriş Zamanı,Çıkış Zamanı,Yön,Giriş Fiyatı,Çıkış Fiyatı,PnL ($),Bakiye ($)
            df.columns = ["start_time", "end_time", "side", "entry_price", "exit_price", "pnl", "balance"]
            df["bot_name"] = "LEGACY_BOT" # Eski datalar icin bot ismi
            
            # Mevcut islem sayisini kontrol et
            conn = self._get_connection()
            count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
            
            if len(df) > count:
                # Sadece yeni satirlari ekle (bot_name'i sona veya dogru siraya koy)
                new_data = df.iloc[count:][["bot_name", "start_time", "end_time", "side", "entry_price", "exit_price", "pnl", "balance"]]
                new_data.to_sql('trades', conn, if_exists='append', index=False)
                print(f"DB: {len(new_data)} yeni islem senkronize edildi.")
            
            conn.close()
        except Exception as e:
            print(f"DB Sync Hatasi: {e}")

    def log_virtual_trade(self, bot_name, entry_time, exit_time, side, entry_price, exit_price, pnl, balance):
        """Gercek zamanli bir islemi veritabanina kaydeder."""
        conn = self._get_connection()
        try:
            conn.execute('''
                INSERT INTO trades (bot_name, start_time, end_time, side, entry_price, exit_price, pnl, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bot_name, entry_time, exit_time, side, entry_price, exit_price, pnl, balance))
            conn.commit()
        except Exception as e:
            print(f"DB Log Hatasi: {e}")
        finally:
            conn.close()

    def get_metrics(self):
        """Genel metrikleri doner (Frontend uyumlu keyler ile)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Sadece yeni sanal islem varsa onlari da hesaba kat (veya sadece onlari don)
            # Simdilik tumunu donelim ama keyleri duzeltelim
            total_pnl = cursor.execute("SELECT SUM(pnl) FROM trades").fetchone()[0] or 0.0
            last_balance = cursor.execute("SELECT balance FROM trades ORDER BY id DESC LIMIT 1").fetchone()
            last_balance = last_balance[0] if last_balance else 250.0
            
            # Son 10 islem (Frontend'in bekledigi PascalCase keyler ile)
            cursor.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            
            trades = []
            for row in rows:
                trades.append({
                    "Bot": row[1], # bot_name
                    "Date": row[3], # end_time (veya start_time)
                    "Side": row[4], # side
                    "Entry": row[5], # entry_price
                    "Exit": row[6], # exit_price
                    "PnL": row[7], # pnl
                    "Balance": row[8] # balance
                })
            
            return {
                "total_pnl": round(total_pnl, 2),
                "balance": round(last_balance, 2),
                "trades": trades
            }
        finally:
            conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    print("Veritabani basariyla hazirlandi.")
    db.sync_from_csv(r"C:\Google Antigravity\borsa_botu\sampiyon_islemler.csv")
    metrics = db.get_metrics()
    print(f"Metrikler: {metrics['total_pnl']} PnL, {metrics['balance']} Bakiye")
