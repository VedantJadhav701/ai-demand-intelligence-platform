import Link from "next/link";
import { Upload, ArrowRight, TrendingUp, Sparkles, ShieldCheck, Database } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="space-y-12 py-6">
      {/* Hero Section */}
      <div className="bg-[#101216] border border-white/10 p-10 lg:p-14 rounded-2xl relative overflow-hidden shadow-2xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Hero Left Content */}
          <div className="lg:col-span-7 space-y-6">
            <span className="inline-block px-3 py-1 bg-indigo-600/20 text-indigo-400 font-mono text-xs font-semibold rounded-full border border-indigo-500/30">
              Cinematic Data Intelligence Platform
            </span>

            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#F5F7FA] tracking-tight leading-tight">
              Forecast demand. <br />
              Understand the drivers. <br />
              <span className="text-indigo-400">Make better decisions.</span>
            </h1>

            <p className="text-[#9AA2B1] text-base leading-relaxed max-w-xl">
              Turn raw historical sales data into explainable multi-horizon demand forecasts, SHAP feature attributions, and actionable inventory risk intelligence.
            </p>

            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/datasets"
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-bold flex items-center gap-2 shadow-lg transition-all"
              >
                <Upload className="w-4 h-4" />
                Upload Sales Data
              </Link>

              <Link
                href="/forecast"
                className="px-6 py-3 bg-[#15181D] hover:bg-[#1B1F26] text-[#F5F7FA] border border-white/10 rounded-xl text-sm font-semibold transition-all"
              >
                View Demo Dataset
              </Link>
            </div>
          </div>

          {/* Hero Right Decorative Product Preview Card */}
          <div className="lg:col-span-5">
            <div className="bg-[#15181D] border border-white/10 p-6 rounded-2xl space-y-6 shadow-xl relative">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <span className="text-xs font-mono text-[#9AA2B1]">Forecast Preview</span>
                <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 text-3xs font-semibold rounded border border-emerald-800">
                  ● Model Active
                </span>
              </div>

              <div className="space-y-2">
                <span className="text-xs text-[#9AA2B1] uppercase font-bold tracking-wider">
                  Store 17 • Product A
                </span>
                <div className="text-4xl font-extrabold text-indigo-400">
                  194 <span className="text-lg text-[#F5F7FA] font-normal">units</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-emerald-400 font-semibold">
                  <TrendingUp className="w-4 h-4" />
                  ↑ 12.4% vs previous period
                </div>
              </div>

              {/* Mini Sparkline Chart */}
              <div className="h-20 w-full bg-[#08090B] rounded-xl border border-white/5 p-3 flex items-end justify-between gap-1">
                {[45, 52, 68, 74, 60, 85, 92, 110, 125, 140, 194].map((v, i) => (
                  <div
                    key={i}
                    className={`w-full rounded-t ${i >= 8 ? "bg-indigo-500" : "bg-slate-700"}`}
                    style={{ height: `${(v / 200) * 100}%` }}
                  ></div>
                ))}
              </div>

              <div className="flex justify-between text-2xs text-[#626A78] font-mono pt-1">
                <span>WAPE: 11.27%</span>
                <span>Horizon: 7 Days</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Core Capability Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl space-y-3">
          <Database className="w-6 h-6 text-indigo-400" />
          <h3 className="text-base font-bold text-[#F5F7FA]">Automated Data Profiling</h3>
          <p className="text-xs text-[#9AA2B1] leading-relaxed">
            Upload raw sales CSV files. The platform automatically validates schemas, handles missing values, and builds ML lag & rolling features.
          </p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl space-y-3">
          <Sparkles className="w-6 h-6 text-amber-400" />
          <h3 className="text-base font-bold text-[#F5F7FA]">SHAP Prediction Drivers</h3>
          <p className="text-xs text-[#9AA2B1] leading-relaxed">
            Understand exactly why a forecast was made. Inspect positive demand drivers and negative price/discount headwinds per prediction.
          </p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl space-y-3">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          <h3 className="text-base font-bold text-[#F5F7FA]">Production Model Registry</h3>
          <p className="text-xs text-[#9AA2B1] leading-relaxed">
            Optuna-tuned CatBoost models registered in MLflow across 1d, 7d, 14d, and 30d horizons with live PSI drift monitoring.
          </p>
        </div>
      </div>
    </div>
  );
}
