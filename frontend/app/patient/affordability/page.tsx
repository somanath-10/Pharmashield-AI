'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function AffordabilityPage() {
  const [medicine, setMedicine] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const checkAffordability = () => {
    if (!medicine) return;
    setLoading(true);
    setTimeout(() => {
      setResult({
        recommendation: "Ask pharmacist for generic equivalent.",
        alternatives: [
          { brand: "Jan Aushadhi Generic", estimated_savings: "70%" },
          { brand: "Generic A", estimated_savings: "40%" }
        ]
      });
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>💰 Affordability Check</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Find cheaper, safe alternatives for your medicine.</p>
        </div>
        <Link href="/patient/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Prescribed Medicine Name</label>
        <input type="text" className="premium-input" style={{ marginBottom: '20px' }} value={medicine} onChange={e => setMedicine(e.target.value)} placeholder="e.g. Augmentin 625" />
        <button className={`btn-primary ${loading ? 'btn-disabled' : ''}`} onClick={checkAffordability} disabled={loading || !medicine} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? 'Checking...' : 'Check Alternatives'}
        </button>
      </div>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px' }}>
           <h3 style={{ marginBottom: '16px', color: '#34d399' }}>✅ Alternatives Found</h3>
           <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}><strong>Guidance:</strong> {result.recommendation}</p>
           
           <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
             {result.alternatives.map((alt: any, i: number) => (
               <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                 <strong style={{ color: 'white' }}>{alt.brand}</strong>
                 <span style={{ color: '#34d399', fontWeight: 700 }}>Save up to {alt.estimated_savings}</span>
               </div>
             ))}
           </div>
           
           <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(239,68,68,0.1)', borderRadius: '8px', color: '#fca5a5', fontSize: '0.85rem' }}>
             ⚠️ Do not replace critical medicines without your doctor's approval.
           </div>
        </div>
      )}
    </div>
  );
}