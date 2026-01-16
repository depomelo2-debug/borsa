import os
import time
import borsapy as bp
import concurrent.futures
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

# --- AYARLAR ---
MAX_WORKERS = 15  # Hız için 15 paralel robot
BATCH_SIZE = 50   # Veritabanına 50'şer 50'şer paketle

def hisse_verisi_getir(kod):
    """
    Tek bir hissenin Fiyat, Değişim ve Hacim verisini çeker.
    """
    try:
        hisse = bp.Ticker(kod)
        if hisse.info and "last" in hisse.info:
            fiyat = hisse.info["last"]
            degisim = hisse.info.get("percentage_change")
            hacim = hisse.info.get("volume")

            # Veri temizliği (None gelirse 0 yap)
            f_fiyat = float(fiyat) if fiyat else 0.0
            f_degisim = float(degisim) if degisim else 0.0
            f_hacim = float(hacim) if hacim else 0.0

            return {
                "symbol": kod,
                "price": f_fiyat,
                "change_rate": f_degisim, # Yüzdelik değişim
                "volume": f_hacim,        # Hacim
                "category": "hisse",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
    except:
        return None
    return None

def veri_gonder_toplu(veri_listesi, tablo="live_market"):
    """Verileri paket halinde veritabanına yazar"""
    if not veri_listesi: return
    try:
        supabase.table(tablo).upsert(veri_listesi).execute()
        print(f"📡 {len(veri_listesi)} adet veri {tablo} tablosuna işlendi.")
    except Exception as e:
        print(f"⚠️ Yazma hatası: {e}")

def main():
    print("🚀 KOMBO MOD: Tam Kapsamlı Veri Akışı Başlıyor...")
    
    # ---------------------------------------------------------
    # 1. HİSSE SENETLERİ (PARALEL İŞLEM)
    # ---------------------------------------------------------
    hisse_listesi = []
    try:
        # Otomatik tüm listeyi çekmeyi dene
        tum_sirketler = bp.companies()
        if hasattr(tum_sirketler, 'index'):
            hisse_listesi = tum_sirketler.index.tolist()
    except:
        pass

    # Otomatik liste boşsa veya hata verdiyse DEV YEDEK LİSTE'yi kullan
    if len(hisse_listesi) < 10:
        print("⚠️ Otomatik liste alınamadı, Manuel Dev Liste devreye giriyor.")
        hisse_listesi = [
            "THYAO", "GARAN", "ASELS", "SISE", "KCHOL", "AKBNK", "EREGL", "TUPRS", "FROTO", "BIMAS",
            "SASA", "HEKTS", "PETKM", "ISCTR", "YKBNK", "SAHOL", "ENKAI", "TCELL", "TTKOM", "KRDMD",
            "KOZAL", "ODAS", "ZOREN", "ASTOR", "EUPWR", "KONTR", "GESAN", "REEDR", "MIATK", "ALFAS",
            "CANTE", "PENTA", "QUAGR", "SMRTG", "GUBRF", "EKGYO", "VESTL", "ARCLK", "TOASO", "AEFES",
            "AGHOL", "AHGAZ", "AKFGY", "AKGRT", "AKSA", "AKSEN", "ALARK", "ALBRK", "ALGYO", "ALKIM",
            "AYDEM", "BAGFS", "BERA", "BIOEN", "BOBET", "BRSAN", "BRYAT", "BUCIM", "CEMTS", "CIMSA",
            "CWENE", "DOHOL", "ECILC", "EGEEN", "ENJSA", "GENIL", "GLYHO", "GOZDE", "GWIND", "HALKB",
            "IHLAS", "IPEKE", "ISDMR", "ISGYO", "ISMEN", "IZMDC", "KARSN", "KAYSE", "KCAER", "KMPUR",
            "KONYA", "KORDS", "KOZAA", "MTRKS", "MAVI", "MGROS", "NTHOL", "OYAKC", "PGSUS", "PSGYO",
            "SAKLA", "SDTTR", "SELEC", "SKBNK", "SNGYO", "SOKM", "TATGD", "TAVHL", "TKFEN", "TMSN",
            "TSKB", "TURSG", "ULKER", "VAKBN", "VESBE", "YEOTK", "YYLGD"
        ]

    print(f"📊 {len(hisse_listesi)} Hisse taranıyor...")
    
    toplanacak_veriler = []
    # ThreadPoolExecutor: Aynı anda 15 hisseyi tarar
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        sonuclar = executor.map(hisse_verisi_getir, hisse_listesi)
        
        for veri in sonuclar:
            if veri:
                toplanacak_veriler.append(veri)
                if len(toplanacak_veriler) >= BATCH_SIZE:
                    veri_gonder_toplu(toplanacak_veriler)
                    toplanacak_veriler = []

    if toplanacak_veriler:
        veri_gonder_toplu(toplanacak_veriler)

    # ---------------------------------------------------------
    # 2. FONLAR (TOPTAN ÇEKİM - BULK)
    # ---------------------------------------------------------
    print("📈 Tüm Fonlar taranıyor...")
    try:
        fon_tablosu = bp.screen_funds()
        fon_verileri = []
        if not fon_tablosu.empty:
            for kod, satir in fon_tablosu.iterrows():
                try:
                    fiyat = satir.get("price")
                    if fiyat:
                        fon_verileri.append({
                            "symbol": kod,
                            "price": float(fiyat),
                            "category": "fon",
                            "last_updated": datetime.now(timezone.utc).isoformat(),
                            "change_rate": 0, # Fonlarda anlık değişim verisi genelde olmaz
                            "volume": 0
                        })
                except: continue
        
        # 100'erli paketler halinde gönder
        for i in range(0, len(fon_verileri), 100):
            veri_gonder_toplu(fon_verileri[i:i+100])
            
    except Exception as e:
        print(f"❌ Fon hatası: {e}")

    # ---------------------------------------------------------
    # 3. DÖVİZ & ALTIN
    # ---------------------------------------------------------
    print("💰 Döviz ve Altın taranıyor...")
    try:
        doviz_listesi = []
        zaman = datetime.now(timezone.utc).isoformat()
        for kur in ["USD", "EUR", "GBP", "GRAM-ALTIN"]:
            veri = bp.FX(kur.lower())
            val = veri.current["last"] if isinstance(veri.current, dict) else veri.current
            
            doviz_listesi.append({
                "symbol": kur,
                "price": float(val),
                "category": "doviz" if "ALTIN" not in kur else "altin",
                "last_updated": zaman,
                "change_rate": 0,
                "volume": 0
            })
            
            # Grafikleri de kaydedelim (Sadece bunlar için)
            supabase.table("price_history").insert({
                 "symbol": kur, "price": float(val), "created_at": zaman
            }).execute()
        
        veri_gonder_toplu(doviz_listesi)
        
    except Exception as e:
        print(f"❌ Döviz hatası: {e}")

    print("🏁 TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    main()