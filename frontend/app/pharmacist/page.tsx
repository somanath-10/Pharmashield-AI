'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCase, uploadDocument, analyzeCase, submitFeedback } from '@/lib/api';
import type { AnalyzeResult } from '@/lib/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#f87171', CRITICAL: '#ef4444',
};

interface PharmacistAnswer {
  prescription_summary?: string;
  compliance_warnings?: string[];
  nsq_batch_status?: string[];
  price_and_generic_guidance?: string[];
  stock_status?: string[];
  online_seller_risk?: string[];
  substitution_caution?: string;
  patient_counseling_points?: string[];
  pharmacist_review_required?: string;
}

export default function PharmacistDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Verify this prescription for dispensing.');
  const [drugName, setDrugName] = useState('');
  const [batchNumber, setBatchNumber] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [quantityOnHand, setQuantityOnHand] = useState('');
  const [sellerType, setSellerType] = useState('');
  const [prescriptionAvailable, setPrescriptionAvailable] = useState(true);
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
        role: 'PHARMACIST',
        case_type: 'PHARMACIST_DISPENSING_CHECK',
        title: file.name,
        query,
      });

      setStep('Uploading prescription...');
      await uploadDocument(case_id, file);

      setStep('Running compliance & intelligence checks...');
      const res = await analyzeCase(case_id, query, {
        drug_name: drugName || undefined,
        batch_number: batchNumber || undefined,
        manufacturer: manufacturer || undefined,
        quantity_on_hand: quantityOnHand !== '' ? Number(quantityOnHand) : undefined,
        seller_type: sellerType || undefined,
        prescription_available: prescriptionAvailable,
        budget_sensitive: true,
        location_id: 'HYD_STORE_001',
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
      await submitFeedback(result.case_id, { rating, feedback_text: `Pharmacist rated ${rating}/5` });
      setFeedbackSent(true);
    } catch { /* silent */ }
  };

  const ans = result?.answer as PharmacistAnswer | undefined;

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.6rem' }}>💊</span>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Pharmacist Assistant</h2>
            <span style={{ background: 'rgba(59,130,246,0.12)', color: '#60a5fa', borderRadius: '999px', padding: '3px 12px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pharmacist</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Check dispensing compliance, NSQ alerts, stock, seller risk, and NPPA pricing.</p>
        </div>
        <Link href="/login" style={{ textDecoration: 'none' }}>
          <button className="btn-primary btn-sm" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid rgba(255,255,255,0.1)' }}>← Change Role</button>
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: '24px' }}>
        {/* Input Panel */}
        <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>📄 Upload Prescription</label>
            <input type="file" accept=".pdf,.txt" onChange={e => e.target.files?.[0] && setFile(e.target.files[0])}
              style={{ display: 'block', color: 'var(--text-primary)' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>❓ Dispensing Query</label>
            <textarea className="premium-input" style={{ height: '70px' }} value={query} onChange={e => setQuery(e.target.value)} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>💊 Drug Name</label>
            <input type="text" className="premium-input" value={drugName} onChange={e => setDrugName(e.target.value)} placeholder="e.g. Augmentin 625" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px', textTransform: 'uppercase' }}>Batch No.</label>
              <input type="text" className="premium-input" value={batchNumber} onChange={e => setBatchNumber(e.target.value)} placeholder="e.g. PCT2026A" />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px', textTransform: 'uppercase' }}>Qty on Hand</label>
              <input type="number" className="premium-input" value={quantityOnHand} onChange={e => setQuantityOnHand(e.target.value)} placeholder="e.g. 0" />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px', textTransform: 'uppercase' }}>Manufacturer</label>
            <input type="text" className="premium-input" value={manufacturer} onChange={e => setManufacturer(e.target.value)} placeholder="e.g. Example Pharma Ltd" />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px', textTransform: 'uppercase' }}>Seller Type (if online)</label>
            <select className="premium-input" value={sellerType} onChange={e => setSellerType(e.target.value)}
              style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)' }}>
              <option value="">— Not applicable —</option>
              <option value="whatsapp_seller">WhatsApp Seller</option>
              <option value="instagram_seller">Instagram Seller</option>
              <option value="unverified_website">Unverified Website</option>
              <option value="licensed_distributor">Licensed Distributor</option>
            </select>
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={prescriptionAvailable} onChange={e => setPrescriptionAvailable(e.target.checked)} />
            Prescription available
          </label>

          <button className={`btn-primary btn-pharmacist${loading ? ' btn-disabled' : ''}`} style={{ width: '100%', justifyContent: 'center', marginTop: '4px' }}
            onClick={handleAnalyze} disabled={loading || !file}>
            {loading ? '⏳ Checking...' : '✅ Check Compliance & Safety'}
          </button>

          {step && <div style={{ color: '#60a5fa', fontSize: '0.85rem', textAlign: 'center' }}>{step}</div>}
          {error && <div style={{ color: '#fca5a5', fontSize: '0.85rem', textAlign: 'center' }}>{error}</div>}
        </div>

        {/* Output Panel */}
        {result && ans ? (
          <div className="glass-card animate-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto', maxHeight: '80vh' }}>
            {/* Risk */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Risk:</span>
              <span style={{ background: `${RISK_COLORS[result.risk_level]}22`, color: RISK_COLORS[result.risk_level], borderRadius: '999px', padding: '3px 14px', fontWeight: 800, fontSize: '0.8rem', textTransform: 'uppercase', border: `1px solid ${RISK_COLORS[result.risk_level]}44` }}>
                {result.risk_level}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Agents: {result.agents_run.join(', ')}</span>
            </div>

            {/* Prescription Summary */}
            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#60a5fa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>📋 Summary</h4>
              <p style={{ color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.6 }}>{ans.prescription_summary}</p>
            </div>

            {/* Compliance Warnings */}
            {(ans.compliance_warnings?.length ?? 0) > 0 && (
              <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', padding: '12px' }}>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>⚠️ Compliance Warnings</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#fca5a5', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.compliance_warnings?.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              </div>
            )}

            {/* NSQ Status */}
            {(ans.nsq_batch_status?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>🔬 NSQ / Batch Status</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#fde68a', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.nsq_batch_status?.map((n, i) => <li key={i}>{n}</li>)}
                </ul>
              </div>
            )}

            {/* Intel Findings */}
            {(result.intel_findings?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>🔎 Intelligence Findings</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#e2e8f0', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {result.intel_findings.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            )}

            {/* Price & Generic Guidance */}
            {(ans.price_and_generic_guidance?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>💰 Price & Generic Guidance</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#6ee7b7', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.price_and_generic_guidance?.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            )}

            {/* Stock */}
            {(ans.stock_status?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>📦 Stock Status</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#e2e8f0', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.stock_status?.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}

            {/* Seller Risk */}
            {(ans.online_seller_risk?.length ?? 0) > 0 && (
              <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', padding: '12px' }}>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>🚨 Online Seller Risk Flags</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#fca5a5', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.online_seller_risk?.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}

            {/* Substitution Caution */}
            {ans.substitution_caution && (
              <div style={{ background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '6px', padding: '10px' }}>
                <span style={{ fontWeight: 700, color: '#f87171', fontSize: '0.8rem' }}>⚠️ {ans.substitution_caution}</span>
              </div>
            )}

            {/* Counseling Points */}
            {(ans.patient_counseling_points?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>💬 Counseling Points</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#34d399', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ans.patient_counseling_points?.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            )}

            {/* Action Plan */}
            {(result.action_plan?.length ?? 0) > 0 && (
              <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>📋 Action Plan</h4>
                <ul style={{ paddingLeft: '16px', margin: 0, color: '#a5b4fc', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {result.action_plan.map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              </div>
            )}

            {/* Review Required */}
            {ans.pharmacist_review_required && (
              <div style={{ marginTop: 'auto', background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '6px', padding: '10px' }}>
                <span style={{ fontWeight: 700, color: '#f87171', fontSize: '0.75rem', textTransform: 'uppercase' }}>⛔ {ans.pharmacist_review_required}</span>
              </div>
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
              💊 Upload a prescription and run analysis to see compliance & safety insights
            </p>
          </div>
        )}
      </div>

      {/* Citations */}
      {result?.citations && result.citations.length > 0 && (
        <div className="glass-card animate-in" style={{ marginTop: '24px', padding: '20px' }}>
          <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>📚 Prescription Citations</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {result.citations.map((cit, i) => (
              <div key={i} style={{ fontSize: '0.85rem', borderLeft: '3px solid #60a5fa', paddingLeft: '12px' }}>
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
