"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Database, 
  ShieldCheck, 
  ChartSpline, 
  TrendingUp, 
  Package, 
  Store, 
  Sparkles, 
  Cpu, 
  Activity, 
  Bot, 
  Settings,
  Activity as LogoIcon,
  Circle
} from "lucide-react";

interface NavGroup {
  group: string;
  items: {
    href: string;
    label: string;
    icon: any;
    badge?: string;
  }[];
}

const navigation: NavGroup[] = [
  {
    group: "OVERVIEW",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    ],
  },
  {
    group: "DATA",
    items: [
      { href: "/datasets", label: "Datasets", icon: Database },
      { href: "/data-quality", label: "Data Quality", icon: ShieldCheck },
      { href: "/eda", label: "EDA", icon: ChartSpline },
    ],
  },
  {
    group: "FORECASTING",
    items: [
      { href: "/forecast", label: "Forecast Studio", icon: TrendingUp },
    ],
  },
  {
    group: "ANALYTICS",
    items: [
      { href: "/explainability", label: "Explainability", icon: Sparkles },
      { href: "/performance", label: "Model Leaderboard", icon: Cpu },
    ],
  },
  {
    group: "MONITORING",
    items: [
      { href: "/monitoring", label: "Model Health", icon: Activity },
    ],
  },
  {
    group: "AI",
    items: [
      { href: "/analyst", label: "AI Analyst", icon: Bot, badge: "Phase 8" },
    ],
  },
  {
    group: "SYSTEM",
    items: [
      { href: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#101216] border-r border-white/10 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center gap-3 border-b border-white/10">
          <div className="bg-indigo-600 p-1.5 rounded-lg text-white">
            <LogoIcon className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-[#F5F7FA] tracking-tight">
              AI Demand Intelligence
            </h1>
            <span className="text-3xs font-mono text-[#9AA2B1]">Enterprise v1.0</span>
          </div>
        </div>

        {/* Nav Items */}
        <nav className="p-4 space-y-6 overflow-y-auto max-h-[calc(100vh-8rem)]">
          {navigation.map((section) => (
            <div key={section.group} className="space-y-1.5">
              <h3 className="px-3 text-3xs font-bold font-mono text-[#626A78] uppercase tracking-wider">
                {section.group}
              </h3>
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (pathname === "/" && item.href === "/dashboard");
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? "bg-indigo-600/20 text-[#F5F7FA] border border-indigo-500/40 font-semibold"
                        : "text-[#9AA2B1] hover:bg-[#15181D] hover:text-[#F5F7FA]"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-[#626A78]"}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className="text-3xs px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800/40">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>
      </div>

      {/* Environment Status Footer */}
      <div className="p-4 border-t border-white/10 bg-[#08090B]">
        <div className="flex items-center justify-between text-2xs text-[#9AA2B1]">
          <span className="flex items-center gap-1.5 font-medium">
            <Circle className="w-2.5 h-2.5 text-emerald-400 fill-emerald-400 animate-pulse" />
            Environment
          </span>
          <span className="font-mono text-emerald-400 font-semibold">● Production</span>
        </div>
      </div>
    </aside>
  );
}
