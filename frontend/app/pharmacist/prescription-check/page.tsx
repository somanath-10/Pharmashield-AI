'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase } from '@/lib/api';

export default function PrescriptionCheckPage() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState('Verify prescription authenticity and doctor details.');
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('');
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setStep('Creating Case...');
    try {
      const { case_id } = await createCase({ 
        role: 'PHARMACIST', 
        case_type: 'PHARMACIST_DISPENSING_CHECK', 
        title: 'Rx Authenticity Check', 
        query: question 
      });
      const uploadRes = await uploadDocument(case_id, file);
      if (uploadRes.status === 'OCR_PENDING') {
        setResult({
          risk_level: 'UNKNOWN',
          answer: {
            prescription_summary: uploadRes.message,
            answer: uploadRes.message
          }
        });
        setLoading(false); setStep('');
        return;
      }
      setStep('Analyzing with RAG...');
      const res = await analyzeCase(case_id, question, {});
      setResult(res);
    } catch (e: any) {
      setError(e?.message || 'Failed to check prescription');
    }
    setLoading(false); setStep('');
  };

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📝 Rx Authenticity & RAG</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Verify documents and ask AI specific questions about the clinical context.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        {error && <div style={{ marginBottom: '16px', color: '#f87171' }}>❌ {error}</div>}
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Upload Prescription/Report</label>
        <input type="file" accept=".pdf,.jpg,.png" onChange={e => { setError(''); e.target.files?.[0] && setFile(e.target.files[0]); }} style={{ marginBottom: '20px', display: 'block', color: 'white' }} />
        
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Specific Question (Optional)</label>
        <textarea 
          className="premium-input" 
          value={question} 
          onChange={e => setQuestion(e.target.value)} 
          placeholder="e.g. Is the doctor's registration number valid? Does the date look correct?"
          style={{ marginBottom: '20px', height: '60px' }} 
        />

        <button className={`btn-primary ${loading ? 'btn-disabled' : ''}`} onClick={handleAnalyze} disabled={loading || !file} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? step : 'Run RAG Check'}
        </button>
      </div>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px' }}>
           <h3 style={{ marginBottom: '16px', color: '#60a5fa' }}>Analysis Complete</h3>
           
           <div style={{ marginBottom: '20px' }}>
             <h4 style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>🤖 RAG Answer:</h4>
             <p style={{ color: 'white', lineHeight: 1.6, background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
               {result.answer?.answer || "No specific answer found in the document."}
             </p>
           </div>

           <h4 style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>Summary:</h4>
           <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.answer?.prescription_summary}</p>
           
           {result.answer?.compliance_warnings && result.answer.compliance_warnings.length > 0 && (
             <div style={{ marginTop: '16px', background: 'rgba(239,68,68,0.1)', padding: '16px', borderRadius: '8px', color: '#fca5a5' }}>
               <h4 style={{ marginBottom: '8px' }}>⚠️ Compliance Warnings</h4>
               <ul style={{ margin: 0, paddingLeft: '20px' }}>
                 {result.answer.compliance_warnings.map((w: string, i: number) => <li key={i}>{w}</li>)}
               </ul>
             </div>
           )}
        </div>
      )}
    </div>
  );
}