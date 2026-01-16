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
MAX_WORKERS = 20   # Hız için robot sayısını artırdım
BATCH_SIZE = 100   # 100'erli paketler

def hisse_verisi_getir(kod):
    """Tek bir hissenin verisini çeker"""
    try:
        kod = str(kod).strip()
        hisse = bp.Ticker(kod)
        
        if hisse.info:
            fiyat = hisse.info.get("last") or hisse.info.get("price")
            if fiyat:
                degisim = hisse.info.get("percentage_change", 0)
                hacim = hisse.info.get("volume", 0)
                return {
                    "symbol": kod,
                    "price": float(fiyat),
                    "change_rate": float(degisim) if degisim else 0.0,
                    "volume": float(hacim) if hacim else 0.0,
                    "category": "hisse",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
    except:
        return None
    return None

def veri_gonder_toplu(veri_listesi, tablo="live_market"):
    if not veri_listesi: return
    try:
        supabase.table(tablo).upsert(veri_listesi).execute()
        print(f"📡 {len(veri_listesi)} satır veri gönderildi.")
    except Exception as e:
        print(f"⚠️ Yazma hatası: {e}")

def main():
    print("🚀 TURBO V3: Manuel Dev Liste Modu...")
    
    # ---------------------------------------------------------
    # 1. HİSSE SENETLERİ (A'dan Z'ye TÜM BORSA)
    # ---------------------------------------------------------
    # Otomatik çekim hata verdiği için listeyi ELLE veriyoruz.
    # Bu liste BIST Tüm endeksindeki hisseleri kapsar.
    hisse_listesi = [
        "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AGYO", "AHGAZ",
        "AKBNK", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY", "AKSUE",
        "AKYHO", "ALARK", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALGYO", "ALKA", "ALKIM", "ALMAD", "ALTNY",
        "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ARZUM", "ASELS",
        "ASGYO", "ASTOR", "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL",
        "AVOD", "AVPGY", "AYCES", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAKAB", "BALAT",
        "BANVT", "BARMA", "BASCM", "BASGZ", "BAYRK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENY", "BIGCH",
        "BIMAS", "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTL", "BNTAS", "BOBET", "BOSSA", "BRISA",
        "BRKO", "BRKSN", "BRKVY", "BRLSM", "BRMEN", "BRSAN", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE",
        "BURVA", "BVSAN", "BYDNR", "CANTE", "CASA", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CEOEM",
        "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE",
        "DAGHL", "DAGI", "DAPGM", "DARDL", "DENGE", "DERHL", "DERIM", "DESA", "DESPC", "DEVA", "DGATE",
        "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMSAS", "DNISI", "DOAS", "DOBUR", "DOCO", "DOGUB", "DOHOL",
        "DOKTA", "DURDO", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EGEEN", "EGEPO",
        "EGGUB", "EGPRO", "EGSER", "EKGYO", "EKIZ", "EKSUN", "ELITE", "EMKEL", "EMNIS", "ENJSA", "ENKAI",
        "ENSRI", "EPLAS", "ERBOS", "ERCB", "EREGL", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR", "ETYAT",
        "EUHOL", "EUKYO", "EUPWR", "EUREN", "EUYO", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET",
        "FORMT", "FRIGO", "FROTO", "FZLGY", "GARAN", "GARFA", "GEDIK", "GEDZA", "GENIL", "GENTS", "GEREL",
        "GESAN", "GLBMD", "GLCVY", "GLRYH", "GLYHO", "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO",
        "GRSEL", "GSDDE", "GSDHO", "GSRAY", "GUBRF", "GWIND", "GZNMI", "HALKB", "HATEK", "HDFGS", "HEDEF",
        "HEKTS", "HKTM", "HLGYO", "HTTBT", "HUBVC", "HUNER", "HURGZ", "ICBCT", "IDEAS", "IDGYO", "IEYHO",
        "IHAAS", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM",
        "INVEO", "INVES", "IPEKE", "ISATR", "ISBIR", "ISBTR", "ISCTR", "ISDMR", "ISFIN", "ISGSY", "ISGYO",
        "ISKPL", "ISKUR", "ISMEN", "ISSEN", "ISYAT", "ITTFH", "IZFAS", "IZINV", "IZMDC", "JANTS", "KAPLM",
        "KAREL", "KARSN", "KARYE", "KATMR", "KAYSE", "KBORU", "KCAER", "KCMKW", "KENT", "KERVN", "KERVT",
        "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLKIM", "KLMSN", "KLNMA", "KLRHO", "KLSYN", "KMPUR", "KNFRT",
        "KONKA", "KONTR", "KONYA", "KOPOL", "KORDS", "KOZAA", "KOZAL", "KRDMA", "KRDMB", "KRDMD", "KRGYO",
        "KRONT", "KRPLS", "KRSTL", "KRTEK", "KRVGD", "KSTUR", "KTLEV", "KTSKR", "KUTPO", "KUVVA", "KUYAS",
        "KZBGY", "KZGYO", "LIDER", "LIDFA", "LINK", "LKMNH", "LOGO", "LUPUS", "LUKSK", "MAALT", "MACKO",
        "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEKAG",
        "MNDRS", "MERCN", "MERIT", "MERKO", "METUR", "MGROS", "MIATK", "MIPAZ", "MMCAS", "MNDTR", "MOBTL",
        "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MUNDA", "NATEN", "NETAS", "NIBAS", "NTGAZ",
        "NTHOL", "NUGYO", "NUHCM", "OBASE", "ODAS", "OFCYM", "ONCSM", "ORCAY", "ORGE", "ORMA", "OSMEN",
        "OSTIM", "OTKAR", "OTTO", "OYAKC", "OYAYO", "OYLUM", "OYYAT", "OZGYO", "OZKGY", "OZRDN", "OZSUB",
        "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PASEU", "PCILT", "PEGYO", "PEKGY", "PENGD", "PENTA",
        "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PLTUR", "PNLSN", "PNSUT", "POLHO", "POLTK",
        "PRDGS", "PRKAB", "PRKME", "PRZMA", "PSGYO", "PSDTC", "QNBFB", "QNBFL", "QUAGR", "RALYH", "RAYSG",
        "RNPOL", "REEDR", "RHEAG", "RODRG", "ROYAL", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAHOL",
        "SAMAT", "SANEL", "SANFM", "SANKO", "SARKY", "SASA", "SAYAS", "SDTTR", "SEKFK", "SEKUR", "SELEC",
        "SELGD", "SELVA", "SEYKM", "SILVR", "SISE", "SKBNK", "SKTAS", "SMART", "SMRTG", "SNGYO", "SNKRN",
        "SNPAM", "SODSN", "SOKE", "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SUWEN", "TABGD", "TARKM",
        "TATGD", "TAVHL", "TBORG", "TCELL", "TDGYO", "TEKTU", "TERA", "TETMT", "TEZOL", "TGSAS", "THYAO",
        "TKFEN", "TKNSA", "TLMAN", "TMPOL", "TMSN", "TNZTP", "TOASO", "TRCAS", "TRGYO", "TRILC", "TSGYO",
        "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURGG", "TURSG", "UFUK",
        "ULAS", "ULKER", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNLU", "USAK", "UZERB", "VAKBN", "VAKFN",
        "VAKKO", "VANGD", "VBTYZ", "VERUS", "VESBE", "VESTL", "VKFYO", "VKGYO", "VKING", "YAPRK", "YATAS",
        "YAYLA", "YEOTK", "YESIL", "YGGYO", "YGYO", "YKBNK", "YKSLN", "YONGA", "YUNSA", "YYAPI", "YYLGD",
        "ZEDUR", "ZOREN", "ZRGYO"
    ]

    print(f"📊 {len(hisse_listesi)} Hisse taranıyor...")
    
    # Paralel Tarama
    toplanacak_veriler = []
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
    # 2. FONLAR (TOPTAN ÇEKİM)
    # ---------------------------------------------------------
    print("📈 Fonlar taranıyor...")
    try:
        # Fonlarda da timeout olabilir, o yüzden hata yakalama ekledik
        fon_tablosu = bp.screen_funds()
        fon_verileri = []
        if not fon_tablosu.empty:
            print(f"📦 {len(fon_tablosu)} Adet Fon Bulundu.")
            for kod, satir in fon_tablosu.iterrows():
                try:
                    fiyat = satir.get("price")
                    if fiyat:
                        fon_verileri.append({
                            "symbol": str(kod),
                            "price": float(fiyat),
                            "change_rate": 0, "volume": 0,
                            "category": "fon",
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        })
                except: continue
        
        for i in range(0, len(fon_verileri), 200):
            veri_gonder_toplu(fon_verileri[i:i+200])
            
    except Exception as e:
        print(f"❌ Fon hatası: {e} (Geçici sunucu yoğunluğu olabilir)")

    # ---------------------------------------------------------
    # 3. DÖVİZ
    # ---------------------------------------------------------
    print("💰 Dövizler...")
    try:
        dovizler = []
        zaman = datetime.now(timezone.utc).isoformat()
        for k in ["USD", "EUR", "GBP", "GRAM-ALTIN"]:
            try:
                v = bp.FX(k.lower())
                val = v.current["last"] if isinstance(v.current, dict) else v.current
                dovizler.append({
                    "symbol": k,
                    "price": float(val),
                    "change_rate": 0, "volume": 0,
                    "category": "doviz" if "ALTIN" not in k else "altin",
                    "last_updated": zaman
                })
                supabase.table("price_history").insert({
                    "symbol": k, "price": float(val), "created_at": zaman
                }).execute()
            except: pass
        veri_gonder_toplu(dovizler)
    except: pass

    print("🏁 İŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    main()