"use client";

import { useEffect, useState } from "react";
import { ShieldAlert, CheckCircle2, AlertTriangle, RefreshCw, Activity, Zap, BarChart2 } from "lucide-react";
import { fetchDriftReport, DriftReportResponseData } from "@/lib/api";

export default function DriftMonitoringPage() {
  const [driftData, setDriftData] = useState<DriftReportResponseData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchDriftReport();
      setDriftData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load drift monitoring report.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-7 h-7 text-cyan-400" />
            Model Drift & Residual Health Monitoring
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Statistical PSI drift tracking, Kolmogorov-Smirnov distribution tests, and residual forecast bias.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-all shadow-md disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh Health Report
        </button>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 p-4 rounded-lg flex items-center gap-3 text-sm">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="bg-slate-900 border border-slate-800 p-12 rounded-xl text-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-cyan-400" />
          <p className="text-sm">Executing statistical drift tests (PSI & KS-test)...</p>
        </div>
      ) : driftData ? (
        <div className="space-y-8">
          {/* Status Alert Summary */}
          <div className={`p-6 rounded-xl border shadow-lg ${
            driftData.overall_status === "HEALTHY"
              ? "bg-emerald-950/40 border-emerald-800 text-emerald-200"
              : driftData.overall_status === "WARNING"
              ? "bg-amber-950/40 border-amber-800 text-amber-200"
              : "bg-red-950/40 border-red-800 text-red-200"
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {driftData.overall_status === "HEALTHY" ? (
                  <CheckCircle2 className="w-7 h-7 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-7 h-7 text-amber-400" />
                )}
                <div>
                  <span className="text-xs uppercase font-bold tracking-wider">Overall Model Health Status</span>
                  <h2 className="text-xl font-extrabold">{driftData.overall_status}</h2>
                </div>
              </div>
              <span className="text-xs font-mono bg-slate-900/80 px-3 py-1 rounded border border-slate-800">
                Updated: {new Date(driftData.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <p className="text-xs mt-3 opacity-90">{driftData.summary_message}</p>
          </div>

          {/* Residual & Forecast Bias Cards */}
          {driftData.residual_analysis && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Residual WAPE
                </span>
                <div className="text-2xl font-extrabold text-slate-100 mt-2">
                  {driftData.residual_analysis.wape.toFixed(2)}%
                </div>
                <p className="text-xs text-slate-400 mt-1">Sample MAE: {driftData.residual_analysis.mae.toFixed(2)} units</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Normalized Forecast Bias
                </span>
                <div className="text-2xl font-extrabold text-indigo-400 mt-2">
                  {driftData.residual_analysis.forecast_bias.toFixed(3)}
                </div>
                <p className="text-xs text-slate-400 mt-1">Range [-1.0, 1.0] (0 = Unbiased)</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Tracking Signal
                </span>
                <div className="text-2xl font-extrabold text-cyan-400 mt-2">
                  {driftData.residual_analysis.tracking_signal.toFixed(2)}
                </div>
                <p className="text-xs text-slate-400 mt-1">Cum Error / MAD</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Residual Health Status
                </span>
                <div className="text-2xl font-extrabold text-emerald-400 mt-2">
                  {driftData.residual_analysis.status}
                </div>
                <p className="text-xs text-slate-400 mt-1">{driftData.residual_analysis.sample_count} samples evaluated</p>
              </div>
            </div>
          )}

          {/* Feature Drift Table */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Feature Stability & PSI Drift Indicators</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(driftData.feature_drift).map(([featName, featObj]) => (
                <div key={featName} className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold text-slate-100">{featName}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        featObj.status === "NO_DRIFT"
                          ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                          : featObj.status === "MODERATE_DRIFT"
                          ? "bg-amber-950 text-amber-400 border border-amber-800"
                          : "bg-red-950 text-red-400 border border-red-800"
                      }`}>
                        {featObj.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{featObj.message}</p>
                  </div>

                  <div className="text-right">
                    <span className="text-xs text-slate-500 uppercase block">PSI Value</span>
                    <span className="font-mono font-bold text-sm text-slate-200">{featObj.psi.toFixed(4)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
