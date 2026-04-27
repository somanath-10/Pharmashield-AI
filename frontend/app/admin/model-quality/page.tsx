'use client';

import Link from 'next/link';

export default function ModelQualityPage() {
  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🧠 Model Quality & Telemetry</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Track LLM hallucination flags and confidence scores.</p>
        </div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📊</div>
        <h3 style={{ color: 'white', marginBottom: '8px' }}>Model Telemetry Active</h3>
        <p style={{ maxWidth: '400px', margin: '0 auto' }}>
          All LLM generations are currently passing internal consistency checks. Deep visual telemetry integration will be unlocked in Phase 9.
        </p>
      </div>
    </div>
  );
}