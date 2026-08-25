"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  TrendingUp, 
  Sparkles, 
  Award, 
  ShieldAlert, 
  Activity,
  Layers
} from "lucide-react";

const navItems = [
  { href: "/", label: "Executive Dashboard", icon: BarChart3 },
  { href: "/forecast", label: "Forecast Studio", icon: TrendingUp },
  { href: "/explainability", label: "SHAP Explainability", icon: Sparkles },
  { href: "/performance", label: "Model Leaderboard", icon: Award },
  { href: "/monitoring", label: "Drift & Health", icon: ShieldAlert },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-slate-900 border-b border-slate-800 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 p-2 rounded-lg text-white">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-100 tracking-tight">
                Demand<span className="text-indigo-400">IQ</span> Platform
              </span>
              <span className="ml-2 text-xs px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-mono border border-indigo-800">
                Phase 1–7 Live
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
