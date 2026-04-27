'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const roles = [
  { id: 'PATIENT', title: 'Patient', icon: '👤', color: '#10b981', bg: 'rgba(16,185,129,0.1)', path: '/patient', email: 'patient@demo.com' },
  { id: 'PHARMACIST', title: 'Pharmacist', icon: '💊', color: '#3b82f6', bg: 'rgba(59,130,246,0.1)', path: '/pharmacist', email: 'pharmacist@demo.com' },
  { id: 'DOCTOR', title: 'Doctor', icon: '🩺', color: '#6366f1', bg: 'rgba(99,102,241,0.1)', path: '/doctor', email: 'doctor@demo.com' },
  { id: 'ADMIN', title: 'Admin', icon: '⚙️', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', path: '/admin', email: 'admin@demo.com' },
];

export default function LoginPage() {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async () => {
    if (!selectedRole) return;
    const role = roles.find(r => r.id === selectedRole);
    if (!role) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('username', role.email);
      formData.append('password', 'demo123'); // Password not strictly checked in MVP auto-provision

      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();
      
      // Store token in cookie for SSR and middleware support
      document.cookie = `access_token=${data.access_token}; path=/; max-age=86400; samesite=lax`;

      router.push(role.path);
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to log in. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-in" style={{ 
      minHeight: '80vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="glass-card" style={{ 
        width: '100%', 
        maxWidth: '480px', 
        padding: '40px',
        textAlign: 'center'
      }}>
        <div style={{ marginBottom: '32px' }}>
          <span style={{ fontSize: '3rem', marginBottom: '16px', display: 'block' }}>🛡️</span>
          <h1 style={{ 
            fontSize: '1.8rem', 
            fontWeight: 800, 
            background: 'linear-gradient(135deg, #f0f6ff, #94a3b8)', 
            WebkitBackgroundClip: 'text', 
            WebkitTextFillColor: 'transparent',
            marginBottom: '8px'
          }}>
            Welcome Back
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Select your role to securely access the PharmaShield portal
          </p>
        </div>

        {error && (
          <div style={{ padding: '12px', marginBottom: '24px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', borderRadius: '8px', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gap: '12px', 
          marginBottom: '32px' 
        }}>
          {roles.map((role) => (
            <button
              key={role.id}
              onClick={() => setSelectedRole(role.id)}
              disabled={loading}
              style={{
                background: selectedRole === role.id ? role.bg : 'rgba(255,255,255,0.03)',
                border: `1px solid ${selectedRole === role.id ? role.color : 'rgba(255,255,255,0.08)'}`,
                borderRadius: '12px',
                padding: '20px 16px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px',
                opacity: (selectedRole && selectedRole !== role.id) || loading ? 0.6 : 1,
              }}
            >
              <span style={{ fontSize: '1.8rem' }}>{role.icon}</span>
              <span style={{ 
                fontWeight: 600, 
                fontSize: '0.85rem', 
                color: selectedRole === role.id ? role.color : 'var(--text-primary)' 
              }}>
                {role.title}
              </span>
            </button>
          ))}
        </div>

        <button
          onClick={handleLogin}
          disabled={!selectedRole || loading}
          className={`btn-primary ${selectedRole && !loading ? 'pulse-glow' : 'btn-disabled'}`}
          style={{ 
            width: '100%', 
            justifyContent: 'center', 
            height: '48px',
            fontSize: '1rem',
            background: selectedRole 
              ? roles.find(r => r.id === selectedRole)?.color 
              : 'rgba(255,255,255,0.05)',
            cursor: !selectedRole || loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Authenticating...' : selectedRole ? `Enter as ${roles.find(r => r.id === selectedRole)?.title}` : 'Select a Role to Continue'}
        </button>

        <p style={{ marginTop: '24px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          This is an MVP simulator. Clicking will automatically provision a test account and generate a real JWT session token.
        </p>
      </div>
    </div>
  );
}
