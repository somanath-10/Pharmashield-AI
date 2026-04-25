"use client";

import Link from "next/link";
import { MoveRight, Zap, CheckCircle2, ShieldAlert, BadgeInfo } from "lucide-react";
import { motion } from "framer-motion";

import { CaseInput } from "@/components/CaseInput";
import { Card } from "@/components/ui/card";

const modules = [
  {
    title: "Availability & Substitution",
    detail: "Real-time inventory analysis and compliant generic molecule substitution matching.",
    icon: <Zap className="w-6 h-6 text-sky-400" />,
    color: "from-sky-500/20 to-transparent",
    borderColor: "border-sky-500/20"
  },
  {
    title: "Price & Jan Aushadhi",
    detail: "Direct NPPA compliance checks and Jan Aushadhi Kendra affordability assessment.",
    icon: <CheckCircle2 className="w-6 h-6 text-emerald-400" />,
    color: "from-emerald-500/20 to-transparent",
    borderColor: "border-emerald-500/20"
  },
  {
    title: "Quality & Compliance",
    detail: "Automated CDSCO NSQ alert tracking and Schedule H/H1/X compliance validation.",
    icon: <ShieldAlert className="w-6 h-6 text-rose-400" />,
    color: "from-rose-500/20 to-transparent",
    borderColor: "border-rose-500/20"
  }
];

export default function HomePage() {
  return (
    <main className="space-y-16">
      {/* Hero Section */}
      <section className="relative py-12 px-2">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-sky-500/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="max-w-4xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-bold uppercase tracking-widest mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
            </span>
            Memory-Aware Agentic RAG
          </div>
          
          <h1 className="text-6xl md:text-7xl font-extrabold text-white leading-[1.1] tracking-tight">
            Advanced Intelligence for <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-400">
              Indian Pharmacy Operations
            </span>
          </h1>
          
          <p className="mt-8 text-xl text-slate-400 leading-relaxed max-w-2xl font-medium">
            Empower your pharmacy team with AI agents that handle availability, affordability, 
            and complex CDSCO quality alerts with verifiable evidence.
          </p>
          
          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="#case-analyzer"
              className="px-8 py-4 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-2xl transition-all shadow-lg shadow-sky-500/25 flex items-center gap-2 group"
            >
              Analyze New Case
              <MoveRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-2xl transition-all border border-white/5"
            >
              System Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Modules Feed */}
      <section className="grid gap-6 md:grid-cols-3">
        {modules.map((module, index) => (
          <div
            key={module.title}
            className={`glass-panel p-8 rounded-[2.5rem] card-hover border border-white/5 relative overflow-hidden group`}
          >
            <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${module.color} blur-[40px] opacity-50`} />
            <div className="relative z-10">
              <div className="mb-6 p-4 rounded-2xl bg-slate-900/50 w-fit border border-white/5">
                {module.icon}
              </div>
              <h2 className="text-2xl font-bold text-white mb-4">{module.title}</h2>
              <p className="text-slate-400 leading-relaxed text-sm font-medium">{module.detail}</p>
            </div>
            <div className={`absolute bottom-6 right-8 text-[100px] font-black text-white/[0.03] select-none pointer-events-none`}>
              0{index + 1}
            </div>
          </div>
        ))}
      </section>

      {/* Analyzer Section */}
      <section id="case-analyzer" className="relative pt-10">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="flex flex-col items-center mb-12 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">Case Analyzer Engine</h2>
            <p className="text-slate-500 text-lg max-w-xl">
                Submit a pharmacy query to trigger coordinated agent research through current CDSCO, NPPA, and Jan Aushadhi data stores.
            </p>
        </div>
        <CaseInput />
      </section>
    </main>
  );
}
