'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDoctorPatients } from '@/lib/api';

export default function PatientSummaryPage() {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getDoctorPatients();
        setPatients(res);
      } catch(e) { console.error(e); }
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>👤 Patient List</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Extracted clinical summaries.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back to Dashboard</Link>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>Loading...</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px' }}>ID</th>
                <th style={{ padding: '12px 8px' }}>Name</th>
                <th style={{ padding: '12px 8px' }}>Age</th>
                <th style={{ padding: '12px 8px' }}>Active Meds</th>
                <th style={{ padding: '12px 8px' }}>Flags</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.patient_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>{p.patient_id}</td>
                  <td style={{ padding: '12px 8px', fontWeight: 600 }}>{p.name}</td>
                  <td style={{ padding: '12px 8px' }}>{p.age}</td>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>{p.current_medicines.join(', ')}</td>
                  <td style={{ padding: '12px 8px' }}>
                    {p.recent_flags.map((f: string, i: number) => (
                      <span key={i} style={{ background: 'rgba(239,68,68,0.1)', color: '#f87171', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem', marginRight: '4px' }}>{f}</span>
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