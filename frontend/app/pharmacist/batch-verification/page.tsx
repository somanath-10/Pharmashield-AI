'use client';

import { useState } from 'react';
import Link from 'next/link';
import { performBatchCheck } from '@/lib/api';

export default function BatchVerificationPage() {
  const [formData, setFormData] = useState({ medicine_name: '', batch_number: '', expiry_date: '', manufacturer: '', supplier: '' });
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await performBatchCheck({ case_id: 'draft-' + Date.now(), ...formData });
      setResult(res);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📦 Batch Verification</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Verify NSQ databases and quarantine spurious stock.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <form className="glass-card" style={{ padding: '28px', marginBottom: '28px' }} onSubmit={handleCheck}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Medicine Name</label>
            <input required type="text" className="premium-input" value={formData.medicine_name} onChange={e => setFormData({...formData, medicine_name: e.target.value})} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Batch Number</label>
            <input required type="text" className="premium-input" value={formData.batch_number} onChange={e => setFormData({...formData, batch_number: e.target.value})} placeholder="Ends in X = Mock Spurious" />
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Manufacturer (Optional)</label>
            <input type="text" className="premium-input" value={formData.manufacturer} onChange={e => setFormData({...formData, manufacturer: e.target.value})} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Supplier (Optional)</label>
            <input type="text" className="premium-input" value={formData.supplier} onChange={e => setFormData({...formData, supplier: e.target.value})} />
          </div>
        </div>

        <button type="submit" className={`btn-primary ${loading ? 'btn-disabled' : ''}`} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? 'Checking...' : 'Verify Batch'}
        </button>
      </form>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px', borderColor: result.is_quarantined ? '#ef4444' : '#34d399' }}>
           <h3 style={{ marginBottom: '16px', color: result.is_quarantined ? '#f87171' : '#34d399' }}>
             {result.is_quarantined ? '🚨 QUARANTINED' : '✅ Verified Clean'}
           </h3>
           <p style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>Medicine: {result.medicine_name}</p>
           <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Batch: {result.batch_number}</p>
           {result.is_quarantined && (
             <div style={{ background: 'rgba(239,68,68,0.1)', padding: '16px', borderRadius: '8px', color: '#fca5a5' }}>
               <strong>Reason:</strong> {result.quarantine_reason}
             </div>
           )}
        </div>
      )}
    </div>
  );
}