'use client';
import Link from 'next/link';

export default function AdminRiskQueuesPage() {
  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div><h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🚨 Global Risk Queues</h2><p style={{ color: 'var(--text-secondary)' }}>Monitor high-risk cases escalated across the platform.</p></div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>
      <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <h3>🚧 Advanced Filtering Pending</h3>
        <p style={{ marginTop: '16px' }}>Global risk queue aggregation relies on the next ElasticSearch integration phase.</p>
      </div>
    </div>
  );
}