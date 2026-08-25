"use client";

import { useState, useEffect } from "react";
import { 
  Upload, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  Database, 
  RefreshCw,
  ArrowRight,
  ShieldCheck
} from "lucide-react";
import { uploadSalesDataFile, fetchDatasetSummary, DatasetSummaryData } from "@/lib/api";
import Link from "next/link";

export default function DatasetsPage() {
  const [summary, setSummary] = useState<DatasetSummaryData | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatasetSummary()
      .then((res) => {
        if (res && res.total_rows > 0) setSummary(res);
      })
      .catch(() => {});
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadSalesDataFile(file);
      setSummary(res);
    } catch (err: any) {
      setError(err.message || "Dataset validation failed. Please check required columns.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Title Banner */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#F5F7FA] flex items-center gap-2">
            <Database className="w-6 h-6 text-indigo-400" />
            Dataset Management & Ingestion
          </h1>
          <p className="text-[#9AA2B1] text-xs mt-1">
            Upload CSV/Excel sales datasets to trigger automatic schema validation and feature engineering.
          </p>
        </div>
      </div>

      {/* Upload Zone Card */}
      <div className="bg-[#101216] border border-white/10 p-8 rounded-xl shadow-lg space-y-6 text-center">
        <div className="max-w-md mx-auto space-y-2">
          <Upload className="w-10 h-10 mx-auto text-indigo-400" />
          <h2 className="text-lg font-bold text-[#F5F7FA]">Upload Sales Dataset</h2>
          <p className="text-xs text-[#9AA2B1]">
            Drop your raw sales data file or click to browse. Max size 50MB.
          </p>
        </div>

        <div className="max-w-lg mx-auto border-2 border-dashed border-white/10 hover:border-indigo-500/60 rounded-xl p-8 transition-colors bg-[#08090B]/50 space-y-4">
          <input
            type="file"
            accept=".csv, .xlsx, .xls"
            onChange={handleFileChange}
            id="file-input-datasets"
            className="hidden"
          />
          <label htmlFor="file-input-datasets" className="cursor-pointer space-y-3 block">
            <FileSpreadsheet className="w-10 h-10 mx-auto text-[#626A78]" />
            <span className="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all">
              {uploading ? "Validating & Engineering Features..." : "Browse CSV / Excel Files"}
            </span>
            <p className="text-2xs text-[#626A78]">Supported Formats: .csv, .xlsx, .xls</p>
          </label>

          <div className="pt-2 border-t border-white/10 flex justify-center">
            <a
              href="/sample_data.csv"
              download="sample_data.csv"
              className="inline-flex items-center gap-1.5 text-2xs text-indigo-400 hover:text-indigo-300 font-semibold bg-[#15181D] px-3 py-1.5 rounded-lg border border-white/10 transition-colors"
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              Download Sample CSV Template (2,133 Rows)
            </a>
          </div>
        </div>

        {error && (
          <div className="max-w-md mx-auto bg-red-950/80 border border-red-800 text-red-200 p-3 rounded-lg text-xs flex items-center gap-2 text-left">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            {error}
          </div>
        )}

        {/* Required vs Optional Columns Guide */}
        <div className="max-w-2xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-4 text-left pt-4 border-t border-white/10 text-xs">
          <div className="bg-[#15181D] p-4 rounded-lg border border-white/5">
            <span className="font-bold text-indigo-400 uppercase tracking-wider text-3xs block mb-2 font-mono">
              Required Schema Columns
            </span>
            <ul className="space-y-1 font-mono text-[#F5F7FA]">
              <li>• date (YYYY-MM-DD)</li>
              <li>• store_id</li>
              <li>• product_id</li>
              <li>• units_sold</li>
            </ul>
          </div>

          <div className="bg-[#15181D] p-4 rounded-lg border border-white/5">
            <span className="font-bold text-[#9AA2B1] uppercase tracking-wider text-3xs block mb-2 font-mono">
              Optional Feature Columns
            </span>
            <ul className="space-y-1 font-mono text-[#9AA2B1]">
              <li>• price, discount, promotion</li>
              <li>• store_type, product_category</li>
              <li>• holiday, inventory</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Dataset Summary Cards */}
      {summary && (
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg space-y-6">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <h2 className="text-base font-bold text-[#F5F7FA]">Dataset Overview</h2>
            <span className="px-3 py-1 bg-emerald-950 text-emerald-400 text-xs font-semibold rounded-full border border-emerald-800 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              Data Quality: {summary.data_quality} ({100 - summary.missing_pct}%)
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-[#15181D] p-4 rounded-lg border border-white/5">
              <span className="text-2xs text-[#9AA2B1] uppercase font-mono">Total Rows</span>
              <div className="text-xl font-bold text-[#F5F7FA] mt-1 font-mono">{summary.total_rows.toLocaleString()}</div>
            </div>

            <div className="bg-[#15181D] p-4 rounded-lg border border-white/5">
              <span className="text-2xs text-[#9AA2B1] uppercase font-mono">Stores</span>
              <div className="text-xl font-bold text-[#F5F7FA] mt-1 font-mono">{summary.total_stores}</div>
            </div>

            <div className="bg-[#15181D] p-4 rounded-lg border border-white/5">
              <span className="text-2xs text-[#9AA2B1] uppercase font-mono">Products</span>
              <div className="text-xl font-bold text-[#F5F7FA] mt-1 font-mono">{summary.total_products}</div>
            </div>

            <div className="bg-[#15181D] p-4 rounded-lg border border-white/5">
              <span className="text-2xs text-[#9AA2B1] uppercase font-mono">Missing Values</span>
              <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">{summary.missing_pct}%</div>
            </div>
          </div>

          <div className="flex justify-between items-center pt-2 text-xs">
            <span className="text-[#9AA2B1]">Date Range: <strong className="text-[#F5F7FA]">{summary.date_range}</strong></span>
            <Link
              href="/forecast"
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold flex items-center gap-2 transition-all shadow-md"
            >
              Proceed to Forecasting
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
