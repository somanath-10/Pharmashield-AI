'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function PharmacistDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Verify this prescription for dispensing.');
  const [analysis, setAnalysis] = useState<any>(null);
  const [citations, setCitations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);
    setCitations([]);
    
    try {
      setUploadStatus('Creating case...');
      const caseRes = await fetch('http://localhost:8000/api/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'PHARMACIST', case_type: 'PHARMACIST_DISPENSING_CHECK', title: 'Dispensing Check', query: query }),
      });
      const { case_id } = await caseRes.json();

      setUploadStatus('Uploading prescription...');
      const formData = new FormData();
      formData.append('file', file);
      
      const docRes = await fetch(`http://localhost:8000/api/cases/${case_id}/documents`, {
        method: 'POST',
        body: formData,
      });

      if (!docRes.ok) throw new Error('Failed to process document');

      setUploadStatus('Running RAG checks...');
      const res = await fetch(`http://localhost:8000/api/cases/${case_id}/analyze`, { method: 'POST' });
      const data = await res.json();
      
      if (data.answer) {
        setAnalysis(data.answer);
        setCitations(data.citations || []);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err: any) {
      setError(err.message || 'Error communicating with server.');
    }
    setLoading(false);
    setUploadStatus('');
  };

  return (
    <div className="animate-in" style={{ maxWidth: '850px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>💊</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Pharmacist Assistant</h2>
            <span style={{ background: 'rgba(59,130,246,0.12)', color: '#60a5fa', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing:'0.05em' }}>Pharmacist</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Upload prescriptions to check dispensing compliance and counseling points.</p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Input */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            📄 Upload Prescription
          </label>
          <input 
            type="file" 
            accept=".pdf,.txt" 
            onChange={handleFileChange}
            style={{ marginBottom: '16px', display: 'block', color: 'var(--text-primary)' }}
          />
          
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            ❓ Dispensing Query
          </label>
          <textarea 
            className="premium-input" 
            style={{ height: '80px', marginBottom: '20px' }} 
            value={query} 
            onChange={e => setQuery(e.target.value)} 
          />
          
          <button className={`btn-primary btn-pharmacist${loading ? ' btn-disabled' : ''}`} style={{ width: '100%', justifyContent: 'center' }} onClick={handleAnalyze} disabled={loading || !file}>
            {loading ? '⏳ Checking...' : '✅ Check Compliance'}
          </button>
          
          {uploadStatus && <div style={{ color: '#60a5fa', fontSize: '0.85rem', marginTop: '12px', textAlign: 'center' }}>{uploadStatus}</div>}
          {error && <div style={{ color: '#fca5a5', fontSize: '0.85rem', marginTop: '12px', textAlign: 'center' }}>{error}</div>}
        </div>

        {/* Output */}
        {analysis ? (
          <div className="glass-card animate-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#60a5fa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Prescription Summary</h4>
              <p style={{ color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.6 }}>{analysis.prescription_summary}</p>
            </div>
            
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>💊 Medicines</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#60a5fa', fontSize: '0.875rem' }}>
                  {analysis.medicines_found?.map((m: string, i: number) => <li key={i}>{m}</li>)}
                </ul>
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>❓ Missing Info</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#fbbf24', fontSize: '0.875rem' }}>
                  {analysis.missing_information?.map((m: string, i: number) => <li key={i}>{m}</li>)}
                </ul>
              </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '16px' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>🔬 Dispensing Support</h4>
              <ul style={{ paddingLeft: '16px', display: 'flex', flexDirection: 'column', gap: '6px', margin: 0 }}>
                {analysis.dispensing_support?.map((item: string, i: number) => (
                  <li key={i} style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>{item}</li>
                ))}
              </ul>
              {analysis.substitution_caution && (
                <div style={{ marginTop: '10px', fontSize: '0.85rem', color: '#f87171', background: 'rgba(239,68,68,0.1)', padding: '8px', borderRadius: '4px' }}>
                  ⚠️ {analysis.substitution_caution}
                </div>
              )}
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '16px' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>💬 Counseling Points</h4>
              <ul style={{ paddingLeft: '16px', display: 'flex', flexDirection: 'column', gap: '6px', margin: 0 }}>
                {analysis.patient_counseling_points?.map((item: string, i: number) => (
                  <li key={i} style={{ fontSize: '0.875rem', color: '#34d399', lineHeight: 1.5 }}>{item}</li>
                ))}
              </ul>
            </div>
            
            <div style={{ marginTop: 'auto', background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '6px', padding: '10px' }}>
              <span style={{ fontWeight: 700, color: '#f87171', fontSize: '0.75rem', textTransform: 'uppercase' }}>⛔ {analysis.pharmacist_review_required}</span>
            </div>
          </div>
        ) : (
          <div className="glass-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed rgba(255,255,255,0.08)' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textAlign: 'center' }}>
              💊 Upload a prescription and run analysis to see insights here
            </p>
          </div>
        )}
      </div>
      
      {/* Citations below main layout if present */}
      {citations.length > 0 && (
        <div className="glass-card animate-in" style={{ marginTop: '24px', padding: '20px' }}>
          <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>📚 Prescription Citations</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {citations.map((cit, i) => (
              <div key={i} style={{ fontSize: '0.85rem', borderLeft: '3px solid #60a5fa', paddingLeft: '12px' }}>
                <div style={{ color: '#9ca3af', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: '#d1d5db' }}>{cit.document_name}</span> (Page {cit.page_number})
                </div>
                <div style={{ fontStyle: 'italic', color: '#cbd5e1' }}>"{cit.source_snippet}"</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
