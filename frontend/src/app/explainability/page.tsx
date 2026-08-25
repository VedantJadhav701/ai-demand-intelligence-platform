"use client";

import { useEffect, useState } from "react";
import { Sparkles, ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";
import { postExplain, ExplainResponseData } from "@/lib/api";

export default function ExplainabilityPage() {
  const [horizon, setHorizon] = useState<number>(7);
  const [explainData, setExplainData] = useState<ExplainResponseData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadExplanation = async (h: number) => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        horizon: h,
        store_id: "STORE_17",
        product_id: "PRODUCT_A",
        date: "2026-08-25",
        features: {
          price: 19.99,
          discount: 0.0,
          promotion: 1,
          lag_1: 42.0,
          lag_7: 38.0,
          rolling_mean_7: 40.5,
        },
        top_n: 5,
      };
      const res = await postExplain(payload);
      setExplainData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load SHAP explanation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExplanation(horizon);
  }, [horizon]);

  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-amber-400" />
            SHAP Prediction Explainability Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Exact SHAP value feature attributions identifying positive drivers and negative headwinds for every prediction.
          </p>
        </div>

        {/* Horizon Selector Buttons */}
        <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800">
          {[1, 7, 14, 30].map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                horizon === h
                  ? "bg-amber-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {h}d Model
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 p-4 rounded-lg flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="bg-slate-900 border border-slate-800 p-12 rounded-xl text-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-amber-400" />
          <p className="text-sm">Computing SHAP tree explainer values for {horizon}d model...</p>
        </div>
      ) : explainData ? (
        <div className="space-y-8">
          {/* Prediction Summary Header */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Predicted Demand
              </span>
              <div className="text-3xl font-extrabold text-amber-400 mt-2">
                {explainData.prediction.toFixed(1)} <span className="text-sm font-normal text-slate-300">units</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">Final output prediction</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Base Value (Expected Mean)
              </span>
              <div className="text-3xl font-extrabold text-slate-300 mt-2">
                {explainData.base_value.toFixed(1)} <span className="text-sm font-normal text-slate-400">units</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">Model baseline expectation</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Net SHAP Impact
              </span>
              <div className={`text-3xl font-extrabold mt-2 ${
                explainData.prediction >= explainData.base_value ? "text-emerald-400" : "text-rose-400"
              }`}>
                {(explainData.prediction - explainData.base_value).toFixed(2)}
              </div>
              <p className="text-xs text-slate-500 mt-1">Sum of feature attributions</p>
            </div>
          </div>

          {/* Feature Drivers Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Positive Drivers */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
              <h2 className="text-base font-bold text-emerald-400 flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
                <ArrowUpRight className="w-5 h-5" />
                Top Positive Demand Drivers (+SHAP)
              </h2>

              <div className="space-y-4">
                {explainData.top_positive.map((item, idx) => (
                  <div key={idx} className="bg-slate-950 p-4 rounded-lg border border-slate-800/80">
                    <div className="flex justify-between items-center text-sm font-medium">
                      <span className="text-slate-100 font-mono">{item.feature}</span>
                      <span className="text-emerald-400 font-bold font-mono">+{item.shap_value.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>Feature Value: {String(item.feature_value)}</span>
                      <span>Pulls forecast UP</span>
                    </div>
                    <div className="w-full bg-slate-900 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, item.shap_value * 15)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Negative Headwinds */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
              <h2 className="text-base font-bold text-rose-400 flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
                <ArrowDownRight className="w-5 h-5" />
                Top Negative Headwinds (-SHAP)
              </h2>

              <div className="space-y-4">
                {explainData.top_negative.map((item, idx) => (
                  <div key={idx} className="bg-slate-950 p-4 rounded-lg border border-slate-800/80">
                    <div className="flex justify-between items-center text-sm font-medium">
                      <span className="text-slate-100 font-mono">{item.feature}</span>
                      <span className="text-rose-400 font-bold font-mono">{item.shap_value.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>Feature Value: {String(item.feature_value)}</span>
                      <span>Pulls forecast DOWN</span>
                    </div>
                    <div className="w-full bg-slate-900 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-rose-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, Math.abs(item.shap_value) * 15)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Business Insights Box */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
            <h3 className="text-sm font-bold text-slate-100 mb-2">Business Driver Interpretation</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              The primary positive driver for this {horizon}-day forecast is{" "}
              <strong className="text-emerald-400">{explainData.top_positive[0]?.feature}</strong> (+
              {explainData.top_positive[0]?.shap_value.toFixed(2)} units), followed by{" "}
              <strong className="text-emerald-400">{explainData.top_positive[1]?.feature}</strong> (+
              {explainData.top_positive[1]?.shap_value.toFixed(2)} units). The strongest negative drag comes from{" "}
              <strong className="text-rose-400">{explainData.top_negative[0]?.feature}</strong> (
              {explainData.top_negative[0]?.shap_value.toFixed(2)} units).
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
