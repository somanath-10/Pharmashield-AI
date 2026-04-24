import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import { Providers } from "@/app/providers";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "PharmaShield AI",
  description: "Memory-aware multi-agent pharmacy operations intelligence platform."
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            <header className="mb-8 flex flex-col gap-4 rounded-[2rem] border border-white/70 bg-white/70 p-5 shadow-panel backdrop-blur md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slateblue">
                  Pharmacy Operations Intelligence
                </p>
                <Link href="/" className="text-3xl font-semibold text-ink">
                  PharmaShield AI
                </Link>
              </div>
              <nav className="flex flex-wrap gap-3 text-sm">
                <Link href="/" className="rounded-full bg-sand px-4 py-2 hover:bg-mint">
                  Home
                </Link>
                <Link href="/cases" className="rounded-full bg-sand px-4 py-2 hover:bg-mint">
                  Cases
                </Link>
                <Link href="/dashboard" className="rounded-full bg-sand px-4 py-2 hover:bg-mint">
                  Dashboard
                </Link>
                <Link href="/ingest" className="rounded-full bg-sand px-4 py-2 hover:bg-mint">
                  Ingest
                </Link>
              </nav>
            </header>
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
