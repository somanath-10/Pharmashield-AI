'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function PatientDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Please explain my document in simple words.');
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
        body: JSON.stringify({ role: 'PATIENT', case_type: 'PATIENT_REPORT_EXPLANATION', title: 'My Documents', query: query }),
      });
      const { case_id } = await caseRes.json();

      setUploadStatus('Uploading document & extracting text...');
      const formData = new FormData();
      formData.append('file', file);
      
      const docRes = await fetch(`http://localhost:8000/api/cases/${case_id}/documents`, {
        method: 'POST',
        body: formData,
      });

      if (!docRes.ok) {
        throw new Error('Failed to process document');
      }

      setUploadStatus('Analyzing with AI...');
      const res = await fetch(`http://localhost:8000/api/cases/${case_id}/analyze`, { method: 'POST' });
      const data = await res.json();
      
      if (data.answer) {
        setAnalysis(data.answer);
        setCitations(data.citations || []);
      } else {
        throw new Error('Invalid response format');
      }
      
    } catch (err: any) {
      setError(err.message || 'Could not reach the backend. Make sure the server is running.');
    }
    setLoading(false);
    setUploadStatus('');
  };

  return (
    <div className="animate-in" style={{ maxWidth: '780px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>👤</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Patient Assistant</h2>
            <span style={{ background: 'rgba(16,185,129,0.12)', color: '#34d399', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing:'0.05em' }}>Patient</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Upload your prescription or lab report for a simple, safe explanation.
          </p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>
            ← Change Role
          </button>
        </Link>
      </div>

      {/* Input Card */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          📄 Upload Document (PDF or TXT)
        </label>
        
        <input 
          type="file" 
          accept=".pdf,.txt" 
          onChange={handleFileChange}
          style={{ marginBottom: '16px', display: 'block', color: 'var(--text-primary)' }}
        />
        
        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          ❓ Your Question
        </label>
        <input
          type="text"
          className="premium-input"
          style={{ marginBottom: '20px' }}
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="What do you want to know?"
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            className={`btn-primary btn-patient${loading ? ' btn-disabled' : ''}`}
            onClick={handleAnalyze}
            disabled={loading || !file}
          >
            {loading ? (
              <>
                <span style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
                Analyzing...
              </>
            ) : '🔍 Analyze Document'}
          </button>
          {uploadStatus && <span style={{ color: '#a5b4fc', fontSize: '0.85rem' }}>{uploadStatus}</span>}
          {error && <span style={{ color: '#fca5a5', fontSize: '0.85rem' }}>{error}</span>}
        </div>
      </div>

      {/* Results */}
      {analysis && (
        <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Disclaimer */}
          <div className="disclaimer-box">
            <span style={{ fontWeight: 700 }}>⚠️ Important: </span>{analysis.disclaimer}
          </div>

          {/* Summary */}
          <div className="result-section">
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Summary</h4>
            <p style={{ color: 'var(--text-primary)', lineHeight: 1.7 }}>{analysis.simple_summary}</p>
            <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>{analysis.what_this_may_mean}</p>
          </div>

          {/* Medicines & Labs */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {analysis.medicines_found?.length > 0 && (
              <div className="result-section">
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💊 Medicines</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {analysis.medicines_found.map((med: string, i: number) => (
                    <div key={i} className="medicine-pill">
                      <div style={{ fontWeight: 600, color: '#60a5fa' }}>{med}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysis.lab_values_found?.length > 0 && (
              <div className="result-section">
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>🧪 Lab Findings</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {analysis.lab_values_found.map((lab: string, i: number) => (
                    <div key={i} className="lab-pill">
                      <div style={{ fontWeight: 600, color: '#a5b4fc' }}>{lab}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Safe Next Steps */}
          {analysis.safe_next_steps?.length > 0 && (
            <div className="result-section">
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>✅ Safe Next Steps</h4>
              <ul style={{ paddingLeft: '20px', color: '#34d399', fontSize: '0.9rem', lineHeight: 1.6 }}>
                {analysis.safe_next_steps.map((step: string, i: number) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Warning */}
          {analysis.warning_signs?.length > 0 && (
            <div className="warning-box">
              <span style={{ fontWeight: 700 }}>🚨 Warning Signs: </span>
              {analysis.warning_signs.join(' • ')}
            </div>
          )}

          {/* Questions */}
          <div className="result-section">
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💬 Questions for Your Doctor</h4>
            <ol style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {analysis.questions_to_ask_doctor?.map((q: string, i: number) => (
                <li key={i} style={{ color: '#e2e8f0', fontSize: '0.9rem', lineHeight: 1.5 }}>{q}</li>
              ))}
            </ol>
          </div>
          
          {/* Citations */}
          {citations.length > 0 && (
            <div className="result-section" style={{ marginTop: '16px', background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px' }}>
              <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>📚 Sources / Citations</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {citations.map((cit, i) => (
                  <div key={i} style={{ fontSize: '0.8rem', borderLeft: '3px solid #4b5563', paddingLeft: '12px' }}>
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
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
