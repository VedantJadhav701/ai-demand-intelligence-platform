"use client";

import { useState } from "react";
import { TrendingUp, Play, CheckCircle2, AlertCircle, Clock, Tag, ShoppingBag, Store } from "lucide-react";
import { postForecast, ForecastResponseData } from "@/lib/api";

export default function ForecastStudio() {
  const [horizon, setHorizon] = useState<number>(7);
  const [storeId, setStoreId] = useState<string>("STORE_17");
  const [productId, setProductId] = useState<string>("PRODUCT_A");
  const [date, setDate] = useState<string>("2026-08-25");
  
  // Custom Feature Inputs
  const [price, setPrice] = useState<number>(19.99);
  const [discount, setDiscount] = useState<number>(0.0);
  const [promotion, setPromotion] = useState<number>(1);
  const [lag1, setLag1] = useState<number>(42.0);
  const [lag7, setLag7] = useState<number>(38.0);
  const [rollingMean7, setRollingMean7] = useState<number>(40.5);

  const [forecastResult, setForecastResult] = useState<ForecastResponseData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        horizon,
        store_id: storeId,
        product_id: productId,
        date,
        features: {
          price,
          discount,
          promotion,
          lag_1: lag1,
          lag_7: lag7,
          rolling_mean_7: rollingMean7,
        },
      };
      const result = await postForecast(payload);
      setForecastResult(result);
    } catch (err: any) {
      setError(err.message || "Failed to generate forecast.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Title Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <TrendingUp className="w-7 h-7 text-indigo-400" />
          Interactive Demand Forecast Studio
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Configure store, product, and feature scenarios to trigger live inference from production CatBoost models.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Controls Panel */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg space-y-6">
          <h2 className="text-lg font-bold text-slate-100 border-b border-slate-800 pb-3">
            Scenario & Feature Parameters
          </h2>

          {/* Horizon Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Forecast Horizon
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[1, 7, 14, 30].map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className={`py-2 px-3 rounded-lg text-sm font-semibold border transition-all ${
                    horizon === h
                      ? "bg-indigo-600 border-indigo-500 text-white shadow-sm"
                      : "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  {h} Day ({h}d)
                </button>
              ))}
            </div>
          </div>

          {/* Store & Product Selectors */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Store ID
              </label>
              <select
                value={storeId}
                onChange={(e) => setStoreId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="STORE_17">STORE_17 (High Volume)</option>
                <option value="STORE_12">STORE_12 (Urban)</option>
                <option value="STORE_01">STORE_01 (Suburban)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Product ID
              </label>
              <select
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="PRODUCT_A">PRODUCT_A (Grocery)</option>
                <option value="PRODUCT_B">PRODUCT_B (Electronics)</option>
                <option value="PRODUCT_C">PRODUCT_C (Apparel)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Target Date
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Feature Inputs */}
          <div className="pt-4 border-t border-slate-800 space-y-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Feature Variable Inputs
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={price}
                  onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Discount Rate (%)</label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={discount}
                  onChange={(e) => setDiscount(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Lag 1 Sales (Yesterday)</label>
                <input
                  type="number"
                  value={lag1}
                  onChange={(e) => setLag1(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Lag 7 Sales (Last Week)</label>
                <input
                  type="number"
                  value={lag7}
                  onChange={(e) => setLag7(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs text-slate-300 mb-1">Rolling Mean 7 (Units)</label>
              <input
                type="number"
                value={rollingMean7}
                onChange={(e) => setRollingMean7(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-sm font-mono"
              />
            </div>
          </div>

          <button
            onClick={handleGenerateForecast}
            disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-2 shadow-lg transition-all disabled:opacity-50"
          >
            <Play className={`w-4 h-4 fill-current ${loading ? "animate-spin" : ""}`} />
            {loading ? "Running Live Model Inference..." : "Generate Demand Forecast"}
          </button>
        </div>

        {/* Prediction Results Display */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100 border-b border-slate-800 pb-3 mb-4">
              Prediction Results
            </h2>

            {error && (
              <div className="bg-red-950 border border-red-800 text-red-300 p-3 rounded-lg text-xs flex items-center gap-2 mb-4">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}

            {forecastResult ? (
              <div className="space-y-6">
                <div className="bg-slate-950 border border-slate-800 p-6 rounded-xl text-center">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Projected Demand ({horizon}d Horizon)
                  </span>
                  <div className="mt-2 text-4xl font-extrabold text-indigo-400">
                    {forecastResult.forecast.toFixed(1)}{" "}
                    <span className="text-base font-normal text-slate-300">units</span>
                  </div>
                  <span className="inline-block mt-3 px-3 py-1 bg-indigo-950 text-indigo-300 text-xs font-mono rounded border border-indigo-800">
                    ID: {forecastResult.prediction_id}
                  </span>
                </div>

                <div className="space-y-3 text-xs text-slate-300">
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Model Registry Name</span>
                    <span className="font-mono text-indigo-300">{forecastResult.model_registry_name}</span>
                  </div>

                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Model Alias</span>
                    <span className="font-semibold text-emerald-400 uppercase">{forecastResult.model_alias}</span>
                  </div>

                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Feature Version</span>
                    <span className="font-mono">{forecastResult.feature_version}</span>
                  </div>

                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Inference Latency</span>
                    <span className="font-mono text-cyan-400 font-bold">{forecastResult.inference_time_ms.toFixed(2)} ms</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500">
                <TrendingUp className="w-12 h-12 mx-auto text-slate-700 mb-3" />
                <p className="text-sm">Configure parameters and click "Generate Demand Forecast" to view live predictions.</p>
              </div>
            )}
          </div>

          <div className="mt-6 text-xs text-slate-500 text-center border-t border-slate-800 pt-4">
            Outputs are verified against leakage & zero-target rules.
          </div>
        </div>
      </div>
    </div>
  );
}
