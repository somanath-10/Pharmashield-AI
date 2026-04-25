import Link from 'next/link';

const roles = [
  {
    title: 'Patient',
    path: '/patient',
    icon: '👤',
    cls: 'patient',
    badge: { bg: 'rgba(16,185,129,0.12)', color: '#34d399', label: 'Patient' },
    description: 'Upload prescriptions and lab reports. Get simple, safe explanations in plain language.',
    features: ['Prescription explanation', 'Lab report summary', 'Doctor Q&A checklist'],
  },
  {
    title: 'Pharmacist',
    path: '/pharmacist',
    icon: '💊',
    cls: 'pharmacist',
    badge: { bg: 'rgba(59,130,246,0.12)', color: '#60a5fa', label: 'Pharmacist' },
    description: 'Verify prescriptions, check Schedule H/X compliance, and explore therapeutic substitutions.',
    features: ['Dispensing compliance', 'Schedule H/X check', 'Counseling points'],
  },
  {
    title: 'Doctor',
    path: '/doctor',
    icon: '🩺',
    cls: 'doctor',
    badge: { bg: 'rgba(99,102,241,0.12)', color: '#a5b4fc', label: 'Doctor' },
    description: 'Get summarized patient case highlights from uploaded documents and lab reports.',
    features: ['Clinical summary', 'Lab abnormalities', 'Follow-up checklist'],
  },
  {
    title: 'Admin',
    path: '/admin',
    icon: '⚙️',
    cls: 'admin',
    badge: { bg: 'rgba(245,158,11,0.12)', color: '#fbbf24', label: 'Admin' },
    description: 'Monitor case workflows, high-risk flags, and system-wide usage analytics.',
    features: ['Case tracking', 'Risk monitoring', 'Role analytics'],
  },
];

export default function RoleSelection() {
  return (
    <div>
      {/* Hero */}
      <div style={{ textAlign: 'center', marginBottom: '56px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(59,130,246,0.1)',
          border: '1px solid rgba(59,130,246,0.2)',
          borderRadius: '999px',
          padding: '6px 18px',
          fontSize: '0.8rem',
          color: '#60a5fa',
          fontWeight: 600,
          marginBottom: '24px',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
        }}>
          <span>🇮🇳</span> India-First Healthcare AI
        </div>
        <h1 style={{
          fontSize: 'clamp(2rem, 5vw, 3rem)',
          fontWeight: 900,
          lineHeight: 1.15,
          background: 'linear-gradient(135deg, #f0f6ff 30%, #94a3b8)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '16px',
        }}>
          PharmaShield India AI
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: '560px', margin: '0 auto', lineHeight: 1.6 }}>
          Role-based AI assistant for patients, doctors, and pharmacists — safe, simple, and regulatory-aligned.
        </p>
      </div>

      {/* Role Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
        {roles.map((role) => (
          <Link key={role.title} href={role.path} style={{ textDecoration: 'none' }}>
            <div className={`role-card ${role.cls}`} style={{ height: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>
                <span style={{ fontSize: '2.4rem' }}>{role.icon}</span>
                <span style={{
                  background: role.badge.bg,
                  color: role.badge.color,
                  borderRadius: '999px',
                  padding: '3px 12px',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                }}>{role.badge.label}</span>
              </div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
                {role.title}
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.6, marginBottom: '16px' }}>
                {role.description}
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {role.features.map((f) => (
                  <li key={f} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <span style={{ color: role.badge.color, fontSize: '0.7rem' }}>✦</span> {f}
                  </li>
                ))}
              </ul>
            </div>
          </Link>
        ))}
      </div>

      {/* Bottom notice */}
      <div style={{ textAlign: 'center', marginTop: '48px' }}>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
          All AI outputs include mandatory professional review prompts. This is a decision-support tool, not a replacement for clinical judgment.
        </p>
      </div>
    </div>
  );
}
