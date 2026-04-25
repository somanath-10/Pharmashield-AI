'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function PharmacistDashboard() {
  const [text, setText] = useState('Patient has prescription for Augmentin 625mg. Valid doctor signature present.');
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setAnalysis(null);
    try {
      const caseRes = await fetch('http://localhost:8000/api/cases', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'PHARMACIST', case_type: 'PHARMACIST_DISPENSING_CHECK', title: 'Dispensing Check', query: 'Verify prescription' }),
      });
      const { case_id } = await caseRes.json();
      await fetch(`http://localhost:8000/api/cases/${case_id}/documents`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_type: 'PRESCRIPTION', file_name: 'rx.pdf', mock_extracted_text: text }),
      });
      const res = await fetch(`http://localhost:8000/api/cases/${case_id}/analyze`, { method: 'POST' });
      const data = await res.json();
      setAnalysis(data.result);
    } catch {}
    setLoading(false);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '780px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>💊</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Pharmacist Assistant</h2>
            <span style={{ background: 'rgba(59,130,246,0.12)', color: '#60a5fa', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing:'0.05em' }}>Pharmacist</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Check dispensing compliance, Schedule H/X status, and patient counseling points.</p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          📋 Prescription / Medicine Details
        </label>
        <textarea className="premium-input" style={{ height: '100px', marginBottom: '20px' }} value={text} onChange={e => setText(e.target.value)} />
        <button className={`btn-primary btn-pharmacist${loading ? ' btn-disabled' : ''}`} onClick={handleAnalyze} disabled={loading}>
          {loading ? '⏳ Checking...' : '✅ Check Compliance'}
        </button>
      </div>

      {analysis && (
        <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="result-section">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>🔬 Dispensing Assessment</h4>
              <span style={{ background: 'rgba(59,130,246,0.12)', color: '#60a5fa', borderRadius: '999px', padding: '2px 10px', fontSize: '0.75rem', fontWeight: 700 }}>{analysis.medicine}</span>
            </div>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {analysis.assessment?.map((item: string, i: number) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                  <span style={{ color: '#60a5fa', marginTop: '2px' }}>›</span>{item}
                </li>
              ))}
            </ul>
          </div>

          <div className="result-section">
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💬 Patient Counseling Points</h4>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {analysis.patient_counseling?.map((item: string, i: number) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                  <span style={{ color: '#34d399', marginTop: '2px' }}>✓</span>{item}
                </li>
              ))}
            </ul>
          </div>

          <div style={{ background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '10px', padding: '14px 18px' }}>
            <span style={{ fontWeight: 700, color: '#f87171', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>⛔ {analysis.disclaimer}</span>
          </div>
        </div>
      )}
    </div>
  );
}
