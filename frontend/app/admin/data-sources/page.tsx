'use client';
import Link from 'next/link';

export default function AdminDataSourcesPage() {
  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div><h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🔌 Data Sources</h2><p style={{ color: 'var(--text-secondary)' }}>Status of mock data adapters (NSQ, NPPA).</p></div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>
      <div className="glass-card" style={{ padding: '40px', textAlign: 'left', color: 'var(--text-secondary)' }}>
        <h3 style={{ color: 'white', marginBottom: '16px' }}>Active Adapters</h3>
        <ul style={{ paddingLeft: '20px', lineHeight: 1.8 }}>
          <li><span style={{ color: '#34d399', fontWeight: 'bold' }}>[ONLINE]</span> NPPA Pricing DB Mock (Fallback)</li>
          <li><span style={{ color: '#34d399', fontWeight: 'bold' }}>[ONLINE]</span> CDSCO NSQ Mock (Fallback)</li>
          <li><span style={{ color: '#fbbf24', fontWeight: 'bold' }}>[IDLE]</span> Qdrant Vector Store</li>
          <li><span style={{ color: '#f87171', fontWeight: 'bold' }}>[OFFLINE]</span> Live Government API Bridges</li>
        </ul>
      </div>
    </div>
  );
}