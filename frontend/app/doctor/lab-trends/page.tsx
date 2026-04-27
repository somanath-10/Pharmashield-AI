'use client';

import Link from 'next/link';

export default function LabTrendsPage() {
  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📈 Lab Trends</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Longitudinal analysis of patient lab markers.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <h3>🚧 Feature Pending Data Integration</h3>
        <p style={{ marginTop: '16px', maxWidth: '400px', margin: '16px auto 0' }}>
          Lab extraction models are active, but historical integration requires the next EHR update phase.
        </p>
      </div>
    </div>
  );
}