'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAdminAuditLogs } from '@/lib/api';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await getAdminAuditLogs(20);
        setLogs(res.logs || []);
      } catch (e) { console.error(e); }
      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="animate-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>📜 System Audit Logs</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Immutable ledger of system mutations and API ingests.</p>
        </div>
        <Link href="/admin/dashboard" style={{ color: '#60a5fa', textDecoration: 'none' }}>← Back</Link>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>Loading logs...</div>
        ) : logs.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '20px' }}>No audit logs found.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', fontFamily: 'monospace' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px' }}>Timestamp</th>
                <th style={{ padding: '12px 8px' }}>Action</th>
                <th style={{ padding: '12px 8px' }}>Actor</th>
                <th style={{ padding: '12px 8px' }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log: any) => (
                <tr key={log.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>{new Date(log.created_at).toLocaleString()}</td>
                  <td style={{ padding: '12px 8px', color: '#60a5fa' }}>{log.action}</td>
                  <td style={{ padding: '12px 8px' }}>{log.user_id}</td>
                  <td style={{ padding: '12px 8px', color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '300px' }}>{JSON.stringify(log.metadata)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}