'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDoctorMessages, replyToDoctorMessage } from '@/lib/api';

export default function PharmacistQuestionsPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState<Record<string, string>>({});
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const data = await getDoctorMessages();
      setMessages(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load inquiries');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleReply = async (msgId: string) => {
    const text = replyText[msgId];
    if (!text) return;
    try {
      await replyToDoctorMessage(msgId, text);
      setReplyText({ ...replyText, [msgId]: '' });
      await load();
      alert('Reply sent successfully');
    } catch (e: any) {
      alert('Failed to send reply: ' + (e?.message || 'Unknown error'));
    }
  };

  return (
    <div className="animate-in" style={{ maxWidth: '850px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>💬 Pharmacist Inquiries</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Direct queries from dispensing pharmacists regarding prescriptions and patient safety.</p>
        </div>
        <Link href="/doctor/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading inquiries…</div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '24px', color: '#f87171' }}>❌ {error}</div>
      ) : messages.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p>No active inquiries from pharmacists.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {messages.map((m) => (
            <div key={m.message_id} className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>From: {m.sender_role} (ID: {m.sender_id.slice(0,8)})</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{new Date(m.created_at).toLocaleString()}</span>
              </div>
              <p style={{ marginBottom: '20px', lineHeight: 1.5 }}>{m.message}</p>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <input 
                  type="text" 
                  className="premium-input" 
                  placeholder="Type your response..." 
                  value={replyText[m.message_id] || ''} 
                  onChange={(e) => setReplyText({ ...replyText, [m.message_id]: e.target.value })}
                  style={{ flex: 1 }}
                />
                <button 
                  className="btn-primary" 
                  onClick={() => handleReply(m.message_id)}
                  disabled={!replyText[m.message_id]}
                >
                  Send Reply
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}