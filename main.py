import os
import time
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

def veri_gonder(sembol, fiyat, kategori, grafik_kaydet=False):
    zaman = datetime.now(timezone.utc).isoformat()
    
    try:
        # 1. CANLI TABLOYU GÜNCELLE (Hepsini kaydet)
        data_live = {
            "symbol": sembol,
            "price": float(fiyat),
            "category": kategori,
            "last_updated": zaman
        }
        supabase.table("live_market").upsert(data_live).execute()
        
        # 2. GEÇMİŞ TABLOSUNA EKLE (Sadece seçilenleri kaydet - Kota dostu)
        if grafik_kaydet:
            data_history = {
                "symbol": sembol,
                "price": float(fiyat),
                "created_at": zaman
            }
            supabase.table("price_history").insert(data_history).execute()
            print(f"✅ {sembol}: {fiyat} TL -> Güncellendi (+Grafik)")
        else:
            print(f"✅ {sembol}: {fiyat} TL -> Güncellendi (Sadece Fiyat)")
            
    except Exception as e:
        print(f"⚠️ {sembol} DB hatası: {e}")

def main():
    print("🚀 DEV Veri akışı başlıyor...")
    
    # --- 1. BÜTÜN HİSSELERİ BUL (Otomatik Liste) ---
    print("📋 Borsa İstanbul şirket listesi çekiliyor...")
    try:
        # borsapy'den tüm şirketleri çekiyoruz
        tum_sirketler = bp.companies()
        
        # Sadece BIST 100 (Popüler) hisselerinin grafiğini tutalım, diğerlerinin sadece fiyatını.
        # Not: BIST 100 listesini dinamik almak uzun sürerse diye, en popülerleri elle işaretleyebiliriz
        # veya basitçe tüm hisseleri tararız. Şimdilik hepsini tarayalım:
        
        sembol_listesi = tum_sirketler.index.tolist() if hasattr(tum_sirketler, 'index') else []
        
        # Eğer liste boş gelirse (hata olursa) yedek liste devreye girsin
        if not sembol_listesi:
            print("⚠️ Liste otomatik çekilemedi, yedek liste kullanılıyor.")
            sembol_listesi = ["THYAO", "GARAN", "ASELS", "SISE", "KCHOL", "AKBNK", "EREGL", "TUPRS"]
        
        print(f"📊 Toplam {len(sembol_listesi)} hisse tarancak.")
        
        for i, kod in enumerate(sembol_listesi):
            try:
                # Çok yüklenmemek için her 50 hissede bir 2 saniye mola
                if i % 50 == 0 and i > 0:
                    print("☕ Kahve molası (Sunucuyu yormamak için 2sn bekle)...")
                    time.sleep(2)
                
                hisse = bp.Ticker(kod)
                # Veriyi güvenli çek
                if hisse.info and "last" in hisse.info:
                    fiyat = hisse.info["last"]
                    
                    # ÖNEMLİ: Grafik kaydını hepsine yaparsak veritabanı şişer.
                    # Sadece popüler olanlara veya belirli bir listeye grafik izni verelim.
                    # Şimdilik örnek olarak hepsine 'False' diyoruz, sadece CANLI fiyatı güncelliyoruz.
                    # İstersen önemli hisseler için True yapabilirsin.
                    grafik_varmi = False 
                    
                    # Örnek: Sadece BIST 30 hisselerine grafik açmak istersen:
                    bist30_ornek = ["THYAO", "GARAN", "ASELS", "AKBNK", "EREGL", "TUPRS", "BIMAS"]
                    if kod in bist30_ornek:
                        grafik_varmi = True
                        
                    veri_gonder(kod, fiyat, "hisse", grafik_kaydet=grafik_varmi)
                    
                    # Her işlemden sonra sunucuya nefes aldır (0.2 saniye)
                    time.sleep(0.2)
            except Exception as e:
                print(f"❌ {kod} pas geçildi.")

    except Exception as e:
        print(f"❌ Şirket listesi hatası: {e}")

    # --- 2. POPÜLER FONLAR (Otomatik Tarama) ---
    print("📈 Popüler Fonlar taranıyor...")
    try:
        # Son 1 ayda en çok kazandıran ilk 20 fonu bulup ekleyelim
        # screen_funds bize bir DataFrame döner
        populer_fonlar = bp.screen_funds(min_return_1m=1) # %1 üzeri getirenler
        
        # İlk 20 tanesini alalım
        if not populer_fonlar.empty:
            top_fonlar = populer_fonlar.head(20).index.tolist() # Fon kodlarını al
            
            for kod in top_fonlar:
                try:
                    fon = bp.Fund(kod)
                    fiyat = fon.info.get("last_price") or fon.info.get("price")
                    if fiyat:
                        veri_gonder(kod, fiyat, "fon", grafik_kaydet=True) # Fonların grafiği olsun
                        time.sleep(0.2)
                except:
                    pass
    except Exception as e:
        print(f"❌ Fon tarama hatası: {e}")

    # --- 3. DÖVİZ & ALTIN ---
    print("💰 Dövizler...")
    dovizler = ["USD", "EUR", "GBP"]
    for d in dovizler:
        try:
            kur = bp.FX(d)
            val = kur.current["last"] if isinstance(kur.current, dict) else kur.current
            veri_gonder(d, val, "doviz", grafik_kaydet=True)
        except:
            pass
            
    try:
        altin = bp.FX("gram-altin")
        val = altin.current["last"] if isinstance(altin.current, dict) else altin.current
        veri_gonder("GRAM-ALTIN", val, "altin", grafik_kaydet=True)
    except:
        pass

if __name__ == "__main__":
    main()