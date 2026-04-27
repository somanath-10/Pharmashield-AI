'use client';

import { useState } from 'react';
import Link from 'next/link';
import { performPriceCheck } from '@/lib/api';

export default function PriceCheckPage() {
  const [formData, setFormData] = useState({ medicine_name: '', mrp: '', charged_price: '' });
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await performPriceCheck({
        case_id: 'draft-' + Date.now(),
        medicine_name: formData.medicine_name,
        mrp: parseFloat(formData.mrp),
        charged_price: parseFloat(formData.charged_price)
      });
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
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>💰 Price Compliance</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Check MRP against NPPA ceiling prices.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <form className="glass-card" style={{ padding: '28px', marginBottom: '28px' }} onSubmit={handleCheck}>
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Medicine Name</label>
        <input required type="text" className="premium-input" style={{ marginBottom: '16px' }} value={formData.medicine_name} onChange={e => setFormData({...formData, medicine_name: e.target.value})} />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>MRP (₹)</label>
            <input required type="number" step="0.01" className="premium-input" value={formData.mrp} onChange={e => setFormData({...formData, mrp: e.target.value})} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Charged Price (₹)</label>
            <input required type="number" step="0.01" className="premium-input" value={formData.charged_price} onChange={e => setFormData({...formData, charged_price: e.target.value})} />
          </div>
        </div>

        <button type="submit" className={`btn-primary ${loading ? 'btn-disabled' : ''}`} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? 'Checking...' : 'Check Compliance'}
        </button>
      </form>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px', borderColor: result.is_overcharged ? '#ef4444' : '#34d399' }}>
           <h3 style={{ marginBottom: '16px', color: result.is_overcharged ? '#f87171' : '#34d399' }}>
             {result.is_overcharged ? '🚨 OVERCHARGED' : '✅ Compliant'}
           </h3>
           {result.is_overcharged && (
             <div style={{ background: 'rgba(239,68,68,0.1)', padding: '16px', borderRadius: '8px', color: '#fca5a5' }}>
               Charged price (₹{result.charged_price}) exceeds the MRP (₹{result.mrp}). This violates NPPA pricing rules.
             </div>
           )}
        </div>
      )}
    </div>
  );
}