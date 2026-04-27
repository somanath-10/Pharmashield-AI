'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getPharmacistReviewQueue, submitPharmacistReview } from '@/lib/api';

export default function ReviewQueuePage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadQueue = async () => {
    setLoading(true);
    try {
      const res = await getPharmacistReviewQueue();
      setCases(res);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { loadQueue(); }, []);

  const handleReview = async (caseId: string, action: 'VERIFIED' | 'REJECTED') => {
    try {
      await submitPharmacistReview(caseId, { action_taken: action, notes: `Pharmacist marked as ${action}` });
      await loadQueue();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="animate-in" style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📋 Dispensing Review Queue</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Prescriptions requiring pharmacist verification.</p>
        </div>
        <Link href="/pharmacist/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back to Dashboard</Link>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>Loading...</div>
        ) : cases.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>No pending reviews.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px' }}>Date</th>
                <th style={{ padding: '12px 8px' }}>Prescription Case</th>
                <th style={{ padding: '12px 8px' }}>Risk</th>
                <th style={{ padding: '12px 8px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.case_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 8px' }}>{new Date(c.created_at).toLocaleDateString()}</td>
                  <td style={{ padding: '12px 8px', fontWeight: 600 }}>{c.title}</td>
                  <td style={{ padding: '12px 8px' }}>
                    <span style={{ 
                      color: c.risk_level === 'HIGH' ? '#f87171' : '#34d399', 
                      background: c.risk_level === 'HIGH' ? 'rgba(239,68,68,0.1)' : 'rgba(52,211,153,0.1)',
                      padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem' 
                    }}>
                      {c.risk_level || 'UNKNOWN'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                     <button onClick={() => handleReview(c.case_id, 'VERIFIED')} style={{ background: 'rgba(52,211,153,0.15)', color: '#34d399', border: '1px solid rgba(52,211,153,0.3)', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', marginRight: '8px' }}>Verify</button>
                     <button onClick={() => handleReview(c.case_id, 'REJECTED')} style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>Do Not Dispense</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}