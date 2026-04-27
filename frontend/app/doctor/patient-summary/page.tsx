'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDoctorPatients } from '@/lib/api';

interface PatientSummary {
  patient_id: string;
  name?: string;
  age?: string;
  current_medicines?: string[];
  cases?: { case_id: string; title: string; risk_level: string; status: string }[];
  recent_flags?: string[];
}

export default function PatientSummaryPage() {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setPatients(await getDoctorPatients());
      } catch (e: any) {
        setError(e?.message || 'Failed to load patients');
      }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>👤 Patient List</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Patients linked to your care team.
            {patients.length === 0 && !loading && ' (No patients yet — use Care Team Links to connect patients.)'}
          </p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back to Dashboard</Link>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>Loading…</div>
        ) : error ? (
          <div style={{ color: '#f87171', padding: '16px' }}>❌ {error}</div>
        ) : patients.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '40px' }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '8px' }}>No patient summaries available.</p>
            <p style={{ fontSize: '0.9rem' }}>Summaries appear once patients create cases or you add care team links.</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px' }}>Patient ID</th>
                <th style={{ padding: '12px 8px' }}>Name</th>
                <th style={{ padding: '12px 8px' }}>Cases</th>
                <th style={{ padding: '12px 8px' }}>Active Meds</th>
                <th style={{ padding: '12px 8px' }}>Risk Flags</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.patient_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                    {p.patient_id.slice(0, 12)}…
                  </td>
                  <td style={{ padding: '12px 8px', fontWeight: 600 }}>{p.name ?? 'Patient'}</td>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>
                    {p.cases?.length ?? 0} case{(p.cases?.length ?? 0) !== 1 ? 's' : ''}
                  </td>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>
                    {p.current_medicines && p.current_medicines.length > 0
                      ? p.current_medicines.join(', ')
                      : <span style={{ opacity: 0.5 }}>None recorded</span>}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    {(p.recent_flags ?? []).length === 0
                      ? <span style={{ opacity: 0.4, fontSize: '0.8rem' }}>No flags</span>
                      : (p.recent_flags ?? []).map((f, i) => (
                          <span key={i} style={{ background: 'rgba(239,68,68,0.1)', color: '#f87171', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem', marginRight: '4px', display: 'inline-block', marginBottom: '2px' }}>{f}</span>
                        ))}
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