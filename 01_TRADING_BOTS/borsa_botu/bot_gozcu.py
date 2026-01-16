
import os
import time
import winsound
from datetime import datetime

# Hedef dosya
LOG_FILE = "borsa_gunlugu.txt"
# Kaç dakika sessiz kalırsa uyarı versin?
THRESHOLD_MINUTES = 5

def check_bot_status():
    print(f"👀 Gözcü Başlatıldı: {LOG_FILE} izleniyor...")
    
    while True:
        try:
            if not os.path.exists(LOG_FILE):
                print(f"❌ HATA: {LOG_FILE} dosyası bulunamadı!")
                winsound.Beep(500, 1000)
            else:
                # Son değiştirilme zamanı
                mod_time = os.path.getmtime(LOG_FILE)
                last_update = datetime.fromtimestamp(mod_time)
                now = datetime.now()
                
                diff = now - last_update
                diff_minutes = diff.total_seconds() / 60
                
                status_symbol = "✅" if diff_minutes < THRESHOLD_MINUTES else "⚠️"
                
                print(f"{status_symbol} [{now.strftime('%H:%M:%S')}] Son günceleme: {diff_minutes:.1f} dakika önce.")
                
                if diff_minutes >= THRESHOLD_MINUTES:
                    print(f"🚨 UYARI: Bot {THRESHOLD_MINUTES} dakikadır işlem yapmıyor veya log yazmıyor!")
                    # Alarm sesi (3 kısa bip)
                    winsound.Beep(1000, 200)
                    winsound.Beep(1000, 200)
                    winsound.Beep(1000, 200)
            
            # 60 saniye bekle
            time.sleep(60)
            
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            time.sleep(60)

if __name__ == "__main__":
    check_bot_status()
