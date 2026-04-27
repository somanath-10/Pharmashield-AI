'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase } from '@/lib/api';

const RISK_COLORS: Record<string, string> = { LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444' };

export default function MedicineSafetyPage() {
  const [file, setFile] = useState<File | null>(null);
  const [sellerType, setSellerType] = useState('licensed_pharmacy');
  const [question, setQuestion] = useState('Explain my prescription and check for safety.');
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('');
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setStep('Initializing check...'); setError('');
    try {
      const { case_id } = await createCase({ 
        role: 'PATIENT', 
        case_type: 'PATIENT_PRESCRIPTION_EXPLANATION', 
        title: 'Medicine Safety Check', 
        query: question 
      });
      setStep('Uploading...');
      const uploadRes = await uploadDocument(case_id, file);
      
      if (uploadRes.status === 'OCR_PENDING') {
        setResult({
          risk_level: 'UNKNOWN',
          answer: {
            simple_summary: uploadRes.message,
            answer: uploadRes.message
          }
        });
        setLoading(false); setStep('');
        return;
      }

      setStep('Running safety analysis...');
      const res = await analyzeCase(case_id, question, { seller_type: sellerType });
      setResult(res);
    } catch (e: any) {
      setError(e?.message || 'Failed to analyze safety. Please check your connection.');
      console.error(e);
    }
    setLoading(false); setStep('');
  };

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🛡️ Medicine Safety Scanner</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Upload your prescription or report and ask any question.</p>
        </div>
        <Link href="/patient/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back to Dashboard</Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Upload Document</label>
        <input type="file" accept=".pdf,.txt,.jpg,.png" onChange={e => e.target.files?.[0] && setFile(e.target.files[0])} style={{ marginBottom: '16px', display: 'block', color: 'white' }} />
        
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Your Question</label>
        <textarea 
          className="premium-input" 
          value={question} 
          onChange={e => setQuestion(e.target.value)} 
          placeholder="e.g. What is the dosage for Metformin? Are there any risks?"
          style={{ marginBottom: '16px', height: '80px' }} 
        />

        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Seller Type</label>
        <select className="premium-input" value={sellerType} onChange={e => setSellerType(e.target.value)} style={{ marginBottom: '20px', background: 'rgba(255,255,255,0.05)', color: 'white' }}>
          <option value="licensed_pharmacy">Licensed Pharmacy</option>
          <option value="online_pharmacy">Online Pharmacy (1mg, Apollo, etc)</option>
          <option value="whatsapp_seller">WhatsApp Seller</option>
          <option value="unknown">Unknown</option>
        </select>
        <button className={`btn-primary ${loading ? 'btn-disabled' : ''}`} onClick={handleAnalyze} disabled={loading || !file} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? step : 'Analyze with RAG'}
        </button>

        {error && (
          <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', color: '#f87171', borderRadius: '8px', fontSize: '0.9rem' }}>
            ❌ {error}
          </div>
        )}
      </div>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px' }}>
           <h3 style={{ marginBottom: '16px' }}>Safety & RAG Analysis</h3>
           <div style={{ padding: '12px', borderRadius: '8px', border: `1px solid ${RISK_COLORS[result.risk_level]}44`, background: `${RISK_COLORS[result.risk_level]}22`, display: 'inline-block', marginBottom: '16px' }}>
             <strong style={{ color: RISK_COLORS[result.risk_level] }}>Risk Level: {result.risk_level}</strong>
           </div>
           
           <div style={{ marginBottom: '20px' }}>
             <h4 style={{ color: '#60a5fa', marginBottom: '8px' }}>🤖 AI Answer:</h4>
             <p style={{ color: 'white', lineHeight: 1.6, background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
               {result.answer?.answer || "No specific answer found."}
             </p>
           </div>

           <h4 style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>Summary:</h4>
           <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '16px' }}>
             {result.answer?.simple_summary || result.answer?.seller_warning}
           </p>

           {result.answer?.medicines_found && result.answer.medicines_found.length > 0 && (
             <div style={{ marginTop: '16px' }}>
               <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Medicines Detected:</h4>
               <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                 {result.answer.medicines_found.map((m: string, i: number) => (
                   <span key={i} style={{ background: 'rgba(96, 165, 250, 0.1)', color: '#60a5fa', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem' }}>{m}</span>
                 ))}
               </div>
             </div>
           )}
        </div>
      )}
    </div>
  );
}