'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase, submitFeedback } from '@/lib/api';
import type { AnalyzeResult } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444',
};

interface DoctorAnswer {
  case_summary?: string;
  medicines_identified?: string[];
  lab_highlights?: string[];
  pharmacist_flags?: string[];
  affordability_context?: string[];
  patient_questions?: string[];
  follow_up_considerations?: string[];
  professional_review_note?: string;
}

export default function DoctorDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Summarize the patient case and note any affordability concerns.');
  const [drugName, setDrugName] = useState('');
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('');
  const [error, setError] = useState('');
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleAnalyze = async () => {
    if (!file) { setError('Please select a file first.'); return; }
    setLoading(true); setError(''); setResult(null); setFeedbackSent(false);

    try {
      setStep('Creating case...');
      const { case_id } = await createCase({
        role: 'DOCTOR',
        case_type: 'DOCTOR_CASE_SUMMARY',
        title: file.name,
        query,
      });

      setStep('Uploading patient documents...');
      await uploadDocument(case_id, file);

      setStep('Synthesizing clinical summary...');
      const res = await analyzeCase(case_id, query, {
        drug_name: drugName || undefined,
        budget_sensitive: true,
      });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error communicating with server.');
    }
    setLoading(false); setStep('');
  };

  const sendFeedback = async (rating: number) => {
    if (!result) return;
    try {
      await submitFeedback(result.case_id, { rating, feedback_text: `Doctor rated ${rating}/5` });
      setFeedbackSent(true);
    } catch { /* silent */ }
  };

  const ans = result?.answer as DoctorAnswer | undefined;

  return (
    <div className="animate-in" style={{ maxWidth: '920px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>🩺</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Doctor Dashboard</h2>
            <span style={{ background: 'rgba(99,102,241,0.12)', color: '#a5b4fc', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Doctor</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Review summarized patient case highlights, pharmacist flags, and clinical follow-up points.</p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '20px' }}>
        {/* Input */}
        <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📁 Upload Patient Document</label>
            <input type="file" accept=".pdf,.txt" onChange={e => e.target.files?.[0] && setFile(e.target.files[0])}
              style={{ display: 'block', color: 'var(--text-primary)' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>❓ Clinical Query</label>
            <textarea className="premium-input" style={{ height: '80px' }} value={query} onChange={e => setQuery(e.target.value)} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>💊 Primary Drug (optional)</label>
            <input type="text" className="premium-input" value={drugName} onChange={e => setDrugName(e.target.value)} placeholder="e.g. Augmentin 625" />
          </div>

          <button className={`btn-primary btn-doctor${loading ? ' btn-disabled' : ''}`} style={{ width: '100%', justifyContent: 'center' }}
            onClick={handleAnalyze} disabled={loading || !file}>
            {loading ? '⏳ Synthesizing...' : '📊 Generate Clinical Summary'}
          </button>
          {step && <div style={{ color: '#a5b4fc', fontSize: '0.85rem', textAlign: 'center' }}>{step}</div>}
          {error && <div style={{ color: '#fca5a5', fontSize: '0.85rem', textAlign: 'center' }}>{error}</div>}
        </div>

        {/* Output */}
        {result && ans ? (
          <div className="glass-card animate-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto', maxHeight: '80vh' }}>
            {/* Risk Badge */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Risk:</span>
              <span style={{ background: `${RISK_COLORS[result.risk_level]}22`, color: RISK_COLORS[result.risk_level], borderRadius: '999px', padding: '3px 14px', fontWeight: 800, fontSize: '0.8rem', textTransform: 'uppercase', border: `1px solid ${RISK_COLORS[result.risk_level]}44` }}>
                {result.risk_level}
              </span>
            </div>

            {/* Case Summary */}
            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Case Summary</h4>
              <p style={{ color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.7, whiteSpace: 'pre-line' }}>{ans.case_summary}</p>
            </div>

            {/* Medicines & Labs */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              {(ans.medicines_identified?.length ?? 0) > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>💊 Medicines</h4>
                  <ul style={{ paddingLeft: '16px', margin: 0, color: '#60a5fa', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {ans.medicines_identified?.map((m, i) => <li key={i}>{m}</li>)}
                  </ul>
                </div>
              )}
              {(ans.lab_highlights?.length ?? 0) > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>🧪 Lab Highlights</h4>
                  <ul style={{ paddingLeft: '16px', margin: 0, color: '#fbbf24', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {ans.lab_highlights?.map((l, i) => <li key={i}>{l}</li>)}
                  </ul>
                </div>
              )}
            </div>

            {/* Pharmacist Flags */}
            {(ans.pharmacist_flags?.some(f => !f.includes('No pharmacist')) ?? false) && (
              <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', padding: '12px' }}>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>🚨 Pharmacist Flags</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#fca5a5', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.pharmacist_flags?.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            )}

            {/* Affordability */}
            {(ans.affordability_context?.some(a => !a.includes('No specific')) ?? false) && (
              <div style={{ background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', padding: '12px' }}>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>💰 Affordability Context</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#6ee7b7', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.affordability_context?.map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              </div>
            )}

            {/* Patient Questions */}
            {(ans.patient_questions?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>❓ Patient Questions</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#cbd5e1', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.patient_questions?.map((q, i) => <li key={i} style={{ fontStyle: 'italic' }}>&ldquo;{q}&rdquo;</li>)}
                </ul>
              </div>
            )}

            {/* Follow-up */}
            {(ans.follow_up_considerations?.length ?? 0) > 0 && (
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '14px' }}>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>✅ Follow-up Considerations</h4>
                <ol style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '6px', margin: 0 }}>
                  {ans.follow_up_considerations?.map((item, i) => (
                    <li key={i} style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>{item}</li>
                  ))}
                </ol>
              </div>
            )}

            {/* Professional Note */}
            {ans.professional_review_note && (
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: 'auto' }}>{ans.professional_review_note}</p>
            )}

            {/* Feedback */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Helpful?</span>
              {feedbackSent
                ? <span style={{ color: '#34d399', fontSize: '0.85rem' }}>✓ Thanks!</span>
                : [5, 4, 3].map(r => (
                  <button key={r} onClick={() => sendFeedback(r)}
                    style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '3px 8px', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.75rem' }}>
                    {'⭐'.repeat(r)}
                  </button>
                ))}
            </div>
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
      {result?.citations && result.citations.length > 0 && (
        <div className="glass-card animate-in" style={{ marginTop: '24px', padding: '20px' }}>
          <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>📚 Evidence / Source Documents</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {result.citations.map((cit, i) => (
              <div key={i} style={{ fontSize: '0.85rem', borderLeft: '3px solid #818cf8', paddingLeft: '12px' }}>
                <div style={{ color: '#9ca3af', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: '#d1d5db' }}>{cit.document_name}</span>
                  {cit.page_number && ` (Page ${cit.page_number})`}
                </div>
                <div style={{ fontStyle: 'italic', color: '#cbd5e1' }}>&ldquo;{cit.source_snippet}&rdquo;</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
