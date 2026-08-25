"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  TrendingUp, 
  Sparkles, 
  ShieldCheck, 
  Database, 
  ArrowRight, 
  Bot, 
  Cpu, 
  BarChart3,
  Activity,
  AlertTriangle,
  Menu,
  X,
  Layers,
  CheckCircle2,
  Lock,
  Zap,
  LineChart
} from "lucide-react";

export default function AIDemandLandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="bg-[#000000] text-white min-h-screen relative font-sans overflow-x-hidden selection:bg-white selection:text-black">
      
      {/* ========================================================================= */}
      {/* 1. HERO SECTION (HERO BACKGROUND VIDEO SCOPED ONLY TO THIS TOP HERO SECTION) */}
      {/* ========================================================================= */}
      <section className="relative min-h-[90vh] sm:min-h-screen flex flex-col justify-between p-4 sm:p-8 lg:p-12 overflow-hidden bg-black border-b border-white/10">
        
        {/* BACKGROUND VIDEO (SCOPED STRICTLY TO HERO) */}
        <div className="absolute inset-0 z-0 bg-black overflow-hidden pointer-events-none">
          <video
            className="absolute inset-0 w-full h-full object-cover opacity-85"
            autoPlay
            muted
            loop
            playsInline
          >
            <source
              src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"
              type="video/mp4"
            />
          </video>
          {/* Dark Scrim Overlay */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/40 to-black pointer-events-none" />
        </div>

        {/* HERO CONTAINER */}
        <div className="relative z-10 flex-1 flex flex-col justify-between max-w-[1600px] w-full mx-auto">
          
          {/* NAVBAR */}
          <header className="grid grid-cols-[1fr_auto_1fr] items-center w-full select-none">
            
            {/* LEFT — LOGO */}
            <Link
              href="/"
              className="inline-flex items-center gap-2.5 justify-self-start text-base font-semibold tracking-[-0.03em] text-white appear appear--scale"
              style={{ "--d": "0.08s" } as React.CSSProperties}
              aria-label="AI Demand Intelligence"
            >
              {/* Logo Mark SVG */}
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                <g transform="rotate(-30 12 12)">
                  <circle cx="7.3" cy="3.2" r="1.45" />
                  <rect x="5.5" y="4.7" width="3.6" height="14.6" rx="1.8" />
                  <rect x="14.9" y="4.7" width="3.6" height="14.6" rx="1.8" />
                  <circle cx="16.7" cy="20.8" r="1.45" />
                </g>
              </svg>
              <span className="font-bold">AI Demand Intelligence</span>
            </Link>

            {/* CENTER — NAV PILLS */}
            <nav className="hidden lg:flex items-center gap-2 justify-self-center" aria-label="Primary">
              {[
                { label: "Product", href: "#product", d: "0.16s", class: "appear--scale" },
                { label: "How It Works", href: "#how-it-works", d: "0.28s", class: "appear--soft" },
                { label: "Explainability", href: "#explainability", d: "0.40s", class: "appear--scale" },
                { label: "Performance", href: "#performance", d: "0.52s", class: "appear--soft" },
                { label: "AI Analyst", href: "#ai-analyst", d: "0.64s", class: "appear--scale" },
              ].map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className={`nav-pill appear ${item.class}`}
                  style={{ "--d": item.d } as React.CSSProperties}
                >
                  {item.label}
                </a>
              ))}
            </nav>

            {/* RIGHT — HEADER CTA & MOBILE BURGER */}
            <div className="justify-self-end flex items-center gap-3">
              <Link
                href="/forecast"
                className="btn-solid appear appear--scale text-xs font-bold"
                style={{ "--d": "0.34s" } as React.CSSProperties}
              >
                Start Forecasting
              </Link>

              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="lg:hidden p-2.5 bg-black/60 backdrop-blur-md border border-white/20 text-white"
                aria-label="Open menu"
              >
                {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </header>

          {/* MOBILE MENU DROPDOWN */}
          {menuOpen && (
            <div className="fixed inset-0 z-40 bg-black/95 backdrop-blur-2xl lg:hidden flex flex-col justify-center items-center p-8 space-y-6">
              <a href="#product" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">Product</a>
              <a href="#how-it-works" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">How It Works</a>
              <a href="#explainability" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">Explainability</a>
              <a href="#performance" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">Performance</a>
              <a href="#ai-analyst" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">AI Analyst</a>
              <Link href="/forecast" onClick={() => setMenuOpen(false)} className="btn-solid w-full py-4 text-center font-bold text-sm">
                Start Forecasting
              </Link>
            </div>
          )}

          {/* MAIN HERO CONTENT */}
          <main className="mt-12 sm:mt-20 mb-12 flex flex-col items-center text-center max-w-[880px] mx-auto w-full">
            
            {/* EYEBROW BADGE */}
            <div
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#7d7d7d] via-[#2a2a2a] to-[#0a0a0a] text-[#f2f2f2] text-xs font-medium tracking-[-0.01em] mb-6 border border-white/10 appear appear--pop"
              style={{ "--d": "0.22s" } as React.CSSProperties}
            >
              <svg className="w-4 h-4 text-white fill-current filter drop-shadow-[0_0_3px_rgba(255,255,255,0.45)]" viewBox="0 0 24 24">
                <path d="M12 2.6C12.55 2.6 12.88 3.15 13.08 4.7c.62 4.7 1.52 5.6 6.22 6.22 1.55.2 2.1.53 2.1 1.08s-.55.88-2.1 1.08c-4.7.62-5.6 1.52-6.22 6.22-.2 1.55-.53 2.1-1.08 2.1s-.88-.55-1.08-2.1c-.62-4.7-1.52-5.6-6.22-6.22C3.15 12.88 2.6 12.55 2.6 12s.55-.88 2.1-1.08c4.7-.62 5.6-1.52 6.22-6.22C11.12 3.15 11.45 2.6 12 2.6Z" />
              </svg>
              <span>AI-POWERED DEMAND INTELLIGENCE</span>
            </div>

            {/* H1 HEADLINE WITH INSTRUMENT SERIF ITALIC EM */}
            <h1 className="text-[clamp(2.5rem,5.5vw,4.5rem)] font-medium leading-[1.12] tracking-[-0.045em] text-white">
              <span className="block overflow-hidden py-1">
                <span className="block appear appear--mask" style={{ "--d": "0.42s" } as React.CSSProperties}>
                  Know What Demand Is <em className="serif-italic">Coming Next.</em>
                </span>
              </span>
            </h1>

            {/* SUBHEADLINE & SUPPORTING TEXT */}
            <p
              className="mt-5 text-sm sm:text-base text-[#9a9a9a] max-w-[580px] leading-relaxed tracking-[-0.015em] appear appear--soft"
              style={{ "--d": "0.82s" } as React.CSSProperties}
            >
              Forecast demand, understand what's driving it, and identify what needs your attention before it becomes a business problem.
            </p>
            <p className="mt-2 text-xs sm:text-sm text-slate-400 font-mono">
              Upload your sales data. Generate explainable forecasts across products and stores.
            </p>

            {/* ACTION CTAs */}
            <div className="flex flex-wrap justify-center gap-3 mt-8">
              <Link
                href="/forecast"
                className="btn-solid h-[46px] px-8 text-sm font-bold appear appear--btn"
                style={{ "--d": "0.96s" } as React.CSSProperties}
              >
                Start Forecasting
              </Link>

              <Link
                href="/dashboard"
                className="btn-ghost h-[46px] px-8 text-sm font-medium appear appear--side"
                style={{ "--d": "1.10s" } as React.CSSProperties}
              >
                Explore Demo
              </Link>
            </div>
          </main>

          {/* BOTTOM HERO LEAF STATS */}
          <div className="pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs font-mono text-[#d8d8d8]">
            <span>✓ Multi-Horizon Time-Series CatBoost Models</span>
            <span>✓ SHAP Explainability Engine</span>
            <span>✓ Walk-Forward Cross-Validation</span>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. PROBLEM SECTION                                                        */}
      {/* ========================================================================= */}
      <section className="bg-[#050505] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-indigo-400 uppercase font-bold tracking-widest">03 • The Problem</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Your Sales Data Knows More Than Your Reports Show.
            </h2>
            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              Demand changes with seasonality, promotions, pricing, products, and customer behavior. Traditional reports tell you what happened. They don't tell you what is likely to happen next—or why.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <span className="text-xs font-mono text-rose-400 font-bold uppercase">01 • Static Reports</span>
              <h3 className="text-lg font-bold text-white">Unpredictable Demand</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Demand changes faster than static reports can capture.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <span className="text-xs font-mono text-amber-400 font-bold uppercase">02 • Black-Box AI</span>
              <h3 className="text-lg font-bold text-white">Black-Box Predictions</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                A forecast is more useful when you understand what drove it.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <span className="text-xs font-mono text-indigo-400 font-bold uppercase">03 • Data Noise</span>
              <h3 className="text-lg font-bold text-white">Too Much Data</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Thousands of rows of sales data can hide the signals that matter.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 4. SOLUTION SECTION                                                       */}
      {/* ========================================================================= */}
      <section id="how-it-works" className="bg-[#0a0a0a] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-emerald-400 uppercase font-bold tracking-widest">04 • The Solution</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              From Sales Data to Better Decisions.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { num: "01", step: "Upload", desc: "Bring your historical sales data into the platform." },
              { num: "02", step: "Understand", desc: "Automatically uncover trends, seasonality, data quality issues, and business patterns." },
              { num: "03", step: "Forecast", desc: "Generate demand forecasts for 1, 7, 14, and 30-day horizons." },
              { num: "04", step: "Explain", desc: "Understand the factors driving every prediction." },
              { num: "05", step: "Decide", desc: "Identify emerging demand changes, risks, and opportunities." },
            ].map((item) => (
              <div key={item.num} className="bg-[#121212] border border-white/10 p-6 space-y-3">
                <span className="text-xs font-mono font-bold text-emerald-400">{item.num} — {item.step}</span>
                <p className="text-xs text-slate-300 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 5. CORE FEATURES SECTION                                                  */}
      {/* ========================================================================= */}
      <section id="product" className="bg-[#050505] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-cyan-400 uppercase font-bold tracking-widest">05 • Core Features</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Intelligence Built Around Your Demand.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <TrendingUp className="w-7 h-7 text-indigo-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Demand Forecasting</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Predict future demand across stores and products using time-series machine learning.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <Sparkles className="w-7 h-7 text-amber-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Explainable AI</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Understand which factors are increasing or decreasing each prediction.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <BarChart3 className="w-7 h-7 text-emerald-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Store Intelligence</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Compare store performance and identify emerging demand patterns.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <Activity className="w-7 h-7 text-cyan-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Product Intelligence</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Discover high-growth, declining, and high-demand products.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <Cpu className="w-7 h-7 text-purple-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Model Intelligence</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Evaluate forecasting performance across multiple horizons.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3 relative overflow-hidden">
              <span className="absolute top-4 right-4 px-2 py-0.5 bg-amber-950 text-amber-300 font-mono text-3xs font-bold border border-amber-800">
                AI Analyst — Coming Soon
              </span>
              <Bot className="w-7 h-7 text-amber-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">AI Demand Analyst</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Ask questions about your data and get business-focused answers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 6. EXPLAINABILITY SECTION                                                 */}
      {/* ========================================================================= */}
      <section id="explainability" className="bg-[#0a0a0a] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-4">
            <span className="text-xs font-mono text-amber-400 uppercase font-bold tracking-widest">06 • Explainability</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Don't Just Get a Forecast. Understand It.
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              Every prediction can be analyzed through its underlying drivers, giving you a clearer path from prediction to decision.
            </p>

            <Link
              href="/explainability"
              className="btn-solid inline-flex h-[42px] px-6 text-xs font-bold"
            >
              Explore Explainability
            </Link>
          </div>

          <div className="bg-[#121212] border border-white/10 p-8 space-y-6">
            <div className="border-b border-white/10 pb-4">
              <span className="text-xs text-slate-400 font-mono uppercase">Example Analysis</span>
              <h3 className="text-base font-bold text-white mt-1">Why is demand expected to increase?</h3>
            </div>

            <div className="space-y-4 font-mono text-xs">
              <div>
                <div className="flex justify-between text-emerald-400 font-bold mb-1">
                  <span>Promotion</span>
                  <span>+31%</span>
                </div>
                <div className="w-full bg-[#0a0a0a] h-2"><div className="bg-emerald-500 h-full w-[31%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-emerald-400 font-bold mb-1">
                  <span>Recent Demand</span>
                  <span>+22%</span>
                </div>
                <div className="w-full bg-[#0a0a0a] h-2"><div className="bg-emerald-500 h-full w-[22%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-emerald-400 font-bold mb-1">
                  <span>Seasonality</span>
                  <span>+15%</span>
                </div>
                <div className="w-full bg-[#0a0a0a] h-2"><div className="bg-emerald-500 h-full w-[15%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-indigo-400 font-bold mb-1">
                  <span>Holiday</span>
                  <span>+9%</span>
                </div>
                <div className="w-full bg-[#0a0a0a] h-2"><div className="bg-indigo-500 h-full w-[9%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-rose-400 font-bold mb-1">
                  <span>Price</span>
                  <span>-6%</span>
                </div>
                <div className="w-full bg-[#0a0a0a] h-2"><div className="bg-rose-500 h-full w-[6%]"></div></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 7. BUSINESS INTELLIGENCE SECTION                                         */}
      {/* ========================================================================= */}
      <section className="bg-[#050505] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-rose-400 uppercase font-bold tracking-widest">07 • Business Intelligence</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Know What Needs Your Attention.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-emerald-400">Demand Spike</span>
                <span className="text-lg font-bold font-mono text-emerald-400">+31%</span>
              </div>
              <h3 className="text-base font-bold text-white font-mono">Product A • Store 17</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Demand is expected to increase significantly.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-rose-400">Declining Demand</span>
                <span className="text-lg font-bold font-mono text-rose-400">-14%</span>
              </div>
              <h3 className="text-base font-bold text-white font-mono">Store 12</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Recent demand is trending downward.
              </p>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-amber-400">Inventory Risk</span>
                <span className="px-2.5 py-0.5 bg-red-950 text-red-400 border border-red-800 text-3xs font-mono font-bold">HIGH</span>
              </div>
              <h3 className="text-base font-bold text-white font-mono">Product C</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Projected demand is approaching available inventory.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 8. AI ANALYST SECTION                                                     */}
      {/* ========================================================================= */}
      <section id="ai-analyst" className="bg-[#0a0a0a] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-amber-400 uppercase font-bold tracking-widest">08 • AI Analyst</span>
              <span className="px-2 py-0.5 bg-amber-950 text-amber-300 font-mono text-3xs font-bold border border-amber-800">
                Coming Soon
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Don't Search Through Dashboards. Ask.
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              Ask questions about your demand, products, stores, and forecasts in natural language.
            </p>

            <Link
              href="/analyst"
              className="btn-ghost inline-flex h-[42px] px-6 text-xs font-semibold"
            >
              Meet the AI Demand Analyst
            </Link>
          </div>

          <div className="bg-[#121212] border border-white/10 p-8 space-y-4 font-mono text-xs">
            <span className="text-[#626A78] uppercase text-3xs font-bold block mb-2">Example Natural Language Questions:</span>
            {[
              "Which products are likely to have the highest demand next month?",
              "Why is Store 17's demand increasing?",
              "Which stores need attention?",
              "Compare Store 12 and Store 17.",
              "What changed since last month?",
            ].map((q) => (
              <div key={q} className="bg-[#0a0a0a] p-3 rounded border border-white/5 text-slate-300 flex items-center gap-2">
                <span className="text-amber-400 font-bold">•</span>
                <span>{q}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 9. PERFORMANCE TABLE SECTION                                              */}
      {/* ========================================================================= */}
      <section id="performance" className="bg-[#050505] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-purple-400 uppercase font-bold tracking-widest">09 • Model Performance</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Measured Across Multiple Forecast Horizons.
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              Models are evaluated using chronological walk-forward validation rather than random train/test splits.
            </p>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 p-6 overflow-x-auto">
            <table className="w-full text-left text-xs font-mono min-w-[550px]">
              <thead className="bg-[#121212] text-slate-400 uppercase text-3xs border-b border-white/10">
                <tr>
                  <th className="px-6 py-4">Forecast Horizon</th>
                  <th className="px-6 py-4">Model</th>
                  <th className="px-6 py-4">CV WAPE</th>
                  <th className="px-6 py-4">Test WAPE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-200">
                <tr className="hover:bg-[#121212]">
                  <td className="px-6 py-4 font-bold text-white">1 Day</td>
                  <td className="px-6 py-4 text-amber-400">CatBoost</td>
                  <td className="px-6 py-4">11.83%</td>
                  <td className="px-6 py-4 font-bold text-emerald-400">10.46%</td>
                </tr>
                <tr className="hover:bg-[#121212]">
                  <td className="px-6 py-4 font-bold text-white">7 Days</td>
                  <td className="px-6 py-4 text-amber-400">CatBoost</td>
                  <td className="px-6 py-4">11.27%</td>
                  <td className="px-6 py-4 font-bold text-emerald-400">10.13%</td>
                </tr>
                <tr className="hover:bg-[#121212]">
                  <td className="px-6 py-4 font-bold text-white">14 Days</td>
                  <td className="px-6 py-4 text-amber-400">CatBoost</td>
                  <td className="px-6 py-4">11.42%</td>
                  <td className="px-6 py-4 font-bold text-emerald-400">10.17%</td>
                </tr>
                <tr className="hover:bg-[#121212]">
                  <td className="px-6 py-4 font-bold text-white">30 Days</td>
                  <td className="px-6 py-4 text-amber-400">CatBoost</td>
                  <td className="px-6 py-4">11.98%</td>
                  <td className="px-6 py-4 font-bold text-emerald-400">11.61%</td>
                </tr>
              </tbody>
            </table>
            <p className="text-3xs font-mono text-slate-500 mt-4">* Lower WAPE indicates lower forecast error.</p>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 10. TECHNOLOGY / TRUST SECTION                                            */}
      {/* ========================================================================= */}
      <section className="bg-[#0a0a0a] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-indigo-400 uppercase font-bold tracking-widest">10 • Technology Stack</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Built for Reliable Machine Learning.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#121212] border border-white/10 p-6 space-y-2">
              <h3 className="text-base font-bold text-white">Time-Series Validation</h3>
              <p className="text-xs text-slate-400 leading-relaxed">Walk-forward evaluation designed for forecasting data.</p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 space-y-2">
              <h3 className="text-base font-bold text-white">Model Benchmarking</h3>
              <p className="text-xs text-slate-400 leading-relaxed">Multiple baselines and machine-learning models are evaluated before selection.</p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 space-y-2">
              <h3 className="text-base font-bold text-white">Optimization</h3>
              <p className="text-xs text-slate-400 leading-relaxed">Optuna-based hyperparameter optimization.</p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 space-y-2">
              <h3 className="text-base font-bold text-white">Explainability</h3>
              <p className="text-xs text-slate-400 leading-relaxed">SHAP-based prediction analysis.</p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 space-y-2">
              <h3 className="text-base font-bold text-white">Experiment Tracking</h3>
              <p className="text-xs text-slate-400 leading-relaxed">MLflow experiment tracking and model registry.</p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 space-y-2">
              <h3 className="text-base font-bold text-white">Production Serving</h3>
              <p className="text-xs text-slate-400 leading-relaxed">FastAPI + Docker with production model loading.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 11. HOW IT WORKS / PIPELINE FLOW SECTION                                  */}
      {/* ========================================================================= */}
      <section className="bg-[#050505] text-white py-20 sm:py-28 px-4 sm:px-8 border-b border-white/10">
        <div className="max-w-[1280px] mx-auto space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-emerald-400 uppercase font-bold tracking-widest">11 • End-to-End Pipeline</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              From Historical Data to Production Forecasts.
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              A complete machine-learning pipeline turns historical sales data into continuously usable demand intelligence.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 font-mono text-xs">
            {[
              "Historical Sales Data",
              "Data Validation",
              "EDA & Feature Engineering",
              "Time-Series Evaluation",
              "Model Benchmarking",
              "Model Optimization",
              "Model Selection",
              "MLflow Model Registry",
              "Production Forecast API"
            ].map((step, idx, arr) => (
              <div key={step} className="flex items-center gap-3">
                <span className="px-4 py-3 bg-[#0a0a0a] border border-white/10 text-slate-200 font-semibold">
                  {step}
                </span>
                {idx < arr.length - 1 && <span className="text-emerald-400 font-bold">➔</span>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 12. FINAL CTA SECTION                                                     */}
      {/* ========================================================================= */}
      <section className="bg-[#0a0a0a] text-white py-24 sm:py-32 px-4 sm:px-8 text-center border-b border-white/10">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Turn Your Sales Data Into Your Next Decision.
          </h2>
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            Upload your historical sales data and discover what demand is likely to do next.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
            <Link
              href="/forecast"
              className="btn-solid h-[50px] px-8 text-sm font-bold w-full sm:w-auto"
            >
              Start Forecasting
            </Link>
            <Link
              href="/dashboard"
              className="btn-ghost h-[50px] px-8 text-sm font-medium w-full sm:w-auto"
            >
              Explore Demo
            </Link>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 13. FOOTER                                                                */}
      {/* ========================================================================= */}
      <footer className="bg-[#000000] text-slate-400 py-16 px-4 sm:px-8 text-xs font-mono">
        <div className="max-w-[1280px] mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12 border-b border-white/10 pb-12">
          <div className="space-y-3">
            <span className="font-bold text-white text-sm">AI Demand Intelligence</span>
            <p className="text-slate-500 text-2xs leading-relaxed">
              Forecast. Explain. Decide.
            </p>
          </div>

          <div className="space-y-2">
            <span className="font-bold text-white uppercase text-3xs tracking-wider">Product</span>
            <ul className="space-y-1.5 text-slate-400">
              <li><Link href="/forecast" className="hover:text-white">Forecasting</Link></li>
              <li><Link href="/explainability" className="hover:text-white">Explainability</Link></li>
              <li><Link href="/eda" className="hover:text-white">Store Intelligence</Link></li>
              <li><Link href="/eda" className="hover:text-white">Product Intelligence</Link></li>
              <li><Link href="/analyst" className="hover:text-white">AI Analyst</Link></li>
            </ul>
          </div>

          <div className="space-y-2">
            <span className="font-bold text-white uppercase text-3xs tracking-wider">Technology</span>
            <ul className="space-y-1.5 text-slate-400">
              <li>CatBoost</li>
              <li>SHAP</li>
              <li>MLflow</li>
              <li>FastAPI</li>
              <li>Next.js</li>
            </ul>
          </div>

          <div className="space-y-2">
            <span className="font-bold text-white uppercase text-3xs tracking-wider">Resources</span>
            <ul className="space-y-1.5 text-slate-400">
              <li><a href="https://demand-intelligence-api.onrender.com/docs" target="_blank" rel="noreferrer" className="hover:text-white">Documentation / API</a></li>
              <li><a href="https://github.com/VedantJadhav701/ai-demand-intelligence-platform" target="_blank" rel="noreferrer" className="hover:text-white">GitHub Repository</a></li>
            </ul>
          </div>
        </div>

        <div className="max-w-[1280px] mx-auto pt-8 flex flex-col sm:flex-row justify-between items-center gap-2 text-3xs text-slate-600">
          <span>© 2026 AI Demand Intelligence. All rights reserved.</span>
          <span>Forecast. Explain. Decide.</span>
        </div>
      </footer>
    </div>
  );
}
