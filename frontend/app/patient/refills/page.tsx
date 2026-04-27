'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { getPatientCases } from '@/lib/api';

export default function PatientRefillsPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setCases(await getPatientCases());
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const refillCandidates = useMemo(
    () => cases.filter((c) => c.status === 'ANALYZED' || c.status === 'RESOLVED'),
    [cases]
  );

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto', padding: '24px' }}>
      <div style={{ marginBottom: '16px' }}>
        <Link href="/patient/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>
      <div className="glass-card" style={{ padding: '32px' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '12px' }}>Refill Tracker</h2>
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Loading refill candidates...</p>
        ) : refillCandidates.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>
            No refill-eligible cases yet. Complete a medicine safety check to create trackable medication records.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {refillCandidates.map((c) => (
              <div key={c.case_id} style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255,255,255,0.04)' }}>
                <div style={{ fontWeight: 700 }}>{c.title}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Status: {c.status} • Risk: {c.risk_level || 'UNKNOWN'}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}