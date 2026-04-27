'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { getCase } from '@/lib/api';

export default function DoctorCasePage() {
  const params = useParams<{ id: string }>();
  const caseId = params?.id as string;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!caseId) return;
    (async () => {
      try { setData(await getCase(caseId)); }
      catch (e: any) { setError(e?.message || 'Failed to load case details'); }
      setLoading(false);
    })();
  }, [caseId]);

  return (
    <div className="animate-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>
      {loading ? (
        <div className="glass-card" style={{ padding: '24px' }}>Loading case...</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '12px' }}>{data?.title}</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>{data?.query}</p>
          <p><strong>Case ID:</strong> {data?.case_id}</p>
          <p><strong>Status:</strong> {data?.status}</p>
          <p><strong>Risk:</strong> {data?.risk_level || 'Not analyzed'}</p>
          <p><strong>Role:</strong> {data?.role}</p>
        </div>
      )}
    </div>
  );
}