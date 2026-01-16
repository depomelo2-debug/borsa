'use client';
import { useEffect, useState, use } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Link from 'next/link';

// Supabase Ayarları (Kendi URL ve Key'ini buraya yazmayı unutma!)
const supabase = createClient(
  'https://oxtihxyfluoliaupeshe.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im94dGloeHlmbHVvbGlhdXBlc2hlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1NjEwMjYsImV4cCI6MjA4NDEzNzAyNn0.Ax7KUFiVynSU_Pvdg5KAKZo6s5dzKWf0LjAudHYz7yQ'
);

export default function DetaySayfasi({ params }: { params: Promise<{ symbol: string }> }) {
  // Next.js 15+ için params'ı unwrap ediyoruz
  const resolvedParams = use(params);
  const symbol = decodeURIComponent(resolvedParams.symbol);

  const [gecmisVeriler, setGecmisVeriler] = useState<any[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    async function veriCek() {
      // Bu sembolün geçmiş verilerini çek (Eskiden yeniye sırala)
      const { data, error } = await supabase
        .from('price_history')
        .select('*')
        .eq('symbol', symbol)
        .order('created_at', { ascending: true }); // Grafik için tarih sırası önemli

      if (data) {
        // Tarihi okunabilir formata çevirelim (Saat:Dakika)
        const formatliData = data.map(d => ({
          ...d,
          saat: new Date(d.created_at).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
        }));
        setGecmisVeriler(formatliData);
      }
      setYukleniyor(false);
    }
    veriCek();
  }, [symbol]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <Link href="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">← Geri Dön</Link>
      
      <h1 className="text-3xl font-bold mb-2">{symbol} Analizi</h1>
      <p className="text-gray-400 mb-8">Fiyat Geçmişi Grafiği</p>

      {yukleniyor ? (
        <p>Grafik yükleniyor...</p>
      ) : (
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 h-[400px]">
          {gecmisVeriler.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={gecmisVeriler}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="saat" stroke="#9CA3AF" />
                <YAxis domain={['auto', 'auto']} stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#3B82F6" 
                  strokeWidth={3}
                  dot={{ r: 4 }} 
                  activeDot={{ r: 8 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              Henüz yeterli geçmiş veri yok.
            </div>
          )}
        </div>
      )}
    </div>
  );
}