'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminDataSources } from '@/lib/api';

const STATUS_COLORS: Record<string, string> = {
  CONNECTED: '#22c55e',
  MOCK_MODE: '#eab308',
  NOT_CONNECTED: '#6b7280',
  FAILED: '#ef4444',
  MEMORY_MODE: '#f97316',
};

export default function AdminDataSourcesPage() {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try { setSources(await getAdminDataSources()); }
      catch (e: any) { setError(e?.message || 'Failed to load data sources'); }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🔗 Data Source Status</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Live status of external data adapters (NSQ, NPPA, Qdrant, PvPI, Jan Aushadhi).</p>
        </div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {sources.map((s: any, i: number) => (
            <div key={s.source_name ?? i} className="glass-card" style={{ padding: '20px', borderLeft: `3px solid ${STATUS_COLORS[s.status] ?? '#60a5fa'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontWeight: 700 }}>{s.source_name}</span>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>
                    {s.note}
                  </div>
                  {s.last_synced && (
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
                      Last synced: {new Date(s.last_synced).toLocaleString()}
                      {s.records_loaded != null && ` • ${s.records_loaded.toLocaleString()} records`}
                    </div>
                  )}
                </div>
                <span style={{ background: `${STATUS_COLORS[s.status] ?? '#60a5fa'}22`, color: STATUS_COLORS[s.status] ?? '#60a5fa', padding: '4px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, whiteSpace: 'nowrap' }}>
                  {s.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}