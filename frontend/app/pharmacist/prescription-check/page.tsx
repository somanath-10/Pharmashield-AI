'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase } from '@/lib/api';

export default function PrescriptionCheckPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('');

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setStep('Creating Case...');
    try {
      const { case_id } = await createCase({ role: 'PHARMACIST', case_type: 'PHARMACIST_DISPENSING_CHECK', title: 'Rx Authenticity Check', query: 'Verify prescription' });
      setStep('Uploading...');
      await uploadDocument(case_id, file);
      setStep('Analyzing authenticity...');
      const res = await analyzeCase(case_id, 'Verify doctor details and date', {});
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
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📝 Prescription Authenticity</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Check for missing doctor details, dates, or AI-generated patterns.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <input type="file" accept=".pdf,.jpg,.png" onChange={e => e.target.files?.[0] && setFile(e.target.files[0])} style={{ marginBottom: '20px', display: 'block', color: 'white' }} />
        <button className={`btn-primary ${loading ? 'btn-disabled' : ''}`} onClick={handleAnalyze} disabled={loading || !file} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? step : 'Run Check'}
        </button>
      </div>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px' }}>
           <h3 style={{ marginBottom: '16px', color: '#60a5fa' }}>Analysis Complete</h3>
           <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.answer?.prescription_summary || "Prescription verified successfully."}</p>
           {result.answer?.compliance_warnings && result.answer.compliance_warnings.length > 0 && (
             <div style={{ marginTop: '16px', background: 'rgba(239,68,68,0.1)', padding: '16px', borderRadius: '8px', color: '#fca5a5' }}>
               <h4 style={{ marginBottom: '8px' }}>⚠️ Warnings</h4>
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