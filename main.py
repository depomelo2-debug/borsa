import os
import borsapy as bp
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# 1. Ayarları Yükle
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("HATA: .env dosyasında SUPABASE_URL veya SUPABASE_KEY eksik!")
    exit()

# Supabase Bağlantısı
supabase: Client = create_client(url, key)

def veri_gonder(sembol, fiyat, kategori):
    """Veriyi Supabase'e yazar"""
    data = {
        "symbol": sembol,
        "price": fiyat,
        "category": kategori,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    # 'upsert': Kayıt varsa günceller, yoksa yeni ekler
    response = supabase.table("live_market").upsert(data).execute()
    print(f"✅ {sembol} güncellendi: {fiyat}")

def main():
    print("🚀 Veri akışı başlıyor...")
    
    # --- HİSSE SENETLERİ ---
    hisseler = ["THYAO", "GARAN", "ASELS", "SISE"] # İstediklerini ekle
    for kod in hisseler:
        try:
            hisse = bp.Ticker(kod)
            fiyat = hisse.info.get("last") # Hata almamak için .get kullandık
            if fiyat:
                veri_gonder(kod, fiyat, "hisse")
        except Exception as e:
            print(f"❌ {kod} hatası: {e}")

    # --- DÖVİZ & ALTIN ---
    try:
        # Dolar
        usd = bp.FX("USD")
        if usd.current:
            # borsapy bazen dict dönüyor, bazen float. Kontrol edelim:
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