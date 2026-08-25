"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Database, Circle, Menu } from "lucide-react";
import { fetchHealth } from "@/lib/api";

interface TopbarProps {
  onOpenMobileSidebar?: () => void;
}

export default function Topbar({ onOpenMobileSidebar }: TopbarProps) {
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
    <header className="h-16 bg-[#101216] border-b border-white/10 px-4 sm:px-6 flex items-center justify-between select-none shrink-0 sticky top-0 z-30">
      {/* Mobile Menu Toggle & Breadcrumb */}
      <div className="flex items-center gap-3 text-xs">
        <button
          onClick={onOpenMobileSidebar}
          className="lg:hidden p-2 text-[#9AA2B1] hover:text-white bg-[#15181D] border border-white/10 rounded-none"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-1.5 text-2xs sm:text-xs">
          <span className="hidden sm:inline text-[#626A78]">AI Demand Intelligence</span>
          <span className="hidden sm:inline text-[#626A78]">/</span>
          <span className="font-bold text-[#F5F7FA] truncate max-w-[160px] sm:max-w-none">
            {getPageTitle(pathname)}
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 text-xs">
        {/* Active Dataset Pill */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 bg-[#15181D] border border-white/10 text-[#9AA2B1] text-2xs">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span>Active: <strong className="text-[#F5F7FA]">sample_data.csv</strong></span>
        </div>

        {/* Backend Status */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 sm:px-3 sm:py-1.5 text-2xs sm:text-xs font-semibold border ${
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
