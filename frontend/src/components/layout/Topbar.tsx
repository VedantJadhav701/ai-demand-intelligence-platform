"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Database, ShieldCheck, AlertCircle, Circle } from "lucide-react";
import { fetchHealth } from "@/lib/api";

export default function Topbar() {
  const pathname = usePathname();
  const [healthStatus, setHealthStatus] = useState<"healthy" | "degraded" | "error">("healthy");

  useEffect(() => {
    fetchHealth()
      .then((res) => {
        if (res && res.status === "healthy") setHealthStatus("healthy");
        else setHealthStatus("degraded");
      })
      .catch(() => setHealthStatus("error"));
  }, []);

  const getPageTitle = (path: string) => {
    switch (path) {
      case "/": return "Landing Page";
      case "/dashboard": return "Overview Dashboard";
      case "/datasets": return "Dataset Management";
      case "/data-quality": return "Data Quality Health";
      case "/eda": return "Exploratory Data Analysis (EDA)";
      case "/forecast": return "Demand Forecast Studio";
      case "/explainability": return "SHAP Explainability";
      case "/performance": return "Model Leaderboard";
      case "/monitoring": return "Model Health & Drift";
      case "/analyst": return "AI Demand Analyst";
      case "/settings": return "System Settings";
      default: return "Dashboard";
    }
  };

  return (
    <header className="h-16 bg-[#101216] border-b border-white/10 px-6 flex items-center justify-between select-none">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs">
        <span className="text-[#626A78]">AI Demand Intelligence</span>
        <span className="text-[#626A78]">/</span>
        <span className="font-semibold text-[#F5F7FA]">{getPageTitle(pathname)}</span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4 text-xs">
        {/* Active Dataset Pill */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#15181D] border border-white/10 text-[#9AA2B1]">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span>Active: <strong className="text-[#F5F7FA]">sample_data.csv</strong></span>
        </div>

        {/* Backend Status */}
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border ${
          healthStatus === "healthy"
            ? "bg-emerald-950/40 border-emerald-800/60 text-emerald-400"
            : healthStatus === "degraded"
            ? "bg-amber-950/40 border-amber-800/60 text-amber-400"
            : "bg-red-950/40 border-red-800/60 text-red-400"
        }`}>
          <Circle className={`w-2 h-2 fill-current ${
            healthStatus === "healthy" ? "text-emerald-400 animate-pulse" : "text-amber-400"
          }`} />
          <span>
            {healthStatus === "healthy" ? "API Healthy" : healthStatus === "degraded" ? "API Degraded" : "API Offline"}
          </span>
        </div>
      </div>
    </header>
  );
}
