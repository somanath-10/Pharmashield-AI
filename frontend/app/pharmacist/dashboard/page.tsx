'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getPharmacistDashboard } from '@/lib/api';

export default function PharmacistDashboardPage() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await getPharmacistDashboard();
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
            <span style={{ fontSize: '1.6rem' }}>💊</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Pharmacist Command Center</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Manage verification queues, batch checking, and dispensing compliance.
          </p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>Loading queues...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '32px' }}>
          <Link href="/pharmacist/review-queue" style={{ textDecoration: 'none' }}>
            <div className="glass-card" style={{ padding: '24px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s', border: '1px solid rgba(59,130,246,0.3)' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#60a5fa' }}>{dashboard?.pending_verifications || 0}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Pending Verifications</div>
            </div>
          </Link>
          <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#f87171' }}>{dashboard?.high_risk_cases || 0}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>High-Risk Prescriptions</div>
          </div>
          <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#fbbf24' }}>{dashboard?.quarantined_batches || 0}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Quarantined Batches</div>
          </div>
        </div>
      )}

      <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>Quick Tools</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
         <Link href="/pharmacist/prescription-check" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#60a5fa', marginBottom: '8px' }}>📝 Prescription Check</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Analyze prescription authenticity and missing details.</p>
           </div>
         </Link>
         <Link href="/pharmacist/batch-verification" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#fbbf24', marginBottom: '8px' }}>📦 Batch & Expiry Check</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Verify NSQ spurious databases and quarantine stock.</p>
           </div>
         </Link>
         <Link href="/pharmacist/price-check" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#34d399', marginBottom: '8px' }}>💰 Price Compliance</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Check MRP against NPPA ceiling prices.</p>
           </div>
         </Link>
         <Link href="/pharmacist/substitution-check" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#c084fc', marginBottom: '8px' }}>🔄 Substitution Safety</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Compare molecules and routes for generic substitution.</p>
           </div>
         </Link>
         <Link href="/pharmacist/adr-drafts" style={{ textDecoration: 'none' }}>
           <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
             <h4 style={{ color: '#f87171', marginBottom: '8px' }}>⚠️ ADR Drafts</h4>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Create side-effect reports for doctor review.</p>
           </div>
         </Link>
      </div>
    </div>
  );
}