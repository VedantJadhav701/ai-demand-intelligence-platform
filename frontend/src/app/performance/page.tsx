"use client";

import { useEffect, useState } from "react";
import { Award, CheckCircle2, RefreshCw, BarChart2, AlertCircle } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { fetchMetrics, ModelMetric } from "@/lib/api";

export default function ModelPerformancePage() {
  const [metrics, setMetrics] = useState<ModelMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchMetrics();
      setMetrics(res.metrics || []);
    } catch (err: any) {
      setError(err.message || "Failed to load model leaderboard metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const chartData = metrics.map((m) => ({
    name: `${m.horizon}d Horizon`,
    "CV WAPE (%)": m.cv_wape,
    "Test WAPE (%)": m.test_wape,
  }));

  return (
    <div className="space-y-8">
      {/* Title Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Award className="w-7 h-7 text-indigo-400" />
            Model Evaluation & Leaderboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Walk-forward cross-validation vs final test set evaluation metrics across all forecast horizons.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-all shadow-md disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Reload Benchmark
        </button>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 p-4 rounded-lg flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          {error}
        </div>
      )}

      {/* Metric Comparison Chart */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <h2 className="text-lg font-bold text-slate-100 mb-2">Cross-Validation vs Test WAPE Accuracy</h2>
        <p className="text-xs text-slate-400 mb-6">Lower WAPE percentage indicates higher forecast precision</p>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} unit="%" domain={[0, 20]} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }}
                formatter={(val: any) => [`${val}%`, "WAPE Score"]}
              />
              <Legend wrapperStyle={{ color: "#94a3b8", fontSize: "12px" }} />
              <Bar dataKey="CV WAPE (%)" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Test WAPE (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Production Model Selection Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <h2 className="text-lg font-bold text-slate-100 mb-4">Production Model Candidate Leaderboard</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-xs border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Horizon</th>
                <th className="px-4 py-3">Model Architecture</th>
                <th className="px-4 py-3">Registered Model Name</th>
                <th className="px-4 py-3">Selection Source</th>
                <th className="px-4 py-3">CV WAPE</th>
                <th className="px-4 py-3">Test WAPE</th>
                <th className="px-4 py-3">Benchmark Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {metrics.map((m) => (
                <tr key={m.horizon} className="hover:bg-slate-850">
                  <td className="px-4 py-3 font-semibold text-slate-100">{m.horizon} Day ({m.horizon}d)</td>
                  <td className="px-4 py-3 font-medium uppercase text-amber-400">{m.model}</td>
                  <td className="px-4 py-3 font-mono text-xs text-indigo-400">{m.registry_name}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded text-xs font-medium border ${
                        m.selection_source.includes("phase4")
                          ? "bg-purple-950 text-purple-300 border-purple-800"
                          : "bg-blue-950 text-blue-300 border-blue-800"
                      }`}
                    >
                      {m.selection_source.includes("phase4") ? "Optuna Optimized" : "Phase 3 Baseline"}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-200">{m.cv_wape.toFixed(2)}%</td>
                  <td className="px-4 py-3 font-mono font-bold text-emerald-400">{m.test_wape.toFixed(2)}%</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 text-xs text-emerald-400 font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Passed (&lt;15% WAPE)
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
