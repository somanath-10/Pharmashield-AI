'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getPatientDashboard, getPatientCases, type PatientDashboard } from '@/lib/api';

export default function PatientDashboardPage() {
  const [dashboard, setDashboard] = useState<PatientDashboard | null>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [dashRes, casesRes] = await Promise.all([
          getPatientDashboard(),
          getPatientCases()
        ]);
        setDashboard(dashRes);
        setCases(casesRes);
      } catch (e) {
        console.error("Failed to load dashboard", e);
      }
      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>👤</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Patient Dashboard</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Your medication timeline and safety overview.
          </p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>Loading...</div>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '32px' }}>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#60a5fa' }}>{dashboard?.active_cases || 0}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Active Cases</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f87171' }}>{dashboard?.adr_reports || 0}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Reported Side Effects</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#34d399' }}>{dashboard?.adherence_status || 'Unknown'}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Adherence Status</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '32px' }}>
             <Link href="/patient/medicine-safety" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '24px', cursor: 'pointer', border: '1px solid rgba(59,130,246,0.3)', transition: 'all 0.2s' }}>
                 <h3 style={{ color: '#60a5fa', marginBottom: '8px' }}>🛡️ Medicine Safety Scanner</h3>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Upload a prescription or medicine strip to check safety and seller risk.</p>
               </div>
             </Link>
             <Link href="/patient/side-effects" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '24px', cursor: 'pointer', border: '1px solid rgba(248,113,113,0.3)', transition: 'all 0.2s' }}>
                 <h3 style={{ color: '#f87171', marginBottom: '8px' }}>⚠️ Report a Side Effect</h3>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Experiencing side effects? Report them here for doctor review.</p>
               </div>
             </Link>
          </div>

          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>Medication Timeline</h3>
          <div className="glass-card" style={{ padding: '20px' }}>
            {cases.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>No medication records found.</div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                    <th style={{ padding: '12px 8px' }}>Date</th>
                    <th style={{ padding: '12px 8px' }}>Case Name</th>
                    <th style={{ padding: '12px 8px' }}>Type</th>
                    <th style={{ padding: '12px 8px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {cases.map((c: any) => (
                    <tr key={c.case_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '12px 8px' }}>{new Date(c.created_at).toLocaleDateString()}</td>
                      <td style={{ padding: '12px 8px', fontWeight: 600 }}>
                        <Link href={`/patient/cases/${c.case_id}`} style={{ color: '#60a5fa', textDecoration: 'none' }}>
                          {c.title}
                        </Link>
                      </td>
                      <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>{c.case_type}</td>
                      <td style={{ padding: '12px 8px' }}>
                         <span style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem' }}>{c.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}