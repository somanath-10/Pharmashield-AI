'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminModelQuality } from '@/lib/api';

export default function AdminModelQualityPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try { setData(await getAdminModelQuality()); }
      catch (e: any) { setError(e?.message || 'Failed to load model quality'); }
      setLoading(false);
    })();
  }, []);

  const StatCard = ({ label, value, sub }: { label: string; value: string | number; sub?: string }) => (
    <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
      <div style={{ fontSize: '2rem', fontWeight: 800, color: '#60a5fa' }}>{value}</div>
      <div style={{ fontWeight: 600, marginTop: '8px' }}>{label}</div>
      {sub && <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>{sub}</div>}
    </div>
  );

  return (
    <div className="animate-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🤖 Model Quality Telemetry</h2>
          <p style={{ color: 'var(--text-secondary)' }}>AI agent run stats, feedback, and low-confidence detection rates.</p>
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
            <StatCard label="Total Agent Runs" value={data.total_ai_analyses ?? 0} />
            <StatCard label="Avg Feedback" value={data.average_feedback_rating != null ? `${Number(data.average_feedback_rating).toFixed(1)} / 5` : 'N/A'} />
            <StatCard label="Low Confidence Runs" value={data.low_confidence_flags ?? 0} sub="< 60% confidence" />
          </div>

          {data.agent_breakdown && Object.keys(data.agent_breakdown).length > 0 && (
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', fontSize: '1rem', fontWeight: 700 }}>Agent Breakdown</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>Agent</th>
                    <th style={{ padding: '8px' }}>Runs</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.agent_breakdown).map(([agent, count]) => (
                    <tr key={agent} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '8px' }}>{agent}</td>
                      <td style={{ padding: '8px', color: '#60a5fa', fontWeight: 700 }}>{String(count)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}