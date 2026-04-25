'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AdminDashboard() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchMetrics(); }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const caseRes = await fetch('http://localhost:8000/api/cases', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'ADMIN', case_type: 'ADMIN_REVIEW', title: 'Dashboard', query: 'metrics' }),
      });
      const { case_id } = await caseRes.json();
      const res = await fetch(`http://localhost:8000/api/cases/${case_id}/analyze`, { method: 'POST' });
      const data = await res.json();
      setAnalysis(data.result);
    } catch {}
    setLoading(false);
  };

  const metrics = [
    { label: 'Patient Cases', key: 'active_patient_cases', icon: '👤', color: '#34d399', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.2)' },
    { label: 'Pharmacist Checks', key: 'pharmacist_checks', icon: '💊', color: '#60a5fa', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.2)' },
    { label: 'Doctor Reviews', key: 'doctor_reviews', icon: '🩺', color: '#a5b4fc', bg: 'rgba(99,102,241,0.08)', border: 'rgba(99,102,241,0.2)' },
    { label: 'High Risk Flags', key: 'high_risk_cases', icon: '🚨', color: '#f87171', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)' },
  ];

  return (
    <div className="animate-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '36px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>⚙️</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Admin Dashboard</h2>
            <span style={{ background: 'rgba(245,158,11,0.12)', color: '#fbbf24', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing:'0.05em' }}>Admin</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>System-wide usage metrics and high-risk case monitoring.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button onClick={fetchMetrics} className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>
            🔄 Refresh
          </button>
          <Link href="/login" style={{ textDecoration: 'none' }}>
            <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
          </Link>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
          <p>Loading metrics...</p>
        </div>
      ) : analysis ? (
        <>
          {/* Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
            {metrics.map(m => (
              <div key={m.key} className="metric-card" style={{ borderTop: `2px solid ${m.border}`, background: m.bg }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ fontSize: '1.4rem' }}>{m.icon}</span>
                  <span style={{ fontSize: '0.7rem', color: m.color, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Live</span>
                </div>
                <div style={{ fontSize: '2.5rem', fontWeight: 900, color: m.color, lineHeight: 1 }}>{analysis.metrics?.[m.key]}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '6px' }}>{m.label}</div>
              </div>
            ))}
          </div>

          {/* System Log */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '14px' }}>📊 System Log</h4>
            <p style={{ color: '#e2e8f0', lineHeight: 1.7 }}>{analysis.insights}</p>
            <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <span style={{ fontSize: '0.75rem', color: '#fbbf24', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>🔒 {analysis.disclaimer}</span>
            </div>
          </div>
        </>
      ) : (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)' }}>Failed to load dashboard data.</div>
      )}
    </div>
  );
}
