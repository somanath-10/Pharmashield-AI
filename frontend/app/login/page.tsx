'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const roles = [
  { id: 'PATIENT', title: 'Patient', icon: '👤', color: '#10b981', bg: 'rgba(16,185,129,0.1)', path: '/patient' },
  { id: 'PHARMACIST', title: 'Pharmacist', icon: '💊', color: '#3b82f6', bg: 'rgba(59,130,246,0.1)', path: '/pharmacist' },
  { id: 'DOCTOR', title: 'Doctor', icon: '🩺', color: '#6366f1', bg: 'rgba(99,102,241,0.1)', path: '/doctor' },
  { id: 'ADMIN', title: 'Admin', icon: '⚙️', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', path: '/admin' },
];

export default function LoginPage() {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = () => {
    if (!selectedRole) return;
    const role = roles.find(r => r.id === selectedRole);
    if (role) {
      // For MVP, we just simulate login by redirecting
      // In a real app, we'd set a session/token here
      router.push(role.path);
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
            Select your role to access the PharmaShield portal
          </p>
        </div>

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
              style={{
                background: selectedRole === role.id ? role.bg : 'rgba(255,255,255,0.03)',
                border: `1px solid ${selectedRole === role.id ? role.color : 'rgba(255,255,255,0.08)'}`,
                borderRadius: '12px',
                padding: '20px 16px',
                cursor: 'pointer',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px',
                opacity: selectedRole && selectedRole !== role.id ? 0.6 : 1,
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
          disabled={!selectedRole}
          className={`btn-primary ${selectedRole ? 'pulse-glow' : 'btn-disabled'}`}
          style={{ 
            width: '100%', 
            justifyContent: 'center', 
            height: '48px',
            fontSize: '1rem',
            background: selectedRole 
              ? roles.find(r => r.id === selectedRole)?.color 
              : 'rgba(255,255,255,0.05)'
          }}
        >
          {selectedRole ? `Enter as ${roles.find(r => r.id === selectedRole)?.title}` : 'Select a Role to Continue'}
        </button>

        <p style={{ marginTop: '24px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          This is an MVP simulator. No password is required for demonstration.
        </p>
      </div>
    </div>
  );
}
