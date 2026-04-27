'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDoctorDashboard } from '@/lib/api';

export default function DoctorDashboardPage() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await getDoctorDashboard();
        setDashboard(res);
      } catch (e) {
        console.error(e);
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
            <span style={{ fontSize: '1.6rem' }}>🩺</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Doctor Command Center</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Review patient summaries, ADR signals, and verify prescriptions.
          </p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>Loading clinic data...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '32px' }}>
          <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#34d399' }}>{dashboard?.active_patients || 0}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Active Patients</div>
          </div>
          <Link href="/doctor/adr-review" style={{ textDecoration: 'none' }}>
            <div className="glass-card" style={{ padding: '24px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s', border: '1px solid rgba(248,113,113,0.3)' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#f87171' }}>{dashboard?.adr_reviews_pending || 0}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Pending ADR Reviews</div>
            </div>
          </Link>
          <div className="glass-card" style={{ padding: '24px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', opacity: 0.6 }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#fbbf24' }}>{dashboard?.pharmacist_questions || 0}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Pharmacist Inquiries</div>
          </div>
        </div>
      )}

      <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>Clinical Tools</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
         <Link href="/doctor/patient-summary" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#60a5fa', marginBottom: '8px' }}>👤 Patient Summaries</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>View extracted clinical timelines and active medications.</p>
           </div>
         </Link>
         <Link href="/doctor/prescription-verification" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#34d399', marginBottom: '8px' }}>✍️ e-Prescription Gen</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Generate cryptographically verified prescriptions.</p>
           </div>
         </Link>
         <Link href="/doctor/adr-review" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#f87171', marginBottom: '8px' }}>⚠️ ADR Review</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Approve or dismiss pharmacist-escalated side effects.</p>
           </div>
         </Link>
      </div>
    </div>
  );
}