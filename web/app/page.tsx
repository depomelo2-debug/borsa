'use client';
import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import Link from 'next/link';

// Supabase Bağlantısı
const supabase = createClient(
  'https://oxtihxyfluoliaupeshe.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im94dGloeHlmbHVvbGlhdXBlc2hlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1NjEwMjYsImV4cCI6MjA4NDEzNzAyNn0.Ax7KUFiVynSU_Pvdg5KAKZo6s5dzKWf0LjAudHYz7yQ'
);

export default function Home() {
  const [veriler, setVeriler] = useState<any[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [aramaMetni, setAramaMetni] = useState('');
  const [seciliKategori, setSeciliKategori] = useState('HEPSI');

  useEffect(() => {
    async function veriGetir() {
      const { data, error } = await supabase
        .from('live_market')
        .select('*')
        .order('category', { ascending: true }); // Önce kategoriye göre sırala

      if (error) console.error('Hata:', error);
      else setVeriler(data || []);
      
      setYukleniyor(false);
    }

    veriGetir();
  }, []);

  // Filtreleme Mantığı
  const filtrelenmisVeriler = veriler.filter((veri) => {
    const sembolUyumu = veri.symbol.toLowerCase().includes(aramaMetni.toLowerCase());
    const kategoriUyumu = seciliKategori === 'HEPSI' || veri.category.toUpperCase() === seciliKategori;
    return sembolUyumu && kategoriUyumu;
  });

  return (
    <main className="min-h-screen bg-gray-900 text-white p-6 md:p-10">
      <div className="max-w-6xl mx-auto">
        
        {/* Başlık ve İstatistik */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            🚀 Finans Terminali
          </h1>
          <div className="text-gray-400 text-sm">
            Toplam Varlık: <span className="text-white font-bold">{veriler.length}</span>
          </div>
        </div>

        {/* Arama ve Filtre Butonları */}
        <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 mb-8 flex flex-col md:flex-row gap-4">
          {/* Arama Kutusu */}
          <input 
            type="text" 
            placeholder="Sembol Ara (Örn: THYAO, USD)..." 
            className="bg-gray-900 border border-gray-700 text-white px-4 py-2 rounded-lg flex-1 focus:outline-none focus:border-blue-500 transition"
            value={aramaMetni}
            onChange={(e) => setAramaMetni(e.target.value)}
          />
          
          {/* Kategori Butonları */}
          <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
            {['HEPSI', 'HISSE', 'FON', 'DOVIZ', 'ALTIN'].map((kat) => (
              <button
                key={kat}
                onClick={() => setSeciliKategori(kat)}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition whitespace-nowrap ${
                  seciliKategori === kat 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {kat}
              </button>
            ))}
          </div>
        </div>

        {/* Listeleme */}
        {yukleniyor ? (
          <div className="text-center py-20 text-gray-500 animate-pulse">Veriler yükleniyor...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtrelenmisVeriler.length > 0 ? (
              filtrelenmisVeriler.map((veri) => (
                <Link key={veri.symbol} href={`/detay/${veri.symbol}`}>
                  <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition cursor-pointer h-full group">
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-2xl font-bold text-white group-hover:text-blue-400 transition">{veri.symbol}</h2>
                      <span className={`text-xs px-2 py-1 rounded uppercase font-bold ${
                        veri.category === 'hisse' ? 'bg-purple-900 text-purple-200' :
                        veri.category === 'fon' ? 'bg-green-900 text-green-200' :
                        veri.category === 'doviz' ? 'bg-yellow-900 text-yellow-200' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {veri.category}
                      </span>
                    </div>
                    
                    <div className="flex items-end gap-2">
                      <p className="text-4xl font-mono font-bold tracking-tight text-white">
                        {veri.price.toLocaleString('tr-TR', { maximumFractionDigits: 4 })}
                      </p>
                      <span className="text-lg text-gray-500 mb-1">TL</span>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-gray-700 flex justify-between items-center text-xs text-gray-500">
                      <span>Son Güncelleme:</span>
                      <span className="font-mono text-gray-400">
                        {new Date(veri.last_updated).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="col-span-full text-center py-10 text-gray-500">
                Aradığınız kriterde veri bulunamadı.
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}