import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Shield, LayoutDashboard, History, Database } from "lucide-react";

import { Providers } from "@/app/providers";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "PharmaShield India AI",
  description: "Advanced Indian pharmacy operations intelligence platform."
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <Providers>
          <div className="mx-auto min-h-screen max-w-7xl px-4 py-8 sm:px-6 lg:px-10">
            <header className="glass-panel mb-12 flex flex-col gap-6 rounded-3xl p-6 md:flex-row md:items-center md:justify-between border border-white/5">
              <Link href="/" className="flex items-center gap-3 group transition-all">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 to-indigo-500 shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
                  <Shield className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-white">
                    PharmaShield <span className="text-sky-400">India AI</span>
                  </h1>
                  <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                    Operations Intelligence Platform
                  </p>
                </div>
              </Link>

              <nav className="flex flex-wrap items-center gap-2 p-1 rounded-2xl bg-slate-900/50 border border-white/5">
                <NavLink href="/" icon={<History className="w-4 h-4" />} label="Home" />
                <NavLink href="/cases" icon={<History className="w-4 h-4" />} label="Cases" />
                <NavLink href="/dashboard" icon={<LayoutDashboard className="w-4 h-4" />} label="Dashboard" />
                <NavLink href="/ingest" icon={<Database className="w-4 h-4" />} label="Manage Data" />
              </nav>
            </header>
            
            <div className="relative">
              {children}
            </div>
            
            <footer className="mt-20 py-8 border-t border-white/5 text-center">
              <p className="text-sm text-slate-500 font-medium tracking-wide">
                &copy; 2026 PharmaShield India AI. Verified Decision Support Tool.
              </p>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}

function NavLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link 
      href={href} 
      className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-all active:scale-95"
    >
      {icon}
      {label}
    </Link>
  );
}
