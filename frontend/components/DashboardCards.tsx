"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";
import { Activity, ShieldCheck, AlertCircle, RefreshCw } from "lucide-react";

import type { DashboardSummary } from "@/lib/types";
import { Card } from "@/components/ui/card";

const COLORS = ['#38bdf8', '#818cf8', '#22d3ee', '#fb7185'];

export function DashboardCards({ summary }: { summary: DashboardSummary }) {
  const riskData = Object.entries(summary.risk_counts).map(([name, value]) => ({ name, value }));
  const complianceData = Object.entries(summary.compliance_issues).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <div className="space-y-8">
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard 
          label="Total Analysis" 
          value={summary.total_cases.toString()} 
          icon={<Activity className="w-5 h-5 text-sky-400" />}
          trend="+12% from last week"
        />
        <MetricCard
          label="In-Stock Matches"
          value={summary.shortage_cases.toString()}
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
          trend="85% accuracy"
        />
        <MetricCard
          label="Risk Detections"
          value={summary.supplier_risk_cases.toString()}
          icon={<AlertCircle className="w-5 h-5 text-rose-400" />}
          trend="3 Critical flagged"
        />
        <MetricCard
          label="Agent Trust Score"
          value={`${Math.round(summary.feedback_acceptance_rate * 100)}%`}
          icon={<RefreshCw className="w-5 h-5 text-indigo-400" />}
          trend="Verified by ROI"
        />
      </div>
      
      <div className="grid gap-8 lg:grid-cols-2">
        <div className="glass-panel p-8 rounded-[2.5rem] border-white/5">
          <div className="flex items-center justify-between mb-8">
               <div>
                    <h3 className="text-xl font-bold text-white">Risk Distribution</h3>
                    <p className="text-sm text-slate-500 font-medium mt-1">Cross-agent threat calculation.</p>
               </div>
               <div className="px-3 py-1 rounded-full bg-slate-900 border border-white/5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    Real-time
               </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis hide />
                <Tooltip 
                     contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px' }}
                     cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]} barSize={40}>
                    {riskData.map((entry, index) => (
                         <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-8 rounded-[2.5rem] border-white/5">
          <div className="flex items-center justify-between mb-8">
               <div>
                    <h3 className="text-xl font-bold text-white">Compliance Alerts</h3>
                    <p className="text-sm text-slate-500 font-medium mt-1">Schedule H/X and NSQ failures.</p>
               </div>
               <div className="px-3 py-1 rounded-full bg-slate-900 border border-white/5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    Operational
               </div>
          </div>
          <div className="space-y-5">
            {complianceData.length ? (
              complianceData.map((item, index) => (
                <div key={item.name} className="group">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">{item.name}</span>
                    <span className="text-xs font-black text-sky-400">{item.value} Errors</span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-slate-900 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-500 transition-all duration-1000"
                      style={{ width: `${Math.min(item.value * 20, 100)}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center py-12 text-slate-600">
                    <ShieldCheck className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-sm font-medium">No operational compliance risks identified.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon,
  trend
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  trend: string;
}) {
  return (
    <div className="glass-panel p-7 rounded-[2.5rem] border-white/5 relative overflow-hidden group hover:border-sky-500/30 transition-all">
      <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-2xl bg-slate-950/50 border border-white/5 text-slate-400 group-hover:text-white transition-colors">
               {icon}
          </div>
          <div className="text-[10px] font-black text-emerald-400/80 bg-emerald-500/5 px-2 py-1 rounded-md border border-emerald-500/10">
               LIVE
          </div>
      </div>
      <div className="space-y-1">
        <p className="text-3xl font-black text-white tracking-tight">{value}</p>
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.15em]">{label}</p>
      </div>
      <div className="mt-4 pt-4 border-t border-white/5">
          <p className="text-[10px] font-bold text-slate-400 italic">{trend}</p>
      </div>
    </div>
  );
}
