'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getAdminAnalytics, getAdminAuditLogs } from '@/lib/api';
import type { AdminAnalytics, AuditLogEntry } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444',
};

function MetricCard({ label, value, icon, color, bg, border }: {
  label: string; value: number | string | null; icon: string;
  color: string; bg: string; border: string;
}) {
  return (
    <div className="metric-card" style={{ borderTop: `2px solid ${border}`, background: bg }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <span style={{ fontSize: '1.4rem' }}>{icon}</span>
        <span style={{ fontSize: '0.65rem', color, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Live</span>
      </div>
      <div style={{ fontSize: '2.2rem', fontWeight: 900, color, lineHeight: 1 }}>
        {value === null || value === undefined ? '—' : value}
      </div>
      <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '6px' }}>{label}</div>
    </div>
  );
}

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [a, logs] = await Promise.all([
        getAdminAnalytics(),
        getAdminAuditLogs(10),
      ]);
      setAnalytics(a);
      setAuditLogs(logs.logs);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics.');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '960px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '36px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>⚙️</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Admin Dashboard</h2>
            <span style={{ background: 'rgba(245,158,11,0.12)', color: '#fbbf24', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Admin</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Live system-wide metrics, risk monitoring, and audit logs.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={load} className="btn-primary btn-sm"
            style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>
            🔄 Refresh
          </button>
          <Link href="/login" style={{ textDecoration: 'none' }}>
            <button className="btn-primary btn-sm"
              style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>
              ← Change Role
            </button>
          </Link>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
          <p>Loading live analytics...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#f87171', background: 'rgba(239,68,68,0.08)', borderRadius: '12px' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>❌</div>
          <p>{error}</p>
          <button onClick={load} style={{ marginTop: '16px', padding: '8px 20px', borderRadius: '8px', background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)', cursor: 'pointer' }}>Retry</button>
        </div>
      ) : analytics ? (
        <>
          {/* Primary Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '24px' }}>
            <MetricCard label="Total Cases" value={analytics.total_cases} icon="📁" color="#a5b4fc" bg="rgba(99,102,241,0.08)" border="rgba(99,102,241,0.2)" />
            <MetricCard label="Patient Cases" value={analytics.patient_cases} icon="👤" color="#34d399" bg="rgba(16,185,129,0.08)" border="rgba(16,185,129,0.2)" />
            <MetricCard label="Pharmacist Checks" value={analytics.pharmacist_cases} icon="💊" color="#60a5fa" bg="rgba(59,130,246,0.08)" border="rgba(59,130,246,0.2)" />
            <MetricCard label="Doctor Reviews" value={analytics.doctor_cases} icon="🩺" color="#818cf8" bg="rgba(99,102,241,0.08)" border="rgba(99,102,241,0.2)" />
            <MetricCard label="High / Critical Risk" value={analytics.high_risk_cases} icon="🚨" color="#f87171" bg="rgba(239,68,68,0.08)" border="rgba(239,68,68,0.2)" />
          </div>

          {/* Intelligence Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '28px' }}>
            <MetricCard label="NSQ Matches" value={analytics.nsq_matches} icon="⚗️" color="#fb923c" bg="rgba(249,115,22,0.08)" border="rgba(249,115,22,0.2)" />
            <MetricCard label="Online Seller Risk Cases" value={analytics.online_seller_risk_cases} icon="🚩" color="#f87171" bg="rgba(239,68,68,0.08)" border="rgba(239,68,68,0.2)" />
            <MetricCard label="Compliance Warnings" value={analytics.prescription_compliance_warnings} icon="📋" color="#fbbf24" bg="rgba(245,158,11,0.08)" border="rgba(245,158,11,0.2)" />
            <MetricCard label="Affordability Requests" value={analytics.affordability_requests} icon="💰" color="#34d399" bg="rgba(16,185,129,0.08)" border="rgba(16,185,129,0.2)" />
            <MetricCard label="Avg Feedback Rating" value={analytics.average_feedback_rating !== null ? `${analytics.average_feedback_rating?.toFixed(1)}/5` : null} icon="⭐" color="#fbbf24" bg="rgba(245,158,11,0.08)" border="rgba(245,158,11,0.2)" />
          </div>

          {/* Agent Breakdown */}
          {analytics.agent_run_breakdown && Object.keys(analytics.agent_run_breakdown).length > 0 && (
            <div className="glass-card" style={{ padding: '22px', marginBottom: '24px' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>🤖 Agent Run Breakdown</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                {Object.entries(analytics.agent_run_breakdown).map(([agent, count]) => (
                  <div key={agent} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{agent.replace(/_agent/, '').replace(/_/g, ' ')}</span>
                    <span style={{ fontWeight: 800, color: '#a5b4fc', fontSize: '0.9rem' }}>{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Audit Logs */}
          <div className="glass-card" style={{ padding: '22px' }}>
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '14px' }}>📊 Recent Audit Log</h4>
            {auditLogs.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>No audit log entries yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {auditLogs.map(log => (
                  <div key={log.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '10px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', background: 'rgba(99,102,241,0.1)', padding: '2px 8px', borderRadius: '4px', whiteSpace: 'nowrap' }}>
                      {log.role}
                    </span>
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: '0.85rem', color: '#e2e8f0', fontWeight: 600 }}>{log.action}</span>
                      {log.case_id && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '8px' }}>Case: {log.case_id.slice(0, 8)}…</span>
                      )}
                    </div>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                      {new Date(log.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
