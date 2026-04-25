'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function DoctorDashboard() {
  const [text, setText] = useState('Patient has elevated HbA1c 8.2. Currently on Metformin. Complaints of frequent urination and fatigue.');
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setAnalysis(null);
    try {
      const caseRes = await fetch('http://localhost:8000/api/cases', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'DOCTOR', case_type: 'DOCTOR_CASE_SUMMARY', title: 'Patient Review', query: 'Summarize the case' }),
      });
      const { case_id } = await caseRes.json();
      await fetch(`http://localhost:8000/api/cases/${case_id}/documents`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_type: 'LAB_REPORT', file_name: 'files.pdf', mock_extracted_text: text }),
      });
      const res = await fetch(`http://localhost:8000/api/cases/${case_id}/analyze`, { method: 'POST' });
      const data = await res.json();
      setAnalysis(data.result);
    } catch {}
    setLoading(false);
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
        <Link href="/" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Input */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
            📁 Patient File Content
          </label>
          <textarea className="premium-input" style={{ height: '140px', marginBottom: '16px', fontFamily: 'monospace', fontSize: '0.82rem' }} value={text} onChange={e => setText(e.target.value)} />
          <button className={`btn-primary btn-doctor${loading ? ' btn-disabled' : ''}`} style={{ width: '100%', justifyContent: 'center' }} onClick={handleAnalyze} disabled={loading}>
            {loading ? '⏳ Synthesizing...' : '📊 Generate Clinical Summary'}
          </button>
        </div>

        {/* Output */}
        {analysis ? (
          <div className="glass-card animate-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Clinical Overview</h4>
              <p style={{ color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.7, whiteSpace: 'pre-line' }}>{analysis.clinical_summary}</p>
            </div>
            <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '16px' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>✅ Follow-up Points</h4>
              <ol style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {analysis.follow_up_points?.map((item: string, i: number) => (
                  <li key={i} style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>{item}</li>
                ))}
              </ol>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: 'auto' }}>{analysis.disclaimer}</p>
          </div>
        ) : (
          <div className="glass-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed rgba(255,255,255,0.08)' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textAlign: 'center' }}>
              🩺 Generate a clinical summary to see insights here
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
