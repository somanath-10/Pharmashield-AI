'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getAdminSellerAnalytics } from '@/lib/api';

export default function AdminSellerAnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try { setData(await getAdminSellerAnalytics()); }
      catch (e: any) { setError(e?.message || 'Failed to load seller analytics'); }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div><h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🏪 Seller Analytics</h2><p style={{ color: 'var(--text-secondary)' }}>Risk analysis of online pharmacies vs local shops.</p></div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>
      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#60a5fa' }}>{data?.total_seller_checks ?? 0}</div>
              <div style={{ marginTop: '8px' }}>Total Seller Checks</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f87171' }}>{data?.high_risk_count ?? 0}</div>
              <div style={{ marginTop: '8px' }}>High Risk Count</div>
            </div>
          </div>

          {data?.flagged_sellers && data.flagged_sellers.length > 0 && (
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', fontWeight: 700 }}>Flagged Sellers</h3>
              {data.flagged_sellers.map((seller: string, idx: number) => (
                <div key={`${seller}-${idx}`} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  <span>{seller}</span>
                  <span style={{ color: '#f87171', fontWeight: 700 }}>HIGH RISK</span>
                </div>
              ))}
            </div>
          )}
        </>

      )}
    </div>
  );
}