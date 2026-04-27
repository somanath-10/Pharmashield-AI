'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getPatientCases } from '@/lib/api';

export default function PatientUploadPage() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const cases = await getPatientCases();
        setCount(cases.length);
      } catch {
        setCount(0);
      }
    })();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto', padding: '24px' }}>
      <div className="glass-card" style={{ padding: '32px' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '12px' }}>Upload Center</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Direct upload intake is routed through the Medicine Safety Scanner.
        </p>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
          You currently have <strong style={{ color: 'white' }}>{count}</strong> recorded case(s).
        </p>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link href="/patient/medicine-safety" style={{ color: '#60a5fa', textDecoration: 'none', fontWeight: 600 }}>
            Go to Medicine Safety Scanner →
          </Link>
          <Link href="/patient/dashboard" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 600 }}>
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}