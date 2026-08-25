"use client";

import { useState } from "react";
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
  Menu,
  X
} from "lucide-react";

export default function MeridianLandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#ffffff] text-[#0a0a0a] font-sans relative overflow-x-hidden selection:bg-[#006cd2] selection:text-white">
      
      {/* ========================================================================= */}
      {/* 1. HERO SECTION WRAPPER (BACKGROUND VIDEO IS SCOPED ONLY TO THIS SECTION) */}
      {/* ========================================================================= */}
      <section className="relative min-h-screen flex flex-col justify-between p-4 sm:p-8 lg:p-12 overflow-hidden bg-white">
        
        {/* BACKGROUND VIDEO (SCOPED STRICTLY TO HERO) */}
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
          <video
            className="absolute inset-0 w-full h-full object-cover opacity-90"
            autoPlay
            muted
            loop
            playsInline
          >
            <source
              src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260808_075824_7c8a2ef3-826c-43ca-81a1-162429faa306.mp4"
              type="video/mp4"
            />
          </video>
        </div>

        {/* HERO CONTENT CONTAINER */}
        <div className="relative z-10 flex-1 flex flex-col justify-between max-w-[1440px] w-full mx-auto">
          {/* NAVBAR */}
          <header className="grid grid-cols-[1fr_auto_1fr] items-center w-full select-none">
            {/* Left Glass Pill Links */}
            <nav className="hidden lg:flex items-center gap-[clamp(16px,2vw,32px)] px-6 py-4 bg-[rgba(0,0,0,0.13)] backdrop-blur-[18px] border-0 justify-self-start">
              {[
                { label: "Product", href: "#product" },
                { label: "How It Works", href: "#how-it-works" },
                { label: "Explainability", href: "#explainability" },
                { label: "Performance", href: "#performance" },
                { label: "AI Analyst", href: "#ai-analyst" },
              ].map((link, idx) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-xs sm:text-sm font-medium text-[#0a0a0a] tracking-[-0.01em] hover:text-[#006cd2] transition-colors relative py-1"
                  style={{ animation: `link-in 0.55s backwards ${0.02 + idx * 0.06}s` }}
                >
                  {link.label}
                </a>
              ))}
            </nav>

            {/* Center 6 Parallelograms SVG Logo */}
            <Link href="/" className="justify-self-start lg:justify-self-center group" aria-label="Meridian AI Demand Intelligence">
              <svg
                className="w-8 sm:w-10 h-auto fill-[#0a0a0a] group-hover:scale-110 transition-transform duration-300"
                viewBox="0 0 42 34"
              >
                <polygon points="12,0 30,0 33.2,3.2 15.2,3.2" style={{ animation: "mark-in 0.5s backwards 0.04s" }} />
                <polygon points="14.6,5.6 32.6,5.6 35.8,8.8 17.8,8.8" style={{ animation: "mark-in 0.5s backwards 0.09s" }} />
                <polygon points="17.2,11.2 35.2,11.2 38.4,14.4 20.4,14.4" style={{ animation: "mark-in 0.5s backwards 0.14s" }} />
                <polygon points="3.2,16.8 21.2,16.8 24.4,20 6.4,20" style={{ animation: "mark-in 0.5s backwards 0.19s" }} />
                <polygon points="5.8,22.4 23.8,22.4 27,25.6 9,25.6" style={{ animation: "mark-in 0.5s backwards 0.24s" }} />
                <polygon points="8.4,28 26.4,28 29.6,31.2 11.6,31.2" style={{ animation: "mark-in 0.5s backwards 0.29s" }} />
              </svg>
            </Link>

            {/* Right CTA Button */}
            <div className="justify-self-end flex items-center gap-3">
              <Link
                href="/forecast"
                className="hidden sm:inline-flex items-center h-[54px] px-6 gap-3 bg-[#006cd2] hover:bg-[#0053a3] text-white font-bold text-sm tracking-[-0.015em] transition-colors relative overflow-hidden group shadow-lg"
                style={{ animation: "wipe-left 0.65s backwards 0.16s" }}
              >
                <span className="relative z-10 font-bold">Start Forecasting</span>
                <div className="w-8 h-8 bg-[#0053a3] group-hover:bg-white flex items-center justify-center relative z-10 transition-colors">
                  <svg className="w-4 h-4 text-white group-hover:text-[#006cd2] transition-colors" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7">
                    <path d="M4 10h10.2M10.4 5.6 15.2 10l-4.8 4.4" />
                  </svg>
                </div>
              </Link>

              {/* Mobile Burger Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-3 bg-black/10 backdrop-blur-md border-0 text-[#0a0a0a]"
                aria-label="Open menu"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </header>

          {/* Mobile Menu Dropdown */}
          {mobileMenuOpen && (
            <div className="lg:hidden mt-4 p-6 bg-black/90 backdrop-blur-xl border border-white/10 text-white space-y-4 flex flex-col z-50">
              <a href="#product" onClick={() => setMobileMenuOpen(false)} className="text-sm font-semibold">Product</a>
              <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)} className="text-sm font-semibold">How It Works</a>
              <a href="#explainability" onClick={() => setMobileMenuOpen(false)} className="text-sm font-semibold">Explainability</a>
              <a href="#performance" onClick={() => setMobileMenuOpen(false)} className="text-sm font-semibold">Performance</a>
              <a href="#ai-analyst" onClick={() => setMobileMenuOpen(false)} className="text-sm font-semibold">AI Analyst</a>
              <Link href="/forecast" className="inline-flex items-center justify-center py-3.5 bg-[#006cd2] text-white font-bold text-sm">
                Start Forecasting
              </Link>
            </div>
          )}

          {/* MAIN HERO CONTENT */}
          <main className="mt-8 sm:mt-16 w-full">
            {/* Eyebrow Badge */}
            <div className="inline-flex items-center gap-2.5 h-[36px] sm:h-[42px] px-3.5 sm:px-4 bg-white/30 border border-[#006cd2]/20 backdrop-blur-[18px] text-[#1a1a1a] text-xs sm:text-sm font-medium tracking-[-0.01em] mb-4 sm:mb-6">
              <span className="w-3 h-3 sm:w-3.5 sm:h-3.5 border-2 border-[#006cd2] bg-white"></span>
              AI-POWERED DEMAND INTELLIGENCE
            </div>

            {/* Headline with Two-Pass Accent Wipe */}
            <h1 className="text-[clamp(2.1rem,5.5vw,5rem)] font-semibold leading-[1.15] tracking-[-0.038em] max-w-5xl break-words">
              <span className="block overflow-hidden">
                <span className="block text-[#0a0a0a]" style={{ animation: "type-rise 0.85s cubic-bezier(0.16,1,0.3,1) backwards 0.26s" }}>
                  Every demand decision
                </span>
              </span>

              <span className="block overflow-hidden mt-1">
                <span className="block" style={{ animation: "type-rise 0.85s cubic-bezier(0.16,1,0.3,1) backwards 0.4s" }}>
                  <span className="text-[#6b7378] font-semibold">starts with a </span>
                  <span className="headline__accent" data-text="better question.">better question.</span>
                </span>
              </span>
            </h1>

            <p className="mt-4 sm:mt-6 text-sm sm:text-lg lg:text-xl text-[#1a1a1a] max-w-3xl leading-relaxed font-normal">
              <strong>Know What Demand Is Coming Next.</strong> Forecast demand, understand what's driving it, and identify what needs your attention before it becomes a business problem.
            </p>

            {/* Action CTAs */}
            <div className="flex flex-col sm:flex-row flex-wrap gap-4 mt-6 sm:mt-8">
              <Link
                href="/forecast"
                className="inline-flex items-center justify-center sm:justify-start h-[54px] sm:h-[58px] px-6 sm:px-8 gap-4 bg-[#006cd2] hover:bg-[#0053a3] text-white font-bold text-sm sm:text-base tracking-[-0.015em] transition-colors relative overflow-hidden group shadow-xl w-full sm:w-auto"
                style={{ animation: "wipe-left 0.7s cubic-bezier(0.16,1,0.3,1) backwards 0.56s" }}
              >
                <span className="relative z-10 font-bold">Start Forecasting</span>
                <div className="w-8 h-8 sm:w-9 sm:h-9 bg-[#0053a3] group-hover:bg-white flex items-center justify-center relative z-10 transition-colors">
                  <svg className="w-4 h-4 text-white group-hover:text-[#006cd2] transition-colors" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7">
                    <path d="M4 10h10.2M10.4 5.6 15.2 10l-4.8 4.4" />
                  </svg>
                </div>
              </Link>

              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center h-[54px] sm:h-[58px] px-8 bg-white/75 hover:bg-white text-[#0a0a0a] backdrop-blur-[24px] border border-black/10 font-bold text-sm sm:text-base transition-colors shadow-md w-full sm:w-auto text-center"
                style={{ animation: "wipe-left 0.7s cubic-bezier(0.16,1,0.3,1) backwards 0.66s" }}
              >
                Explore Demo Platform
              </Link>
            </div>
          </main>

          {/* Bottom Lede */}
          <div className="mt-12 sm:mt-16 max-w-[700px] text-white text-sm sm:text-lg font-light leading-relaxed tracking-[-0.01em] bg-black/60 p-5 sm:p-6 border border-white/10 backdrop-blur-md">
            <p style={{ animation: "type-rise 0.9s cubic-bezier(0.16,1,0.3,1) backwards 0.78s" }}>
              Meridian continuously analyzes sales trends, product usage, customer behavior and store commercial data to identify expansion opportunities, predict demand risks, and recommend the highest-impact actions for your team.
            </p>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SUBSEQUENT SECTIONS (SOLID BACKGROUNDS WITHOUT VIDEO)                     */}
      {/* ========================================================================= */}

      {/* 3. PROBLEM SECTION */}
      <section className="relative z-10 bg-[#0a0a0a] text-white py-16 sm:py-24 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10">
        <div className="max-w-[1440px] mx-auto space-y-12 sm:space-y-16">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-[#006cd2] uppercase font-bold tracking-widest">The Problem</span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
              Your Sales Data Knows More Than Your Reports Show.
            </h2>
            <p className="text-slate-400 text-xs sm:text-base leading-relaxed">
              Demand changes with seasonality, promotions, pricing, products, and customer behavior. Traditional reports tell you what happened. They don't tell you what is likely to happen next—or why.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <span className="text-2xs font-mono text-rose-400 font-bold uppercase">01 • Static Reporting</span>
              <h3 className="text-lg font-bold text-white">Unpredictable Demand</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Demand changes faster than static reports can capture, leading to stockouts and excess inventory costs.
              </p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <span className="text-2xs font-mono text-amber-400 font-bold uppercase">02 • Opaque Models</span>
              <h3 className="text-lg font-bold text-white">Black-Box Predictions</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                A forecast is far more useful when you understand what drove it instead of trusting blind predictions.
              </p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <span className="text-2xs font-mono text-indigo-400 font-bold uppercase">03 • Data Overload</span>
              <h3 className="text-lg font-bold text-white">Too Much Data</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Thousands of rows of sales data hide the critical signals that actually matter for business decisions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. SOLUTION SECTION */}
      <section id="how-it-works" className="relative z-10 bg-[#121212] text-white py-16 sm:py-24 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10">
        <div className="max-w-[1440px] mx-auto space-y-12 sm:space-y-16">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-[#006cd2] uppercase font-bold tracking-widest">The Workflow</span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
              From Sales Data to Better Decisions.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { num: "01", step: "Upload", desc: "Bring your historical sales CSV/Excel data into the platform." },
              { num: "02", step: "Understand", desc: "Automatically uncover trends, seasonality, and data quality issues." },
              { num: "03", step: "Forecast", desc: "Generate demand forecasts for 1, 7, 14, and 30-day horizons." },
              { num: "04", step: "Explain", desc: "Understand the underlying SHAP factors driving every prediction." },
              { num: "05", step: "Decide", desc: "Identify emerging demand changes, risks, and stock opportunities." },
            ].map((item) => (
              <div key={item.num} className="bg-[#0a0a0a] border border-white/10 p-5 space-y-2">
                <span className="text-xs font-mono font-bold text-[#006cd2]">{item.num} — {item.step}</span>
                <p className="text-xs text-slate-300 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. CORE FEATURES SECTION */}
      <section id="product" className="relative z-10 bg-[#0a0a0a] text-white py-16 sm:py-24 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10">
        <div className="max-w-[1440px] mx-auto space-y-12 sm:space-y-16">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-[#006cd2] uppercase font-bold tracking-widest">Platform Capabilities</span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
              Intelligence Built Around Your Demand.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <TrendingUp className="w-8 h-8 text-[#006cd2]" />
              <h3 className="text-base sm:text-lg font-bold text-white">Demand Forecasting</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Predict future demand across stores and products using time-series machine learning.
              </p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <Sparkles className="w-8 h-8 text-amber-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Explainable AI</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Understand which positive and negative factors are increasing or decreasing each prediction.
              </p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <BarChart3 className="w-8 h-8 text-emerald-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Store Intelligence</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Compare store performance and identify emerging demand patterns across locations.
              </p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <Activity className="w-8 h-8 text-cyan-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Product Intelligence</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Discover high-growth, declining, and high-demand products instantly.
              </p>
            </div>

            <div className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3">
              <Cpu className="w-8 h-8 text-purple-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">Model Intelligence</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Evaluate forecasting performance and walk-forward WAPE metrics across multiple horizons.
              </p>
            </div>

            <div id="ai-analyst" className="bg-[#121212] border border-white/10 p-6 sm:p-8 space-y-3 relative overflow-hidden">
              <span className="absolute top-4 right-4 px-2 py-0.5 bg-amber-950 text-amber-300 font-mono text-3xs font-bold border border-amber-800">
                AI Analyst — Coming Soon
              </span>
              <Bot className="w-8 h-8 text-amber-400" />
              <h3 className="text-base sm:text-lg font-bold text-white">AI Demand Analyst</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Ask natural language questions about your demand data and receive audited business answers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. EXPLAINABILITY SECTION */}
      <section id="explainability" className="relative z-10 bg-[#121212] text-white py-16 sm:py-24 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10">
        <div className="max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          <div className="space-y-4 sm:space-y-6">
            <span className="text-xs font-mono text-[#006cd2] uppercase font-bold tracking-widest">Explainable AI</span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
              Don't Just Get a Forecast. Understand It.
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              Every prediction can be analyzed through its underlying drivers, giving you a clearer path from prediction to decision.
            </p>

            <Link
              href="/explainability"
              className="inline-flex items-center gap-2 px-6 py-3.5 bg-[#006cd2] hover:bg-[#0053a3] text-white font-bold text-xs sm:text-sm shadow-md"
            >
              Explore Explainability Engine
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 p-6 sm:p-8 space-y-6">
            <div className="border-b border-white/10 pb-4">
              <span className="text-xs text-slate-400 uppercase font-bold">Prediction Driver Breakdown</span>
              <h3 className="text-base sm:text-lg font-bold text-white mt-1">Why is demand expected to increase?</h3>
            </div>

            <div className="space-y-4 font-mono text-xs">
              <div>
                <div className="flex justify-between text-emerald-400 font-bold mb-1">
                  <span>Promotion</span>
                  <span>+31%</span>
                </div>
                <div className="w-full bg-[#121212] h-2"><div className="bg-emerald-500 h-full w-[31%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-emerald-400 font-bold mb-1">
                  <span>Recent Demand (Lag 7)</span>
                  <span>+22%</span>
                </div>
                <div className="w-full bg-[#121212] h-2"><div className="bg-emerald-500 h-full w-[22%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-emerald-400 font-bold mb-1">
                  <span>Weekly Seasonality</span>
                  <span>+15%</span>
                </div>
                <div className="w-full bg-[#121212] h-2"><div className="bg-emerald-500 h-full w-[15%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-[#006cd2] font-bold mb-1">
                  <span>Holiday Calendar</span>
                  <span>+9%</span>
                </div>
                <div className="w-full bg-[#121212] h-2"><div className="bg-[#006cd2] h-full w-[9%]"></div></div>
              </div>

              <div>
                <div className="flex justify-between text-rose-400 font-bold mb-1">
                  <span>Price Change</span>
                  <span>-6%</span>
                </div>
                <div className="w-full bg-[#121212] h-2"><div className="bg-rose-500 h-full w-[6%]"></div></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 9. PERFORMANCE TABLE SECTION */}
      <section id="performance" className="relative z-10 bg-[#0a0a0a] text-white py-16 sm:py-24 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10">
        <div className="max-w-[1440px] mx-auto space-y-8 sm:space-y-12">
          <div className="max-w-3xl space-y-3">
            <span className="text-xs font-mono text-[#006cd2] uppercase font-bold tracking-widest">Model Intelligence</span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
              Measured Across Multiple Forecast Horizons.
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
              Models are evaluated using chronological walk-forward validation rather than random train/test splits.
            </p>
          </div>

          <div className="bg-[#121212] border border-white/10 p-4 sm:p-6 overflow-x-auto">
            <table className="w-full text-left text-xs font-mono min-w-[550px]">
              <thead className="bg-[#0a0a0a] text-slate-400 uppercase text-3xs border-b border-white/10">
                <tr>
                  <th className="px-4 sm:px-6 py-3.5">Forecast Horizon</th>
                  <th className="px-4 sm:px-6 py-3.5">Model Architecture</th>
                  <th className="px-4 sm:px-6 py-3.5">CV WAPE</th>
                  <th className="px-4 sm:px-6 py-3.5">Test WAPE</th>
                  <th className="px-4 sm:px-6 py-3.5">Selection Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-200">
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-white">1 Day (1d)</td>
                  <td className="px-4 sm:px-6 py-3.5 text-amber-400">CatBoost</td>
                  <td className="px-4 sm:px-6 py-3.5">11.83%</td>
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-emerald-400">10.46%</td>
                  <td className="px-4 sm:px-6 py-3.5 text-[#006cd2]">Phase 4 Optuna</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-white">7 Days (7d)</td>
                  <td className="px-4 sm:px-6 py-3.5 text-amber-400">CatBoost</td>
                  <td className="px-4 sm:px-6 py-3.5">11.27%</td>
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-emerald-400">10.13%</td>
                  <td className="px-4 sm:px-6 py-3.5 text-[#006cd2]">Phase 4 Optuna</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-white">14 Days (14d)</td>
                  <td className="px-4 sm:px-6 py-3.5 text-amber-400">CatBoost</td>
                  <td className="px-4 sm:px-6 py-3.5">11.42%</td>
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-emerald-400">10.17%</td>
                  <td className="px-4 sm:px-6 py-3.5 text-slate-400">Phase 3 Baseline</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-white">30 Days (30d)</td>
                  <td className="px-4 sm:px-6 py-3.5 text-amber-400">CatBoost</td>
                  <td className="px-4 sm:px-6 py-3.5">11.98%</td>
                  <td className="px-4 sm:px-6 py-3.5 font-bold text-emerald-400">11.61%</td>
                  <td className="px-4 sm:px-6 py-3.5 text-[#006cd2]">Phase 4 Optuna</td>
                </tr>
              </tbody>
            </table>
            <p className="text-3xs font-mono text-slate-500 mt-4">* Lower WAPE indicates higher forecast precision and lower prediction error.</p>
          </div>
        </div>
      </section>

      {/* 12. FINAL CTA SECTION */}
      <section className="relative z-10 bg-[#121212] text-white py-16 sm:py-24 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10 text-center">
        <div className="max-w-3xl mx-auto space-y-6 sm:space-y-8">
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
            Turn Your Sales Data Into Your Next Decision.
          </h2>
          <p className="text-slate-400 text-xs sm:text-base leading-relaxed">
            Upload your historical sales data and discover what demand is likely to do next.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-2">
            <Link
              href="/forecast"
              className="inline-flex items-center justify-center h-[54px] sm:h-[58px] px-8 bg-[#006cd2] hover:bg-[#0053a3] text-white font-bold text-sm sm:text-base shadow-xl transition-all w-full sm:w-auto"
            >
              Start Forecasting Now
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center h-[54px] sm:h-[58px] px-8 bg-white/10 hover:bg-white/20 text-white border border-white/20 font-semibold text-sm sm:text-base transition-all w-full sm:w-auto"
            >
              Explore Demo Platform
            </Link>
          </div>
        </div>
      </section>

      {/* 13. FOOTER */}
      <footer className="relative z-10 bg-[#0a0a0a] text-slate-400 py-12 sm:py-16 px-4 sm:px-[clamp(20px,3.52vw,64px)] border-t border-white/10 text-xs font-mono">
        <div className="max-w-[1440px] mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 sm:gap-12 border-b border-white/10 pb-8 sm:pb-12">
          <div className="space-y-3">
            <span className="font-bold text-white text-sm">AI Demand Intelligence</span>
            <p className="text-slate-500 text-2xs leading-relaxed">
              Forecast. Explain. Decide. Multi-horizon time-series machine learning platform.
            </p>
          </div>

          <div className="space-y-2">
            <span className="font-bold text-white uppercase text-3xs tracking-wider">Product</span>
            <ul className="space-y-1 text-slate-400">
              <li><Link href="/forecast" className="hover:text-white">Forecasting Studio</Link></li>
              <li><Link href="/explainability" className="hover:text-white">SHAP Explainability</Link></li>
              <li><Link href="/eda" className="hover:text-white">Store & Product EDA</Link></li>
              <li><Link href="/analyst" className="hover:text-white">AI Demand Analyst</Link></li>
            </ul>
          </div>

          <div className="space-y-2">
            <span className="font-bold text-white uppercase text-3xs tracking-wider">Technology</span>
            <ul className="space-y-1 text-slate-400">
              <li>CatBoost & Optuna</li>
              <li>TreeSHAP Attributions</li>
              <li>MLflow Model Registry</li>
              <li>FastAPI + Docker Container</li>
              <li>Next.js + Tailwind CSS</li>
            </ul>
          </div>

          <div className="space-y-2">
            <span className="font-bold text-white uppercase text-3xs tracking-wider">Resources</span>
            <ul className="space-y-1 text-slate-400">
              <li><a href="https://demand-intelligence-api.onrender.com/docs" target="_blank" rel="noreferrer" className="hover:text-white">FastAPI Docs</a></li>
              <li><a href="https://github.com/VedantJadhav701/ai-demand-intelligence-platform" target="_blank" rel="noreferrer" className="hover:text-white">GitHub Repository</a></li>
            </ul>
          </div>
        </div>

        <div className="max-w-[1440px] mx-auto pt-6 sm:pt-8 flex flex-col sm:flex-row justify-between items-center gap-2 text-3xs text-slate-600">
          <span>&copy; 2026 AI Demand Intelligence. All rights reserved.</span>
          <span>Powered by Render & Vercel</span>
        </div>
      </footer>
    </div>
  );
}
