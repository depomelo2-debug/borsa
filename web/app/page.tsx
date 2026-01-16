'use client';
import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';

// Supabase Bağlantısı (Okuma yetkisi yeterli)
// Not: Normalde env dosyasına koyarız ama şimdilik hızlı test için buraya yazalım.
// .env dosyasındaki URL ve KEY'ini tırnakların içine yapıştır:
const supabase = createClient(
  'https://oxtihxyfluoliaupeshe.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im94dGloeHlmbHVvbGlhdXBlc2hlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1NjEwMjYsImV4cCI6MjA4NDEzNzAyNn0.Ax7KUFiVynSU_Pvdg5KAKZo6s5dzKWf0LjAudHYz7yQ'
);

export default function Home() {
  const [veriler, setVeriler] = useState<any[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    async function veriGetir() {
      // 'live_market' tablosundan tüm verileri çek
      const { data, error } = await supabase
        .from('live_market')
        .select('*')
        .order('price', { ascending: false });

      if (error) console.error('Hata:', error);
      else setVeriler(data || []);
      
      setYukleniyor(false);
    }

    veriGetir();
  }, []);

  return (
    <main className="min-h-screen bg-gray-900 text-white p-10">
      <h1 className="text-3xl font-bold mb-8 text-center">🚀 Finans Terminali</h1>

      {yukleniyor ? (
        <p className="text-center">Veriler yükleniyor...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {veriler.map((veri) => (
            <div key={veri.symbol} className="bg-gray-800 p-6 rounded-xl border border-gray-700 hover:border-blue-500 transition">
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-xl font-bold text-blue-400">{veri.symbol}</h2>
                <span className="text-xs bg-gray-700 px-2 py-1 rounded uppercase text-gray-300">{veri.category}</span>
              </div>
              <p className="text-4xl font-mono font-bold">{veri.price} <span className="text-lg text-gray-400">TL</span></p>
              <p className="text-xs text-gray-500 mt-4 text-right">
                Son Güncelleme: {new Date(veri.last_updated).toLocaleTimeString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}