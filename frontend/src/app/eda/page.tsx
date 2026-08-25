"use client";

import { useState } from "react";
import { ChartSpline, Calendar, TrendingUp, Store, Package } from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const seasonalityData = [
  { day: "Mon", units: 820 },
  { day: "Tue", units: 910 },
  { day: "Wed", units: 890 },
  { day: "Thu", units: 980 },
  { day: "Fri", units: 1120 },
  { day: "Sat", units: 1350 },
  { day: "Sun", units: 990 },
];

const trendData = [
  { date: "Jan 25", demand: 3200 },
  { date: "Feb 25", demand: 3450 },
  { date: "Mar 25", demand: 3800 },
  { date: "Apr 25", demand: 3600 },
  { date: "May 25", demand: 4100 },
  { date: "Jun 25", demand: 4350 },
  { date: "Jul 25", demand: 4600 },
  { date: "Aug 25", demand: 4900 },
];

export default function EDAPage() {
  const [granularity, setGranularity] = useState<"daily" | "weekly" | "monthly">("monthly");

  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#F5F7FA] flex items-center gap-2">
            <ChartSpline className="w-6 h-6 text-indigo-400" />
            Exploratory Data Analysis (EDA)
          </h1>
          <p className="text-[#9AA2B1] text-xs mt-1">
            High-level business demand trends, weekly seasonality, store rankings, and product performance.
          </p>
        </div>
      </div>

      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Total Historical Units</span>
          <div className="text-2xl font-extrabold text-[#F5F7FA] mt-2 font-mono">125,420</div>
          <p className="text-xs text-[#626A78] mt-1">Aggregated sales volume</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Historical Descriptive Revenue*</span>
          <div className="text-2xl font-extrabold text-[#F5F7FA] mt-2 font-mono">$2,480,500</div>
          <p className="text-xs text-[#626A78] mt-1">*Descriptive past metric only</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Average Daily Demand</span>
          <div className="text-2xl font-extrabold text-[#F5F7FA] mt-2 font-mono">118 units</div>
          <p className="text-xs text-[#626A78] mt-1">Per store/product series</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Demand Volatility</span>
          <div className="text-2xl font-extrabold text-indigo-400 mt-2 font-mono">14.2%</div>
          <p className="text-xs text-[#626A78] mt-1">Standard deviation / mean</p>
        </div>
      </div>

      {/* Demand Trend Chart */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-[#F5F7FA]">Macro Demand Trend Over Time</h2>
            <p className="text-xs text-[#9AA2B1]">Aggregated historical demand trajectory</p>
          </div>

          <div className="flex items-center gap-1 bg-[#08090B] p-1 rounded-lg border border-white/10 text-xs font-mono">
            {(["daily", "weekly", "monthly"] as const).map((g) => (
              <button
                key={g}
                onClick={() => setGranularity(g)}
                className={`px-3 py-1 rounded capitalize font-semibold transition-all ${
                  granularity === g ? "bg-indigo-600 text-white" : "text-[#9AA2B1] hover:text-[#F5F7FA]"
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="edaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1B1F26" />
              <XAxis dataKey="date" stroke="#626A78" fontSize={12} />
              <YAxis stroke="#626A78" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: "#101216", borderColor: "rgba(255,255,255,0.1)", color: "#F5F7FA" }} />
              <Area type="monotone" dataKey="demand" stroke="#6366f1" strokeWidth={2} fill="url(#edaGrad)" name="Historical Units" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Seasonality Chart */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-[#F5F7FA]">Day-of-Week Seasonality Pattern</h2>
            <p className="text-xs text-[#9AA2B1]">Weekly demand distribution</p>
          </div>
          <span className="text-xs font-mono text-[#9AA2B1]">
            Peak: <strong className="text-emerald-400">Saturday</strong> | Lowest: <strong className="text-rose-400">Monday</strong>
          </span>
        </div>

        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={seasonalityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1B1F26" />
              <XAxis dataKey="day" stroke="#626A78" fontSize={12} />
              <YAxis stroke="#626A78" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: "#101216", borderColor: "rgba(255,255,255,0.1)", color: "#F5F7FA" }} />
              <Bar dataKey="units" fill="#818cf8" radius={[4, 4, 0, 0]} name="Avg Units" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Store & Product Performance Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Store Performance */}
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
          <h2 className="text-base font-bold text-[#F5F7FA]">Store Ranking & Growth</h2>
          <div className="space-y-3 font-mono text-xs">
            {[
              { store: "Store 17", demand: "194,200", growth: "+18.4%", status: "↑" },
              { store: "Store 12", demand: "181,400", growth: "+12.1%", status: "↑" },
              { store: "Store 03", demand: "98,100", growth: "-4.2%", status: "↓" },
            ].map((s) => (
              <div key={s.store} className="bg-[#15181D] p-3 rounded-lg border border-white/5 flex justify-between items-center">
                <div>
                  <span className="font-bold text-[#F5F7FA]">{s.store}</span>
                  <span className="text-[#626A78] block">{s.demand} units</span>
                </div>
                <span className={`font-bold ${s.growth.startsWith("+") ? "text-emerald-400" : "text-rose-400"}`}>
                  {s.status} {s.growth}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Product Performance */}
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
          <h2 className="text-base font-bold text-[#F5F7FA]">Product Ranking & Category</h2>
          <div className="space-y-3 font-mono text-xs">
            {[
              { product: "Product A", units: "120,400", category: "Electronics", growth: "+22.1%" },
              { product: "Product B", units: "98,200", category: "Home", growth: "+11.3%" },
              { product: "Product C", units: "72,100", category: "Grocery", growth: "-2.1%" },
            ].map((p) => (
              <div key={p.product} className="bg-[#15181D] p-3 rounded-lg border border-white/5 flex justify-between items-center">
                <div>
                  <span className="font-bold text-[#F5F7FA]">{p.product}</span>
                  <span className="text-[#626A78] block">{p.units} units ({p.category})</span>
                </div>
                <span className={`font-bold ${p.growth.startsWith("+") ? "text-emerald-400" : "text-rose-400"}`}>
                  {p.growth}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
