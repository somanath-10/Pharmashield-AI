'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createPharmacistADRDraft } from '@/lib/api';

export default function ADRDraftsPage() {
  const [formData, setFormData] = useState({ medicine_name: '', reaction: '', severity: 'Moderate', timeline: '', batch_number: '', patient_age_range: '' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await createPharmacistADRDraft({
        ...formData
      });
      setSuccess(true);
    } catch (e: any) {
      setError(e?.message || 'Failed to create ADR draft');
    }
    setLoading(false);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>⚠️ ADR Drafts</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Draft adverse drug reaction reports for Doctor review.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {success ? (
        <div className="glass-card" style={{ padding: '32px', textAlign: 'center', borderColor: '#34d399' }}>
          <h3 style={{ color: '#34d399', marginBottom: '16px' }}>✅ Draft Sent to Doctor</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>The ADR report has been queued for doctor review.</p>
          <button className="btn-primary" onClick={() => setSuccess(false)} style={{ margin: '0 auto' }}>Draft Another</button>
        </div>
      ) : (
        <form className="glass-card" style={{ padding: '28px' }} onSubmit={handleSubmit}>
          {error && <div style={{ marginBottom: '16px', color: '#f87171' }}>❌ {error}</div>}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Medicine Name</label>
              <input required type="text" className="premium-input" value={formData.medicine_name} onChange={e => setFormData({...formData, medicine_name: e.target.value})} />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Batch Number</label>
              <input type="text" className="premium-input" value={formData.batch_number} onChange={e => setFormData({...formData, batch_number: e.target.value})} />
            </div>
          </div>

          <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Patient Age Range</label>
          <input type="text" className="premium-input" style={{ marginBottom: '16px' }} placeholder="e.g. 45-55" value={formData.patient_age_range} onChange={e => setFormData({...formData, patient_age_range: e.target.value})} />

          <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Observed Reaction</label>
          <textarea required className="premium-input" style={{ marginBottom: '16px', height: '80px' }} value={formData.reaction} onChange={e => setFormData({...formData, reaction: e.target.value})} />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Severity</label>
              <select className="premium-input" value={formData.severity} onChange={e => setFormData({...formData, severity: e.target.value})} style={{ background: 'rgba(255,255,255,0.05)', color: 'white' }}>
                <option value="Mild">Mild</option>
                <option value="Moderate">Moderate</option>
                <option value="Severe">Severe</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Timeline</label>
              <input required type="text" className="premium-input" placeholder="e.g. 1 hour post dose" value={formData.timeline} onChange={e => setFormData({...formData, timeline: e.target.value})} />
            </div>
          </div>

          <button type="submit" className={`btn-primary ${loading ? 'btn-disabled' : ''}`} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? 'Drafting...' : 'Push Draft to Doctor'}
          </button>
        </form>
      )}
    </div>
  );
}