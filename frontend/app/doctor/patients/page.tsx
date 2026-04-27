'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { listCases } from '@/lib/api';
import type { CaseRecord } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444',
};

export default function DoctorPatientsList() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      const data = await listCases();
      setCases(data.filter(c => c.case_type === 'DOCTOR_CASE_SUMMARY' || c.role === 'DOCTOR'));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load patients.');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>👥</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Patient Case Summaries</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Recent synthesized patient clinical files and lab trends.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={load} className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>🔄 Refresh</button>
          <Link href="/doctor" style={{ textDecoration: 'none' }}>
            <button className="btn-primary btn-sm" style={{ background: 'rgba(99,102,241,0.15)', color: '#a5b4fc', border: '1px solid rgba(99,102,241,0.3)' }}>+ Summarize New Case</button>
          </Link>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)' }}>Loading patient cases...</div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#f87171' }}>{error}</div>
      ) : cases.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>No patient cases found.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {cases.map(c => (
            <div key={c.case_id} className="glass-card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#e2e8f0', marginBottom: '4px' }}>{c.title || 'Unknown Patient Document'}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Notes: {c.query || 'N/A'}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#60a5fa' }}>{c.status}</span>
                {c.risk_level && (
                  <span style={{ background: `${RISK_COLORS[c.risk_level] || '#9ca3af'}22`, color: RISK_COLORS[c.risk_level] || '#9ca3af', borderRadius: '999px', padding: '4px 12px', fontWeight: 800, fontSize: '0.75rem', textTransform: 'uppercase', border: `1px solid ${RISK_COLORS[c.risk_level] || '#9ca3af'}44` }}>
                    {c.risk_level} Risk
                  </span>
                )}
                <Link href="/doctor" style={{ textDecoration: 'none' }}>
                  <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.1)' }}>View Summary</button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
