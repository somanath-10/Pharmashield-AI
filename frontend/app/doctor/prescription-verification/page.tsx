'use client';

import { useState } from 'react';
import Link from 'next/link';
import { generateDoctorPrescription } from '@/lib/api';

export default function PrescriptionVerificationPage() {
  const [formData, setFormData] = useState({ patient_name: '', medicine: '', notes: '' });
  const [medicines, setMedicines] = useState<string[]>([]);
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addMedicine = () => {
    if (formData.medicine.trim()) {
      setMedicines([...medicines, formData.medicine]);
      setFormData({ ...formData, medicine: '' });
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await generateDoctorPrescription({
        patient_name: formData.patient_name,
        medicines: medicines,
        notes: formData.notes
      });
      setResult(res);
    } catch(e: any) { setError(e?.message || 'Failed to generate prescription'); }
    setLoading(false);
  };

  return (
    <div className="animate-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>✍️ e-Prescription Generator</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Generate cryptographically verified e-prescriptions.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        {error && <div style={{ marginBottom: '16px', color: '#f87171' }}>❌ {error}</div>}
        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Patient Name</label>
        <input required type="text" className="premium-input" style={{ marginBottom: '16px' }} value={formData.patient_name} onChange={e => setFormData({...formData, patient_name: e.target.value})} />

        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Add Medicine</label>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input type="text" className="premium-input" style={{ flex: 1 }} value={formData.medicine} onChange={e => setFormData({...formData, medicine: e.target.value})} placeholder="e.g. Amoxicillin 500mg TDS" />
          <button type="button" onClick={addMedicine} className="btn-primary" style={{ background: 'rgba(255,255,255,0.1)', color: 'white' }}>Add</button>
        </div>

        {medicines.length > 0 && (
          <ul style={{ marginBottom: '16px', background: 'rgba(0,0,0,0.2)', padding: '12px 24px', borderRadius: '8px' }}>
            {medicines.map((m, i) => <li key={i} style={{ color: 'var(--text-secondary)', marginBottom: '4px' }}>{m}</li>)}
          </ul>
        )}

        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Clinical Notes</label>
        <textarea className="premium-input" style={{ marginBottom: '24px', height: '80px' }} value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} />

        <button onClick={handleGenerate} className={`btn-primary ${loading ? 'btn-disabled' : ''}`} disabled={loading || medicines.length === 0 || !formData.patient_name} style={{ width: '100%', justifyContent: 'center' }}>
          {loading ? 'Generating...' : 'Sign & Generate Prescription'}
        </button>
      </div>

      {result && (
        <div className="glass-card animate-in" style={{ padding: '24px', borderColor: '#34d399' }}>
           <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '16px', marginBottom: '16px' }}>
             <h3 style={{ color: '#34d399' }}>✅ Verified e-Prescription</h3>
             <span style={{ fontFamily: 'monospace', background: 'rgba(255,255,255,0.1)', padding: '4px 8px', borderRadius: '4px' }}>ID: {result.verification_id}</span>
           </div>
           <p style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}><strong>Doctor:</strong> Dr. {result.doctor_name}</p>
           <p style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}><strong>Patient:</strong> {result.patient}</p>
           <h4 style={{ marginBottom: '8px' }}>Rx:</h4>
           <ul style={{ paddingLeft: '20px', color: 'var(--text-secondary)' }}>
             {result.medicines.map((m: string, i: number) => <li key={i}>{m}</li>)}
           </ul>
        </div>
      )}
    </div>
  );
}