'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getDoctorPatients } from '@/lib/api';

export default function LabTrendsPage() {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setPatients(await getDoctorPatients());
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📈 Lab Trends</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Longitudinal analysis of patient lab markers.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {loading ? (
        <div className="glass-card" style={{ padding: '24px', color: 'var(--text-secondary)' }}>Loading linked patient data...</div>
      ) : patients.length === 0 ? (
        <div className="glass-card" style={{ padding: '24px', color: 'var(--text-secondary)' }}>
          No linked patients yet. Create care-team links to enable lab trend tracking.
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '12px' }}>Linked Patients Ready for Trend Review</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {patients.map((p) => (
              <div key={p.patient_id} style={{ padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)' }}>
                <div style={{ fontWeight: 700 }}>{p.name || 'Patient'}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Cases: {(p.cases || []).length} • Recent flags: {(p.recent_flags || []).length}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}