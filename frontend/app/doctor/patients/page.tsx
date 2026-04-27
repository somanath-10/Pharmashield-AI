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

export default function DoctorPatientsPage() {
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
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>👥 Patient Roster</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Consolidated view of all patients linked to your clinical care team.
          </p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back to Dashboard</Link>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>Loading roster…</div>
        ) : error ? (
          <div style={{ color: '#f87171', padding: '16px' }}>❌ {error}</div>
        ) : patients.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '40px' }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '8px' }}>No patients linked yet.</p>
            <p style={{ fontSize: '0.9rem' }}>Patient summaries appear here once you add care team links or patients create cases.</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px' }}>Name</th>
                <th style={{ padding: '12px 8px' }}>Age</th>
                <th style={{ padding: '12px 8px' }}>Active Cases</th>
                <th style={{ padding: '12px 8px' }}>Risk Flags</th>
                <th style={{ padding: '12px 8px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.patient_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 8px', fontWeight: 600 }}>{p.name ?? 'Patient'}</td>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>{p.age ?? '—'}</td>
                  <td style={{ padding: '12px 8px' }}>{p.cases?.length ?? 0}</td>
                  <td style={{ padding: '12px 8px' }}>
                    {(p.recent_flags ?? []).length === 0 ? (
                      <span style={{ opacity: 0.4 }}>None</span>
                    ) : (
                      <span style={{ color: '#f87171', fontWeight: 700 }}>{(p.recent_flags ?? []).length} Flags</span>
                    )}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <Link href="/doctor/patient-summary">
                      <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.1)' }}>Details</button>
                    </Link>
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
