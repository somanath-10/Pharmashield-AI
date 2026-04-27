'use client';
import Link from 'next/link';

export default function AdminSellerAnalyticsPage() {
  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div><h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🏪 Seller Analytics</h2><p style={{ color: 'var(--text-secondary)' }}>Risk analysis of online pharmacies vs local shops.</p></div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>
      <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <h3>🚧 Analytics Engine Pending</h3>
        <p style={{ marginTop: '16px' }}>Seller geography heatmaps will be available in the next mapping integration phase.</p>
      </div>
    </div>
  );
}