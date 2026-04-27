'use client';

import Link from 'next/link';

export default function PharmacistQuestionsPage() {
  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>💬 Pharmacist Inquiries</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Direct queries from dispensing pharmacists regarding prescriptions.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <p>No active inquiries from pharmacists.</p>
      </div>
    </div>
  );
}