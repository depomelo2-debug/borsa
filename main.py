import os
import borsapy as bp
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

# Ayarları yükle
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("HATA: API anahtarları eksik! .env dosyasını kontrol et.")
    exit()

supabase: Client = create_client(url, key)

def veri_gonder(sembol, fiyat, kategori):
    # Datetime uyarısını düzelttik: timezone.utc kullanıyoruz
    zaman = datetime.now(timezone.utc).isoformat()
    
    # 1. CANLI TABLOYU GÜNCELLE
    try:
        data_live = {
            "symbol": sembol,
            "price": float(fiyat), # Sayıya çevirmeyi garantiye alalım
            "category": kategori,
            "last_updated": zaman
        }
        supabase.table("live_market").upsert(data_live).execute()
        
        # 2. GEÇMİŞ TABLOSUNA EKLE
        data_history = {
            "symbol": sembol,
            "price": float(fiyat),
            "created_at": zaman
        }
        supabase.table("price_history").insert(data_history).execute()
        
        print(f"✅ {sembol}: {fiyat} TL -> Kaydedildi.")
        
    except Exception as e:
        print(f"⚠️ {sembol} veritabanı hatası: {e}")

def main():
    print("🚀 Veri akışı başlıyor...")
    
    # --- HİSSELER ---
    # Listeyi şimdilik kısa tutalım, çalışırsa artırırız
    hisseler = ["THYAO", "GARAN", "ASELS", "SISE"] 
    
    print("📊 Hisseler taranıyor...")
    for kod in hisseler:
        try:
            # Doğrudan test dosyasındaki gibi basit çekiyoruz
            hisse = bp.Ticker(kod)
            # Veriyi zorla çekip ekrana yazdıralım ki ne geldiğini görelim
            raw_info = hisse.info 
            
            # Fiyatı almayı dene
            fiyat = raw_info["last"]
            veri_gonder(kod, fiyat, "hisse")
            
        except Exception as e:
            # Sessiz kalma, hatayı bağır!
            print(f"❌ {kod} verisi çekilemedi! Sebep: {e}")

    # --- DÖVİZ & ALTIN ---
    print("💰 Dövizler taranıyor...")
    try:
        # Dolar
        usd = bp.FX("USD")
        if usd.current:
            fiyat = usd.current["last"] if isinstance(usd.current, dict) else usd.current
            veri_gonder("USD", fiyat, "doviz")
            
        # Gram Altın
        altin = bp.FX("gram-altin")
        if altin.current:
            fiyat = altin.current["last"] if isinstance(altin.current, dict) else altin.current
            veri_gonder("GRAM-ALTIN", fiyat, "altin")
            
    except Exception as e:
        print(f"❌ Döviz hatası: {e}")

if __name__ == "__main__":
    main()