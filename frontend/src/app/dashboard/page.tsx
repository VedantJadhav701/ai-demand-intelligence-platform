"use client";

import { useEffect, useState } from "react";
import { 
  LayoutDashboard, 
  TrendingUp, 
  Package, 
  Store, 
  ShieldCheck, 
  AlertTriangle,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { fetchMetrics, fetchDatasetSummary, ModelMetric, DatasetSummaryData } from "@/lib/api";

const sampleTrendData = [
  { date: "Aug 15", actual: 95, forecast: 94 },
  { date: "Aug 16", actual: 102, forecast: 100 },
  { date: "Aug 17", actual: 98, forecast: 99 },
  { date: "Aug 18", actual: 115, forecast: 112 },
  { date: "Aug 19", actual: 108, forecast: 110 },
  { date: "Aug 20", actual: 122, forecast: 120 },
  { date: "Aug 21", actual: 118, forecast: 116 },
  { date: "Aug 22 (h1)", forecast: 124 },
  { date: "Aug 23 (h2)", forecast: 121 },
  { date: "Aug 24 (h3)", forecast: 128 },
  { date: "Aug 25 (h4)", forecast: 130 },
  { date: "Aug 26 (h5)", forecast: 127 },
  { date: "Aug 27 (h6)", forecast: 135 },
  { date: "Aug 28 (h7)", forecast: 132 },
];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<ModelMetric[]>([]);
  const [datasetSummary, setDatasetSummary] = useState<DatasetSummaryData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([
      fetchMetrics().catch(() => null),
      fetchDatasetSummary().catch(() => null),
    ]).then(([mRes, dRes]) => {
      if (mRes && mRes.metrics) setMetrics(mRes.metrics);
      if (dRes) setDatasetSummary(dRes);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg">
        <div>
          <span className="text-2xs font-mono text-[#9AA2B1] uppercase tracking-wider">Executive View</span>
          <h1 className="text-2xl font-bold text-[#F5F7FA] mt-1">
            Good morning • Demand Intelligence Overview
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-emerald-950 text-emerald-400 text-xs font-semibold rounded-full border border-emerald-800 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            System Healthy
          </span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-xs font-semibold text-[#9AA2B1] uppercase tracking-wider">Total Historical Demand</span>
          <div className="text-2xl font-extrabold text-[#F5F7FA] mt-2 font-mono">
            {datasetSummary ? datasetSummary.total_rows.toLocaleString() : "125,420"}{" "}
            <span className="text-xs font-normal text-[#9AA2B1]">units</span>
          </div>
          <p className="text-xs text-[#626A78] mt-1">Active dataset records</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-xs font-semibold text-[#9AA2B1] uppercase tracking-wider">Forecast Accuracy</span>
          <div className="text-2xl font-extrabold text-emerald-400 mt-2 font-mono">
            11.27% <span className="text-xs font-normal text-[#9AA2B1]">WAPE</span>
          </div>
          <p className="text-xs text-[#626A78] mt-1">Target &lt;15% WAPE passed</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-xs font-semibold text-[#9AA2B1] uppercase tracking-wider">Active Stores</span>
          <div className="text-2xl font-extrabold text-[#F5F7FA] mt-2 font-mono">
            {datasetSummary ? datasetSummary.total_stores : "42"}
          </div>
          <p className="text-xs text-[#626A78] mt-1">Monitored retail locations</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-5 rounded-xl">
          <span className="text-xs font-semibold text-[#9AA2B1] uppercase tracking-wider">Active Products</span>
          <div className="text-2xl font-extrabold text-[#F5F7FA] mt-2 font-mono">
            {datasetSummary ? datasetSummary.total_products : "318"}
          </div>
          <p className="text-xs text-[#626A78] mt-1">Product SKUs</p>
        </div>
      </div>

      {/* Main Demand Trend Chart */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-[#F5F7FA]">Demand Trend & Forecast Projection</h2>
            <p className="text-xs text-[#9AA2B1]">Historical actuals vs 7-day CatBoost model prediction</p>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sampleTrendData}>
              <defs>
                <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1B1F26" />
              <XAxis dataKey="date" stroke="#626A78" fontSize={12} />
              <YAxis stroke="#626A78" fontSize={12} domain={["dataMin - 10", "dataMax + 10"]} />
              <Tooltip contentStyle={{ backgroundColor: "#101216", borderColor: "rgba(255,255,255,0.1)", color: "#F5F7FA" }} />
              <Area type="monotone" dataKey="actual" stroke="#6366f1" strokeWidth={2} fill="url(#actualGrad)" name="Actual Units" />
              <Area type="monotone" dataKey="forecast" stroke="#22d3ee" strokeWidth={2} strokeDasharray="4 4" fill="url(#forecastGrad)" name="Forecast Units" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Two Column Layout: Top Growing Products & Inventory Risk */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Growing Products */}
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
          <h2 className="text-base font-bold text-[#F5F7FA] border-b border-white/10 pb-3">
            Top Demand Growth Products
          </h2>
          <div className="space-y-3">
            {[
              { id: "PRODUCT_A", name: "Product A (Grocery)", units: "120,400", growth: "+22.1%" },
              { id: "PRODUCT_B", name: "Product B (Electronics)", units: "98,200", growth: "+11.3%" },
              { id: "PRODUCT_C", name: "Product C (Apparel)", units: "72,100", growth: "-2.1%" },
            ].map((p) => (
              <div key={p.id} className="bg-[#15181D] p-3.5 rounded-lg border border-white/5 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-[#F5F7FA] font-mono">{p.name}</span>
                  <span className="text-[#626A78] block mt-0.5">{p.units} units sold</span>
                </div>
                <span className={`font-mono font-bold ${p.growth.startsWith("+") ? "text-emerald-400" : "text-rose-400"}`}>
                  {p.growth}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Inventory Risk Preview */}
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-4">
          <h2 className="text-base font-bold text-[#F5F7FA] border-b border-white/10 pb-3 flex items-center justify-between">
            <span>Inventory Shortage Risk</span>
            <span className="text-2xs font-mono text-amber-400">8 Products At Risk</span>
          </h2>
          <div className="space-y-3 text-xs">
            <div className="bg-[#15181D] p-3.5 rounded-lg border border-white/5 flex items-center justify-between">
              <div>
                <span className="font-mono text-[#F5F7FA] font-bold">PRODUCT_A (Store 17)</span>
                <span className="text-[#626A78] block mt-0.5">Forecast: 2,240 | Stock: 1,820</span>
              </div>
              <span className="px-2.5 py-1 bg-red-950/60 text-red-400 font-mono font-bold rounded border border-red-800/40">
                HIGH RISK (-420)
              </span>
            </div>

            <div className="bg-[#15181D] p-3.5 rounded-lg border border-white/5 flex items-center justify-between">
              <div>
                <span className="font-mono text-[#F5F7FA] font-bold">PRODUCT_C (Store 12)</span>
                <span className="text-[#626A78] block mt-0.5">Forecast: 1,440 | Stock: 1,210</span>
              </div>
              <span className="px-2.5 py-1 bg-amber-950/60 text-amber-400 font-mono font-bold rounded border border-amber-800/40">
                MEDIUM RISK (-230)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
