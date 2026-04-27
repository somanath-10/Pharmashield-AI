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
        <div className="glass-card" style={{ padding: '24px' }}>
          <p><strong>Total Seller Risk Checks:</strong> {data?.total_seller_risk_checks ?? 0}</p>
          <p><strong>High Risk Seller Cases:</strong> {data?.high_risk_seller_cases ?? 0}</p>
          <p style={{ color: 'var(--text-secondary)' }}>{data?.note ?? ''}</p>
        </div>
      )}
    </div>
  );
}