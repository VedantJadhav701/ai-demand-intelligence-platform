"use client";

import { Settings, Server, Cpu, Database, ShieldCheck, CheckCircle2 } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#F5F7FA] flex items-center gap-2">
            <Settings className="w-6 h-6 text-indigo-400" />
            System Settings & Platform Architecture
          </h1>
          <p className="text-[#9AA2B1] text-xs mt-1">
            API endpoints, MLflow tracking URI, feature store versioning, and environment configurations.
          </p>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Public API Endpoint Card */}
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl space-y-4">
          <h2 className="text-base font-bold text-[#F5F7FA] border-b border-white/10 pb-3 flex items-center gap-2">
            <Server className="w-4 h-4 text-indigo-400" />
            Public API Configuration
          </h2>

          <div className="space-y-3 text-xs font-mono">
            <div>
              <label className="text-[#626A78] uppercase block mb-1 text-3xs">API Base URL (NEXT_PUBLIC_API_URL)</label>
              <input
                type="text"
                readOnly
                value={API_BASE_URL}
                className="w-full bg-[#08090B] border border-white/10 text-indigo-300 rounded-lg px-3 py-2 text-xs"
              />
            </div>

            <div className="flex justify-between py-2 border-b border-white/5">
              <span className="text-[#9AA2B1]">CORS Allowed Origins</span>
              <span className="text-emerald-400 font-bold">Wildcard + *.vercel.app</span>
            </div>

            <div className="flex justify-between py-2 border-b border-white/5">
              <span className="text-[#9AA2B1]">Protocol & Proxy</span>
              <span className="text-[#F5F7FA]">HTTPS / Render Web Service</span>
            </div>
          </div>
        </div>

        {/* ML Machine Learning Infrastructure Card */}
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl space-y-4">
          <h2 className="text-base font-bold text-[#F5F7FA] border-b border-white/10 pb-3 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-amber-400" />
            ML Pipeline Infrastructure
          </h2>

          <div className="space-y-3 text-xs font-mono">
            <div className="flex justify-between py-2 border-b border-white/5">
              <span className="text-[#9AA2B1]">Forecasting Engine</span>
              <span className="text-amber-400 font-bold">CatBoost Multi-Horizon</span>
            </div>

            <div className="flex justify-between py-2 border-b border-white/5">
              <span className="text-[#9AA2B1]">MLflow Tracking URI</span>
              <span className="text-indigo-300 font-bold">file:///app/mlruns</span>
            </div>

            <div className="flex justify-between py-2 border-b border-white/5">
              <span className="text-[#9AA2B1]">Feature Store Version</span>
              <span className="text-[#F5F7FA]">phase4_v1</span>
            </div>

            <div className="flex justify-between py-2 border-b border-white/5">
              <span className="text-[#9AA2B1]">Explainability Engine</span>
              <span className="text-emerald-400 font-bold">TreeSHAP Attributions</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
