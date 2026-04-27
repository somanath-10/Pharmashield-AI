import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

import LogoutButton from './components/LogoutButton'

export const metadata = {
  title: 'PharmaShield India AI',
  description: 'Role-Based AI Assistant for Patients, Doctors, and Pharmacists',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav style={{
          background: 'rgba(10,15,30,0.8)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          padding: '0 32px',
          height: '60px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.4rem' }}>🛡️</span>
            <span style={{ fontWeight: 800, fontSize: '1.05rem', background: 'linear-gradient(135deg, #60a5fa, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              PharmaShield India AI
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
              Role-Based Healthcare Assistant
            </span>
            <LogoutButton />
          </div>
        </nav>

        <main style={{ maxWidth: '1080px', margin: '0 auto', padding: '40px 24px' }}>
          {children}
        </main>
      </body>
    </html>
  )
}
