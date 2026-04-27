'use client';

import { useState } from 'react';
import Link from 'next/link';
import { performSubstitutionCheck } from '@/lib/api';

export default function SubstitutionCheckPage() {
  const [formData, setFormData] = useState({ prescribed: '', substituted: '' });
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await performSubstitutionCheck({
        prescribed_medicine: formData.prescribed,
        substituted_medicine: formData.substituted
      });
      setResult(res);
    } catch (e: any) {
      setError(e?.message || 'Failed to validate substitution');
    }
    setLoading(false);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🔄 Substitution Safety</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Ensure generic substitutions match active molecules.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <form className="glass-card" style={{ padding: '28px', marginBottom: '28px' }} onSubmit={handleCheck}>
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Prescribed Medicine</label>
        <input required type="text" className="premium-input" style={{ marginBottom: '16px' }} value={formData.prescribed} onChange={e => setFormData({...formData, prescribed: e.target.value})} placeholder="e.g. Paracetamol 500mg" />

        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Proposed Substitution</label>
        <input required type="text" className="premium-input" style={{ marginBottom: '24px' }} value={formData.substituted} onChange={e => setFormData({...formData, substituted: e.target.value})} placeholder="e.g. Crocin 500mg" />

        <button type="submit" className={`btn-primary ${loading ? 'btn-disabled' : ''}`} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? 'Checking...' : 'Compare Medicines'}
        </button>
      </form>
      {error && <div className="glass-card" style={{ padding: '16px', marginBottom: '20px', color: '#f87171' }}>❌ {error}</div>}

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px', borderColor: result.is_safe ? '#34d399' : '#ef4444' }}>
           <h3 style={{ marginBottom: '16px', color: result.is_safe ? '#34d399' : '#f87171' }}>
             {result.is_safe ? '✅ SAFE TO SUBSTITUTE' : '🚨 UNSAFE SUBSTITUTION'}
           </h3>
           {!result.is_safe && (
             <div style={{ background: 'rgba(239,68,68,0.1)', padding: '16px', borderRadius: '8px', color: '#fca5a5' }}>
               <strong style={{ display: 'block', marginBottom: '8px' }}>Mismatch Reasons:</strong>
               <ul style={{ margin: 0, paddingLeft: '20px' }}>
                 {result.mismatch_reasons.map((r: string, i: number) => <li key={i}>{r}</li>)}
               </ul>
             </div>
           )}
        </div>
      )}
    </div>
  );
}