
import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(
    page_title="KOZMIK KAPTAN KOSKU",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Başlık ---
st.title("🚀 KOZMIK KAPTAN KÖŞKÜ")
st.markdown("---")

# --- Dosya Yolları ---
LOG_FILE = "borsa_gunlugu.txt"
CSV_FILE = "sampiyon_islemler.csv"

# --- Sidebar: Kontrol ---
with st.sidebar:
    st.header("⚙️ Kontrol Paneli")
    st.info("Bu panel, çalışan 'multi_bot.py' scriptini izler.")
    refresh_rate = st.slider("Yenileme Hızı (sn)", 1, 60, 5)
    
    st.markdown("---")
    st.subheader("💡 Arbitraj Nedir?")
    st.markdown("""
    **Arbitraj**, aynı varlığın farklı borsalardaki fiyat farkından kâr etmektir.
    
    **Nasıl Yapacağız?**
    1. Binance ve Gate.io gibi iki borsaya bağlanacağız.
    2. Fiyatları anlık çekeceğiz (Örn: BTC Binance: 100$, BTC Gate: 101$).
    3. Ucuz yerden alıp pahalı yerde satacağız.
    
    *Bu özellik yakında eklenecek!*
    """)

# --- Ana Dashboard ---

# 1. Metrikler (CSV'den)
if os.path.exists(CSV_FILE):
    try:
        # CSV formatı: BotName,Date,Side,Entry,Exit,PnL,Balance
        df = pd.read_csv(CSV_FILE, names=["Bot", "Tarih", "Yön", "Giriş", "Çıkış", "PnL", "Bakiye"])
        
        if not df.empty:
            total_pnl = df["PnL"].sum()
            win_count = len(df[df["PnL"] > 0])
            total_trades = len(df)
            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
            current_balance = df["Bakiye"].iloc[-1]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Toplam Kâr/Zarar", f"{total_pnl:.2f}$", delta_color="normal")
            col2.metric("🏦 Güncel Kasa", f"{current_balance:.2f}$")
            col3.metric("🎯 Başarı Oranı", f"%{win_rate:.1f}")
            col4.metric("📊 Toplam İşlem", total_trades)
            
            # Grafik
            st.subheader("📈 Kasa Büyümesi")
            st.line_chart(df["Bakiye"])
            
            # Tablo
            with st.expander("📜 İşlem Geçmişi (CSV)", expanded=False):
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        else:
            st.warning("Henüz hiç işlem kapatılmamış.")
            
    except Exception as e:
        st.error(f"CSV Okuma Hatası: {e}")
else:
    st.info("Henüz işlem kaydı (CSV) yok. Bot işlem yaptıkça burası dolacak.")


# 2. Canlı Loglar (TXT'den)
st.subheader("📝 Canlı Bot Günlüğü")
log_placeholder = st.empty()

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_lines = lines[-20:] # Son 20 satır
        
    log_text = "".join(last_lines)
    log_placeholder.code(log_text, language="log")
else:
    log_placeholder.warning("Log dosyası bulunamadı. Bot çalışıyor mu?")

# Otomatik Yenileme
time.sleep(refresh_rate)
st.rerun()
