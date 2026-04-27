'use client';

export default function LogoutButton() {
  const handleLogout = () => {
    document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    window.location.href = "/login";
  };

  return (
    <button 
      onClick={handleLogout}
      style={{ 
        background: 'rgba(255,255,255,0.06)',
        color: 'var(--text-primary)',
        fontSize: '0.75rem',
        fontWeight: 700,
        padding: '6px 14px',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)',
        cursor: 'pointer',
        transition: 'all 0.2s'
      }}
    >
      Log Out
    </button>
  );
}
