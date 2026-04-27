'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminADRMonitoring } from '@/lib/api';

const SEV_COLORS: Record<string, string> = {
  Severe: '#ef4444',
  'Life-threatening': '#dc2626',
  Moderate: '#f97316',
  Mild: '#eab308',
};

export default function AdminADRMonitoringPage() {
  const [adrs, setAdrs] = useState<any[]>([]);
  const [summary, setSummary] = useState<{ total_adr_reports?: number; pending_doctor_review?: number; reviewed?: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = await getAdminADRMonitoring();
        setSummary(data.summary || null);
        setAdrs(data.reports || []);
      }
      catch (e: any) { setError(e?.message || 'Failed to load ADR reports'); }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>💊 ADR Monitoring</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Adverse Drug Reaction reports across the platform (PvPI-compatible format).</p>
        </div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
            <div className="glass-card" style={{ padding: '16px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{summary?.total_adr_reports ?? 0}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Total Reports</div>
            </div>
            <div className="glass-card" style={{ padding: '16px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{summary?.pending_doctor_review ?? 0}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Pending Doctor Review</div>
            </div>
            <div className="glass-card" style={{ padding: '16px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{summary?.reviewed ?? 0}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Reviewed</div>
            </div>
          </div>
          {adrs.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <h3>No ADR Reports</h3>
          <p style={{ marginTop: '12px' }}>ADR reports submitted by pharmacists and patients will appear here.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {adrs.map((a: any, i: number) => (
            <div key={a.adr_id ?? i} className="glass-card" style={{ padding: '20px', borderLeft: `3px solid ${SEV_COLORS[a.severity] ?? '#60a5fa'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontWeight: 700 }}>{a.medicine_name}</span>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>
                    Reaction: {a.reaction} • Timeline: {a.timeline}
                    {a.batch_number && ` • Batch: ${a.batch_number}`}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
                    Status: <strong style={{ color: 'white' }}>{a.status}</strong>
                    {a.patient_age_range && ` • Age: ${a.patient_age_range}`}
                  </div>
                </div>
                <span style={{ background: `${SEV_COLORS[a.severity] ?? '#60a5fa'}22`, color: SEV_COLORS[a.severity] ?? '#60a5fa', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, whiteSpace: 'nowrap' }}>
                  {a.severity}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
        </>
      )}
    </div>
  );
}