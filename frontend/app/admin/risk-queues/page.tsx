'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminRiskQueues } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#22c55e',
};

export default function AdminRiskQueuesPage() {
  const [queues, setQueues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try { setQueues(await getAdminRiskQueues()); }
      catch (e: any) { setError(e?.message || 'Failed to load risk queues'); }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🚨 Global Risk Queues</h2>
          <p style={{ color: 'var(--text-secondary)' }}>High-risk cases escalated across the platform.</p>
        </div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : queues.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <h3>✅ No High-Risk Cases</h3>
          <p style={{ marginTop: '12px' }}>All cases are within acceptable risk thresholds.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {queues.map((q: any, i: number) => (
            <div key={q.case_id ?? i} className="glass-card" style={{ padding: '20px', borderLeft: `3px solid ${RISK_COLORS[q.risk_level] ?? '#60a5fa'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontWeight: 700, fontSize: '1rem' }}>{q.title ?? q.case_id}</span>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>
                    Role: {q.role} • Status: {q.status} • Case ID: <code style={{ fontSize: '0.8rem' }}>{q.case_id}</code>
                  </div>
                </div>
                <span style={{ background: `${RISK_COLORS[q.risk_level] ?? '#60a5fa'}22`, color: RISK_COLORS[q.risk_level] ?? '#60a5fa', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700 }}>
                  {q.risk_level}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}