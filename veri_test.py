import borsapy as bp

# 1. Borsa verisini çekelim (THY Örneği)
print("Veri çekiliyor...")
hisse = bp.Ticker("THYAO")
fiyat = hisse.info["last"] # Son fiyat

print(f"THYAO Güncel Fiyatı: {fiyat} TL")

# 2. Döviz verisini çekelim
usd = bp.FX("USD")
dolar_kuru = usd.current
print(f"Dolar Kuru: {dolar_kuru} TL")

print("Sistem başarıyla çalışıyor! Şimdi Supabase bağlantısına geçebiliriz.")