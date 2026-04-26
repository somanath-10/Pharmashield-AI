'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase, submitFeedback } from '@/lib/api';
import type { AnalyzeResult } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#34d399',
  MEDIUM: '#fbbf24',
  HIGH: '#f87171',
  CRITICAL: '#ef4444',
};

interface PatientAnswer {
  simple_summary?: string;
  what_this_may_mean?: string;
  affordability_guidance?: string;
  scheme_guidance?: string;
  seller_warning?: string;
  medicines_found?: string[];
  lab_values_found?: string[];
  safe_next_steps?: string[];
  warning_signs?: string[];
  questions_to_ask_doctor?: string[];
}

export default function PatientDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Explain my prescription in simple words. Is there a cheaper option?');
  const [drugName, setDrugName] = useState('');
  const [budgetSensitive, setBudgetSensitive] = useState(false);
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
        role: 'PATIENT',
        case_type: 'PATIENT_PRESCRIPTION_EXPLANATION',
        title: file.name,
        query,
      });

      setStep('Uploading & extracting document...');
      await uploadDocument(case_id, file);

      setStep('Running AI analysis...');
      const res = await analyzeCase(case_id, query, {
        drug_name: drugName || undefined,
        budget_sensitive: budgetSensitive,
        purchase_context: 'retail_pharmacy',
        scheme_name: 'PM-JAY',
      });
      setResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Could not reach backend.';
      setError(msg);
    }
    setLoading(false); setStep('');
  };

  const sendFeedback = async (rating: number) => {
    if (!result) return;
    try {
      await submitFeedback(result.case_id, { rating, feedback_text: `Patient rated ${rating}/5` });
      setFeedbackSent(true);
    } catch { /* silent */ }
  };

  const ans = result?.answer as PatientAnswer | undefined;

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>👤</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Patient Assistant</h2>
            <span style={{ background: 'rgba(16,185,129,0.12)', color: '#34d399', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Patient</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Upload your prescription or lab report. We will explain it simply and check affordability.
          </p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      {/* Input */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          📄 Upload Document (PDF or TXT)
        </label>
        <input type="file" accept=".pdf,.txt" onChange={e => e.target.files?.[0] && setFile(e.target.files[0])}
          style={{ marginBottom: '16px', display: 'block', color: 'var(--text-primary)' }} />

        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          💊 Medicine Name (optional — for price/compliance check)
        </label>
        <input type="text" className="premium-input" style={{ marginBottom: '16px' }} value={drugName}
          onChange={e => setDrugName(e.target.value)} placeholder="e.g. Augmentin 625" />

        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          ❓ Your Question
        </label>
        <input type="text" className="premium-input" style={{ marginBottom: '16px' }} value={query}
          onChange={e => setQuery(e.target.value)} placeholder="What do you want to know?" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={budgetSensitive} onChange={e => setBudgetSensitive(e.target.checked)} />
            💰 I am budget-sensitive (check Jan Aushadhi / NPPA prices)
          </label>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button className={`btn-primary btn-patient${loading ? ' btn-disabled' : ''}`}
            onClick={handleAnalyze} disabled={loading || !file}>
            {loading
              ? <><span style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} /> Analyzing...</>
              : '🔍 Analyze Document'}
          </button>
          {step && <span style={{ color: '#a5b4fc', fontSize: '0.85rem' }}>{step}</span>}
          {error && <span style={{ color: '#fca5a5', fontSize: '0.85rem' }}>{error}</span>}
        </div>
      </div>

      {/* Results */}
      {result && ans && (
        <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Risk Badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Risk Level:</span>
            <span style={{ background: `${RISK_COLORS[result.risk_level]}22`, color: RISK_COLORS[result.risk_level], borderRadius: '999px', padding: '4px 16px', fontWeight: 800, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.06em', border: `1px solid ${RISK_COLORS[result.risk_level]}44` }}>
              {result.risk_level}
            </span>
            {(result.agents_run?.length ?? 0) > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Agents: {result.agents_run.join(', ')}</span>
            )}
          </div>

          {/* Mandatory Disclaimer */}
          <div className="disclaimer-box">
            <span style={{ fontWeight: 700 }}>⚠️ Important: </span>{result.mandatory_disclaimer}
          </div>

          {/* Summary */}
          <div className="result-section">
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>📋 Summary</h4>
            <p style={{ color: 'var(--text-primary)', lineHeight: 1.7 }}>{ans.simple_summary}</p>
            {ans.what_this_may_mean && <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>{ans.what_this_may_mean}</p>}
          </div>

          {/* Intel Findings */}
          {(result.intel_findings?.length ?? 0) > 0 && (
            <div className="result-section" style={{ background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>🔎 Intelligence Findings</h4>
              <ul style={{ paddingLeft: '18px', margin: 0, display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {result.intel_findings.map((f, i) => <li key={i} style={{ color: '#fca5a5', fontSize: '0.875rem' }}>{f}</li>)}
              </ul>
            </div>
          )}

          {/* Affordability Guidance */}
          {(ans.affordability_guidance || ans.scheme_guidance) && (
            <div className="result-section" style={{ background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)' }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>💰 Affordability & Scheme Guidance</h4>
              {ans.affordability_guidance && <p style={{ color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.6, marginBottom: '8px' }}>{ans.affordability_guidance}</p>}
              {ans.scheme_guidance && <p style={{ color: '#6ee7b7', fontSize: '0.875rem', lineHeight: 1.6 }}>{ans.scheme_guidance}</p>}
            </div>
          )}

          {/* Seller Warning */}
          {ans.seller_warning && (
            <div className="warning-box">
              <span style={{ fontWeight: 700 }}>🚨 Seller Risk: </span>{ans.seller_warning}
            </div>
          )}

          {/* Medicines & Labs Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {(ans.medicines_found?.length ?? 0) > 0 && (
              <div className="result-section">
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💊 Medicines</h4>
                {ans.medicines_found?.map((m, i) => (
                  <div key={i} className="medicine-pill"><div style={{ fontWeight: 600, color: '#60a5fa' }}>{m}</div></div>
                ))}
              </div>
            )}
            {(ans.lab_values_found?.length ?? 0) > 0 && (
              <div className="result-section">
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>🧪 Lab Findings</h4>
                {ans.lab_values_found?.map((l, i) => (
                  <div key={i} className="lab-pill"><div style={{ fontWeight: 600, color: '#a5b4fc' }}>{l}</div></div>
                ))}
              </div>
            )}
          </div>

          {/* Action Plan */}
          {(result.action_plan?.length ?? 0) > 0 && (
            <div className="result-section">
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>✅ Action Plan</h4>
              <ul style={{ paddingLeft: '20px', color: '#34d399', fontSize: '0.9rem', lineHeight: 1.6, margin: 0 }}>
                {result.action_plan.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </div>
          )}

          {/* Safe Next Steps */}
          {(ans.safe_next_steps?.length ?? 0) > 0 && (
            <div className="result-section">
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>🚀 Safe Next Steps</h4>
              <ul style={{ paddingLeft: '20px', color: '#34d399', fontSize: '0.9rem', lineHeight: 1.6, margin: 0 }}>
                {ans.safe_next_steps?.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}

          {/* Warning Signs */}
          {(ans.warning_signs?.length ?? 0) > 0 && (
            <div className="warning-box">
              <span style={{ fontWeight: 700 }}>🚨 Warning Signs: </span>{ans.warning_signs?.join(' • ')}
            </div>
          )}

          {/* Questions for Doctor */}
          {(ans.questions_to_ask_doctor?.length ?? 0) > 0 && (
            <div className="result-section">
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>💬 Questions for Your Doctor</h4>
              <ol style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px', margin: 0 }}>
                {ans.questions_to_ask_doctor?.map((q, i) => (
                  <li key={i} style={{ color: '#e2e8f0', fontSize: '0.9rem', lineHeight: 1.5 }}>{q}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Citations */}
          {result.citations.length > 0 && (
            <div className="result-section" style={{ background: 'rgba(0,0,0,0.2)' }}>
              <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>📚 Sources</h4>
              {result.citations.map((cit, i) => (
                <div key={i} style={{ fontSize: '0.8rem', borderLeft: '3px solid #4b5563', paddingLeft: '12px', marginBottom: '8px' }}>
                  <div style={{ color: '#9ca3af', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: '#d1d5db' }}>{cit.document_name}</span>
                    {cit.page_number && ` (Page ${cit.page_number})`}
                  </div>
                  <div style={{ fontStyle: 'italic', color: '#cbd5e1' }}>&ldquo;{cit.source_snippet}&rdquo;</div>
                </div>
              ))}
            </div>
          )}

          {/* Feedback */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Was this helpful?</span>
            {feedbackSent ? (
              <span style={{ color: '#34d399', fontSize: '0.85rem' }}>✓ Thank you!</span>
            ) : (
              [5, 4, 3].map(r => (
                <button key={r} onClick={() => sendFeedback(r)}
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '4px 10px', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.8rem' }}>
                  {'⭐'.repeat(r)}
                </button>
              ))
            )}
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
