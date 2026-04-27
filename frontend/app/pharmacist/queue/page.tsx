'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { listCases } from '@/lib/api';
import type { CaseRecord } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444',
};

export default function PharmacistQueue() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      const data = await listCases();
      // Filter for pharmacist checks or just show all for the demo
      setCases(data.filter(c => c.case_type === 'PHARMACIST_DISPENSING_CHECK' || c.role === 'PHARMACIST'));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load cases.');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>📋</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Prescription Queue</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Recent prescriptions waiting for dispensing verification.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={load} className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>🔄 Refresh</button>
          <Link href="/pharmacist" style={{ textDecoration: 'none' }}>
            <button className="btn-primary btn-sm" style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.3)' }}>+ New Verification</button>
          </Link>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)' }}>Loading queue...</div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#f87171' }}>{error}</div>
      ) : cases.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>No prescriptions in queue.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {cases.map(c => (
            <div key={c.case_id} className="glass-card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#e2e8f0', marginBottom: '4px' }}>{c.title || 'Untitled Prescription'}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Query: {c.query || 'N/A'}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#a5b4fc' }}>{c.status}</span>
                {c.risk_level && (
                  <span style={{ background: `${RISK_COLORS[c.risk_level] || '#9ca3af'}22`, color: RISK_COLORS[c.risk_level] || '#9ca3af', borderRadius: '999px', padding: '4px 12px', fontWeight: 800, fontSize: '0.75rem', textTransform: 'uppercase', border: `1px solid ${RISK_COLORS[c.risk_level] || '#9ca3af'}44` }}>
                    {c.risk_level} Risk
                  </span>
                )}
                <Link href="/pharmacist" style={{ textDecoration: 'none' }}>
                  <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.1)' }}>Review</button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
