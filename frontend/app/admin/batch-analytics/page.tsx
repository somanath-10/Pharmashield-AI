'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminBatchAnalytics } from '@/lib/api';

export default function AdminBatchAnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try { setData(await getAdminBatchAnalytics()); }
      catch (e: any) { setError(e?.message || 'Failed to load batch analytics'); }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🧪 Batch Analytics</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Quarantined and suspicious batch statistics across manufacturers and suppliers.</p>
        </div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : data ? (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#ef4444' }}>{data.total_quarantined ?? 0}</div>
              <div style={{ marginTop: '8px' }}>Quarantined Batches</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#60a5fa' }}>{data.total_checked ?? 0}</div>
              <div style={{ marginTop: '8px' }}>Total Checked</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f97316' }}>{data.high_risk ?? 0}</div>
              <div style={{ marginTop: '8px' }}>High Risk</div>
            </div>
          </div>

          {data.by_manufacturer && Object.keys(data.by_manufacturer).length > 0 && (
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', fontWeight: 700 }}>By Manufacturer</h3>
              {Object.entries(data.by_manufacturer).map(([mfr, count]) => (
                <div key={mfr} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  <span>{mfr}</span>
                  <span style={{ color: '#f97316', fontWeight: 700 }}>{String(count)}</span>
                </div>
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}