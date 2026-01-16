import os
import borsapy as bp
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("HATA: API anahtarları eksik!")
    exit()

supabase: Client = create_client(url, key)

def veri_gonder(sembol, fiyat, kategori):
    zaman = datetime.utcnow().isoformat()
    
    # 1. CANLI TABLOYU GÜNCELLE (Ana Sayfa İçin)
    # Upsert: Varsa güncelle, yoksa ekle
    data_live = {
        "symbol": sembol,
        "price": fiyat,
        "category": kategori,
        "last_updated": zaman
    }
    supabase.table("live_market").upsert(data_live).execute()
    
    # 2. GEÇMİŞ TABLOSUNA EKLE (Grafik İçin)
    # Insert: Hep yeni satır ekle
    data_history = {
        "symbol": sembol,
        "price": fiyat,
        "created_at": zaman
    }
    supabase.table("price_history").insert(data_history).execute()
    
    print(f"✅ {sembol} -> Canlı: {fiyat} | Geçmişe Eklendi.")

def main():
    print("🚀 Veri akışı başlıyor...")
    
    # --- HİSSELER ---
    hisseler = ["THYAO", "GARAN", "ASELS", "SISE", "KCHOL"] 
    for kod in hisseler:
        try:
            hisse = bp.Ticker(kod)
            # Safe access
            if hasattr(hisse, 'info') and isinstance(hisse.info, dict):
                fiyat = hisse.info.get("last")
                if fiyat:
                    veri_gonder(kod, fiyat, "hisse")
        except Exception as e:
            print(f"❌ {kod} hatası: {e}")

    # --- DÖVİZ & ALTIN ---
    try:
        usd = bp.FX("USD")
        if usd.current:
            fiyat = usd.current["last"] if isinstance(usd.current, dict) else usd.current
            veri_gonder("USD", fiyat, "doviz")
            
        altin = bp.FX("gram-altin")
        if altin.current:
            fiyat = altin.current["last"] if isinstance(altin.current, dict) else altin.current
            veri_gonder("GRAM-ALTIN", fiyat, "altin")
            
    except Exception as e:
        print(f"❌ Döviz hatası: {e}")

if __name__ == "__main__":
    main()