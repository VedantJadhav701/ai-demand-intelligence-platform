"use client";

import { useState } from "react";
import { Bot, Send, Sparkles, Database, TrendingUp, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function AnalystPage() {
  const [query, setQuery] = useState<string>("");
  const [messages, setMessages] = useState<
    { sender: "user" | "analyst"; text: string; audit?: any }[]
  >([
    {
      sender: "analyst",
      text: "Hello! I am your AI Demand Analyst. Ask me questions about your forecasted demand, inventory risks, or prediction drivers.",
    },
  ]);

  const handleSend = () => {
    if (!query.trim()) return;
    const userMsg = query;
    setQuery("");
    setMessages((prev) => [...prev, { sender: "user", text: userMsg }]);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "analyst",
          text: "I analyzed forecasted demand and current inventory across active stores. 3 stores have elevated inventory risk for next month.",
          audit: {
            sources: ["CatBoost Forecast Engine", "Inventory DB", "SHAP Explainer"],
            riskDetails: [
              { store: "Store 17", forecast: "12,400 units", stock: "9,800 units", risk: "HIGH" },
              { store: "Store 12", forecast: "9,100 units", stock: "7,900 units", risk: "MEDIUM" },
            ],
          },
        },
      ]);
    }, 600);
  };

  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="bg-[#101216] border border-white/10 p-6 rounded-xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-[#F5F7FA]">AI Demand Analyst</h1>
            <span className="text-3xs font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/60 font-semibold">
              Phase 8 Preview
            </span>
          </div>
          <p className="text-[#9AA2B1] text-xs mt-1">
            Natural-language analytics interface translating complex demand predictions into audited business answers.
          </p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="bg-[#101216] border border-white/10 rounded-2xl shadow-xl flex flex-col h-[560px] overflow-hidden">
        {/* Chat History */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-3 ${m.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              {m.sender === "analyst" && (
                <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center shrink-0 text-indigo-400">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-xl p-4 rounded-xl text-xs leading-relaxed space-y-3 ${
                m.sender === "user"
                  ? "bg-indigo-600 text-white rounded-br-none"
                  : "bg-[#15181D] border border-white/10 text-[#F5F7FA] rounded-bl-none"
              }`}>
                <p>{m.text}</p>

                {/* Auditability Details Card */}
                {m.audit && (
                  <div className="pt-3 border-t border-white/10 space-y-3 font-mono">
                    <div className="flex items-center gap-2 text-2xs text-[#9AA2B1]">
                      <span className="font-bold uppercase text-[#626A78]">Sources / Tool Executions:</span>
                      {m.audit.sources.map((s: string) => (
                        <span key={s} className="px-2 py-0.5 bg-[#08090B] rounded border border-white/10 text-indigo-300">
                          {s}
                        </span>
                      ))}
                    </div>

                    <div className="space-y-2">
                      {m.audit.riskDetails.map((r: any) => (
                        <div key={r.store} className="bg-[#08090B] p-2.5 rounded border border-white/5 flex justify-between items-center text-2xs">
                          <div>
                            <span className="font-bold text-[#F5F7FA]">{r.store}</span>
                            <span className="text-[#626A78] block">Projected: {r.forecast} | Stock: {r.stock}</span>
                          </div>
                          <span className={`px-2 py-0.5 rounded font-bold ${
                            r.risk === "HIGH" ? "bg-red-950 text-red-400 border border-red-800" : "bg-amber-950 text-amber-400 border border-amber-800"
                          }`}>
                            Risk: {r.risk}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Prompt Suggestions */}
        <div className="px-6 py-3 bg-[#15181D] border-t border-white/10 flex flex-wrap gap-2 text-3xs font-mono">
          <span className="text-[#626A78] self-center">Suggestions:</span>
          {[
            "Which stores should increase inventory next month?",
            "Why is Store 17 demand increasing?",
            "Compare Store 17 and Store 12",
          ].map((prompt) => (
            <button
              key={prompt}
              onClick={() => setQuery(prompt)}
              className="px-2.5 py-1 bg-[#08090B] hover:bg-[#1B1F26] text-[#9AA2B1] hover:text-[#F5F7FA] rounded border border-white/10 transition-colors"
            >
              • {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-[#08090B] border-t border-white/10 flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask questions about your demand data..."
            className="flex-1 bg-[#101216] border border-white/10 text-[#F5F7FA] rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-indigo-500"
          />
          <button
            onClick={handleSend}
            className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold flex items-center gap-2 text-xs transition-all shadow-md"
          >
            <Send className="w-4 h-4" />
            Ask Analyst
          </button>
        </div>
      </div>
    </div>
  );
}
