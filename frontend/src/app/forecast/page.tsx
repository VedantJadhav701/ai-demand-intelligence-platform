"use client";

import { useEffect, useState } from "react";
import { 
  Upload, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp, 
  Sparkles, 
  ArrowRight, 
  Clock, 
  ChevronRight,
  Database,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  SlidersHorizontal
} from "lucide-react";
import { 
  uploadSalesDataFile, 
  fetchDatasetSummary, 
  fetchDerivedFeatures, 
  postForecast, 
  postExplain, 
  DatasetSummaryData, 
  ForecastResponseData, 
  ExplainResponseData 
} from "@/lib/api";

export default function ForecastStudio() {
  const [step, setStep] = useState<number>(1); // 1: Upload, 2: Configure, 3: Result & Explain

  // Step 1: Upload Data State
  const [datasetSummary, setDatasetSummary] = useState<DatasetSummaryData | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Step 2: Forecast Configuration State
  const [selectedStore, setSelectedStore] = useState<string>("STORE_17");
  const [selectedProduct, setSelectedProduct] = useState<string>("PRODUCT_A");
  const [horizon, setHorizon] = useState<number>(7);
  const [targetDate, setTargetDate] = useState<string>("2026-08-26");

  // Step 2 Optional Future Assumptions
  const [showBusinessAssumptions, setShowBusinessAssumptions] = useState<boolean>(false);
  const [plannedPrice, setPlannedPrice] = useState<string>("Auto");
  const [plannedDiscount, setPlannedDiscount] = useState<number>(0);
  const [plannedPromotion, setPlannedPromotion] = useState<number>(0);

  // Step 3: Result & SHAP State
  const [forecastResult, setForecastResult] = useState<ForecastResponseData | null>(null);
  const [explainResult, setExplainResult] = useState<ExplainResponseData | null>(null);
  const [generating, setGenerating] = useState<boolean>(false);
  const [explaining, setExplaining] = useState<boolean>(false);
  const [forecastError, setForecastError] = useState<string | null>(null);

  // Initial load of existing dataset summary
  useEffect(() => {
    fetchDatasetSummary()
      .then((res) => {
        if (res && res.total_rows > 0) {
          setDatasetSummary(res);
          if (res.stores.length > 0) setSelectedStore(res.stores[0]);
          if (res.products.length > 0) setSelectedProduct(res.products[0]);
        }
      })
      .catch(() => {});
  }, []);

  // Handle File Upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      const summary = await uploadSalesDataFile(file);
      setDatasetSummary(summary);
      if (summary.stores.length > 0) setSelectedStore(summary.stores[0]);
      if (summary.products.length > 0) setSelectedProduct(summary.products[0]);
    } catch (err: any) {
      setUploadError(err.message || "Failed to parse sales data file.");
    } finally {
      setUploading(false);
    }
  };

  // Trigger Forecast Generation (Auto derives lags & rolling stats from dataset)
  const handleGenerateForecast = async () => {
    setGenerating(true);
    setForecastError(null);
    setForecastResult(null);
    setExplainResult(null);

    try {
      // Automatically derive historical features for series
      const derivedFeatures = await fetchDerivedFeatures(selectedStore, selectedProduct);

      // Apply future business assumptions if overridden
      if (plannedPrice !== "Auto" && !isNaN(parseFloat(plannedPrice))) {
        derivedFeatures["price"] = parseFloat(plannedPrice);
      }
      derivedFeatures["discount"] = plannedDiscount;
      derivedFeatures["promotion"] = plannedPromotion;

      const payload = {
        horizon,
        store_id: selectedStore,
        product_id: selectedProduct,
        date: targetDate,
        features: derivedFeatures,
      };

      const result = await postForecast(payload);
      setForecastResult(result);
      setStep(3);
    } catch (err: any) {
      setForecastError(err.message || "Failed to generate demand forecast.");
    } finally {
      setGenerating(false);
    }
  };

  // Trigger SHAP Explanation
  const handleExplainPrediction = async () => {
    if (!forecastResult) return;
    setExplaining(true);
    try {
      const derivedFeatures = await fetchDerivedFeatures(selectedStore, selectedProduct);
      if (plannedPrice !== "Auto" && !isNaN(parseFloat(plannedPrice))) {
        derivedFeatures["price"] = parseFloat(plannedPrice);
      }
      derivedFeatures["discount"] = plannedDiscount;
      derivedFeatures["promotion"] = plannedPromotion;

      const payload = {
        horizon,
        store_id: selectedStore,
        product_id: selectedProduct,
        date: targetDate,
        features: derivedFeatures,
        top_n: 5,
      };

      const res = await postExplain(payload);
      setExplainResult(res);
    } catch (err: any) {
      setForecastError(err.message || "Failed to compute SHAP explanation.");
    } finally {
      setExplaining(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Title & Step Navigation Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <TrendingUp className="w-7 h-7 text-indigo-400" />
          AI Demand Intelligence & Forecasting Studio
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Automated end-to-end workflow: Upload raw sales data ➔ Automatic Feature Engineering ➔ Multi-horizon CatBoost Forecast ➔ SHAP Insights.
        </p>

        {/* Step Progress Pills */}
        <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-4 text-xs font-semibold">
          <div className={`flex items-center gap-2 ${step >= 1 ? "text-indigo-400" : "text-slate-500"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center border font-bold ${
              step >= 1 ? "bg-indigo-950 border-indigo-500 text-indigo-300" : "border-slate-700 text-slate-500"
            }`}>
              1
            </span>
            Upload Sales Data
          </div>
          <ChevronRight className="w-4 h-4 text-slate-600" />

          <div className={`flex items-center gap-2 ${step >= 2 ? "text-indigo-400" : "text-slate-500"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center border font-bold ${
              step >= 2 ? "bg-indigo-950 border-indigo-500 text-indigo-300" : "border-slate-700 text-slate-500"
            }`}>
              2
            </span>
            Forecast Configuration
          </div>
          <ChevronRight className="w-4 h-4 text-slate-600" />

          <div className={`flex items-center gap-2 ${step >= 3 ? "text-indigo-400" : "text-slate-500"}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center border font-bold ${
              step >= 3 ? "bg-indigo-950 border-indigo-500 text-indigo-300" : "border-slate-700 text-slate-500"
            }`}>
              3
            </span>
            Forecast Result & SHAP
          </div>
        </div>
      </div>

      {/* STEP 1: UPLOAD HISTORICAL SALES DATA */}
      {step === 1 && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-lg text-center space-y-6">
            <div className="max-w-md mx-auto space-y-2">
              <Upload className="w-12 h-12 mx-auto text-indigo-400" />
              <h2 className="text-xl font-bold text-slate-100">Upload Sales Data to Begin</h2>
              <p className="text-xs text-slate-400">
                Primary input should be a CSV or Excel file containing your historical sales records.
              </p>
            </div>

            {/* File Upload Box */}
            <div className="max-w-lg mx-auto border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 transition-colors bg-slate-950/50">
              <input
                type="file"
                accept=".csv, .xlsx, .xls"
                onChange={handleFileUpload}
                id="file-upload"
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer space-y-3 block">
                <FileSpreadsheet className="w-10 h-10 mx-auto text-slate-400" />
                <span className="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold shadow-md transition-all">
                  {uploading ? "Parsing Sales Data..." : "Choose CSV / Excel File"}
                </span>
                <p className="text-xs text-slate-500">Supports .csv, .xlsx files up to 50MB</p>
              </label>
            </div>

            {uploadError && (
              <div className="max-w-md mx-auto bg-red-950 border border-red-800 text-red-300 p-3 rounded-lg text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {uploadError}
              </div>
            )}

            {/* Required & Optional Columns Notice */}
            <div className="max-w-2xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-4 text-left pt-4 border-t border-slate-800 text-xs">
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                <span className="font-bold text-slate-300 uppercase tracking-wider text-2xs block mb-2 text-indigo-400">
                  Required Columns
                </span>
                <ul className="space-y-1 font-mono text-slate-300">
                  <li>• date</li>
                  <li>• store_id</li>
                  <li>• product_id</li>
                  <li>• units_sold</li>
                </ul>
              </div>

              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                <span className="font-bold text-slate-300 uppercase tracking-wider text-2xs block mb-2 text-slate-400">
                  Optional Columns
                </span>
                <ul className="space-y-1 font-mono text-slate-400">
                  <li>• price, discount, promotion</li>
                  <li>• store_type, product_category</li>
                  <li>• holiday, inventory</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Dataset Summary (If Loaded) */}
          {datasetSummary && datasetSummary.total_rows > 0 && (
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg space-y-6">
              <h2 className="text-lg font-bold text-slate-100 flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Database className="w-5 h-5 text-indigo-400" />
                  Dataset Profiling Summary
                </span>
                <span className="px-3 py-1 bg-emerald-950 text-emerald-400 text-xs font-semibold rounded-full border border-emerald-800 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Data Quality: {datasetSummary.data_quality}
                </span>
              </h2>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <span className="text-xs text-slate-400 uppercase">Total Rows</span>
                  <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
                    {datasetSummary.total_rows.toLocaleString()}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <span className="text-xs text-slate-400 uppercase">Stores</span>
                  <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
                    {datasetSummary.total_stores}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <span className="text-xs text-slate-400 uppercase">Products</span>
                  <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
                    {datasetSummary.total_products}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <span className="text-xs text-slate-400 uppercase">Missing Values</span>
                  <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">
                    {datasetSummary.missing_pct}%
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <span className="text-xs text-slate-400">
                  Date Range: <strong className="text-slate-200">{datasetSummary.date_range}</strong>
                </span>
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold flex items-center gap-2 shadow-lg transition-all"
                >
                  Continue to Forecast Configuration
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* STEP 2: FORECAST CONFIGURATION */}
      {step === 2 && (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-lg space-y-8 max-w-3xl mx-auto">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-100">Forecast Configuration</h2>
              <p className="text-xs text-slate-400 mt-1">
                Select target store, product, and horizon. All ML features (lags, rolling stats, calendar) are automatically derived by the pipeline!
              </p>
            </div>
            <button
              onClick={() => setStep(1)}
              className="text-xs text-indigo-400 hover:underline"
            >
              ← Change Dataset
            </button>
          </div>

          <div className="space-y-6">
            {/* Store & Product Selection */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Store Identifier
                </label>
                <select
                  value={selectedStore}
                  onChange={(e) => setSelectedStore(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 font-medium"
                >
                  {datasetSummary?.stores.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  )) || (
                    <>
                      <option value="STORE_17">STORE_17 (High Volume)</option>
                      <option value="STORE_12">STORE_12 (Urban)</option>
                      <option value="STORE_01">STORE_01 (Suburban)</option>
                    </>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Product Identifier
                </label>
                <select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 font-medium"
                >
                  {datasetSummary?.products.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  )) || (
                    <>
                      <option value="PRODUCT_A">PRODUCT_A (Grocery)</option>
                      <option value="PRODUCT_B">PRODUCT_B (Electronics)</option>
                      <option value="PRODUCT_C">PRODUCT_C (Apparel)</option>
                    </>
                  )}
                </select>
              </div>
            </div>

            {/* Horizon Selection */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Forecast Horizon
              </label>
              <div className="grid grid-cols-4 gap-3">
                {[1, 7, 14, 30].map((h) => (
                  <button
                    key={h}
                    onClick={() => setHorizon(h)}
                    className={`py-3 px-4 rounded-xl text-sm font-bold border transition-all ${
                      horizon === h
                        ? "bg-indigo-600 border-indigo-500 text-white shadow-lg scale-102"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    {h} Day{h > 1 ? "s" : ""}
                  </button>
                ))}
              </div>
            </div>

            {/* Optional Future Business Assumptions */}
            <div className="border border-slate-800/80 rounded-xl p-4 bg-slate-950/40 space-y-4">
              <button
                onClick={() => setShowBusinessAssumptions(!showBusinessAssumptions)}
                className="flex items-center justify-between w-full text-xs font-semibold text-slate-400 hover:text-slate-200"
              >
                <span className="flex items-center gap-2">
                  <SlidersHorizontal className="w-4 h-4 text-indigo-400" />
                  Optional Future Business Assumptions (Price / Promotion)
                </span>
                <span>{showBusinessAssumptions ? "▲ Hide" : "▼ Expand"}</span>
              </button>

              {showBusinessAssumptions && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-800">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Planned Price ($)</label>
                    <input
                      type="text"
                      value={plannedPrice}
                      onChange={(e) => setPlannedPrice(e.target.value)}
                      placeholder="Auto"
                      className="w-full bg-slate-900 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-xs font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Planned Discount (%)</label>
                    <input
                      type="number"
                      value={plannedDiscount}
                      onChange={(e) => setPlannedDiscount(parseFloat(e.target.value) || 0)}
                      className="w-full bg-slate-900 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-xs font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Planned Promotion</label>
                    <select
                      value={plannedPromotion}
                      onChange={(e) => setPlannedPromotion(parseInt(e.target.value) || 0)}
                      className="w-full bg-slate-900 border border-slate-800 text-slate-100 rounded-lg px-3 py-2 text-xs"
                    >
                      <option value={0}>No Promotion</option>
                      <option value={1}>Active Promotion</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {forecastError && (
              <div className="bg-red-950 border border-red-800 text-red-300 p-4 rounded-lg text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {forecastError}
              </div>
            )}

            <button
              onClick={handleGenerateForecast}
              disabled={generating}
              className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-base font-bold flex items-center justify-center gap-2 shadow-xl transition-all disabled:opacity-50"
            >
              <TrendingUp className={`w-5 h-5 ${generating ? "animate-spin" : ""}`} />
              {generating ? "Deriving Lags & Executing Model..." : "Generate Forecast"}
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: FORECAST RESULT & SHAP EXPLANATION */}
      {step === 3 && forecastResult && (
        <div className="space-y-8 max-w-4xl mx-auto">
          {/* Main Result Card */}
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs uppercase font-bold text-indigo-400 tracking-wider">
                  Demand Intelligence Forecast Result
                </span>
                <h2 className="text-xl font-bold text-slate-100 mt-1">
                  {selectedStore} • {selectedProduct}
                </h2>
              </div>
              <button
                onClick={() => setStep(2)}
                className="text-xs text-indigo-400 hover:underline"
              >
                ← Edit Parameters
              </button>
            </div>

            {/* Big Output Card */}
            <div className="bg-slate-950 border border-slate-800 p-8 rounded-2xl text-center space-y-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                Expected Demand ({forecastResult.horizon}-Day Horizon)
              </span>
              <div className="text-5xl font-extrabold text-indigo-400">
                {Math.round(forecastResult.forecast)}{" "}
                <span className="text-xl font-normal text-slate-300">units</span>
              </div>
              <p className="text-xs text-slate-500 font-mono pt-2">
                Prediction ID: {forecastResult.prediction_id}
              </p>
            </div>

            {/* Model Metadata Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-xs text-slate-400 uppercase block mb-1">Model Architecture</span>
                <span className="font-bold text-amber-400">CatBoost</span>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-xs text-slate-400 uppercase block mb-1">Target Horizon</span>
                <span className="font-bold text-slate-200">{forecastResult.horizon} Days</span>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-xs text-slate-400 uppercase block mb-1">Benchmark Test WAPE</span>
                <span className="font-bold text-emerald-400">11.27%</span>
              </div>
            </div>

            {/* Explain Prediction Button */}
            <div className="pt-4 flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleExplainPrediction}
                disabled={explaining}
                className="flex-1 py-3.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 shadow-lg transition-all disabled:opacity-50"
              >
                <Sparkles className={`w-4 h-4 ${explaining ? "animate-spin" : ""}`} />
                {explaining ? "Computing SHAP Attributions..." : "Explain Prediction (SHAP Drivers)"}
              </button>

              <button
                onClick={() => setStep(2)}
                className="py-3.5 px-6 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-sm font-bold transition-all"
              >
                New Scenario
              </button>
            </div>
          </div>

          {/* SHAP Explanation Waterfall Panel */}
          {explainResult && (
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  SHAP Driver Waterfall Explanation
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  Base Value: {explainResult.base_value.toFixed(1)} units
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Positive Drivers */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                    <ArrowUpRight className="w-4 h-4" />
                    Positive Demand Drivers (+SHAP)
                  </h4>
                  {explainResult.top_positive.map((item, i) => (
                    <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
                      <div className="flex justify-between font-mono">
                        <span className="text-slate-200">{item.feature}</span>
                        <span className="text-emerald-400 font-bold">+{item.shap_value.toFixed(2)}</span>
                      </div>
                      <div className="w-full bg-slate-900 h-1 rounded-full mt-2 overflow-hidden">
                        <div className="bg-emerald-500 h-full" style={{ width: `${Math.min(100, item.shap_value * 15)}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Negative Headwinds */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1">
                    <ArrowDownRight className="w-4 h-4" />
                    Negative Headwinds (-SHAP)
                  </h4>
                  {explainResult.top_negative.map((item, i) => (
                    <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
                      <div className="flex justify-between font-mono">
                        <span className="text-slate-200">{item.feature}</span>
                        <span className="text-rose-400 font-bold">{item.shap_value.toFixed(2)}</span>
                      </div>
                      <div className="w-full bg-slate-900 h-1 rounded-full mt-2 overflow-hidden">
                        <div className="bg-rose-500 h-full" style={{ width: `${Math.min(100, Math.abs(item.shap_value) * 15)}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
