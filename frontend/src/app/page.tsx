"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

export default function VesperLandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    // Escape key closes mobile menu
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="bg-black text-white min-h-screen relative font-sans overflow-x-hidden selection:bg-white selection:text-black">
      
      {/* 1. HERO BACKGROUND VIDEO */}
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

      {/* 2. PAGE CONTAINER */}
      <div className="relative z-10 min-h-screen flex flex-col justify-between p-4 sm:p-8 lg:p-12 max-w-[1600px] mx-auto">
        
        {/* ========================================================================= */}
        {/* HEADER — 3-COLUMN GRID (Left Logo, Center Nav Pills, Right Header CTA)    */}
        {/* ========================================================================= */}
        <header className="grid grid-cols-[1fr_auto_1fr] items-center w-full relative z-50 select-none">
          
          {/* LEFT — LOGO */}
          <Link
            href="/"
            className="inline-flex items-center gap-2.5 justify-self-start text-base font-semibold tracking-[-0.03em] text-white appear appear--scale"
            style={{ "--d": "0.08s" } as React.CSSProperties}
            aria-label="AI Demand Intelligence Vesper.ai"
          >
            {/* Rotate -30deg Mark SVG */}
            <svg
              className="w-5 h-5 text-white transform -rotate-30"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <g transform="rotate(-30 12 12)">
                <circle cx="7.3" cy="3.2" r="1.45" />
                <rect x="5.5" y="4.7" width="3.6" height="14.6" rx="1.8" />
                <rect x="14.9" y="4.7" width="3.6" height="14.6" rx="1.8" />
                <circle cx="16.7" cy="20.8" r="1.45" />
              </g>
            </svg>
            <span className="font-bold">Vesper<span className="text-[#9a9a9a] font-normal">.ai</span></span>
            <span className="hidden sm:inline-block text-3xs px-2 py-0.5 bg-white/10 text-white font-mono rounded border border-white/20">
              Demand Intelligence
            </span>
          </Link>

          {/* CENTER — NAV PILLS */}
          <nav className="hidden lg:flex items-center gap-2 justify-self-center" aria-label="Primary">
            {[
              { label: "Benefits", href: "#benefits", d: "0.16s", class: "appear--scale" },
              { label: "How It Works", href: "#how-it-works", d: "0.28s", class: "appear--soft" },
              { label: "Explainability", href: "#explainability", d: "0.40s", class: "appear--scale" },
              { label: "Performance", href: "#performance", d: "0.52s", class: "appear--soft" },
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
              Start for Free
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

        {/* MOBILE BACKDROP DRAWER */}
        {menuOpen && (
          <div className="fixed inset-0 z-40 bg-black/90 backdrop-blur-2xl lg:hidden flex flex-col justify-center items-center p-8 space-y-6">
            <a href="#benefits" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">Benefits</a>
            <a href="#how-it-works" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">How It Works</a>
            <a href="#explainability" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">Explainability</a>
            <a href="#performance" onClick={() => setMenuOpen(false)} className="text-xl font-medium text-white">Performance</a>
            <Link href="/forecast" onClick={() => setMenuOpen(false)} className="btn-solid w-full py-4 text-center font-bold text-sm">
              Start for Free
            </Link>
          </div>
        )}

        {/* ========================================================================= */}
        {/* HERO (BOTTOM-CENTERED, NOT VERTICALLY CENTERED)                           */}
        {/* ========================================================================= */}
        <main className="mt-16 mb-12 flex flex-col items-center text-center max-w-[860px] mx-auto w-full">
          
          {/* BADGE */}
          <div
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#7d7d7d] via-[#2a2a2a] to-[#0a0a0a] text-[#f2f2f2] text-xs font-medium tracking-[-0.01em] mb-6 border border-white/10 appear appear--pop"
            style={{ "--d": "0.22s" } as React.CSSProperties}
          >
            {/* Sparkle SVG */}
            <svg className="w-4 h-4 text-white fill-current filter drop-shadow-[0_0_3px_rgba(255,255,255,0.45)]" viewBox="0 0 24 24">
              <path d="M12 2.6C12.55 2.6 12.88 3.15 13.08 4.7c.62 4.7 1.52 5.6 6.22 6.22 1.55.2 2.1.53 2.1 1.08s-.55.88-2.1 1.08c-4.7.62-5.6 1.52-6.22 6.22-.2 1.55-.53 2.1-1.08 2.1s-.88-.55-1.08-2.1c-.62-4.7-1.52-5.6-6.22-6.22C3.15 12.88 2.6 12.55 2.6 12s.55-.88 2.1-1.08c4.7-.62 5.6-1.52 6.22-6.22C11.12 3.15 11.45 2.6 12 2.6Z" />
            </svg>
            <span>Operational AI Infrastructure</span>
          </div>

          {/* H1 HEADLINE WITH INSTRUMENT SERIF ITALIC EM */}
          <h1 className="text-[clamp(2.5rem,5.5vw,4.5rem)] font-medium leading-[1.12] tracking-[-0.045em] text-white">
            <span className="block overflow-hidden py-1">
              <span className="block appear appear--mask" style={{ "--d": "0.42s" } as React.CSSProperties}>
                Train <em className="serif-italic">AI forecasting</em> on your
              </span>
            </span>

            <span className="block overflow-hidden py-1">
              <span className="block appear appear--mask" style={{ "--d": "0.62s" } as React.CSSProperties}>
                workflows in minutes.
              </span>
            </span>
          </h1>

          {/* LEDE */}
          <p
            className="mt-5 text-sm sm:text-base text-[#9a9a9a] max-w-[470px] leading-relaxed tracking-[-0.015em] appear appear--soft"
            style={{ "--d": "0.82s" } as React.CSSProperties}
          >
            Deploy adaptive AI agents that learn, execute, and scale operational demand forecasts across your business.
          </p>

          {/* ACTION BUTTONS */}
          <div className="flex flex-wrap justify-center gap-3 mt-8">
            <Link
              href="/forecast"
              className="btn-solid h-[42px] px-6 text-sm font-bold appear appear--btn"
              style={{ "--d": "0.96s" } as React.CSSProperties}
            >
              Start for Free
            </Link>

            <Link
              href="/dashboard"
              className="btn-ghost h-[42px] px-6 text-sm font-medium appear appear--side"
              style={{ "--d": "1.10s" } as React.CSSProperties}
            >
              See it in action
            </Link>
          </div>
        </main>

        {/* ========================================================================= */}
        {/* FOOTER — THREE STATS                                                      */}
        {/* ========================================================================= */}
        <footer className="flex flex-col md:flex-row items-center justify-between gap-6 pt-6 border-t border-white/10 text-[#d8d8d8] text-xs font-mono select-none">
          
          {/* STAT 1: DUAL PILL WORKFLOW AUTOMATION */}
          <div
            className="inline-flex items-center gap-3 appear appear--stat"
            style={{ "--d": "1.12s" } as React.CSSProperties}
          >
            <svg className="w-5 h-5 text-[#e8e8e8]" viewBox="0 0 24 24">
              <defs>
                <linearGradient id="g1" x1="3" y1="2" x2="14" y2="22" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#ffffff" stopOpacity="0.38" />
                  <stop offset="100%" stopColor="#3a3a3a" stopOpacity="0.62" />
                </linearGradient>
                <linearGradient id="g2" x1="3" y1="2" x2="14" y2="22" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#3a3a3a" stopOpacity="0.38" />
                  <stop offset="100%" stopColor="#ffffff" stopOpacity="0.62" />
                </linearGradient>
              </defs>
              <rect x="3.4" y="2.6" width="7.2" height="18.8" rx="3.6" fill="url(#g1)" />
              <rect x="13.4" y="2.6" width="7.2" height="18.8" rx="3.6" fill="url(#g2)" />
              <rect x="9.2" y="10.9" width="5.6" height="2.2" rx="1.1" fill="#4a4a4a" />
            </svg>
            <span>4.2M+ workflows automated</span>
          </div>

          {/* STAT 2: DOWNLOAD TILE */}
          <div
            className="inline-flex items-center gap-3 appear appear--stat"
            style={{ "--d": "1.28s" } as React.CSSProperties}
          >
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24">
              <rect x="2.4" y="2.4" width="19.2" height="19.2" rx="6.2" fill="#ffffff" />
              <path d="M12 7.1v7.4M8.15 12.35L12 16.2l3.85-3.85" stroke="#111111" strokeWidth="1.85" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            </svg>
            <span>92% reduction in manual operations</span>
          </div>

          {/* STAT 3: THREE AVATARS */}
          <div
            className="inline-flex items-center gap-3 appear appear--stat"
            style={{ "--d": "1.44s" } as React.CSSProperties}
          >
            <svg className="w-10 h-5" viewBox="0 0 40 22">
              <circle cx="10.2" cy="11" r="9.2" fill="#2b2b2b" />
              <ellipse cx="10.2" cy="12.1" rx="4.15" ry="3.7" fill="#f4f4f4" />
              <circle cx="20.2" cy="11" r="9.2" fill="#ffffff" />
              <circle cx="18.5" cy="10" r="1.2" fill="#111111" />
              <circle cx="21.9" cy="10" r="1.2" fill="#111111" />
              <path d="M18.5 13.5 Q20.2 15.5 21.9 13.5" stroke="#111111" strokeWidth="1.2" fill="none" />
              <circle cx="30.2" cy="11" r="9.2" fill="#f26b1d" />
              <text x="30.2" y="15.1" fontSize="12.5" fontWeight="700" fill="#ffffff" textAnchor="middle" fontFamily="Inter">e</text>
            </svg>
            <span>180+ operational teams onboarded</span>
          </div>

        </footer>
      </div>
    </div>
  );
}
