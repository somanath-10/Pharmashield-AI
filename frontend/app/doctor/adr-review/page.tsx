'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDoctorADRReviews, reviewDoctorADR } from '@/lib/api';

export default function ADRReviewPage() {
  const [adrs, setAdrs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadADRs = async () => {
    setLoading(true);
    try {
      const res = await getDoctorADRReviews();
      setAdrs(res);
    } catch(e: any) { setError(e?.message || 'Failed to load ADR reviews'); }
    setLoading(false);
  };

  useEffect(() => { loadADRs(); }, []);

  const handleAction = async (id: string, action: string) => {
    try {
      await reviewDoctorADR(id, { action, notes: `Doctor marked as ${action}` });
      await loadADRs();
    } catch(e: any) { setError(e?.message || 'Failed to submit review'); }
  };

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>⚠️ ADR Review Queue</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Review escalated Adverse Drug Reactions.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {error && <div style={{ marginBottom: '16px', color: '#f87171' }}>❌ {error}</div>}
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>Loading...</div>
        ) : adrs.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>No pending ADRs.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px' }}>Date</th>
                <th style={{ padding: '12px 8px' }}>Medicine</th>
                <th style={{ padding: '12px 8px' }}>Reaction</th>
                <th style={{ padding: '12px 8px' }}>Severity</th>
                <th style={{ padding: '12px 8px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {adrs.map(a => (
                <tr key={a.adr_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>{new Date(a.created_at).toLocaleDateString()}</td>
                  <td style={{ padding: '12px 8px', fontWeight: 600 }}>{a.medicine_name}</td>
                  <td style={{ padding: '12px 8px' }}>{a.reaction}</td>
                  <td style={{ padding: '12px 8px', color: '#f87171' }}>{a.severity}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                    <button onClick={() => handleAction(a.adr_id, 'CONFIRMED_ADR')} className="btn-primary btn-sm" style={{ marginRight: '8px' }}>Confirm ADR</button>
                    <button onClick={() => handleAction(a.adr_id, 'DISMISSED')} className="btn-primary btn-sm" style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.1)' }}>Dismiss</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}