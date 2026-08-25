"use client";

import { ShieldCheck, AlertTriangle, CheckCircle2, Info } from "lucide-react";

export default function DataQualityPage() {
  const columnQuality = [
    { column: "date", type: "datetime", missing: "0.0%", status: "Valid", severity: "healthy" },
    { column: "store_id", type: "string", missing: "0.0%", status: "Valid", severity: "healthy" },
    { column: "product_id", type: "string", missing: "0.0%", status: "Valid", severity: "healthy" },
    { column: "units_sold", type: "integer", missing: "0.0%", status: "Valid", severity: "healthy" },
    { column: "price", type: "float", missing: "0.3%", status: "Imputed", severity: "healthy" },
    { column: "promotion", type: "integer", missing: "0.0%", status: "Valid", severity: "healthy" },
    { column: "discount", type: "float", missing: "0.7%", status: "Imputed", severity: "healthy" },
    { column: "inventory", type: "integer", missing: "1.1%", status: "Imputed", severity: "warning" },
  ];

  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#F5F7FA] flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            Data Quality & Schema Health
          </h1>
          <p className="text-[#9AA2B1] text-xs mt-1">
            Automated missing value checks, data type verification, and integrity auditing.
          </p>
        </div>
      </div>

      {/* Overall Health Score Card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Overall Data Health</span>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">98.8%</div>
          <p className="text-xs text-[#626A78] mt-1">Ready for feature engineering</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Missing Values</span>
          <div className="text-3xl font-extrabold text-[#F5F7FA] mt-2 font-mono">1.2%</div>
          <p className="text-xs text-[#626A78] mt-1">Automatically imputed by pipeline</p>
        </div>

        <div className="bg-[#101216] border border-white/10 p-6 rounded-xl">
          <span className="text-2xs text-[#9AA2B1] font-mono uppercase">Duplicate Rows</span>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">0</div>
          <p className="text-xs text-[#626A78] mt-1">Unique series records</p>
        </div>
      </div>

      {/* Column Quality Table */}
      <div className="bg-[#101216] border border-white/10 rounded-xl p-6 shadow-lg space-y-4">
        <h2 className="text-base font-bold text-[#F5F7FA]">Column Level Integrity Audit</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#9AA2B1]">
            <thead className="bg-[#08090B] text-[#626A78] uppercase text-3xs font-mono border-b border-white/10">
              <tr>
                <th className="px-4 py-3">Column Name</th>
                <th className="px-4 py-3">Data Type</th>
                <th className="px-4 py-3">Missing %</th>
                <th className="px-4 py-3">Audit Status</th>
                <th className="px-4 py-3">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono">
              {columnQuality.map((col) => (
                <tr key={col.column} className="hover:bg-[#15181D]">
                  <td className="px-4 py-3 font-bold text-[#F5F7FA]">{col.column}</td>
                  <td className="px-4 py-3 text-indigo-400">{col.type}</td>
                  <td className="px-4 py-3 text-[#F5F7FA]">{col.missing}</td>
                  <td className="px-4 py-3">{col.status}</td>
                  <td className="px-4 py-3">
                    {col.severity === "healthy" ? (
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Healthy
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-400 font-semibold">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Minor Impute
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Issues Summary Box */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl space-y-3">
        <h3 className="text-sm font-bold text-[#F5F7FA]">Data Integrity Alerts</h3>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>✓ No critical schema or required column missing errors detected.</span>
          </div>
          <div className="flex items-center gap-2 text-amber-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>⚠ inventory contains 1.1% missing values (Forward-filled automatically).</span>
          </div>
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>✓ No duplicate (date, store_id, product_id) series records detected.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
