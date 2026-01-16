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
    zaman = datetime.now(timezone.utc).isoformat()
    
    # 1. CANLI TABLOYU GÜNCELLE
    try:
        data_live = {
            "symbol": sembol,
            "price": float(fiyat),
            "category": kategori,
            "last_updated": zaman
        }
        supabase.table("live_market").upsert(data_live).execute()
        
        # 2. GEÇMİŞ TABLOSUNA EKLE (Grafik için)
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
    
    # --- 1. HİSSE SENETLERİ ---
    hisseler = ["THYAO", "GARAN", "ASELS", "SISE", "KCHOL"] 
    print(f"📊 {len(hisseler)} Hisse taranıyor...")
    
    for kod in hisseler:
        try:
            hisse = bp.Ticker(kod)
            # info'dan son fiyatı alıyoruz
            if hisse.info and "last" in hisse.info:
                fiyat = hisse.info["last"]
                veri_gonder(kod, fiyat, "hisse")
            else:
                 print(f"❌ {kod} fiyatı bulunamadı.")
        except Exception as e:
            print(f"❌ {kod} hatası: {e}")

    # --- 2. YATIRIM FONLARI (TEFAS) ---
    # İsteğin fon kodlarını buraya ekleyebilirsin
    fonlar = ["TTE", "AFT", "MAC", "YAS"] 
    print(f"📈 {len(fonlar)} Fon taranıyor...")

    for kod in fonlar:
        try:
            fon = bp.Fund(kod)
            # Fonlarda fiyat genellikle 'last_price' veya 'price' olarak döner
            # Garanti olsun diye info içindeki olası fiyat alanlarını kontrol edelim
            fiyat = None
            if fon.info:
                # TEFAS verisinde fiyat genelde bu alanlarda olur
                fiyat = fon.info.get("last_price") or fon.info.get("price")
            
            if fiyat:
                veri_gonder(kod, fiyat, "fon")
            else:
                print(f"❌ {kod} fon fiyatı çekilemedi.")
                
        except Exception as e:
             print(f"❌ {kod} fon hatası: {e}")

    # --- 3. DÖVİZ & ALTIN ---
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