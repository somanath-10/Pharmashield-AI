'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function PatientDashboard() {
  const [text, setText] = useState('I got prescribed Metformin 500mg and my HbA1c is 8.2');
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setAnalysis(null);
    try {
      const caseRes = await fetch('http://localhost:8000/api/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'PATIENT', case_type: 'PATIENT_PRESCRIPTION_EXPLANATION', title: 'My Documents', query: 'Please explain my documents.' }),
      });
      const { case_id } = await caseRes.json();

      await fetch(`http://localhost:8000/api/cases/${case_id}/documents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_type: 'PRESCRIPTION', file_name: 'upload.pdf', mock_extracted_text: text }),
      });

      const res = await fetch(`http://localhost:8000/api/cases/${case_id}/analyze`, { method: 'POST' });
      const data = await res.json();
      setAnalysis(data.result);
    } catch {
      setError('Could not reach the backend. Make sure the server is running.');
    }
    setLoading(false);
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
          📄 Document Text (MVP Simulator)
        </label>
        <textarea
          className="premium-input"
          style={{ height: '120px', marginBottom: '20px' }}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Type or paste extracted text (e.g. Metformin 500mg, HbA1c 8.2, Amoxicillin...)"
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            className={`btn-primary btn-patient${loading ? ' btn-disabled' : ''}`}
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <span style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
                Analyzing...
              </>
            ) : '🔍 Analyze Documents'}
          </button>
          {error && <span style={{ color: '#fca5a5', fontSize: '0.85rem' }}>{error}</span>}
        </div>
      </div>

      {/* Results */}
      {analysis && (
        <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Disclaimer - most prominent */}
          <div className="disclaimer-box">
            <span style={{ fontWeight: 700 }}>⚠️ Important: </span>{analysis.disclaimer}
          </div>

          {/* Summary */}
          <div className="result-section">
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Summary</h4>
            <p style={{ color: 'var(--text-primary)', lineHeight: 1.7 }}>{analysis.summary}</p>
          </div>

          {/* Medicines */}
          {analysis.medicines_found?.length > 0 && (
            <div className="result-section">
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💊 Medicines Found</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {analysis.medicines_found.map((med: any, i: number) => (
                  <div key={i} className="medicine-pill">
                    <div style={{ fontWeight: 700, color: '#60a5fa', marginBottom: '4px' }}>{med.name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>{med.purpose}</div>
                    <div style={{ fontSize: '0.82rem', color: '#fbbf24', fontWeight: 600 }}>⚡ {med.instruction}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Lab Values */}
          {analysis.lab_values_found?.length > 0 && (
            <div className="result-section">
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>🧪 Lab Values Found</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {analysis.lab_values_found.map((lab: any, i: number) => (
                  <div key={i} className="lab-pill">
                    <div style={{ fontWeight: 700, color: '#a5b4fc', marginBottom: '4px' }}>{lab.test}: <span style={{ color: '#e0e7ff' }}>{lab.value}</span></div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{lab.explanation}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warning */}
          <div className="warning-box">
            <span style={{ fontWeight: 700 }}>🚨 Warning Signs — Seek immediate care if you notice: </span>
            {analysis.warning_signs?.join(' • ')}
          </div>

          {/* Questions */}
          <div className="result-section">
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💬 Questions to Ask Your Doctor</h4>
            <ol style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {analysis.questions_to_ask_doctor?.map((q: string, i: number) => (
                <li key={i} style={{ color: '#e2e8f0', fontSize: '0.9rem', lineHeight: 1.5 }}>{q}</li>
              ))}
            </ol>
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
