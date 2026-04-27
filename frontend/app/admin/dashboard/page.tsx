'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminAnalytics } from '@/lib/api';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await getAdminAnalytics();
        setStats(res);
      } catch (e) { console.error(e); }
      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>⚙️</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Admin Command Center</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            System overview, compliance monitoring, and model analytics.
          </p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>Loading system data...</div>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '32px' }}>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#60a5fa' }}>{stats?.total_cases || 0}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Total Cases Processed</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center', border: '1px solid rgba(248,113,113,0.3)' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f87171' }}>{stats?.high_risk_cases || 0}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>High Risk Flags</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fbbf24' }}>{stats?.nsq_matches || 0}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>NSQ Spurious Matches</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#34d399' }}>{stats?.prescription_compliance_warnings || 0}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '8px' }}>Rx Compliance Warnings</div>
            </div>
          </div>

          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>System Operations</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
             <Link href="/admin/risk-queues" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
                 <h4 style={{ color: '#f87171', marginBottom: '8px' }}>🚨 Risk Queues</h4>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Monitor globally escalated high-risk cases.</p>
               </div>
             </Link>
             <Link href="/admin/audit-logs" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
                 <h4 style={{ color: '#60a5fa', marginBottom: '8px' }}>📜 Audit Logs</h4>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Track API ingestions and system mutations.</p>
               </div>
             </Link>
             <Link href="/admin/model-quality" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
                 <h4 style={{ color: '#c084fc', marginBottom: '8px' }}>🧠 Model Quality</h4>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Review LLM hallucination checks and confidence scores.</p>
               </div>
             </Link>
             <Link href="/admin/batch-analytics" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
                 <h4 style={{ color: '#fbbf24', marginBottom: '8px' }}>📦 Batch Analytics</h4>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Metrics on flagged manufacturers and batches.</p>
               </div>
             </Link>
             <Link href="/admin/seller-analytics" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
                 <h4 style={{ color: '#34d399', marginBottom: '8px' }}>🏪 Seller Analytics</h4>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Risk analysis of online pharmacies vs local shops.</p>
               </div>
             </Link>
             <Link href="/admin/price-issues" style={{ textDecoration: 'none' }}>
               <div className="glass-card" style={{ padding: '20px', cursor: 'pointer' }}>
                 <h4 style={{ color: '#fb923c', marginBottom: '8px' }}>💰 Price Issues</h4>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>NPPA ceiling violations reported across the network.</p>
               </div>
             </Link>
          </div>
        </>
      )}
    </div>
  );
}