'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase } from '@/lib/api';

const RISK_COLORS: Record<string, string> = { LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444' };

export default function MedicineSafetyPage() {
  const [file, setFile] = useState<File | null>(null);
  const [sellerType, setSellerType] = useState('licensed_pharmacy');
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('');

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setStep('Initializing check...');
    try {
      const { case_id } = await createCase({ role: 'PATIENT', case_type: 'PATIENT_PRESCRIPTION_EXPLANATION', title: 'Medicine Safety Check', query: 'Check medicine safety' });
      setStep('Uploading...');
      await uploadDocument(case_id, file);
      setStep('Running safety analysis...');
      const res = await analyzeCase(case_id, 'Check medicine safety and seller risk', { seller_type: sellerType });
      setResult(res);
    } catch (e) {
      console.error(e);
    }
    setLoading(false); setStep('');
  };

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🛡️ Medicine Safety Scanner</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Upload your prescription, invoice, or medicine photo.</p>
        </div>
        <Link href="/patient/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back to Dashboard</Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <input type="file" accept=".pdf,.txt,.jpg,.png" onChange={e => e.target.files?.[0] && setFile(e.target.files[0])} style={{ marginBottom: '16px', display: 'block', color: 'white' }} />
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Seller Type</label>
        <select className="premium-input" value={sellerType} onChange={e => setSellerType(e.target.value)} style={{ marginBottom: '20px', background: 'rgba(255,255,255,0.05)', color: 'white' }}>
          <option value="licensed_pharmacy">Licensed Pharmacy</option>
          <option value="online_pharmacy">Online Pharmacy (1mg, Apollo, etc)</option>
          <option value="whatsapp_seller">WhatsApp Seller</option>
          <option value="unknown">Unknown</option>
        </select>
        <button className={`btn-primary ${loading ? 'btn-disabled' : ''}`} onClick={handleAnalyze} disabled={loading || !file} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? step : 'Analyze Safety'}
        </button>
      </div>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px' }}>
           <h3 style={{ marginBottom: '16px' }}>Safety Result</h3>
           <div style={{ padding: '12px', borderRadius: '8px', border: `1px solid ${RISK_COLORS[result.risk_level]}44`, background: `${RISK_COLORS[result.risk_level]}22`, display: 'inline-block', marginBottom: '16px' }}>
             <strong style={{ color: RISK_COLORS[result.risk_level] }}>Risk Level: {result.risk_level}</strong>
           </div>
           <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.answer?.simple_summary || result.answer?.seller_warning || "Analysis complete. Please review with a pharmacist."}</p>
        </div>
      )}
    </div>
  );
}