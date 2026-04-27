'use client';

import { useState } from 'react';
import Link from 'next/link';
import { reportSideEffect } from '@/lib/api';

export default function SideEffectsPage() {
  const [formData, setFormData] = useState({ medicine_name: '', reaction: '', severity: 'Mild', timeline: '' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await reportSideEffect({
        case_id: 'draft-' + Date.now(), // Real app would link to an actual case
        ...formData
      });
      setSuccess(true);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>⚠️ Report a Side Effect</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Create an Adverse Drug Reaction (ADR) report.</p>
        </div>
        <Link href="/patient/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {success ? (
        <div className="glass-card" style={{ padding: '32px', textAlign: 'center', borderColor: '#34d399' }}>
          <h3 style={{ color: '#34d399', marginBottom: '16px' }}>✅ Report Submitted Successfully</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Your side effect report has been saved and will be reviewed by a doctor.</p>
          <button className="btn-primary" onClick={() => setSuccess(false)} style={{ margin: '0 auto' }}>Report Another</button>
        </div>
      ) : (
        <form className="glass-card" style={{ padding: '28px' }} onSubmit={handleSubmit}>
          <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Medicine Name</label>
          <input required type="text" className="premium-input" style={{ marginBottom: '16px' }} value={formData.medicine_name} onChange={e => setFormData({...formData, medicine_name: e.target.value})} />

          <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Symptoms / Reaction</label>
          <textarea required className="premium-input" style={{ marginBottom: '16px', height: '80px' }} value={formData.reaction} onChange={e => setFormData({...formData, reaction: e.target.value})} />

          <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Severity</label>
          <select className="premium-input" value={formData.severity} onChange={e => setFormData({...formData, severity: e.target.value})} style={{ marginBottom: '16px', background: 'rgba(255,255,255,0.05)', color: 'white' }}>
            <option value="Mild">Mild</option>
            <option value="Moderate">Moderate</option>
            <option value="Severe">Severe</option>
            <option value="Life-threatening">Life-threatening</option>
          </select>

          {formData.severity === 'Severe' || formData.severity === 'Life-threatening' ? (
             <div style={{ background: 'rgba(239,68,68,0.1)', padding: '12px', borderRadius: '8px', marginBottom: '16px', color: '#fca5a5', fontSize: '0.9rem' }}>
               🚨 Contact a doctor or emergency services urgently.
             </div>
          ) : null}

          <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>When did it start?</label>
          <input required type="text" className="premium-input" style={{ marginBottom: '24px' }} placeholder="e.g., 2 days ago" value={formData.timeline} onChange={e => setFormData({...formData, timeline: e.target.value})} />

          <button type="submit" className={`btn-primary ${loading ? 'btn-disabled' : ''}`} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      )}
    </div>
  );
}