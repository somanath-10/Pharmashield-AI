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
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#ef4444' }}>{data.flagged_batches?.length ?? 0}</div>
              <div style={{ marginTop: '8px' }}>Flagged Batches</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#60a5fa' }}>{data.total_checked ?? 0}</div>
              <div style={{ marginTop: '8px' }}>Total Batch Checks</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f97316' }}>{data.total_quarantined ?? 0}</div>
              <div style={{ marginTop: '8px' }}>Quarantined</div>
            </div>
          </div>

          {data.flagged_batches && data.flagged_batches.length > 0 && (
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', fontWeight: 700 }}>Flagged Batch IDs</h3>
              {data.flagged_batches.map((batch: string, idx: number) => (
                <div key={`${batch}-${idx}`} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  <span>{batch}</span>
                  <span style={{ color: '#f97316', fontWeight: 700 }}>FLAGGED</span>
                </div>
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}