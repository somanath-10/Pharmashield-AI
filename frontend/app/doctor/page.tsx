'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function DoctorDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Summarize the patient case.');
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
        body: JSON.stringify({ role: 'DOCTOR', case_type: 'DOCTOR_CASE_SUMMARY', title: 'Patient Review', query: query }),
      });
      const { case_id } = await caseRes.json();

      setUploadStatus('Uploading documents...');
      const formData = new FormData();
      formData.append('file', file);
      
      const docRes = await fetch(`http://localhost:8000/api/cases/${case_id}/documents`, {
        method: 'POST',
        body: formData,
      });

      if (!docRes.ok) throw new Error('Failed to process document');

      setUploadStatus('Synthesizing clinical summary...');
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
    <div className="animate-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>🩺</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Doctor Dashboard</h2>
            <span style={{ background: 'rgba(99,102,241,0.12)', color: '#a5b4fc', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing:'0.05em' }}>Doctor</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Review summarized patient case highlights and clinical follow-up points.</p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Input */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
            📁 Upload Patient Document
          </label>
          <input 
            type="file" 
            accept=".pdf,.txt" 
            onChange={handleFileChange}
            style={{ marginBottom: '16px', display: 'block', color: 'var(--text-primary)' }}
          />
          
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
            ❓ Clinical Query
          </label>
          <textarea 
            className="premium-input" 
            style={{ height: '80px', marginBottom: '16px' }} 
            value={query} 
            onChange={e => setQuery(e.target.value)} 
          />
          
          <button className={`btn-primary btn-doctor${loading ? ' btn-disabled' : ''}`} style={{ width: '100%', justifyContent: 'center' }} onClick={handleAnalyze} disabled={loading || !file}>
            {loading ? '⏳ Synthesizing...' : '📊 Generate Clinical Summary'}
          </button>
          
          {uploadStatus && <div style={{ color: '#a5b4fc', fontSize: '0.85rem', marginTop: '12px', textAlign: 'center' }}>{uploadStatus}</div>}
          {error && <div style={{ color: '#fca5a5', fontSize: '0.85rem', marginTop: '12px', textAlign: 'center' }}>{error}</div>}
        </div>

        {/* Output */}
        {analysis ? (
          <div className="glass-card animate-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Case Summary</h4>
              <p style={{ color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.7, whiteSpace: 'pre-line' }}>{analysis.case_summary}</p>
            </div>
            
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>💊 Medicines Identified</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#60a5fa', fontSize: '0.875rem' }}>
                  {analysis.medicines_identified?.map((m: string, i: number) => <li key={i}>{m}</li>)}
                </ul>
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>🧪 Lab Highlights</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#fbbf24', fontSize: '0.875rem' }}>
                  {analysis.lab_highlights?.map((m: string, i: number) => <li key={i}>{m}</li>)}
                </ul>
              </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '16px' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>✅ Follow-up Considerations</h4>
              <ol style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px', margin: 0 }}>
                {analysis.follow_up_considerations?.map((item: string, i: number) => (
                  <li key={i} style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>{item}</li>
                ))}
              </ol>
            </div>
            
            {analysis.patient_questions?.length > 0 && (
               <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '16px' }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>❓ Patient Questions</h4>
                <ul style={{ paddingLeft: '16px', display: 'flex', flexDirection: 'column', gap: '6px', margin: 0 }}>
                  {analysis.patient_questions?.map((item: string, i: number) => (
                    <li key={i} style={{ fontSize: '0.875rem', color: '#cbd5e1', lineHeight: 1.5, fontStyle: 'italic' }}>"{item}"</li>
                  ))}
                </ul>
              </div>
            )}
            
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: 'auto' }}>{analysis.professional_review_note}</p>
          </div>
        ) : (
          <div className="glass-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed rgba(255,255,255,0.08)' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textAlign: 'center' }}>
              🩺 Generate a clinical summary to see insights here
            </p>
          </div>
        )}
      </div>
      
      {/* Citations */}
      {citations.length > 0 && (
        <div className="glass-card animate-in" style={{ marginTop: '24px', padding: '20px' }}>
          <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>📚 Evidence / Source Documents</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {citations.map((cit, i) => (
              <div key={i} style={{ fontSize: '0.85rem', borderLeft: '3px solid #818cf8', paddingLeft: '12px' }}>
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
