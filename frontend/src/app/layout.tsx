"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import Topbar from "@/components/layout/Topbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const isLandingPage = pathname === "/";

  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} min-h-full antialiased`}>
      <body className="min-h-screen bg-[#000000] text-[#F5F7FA] font-sans selection:bg-[#006cd2] selection:text-white">
        {isLandingPage ? (
          /* Standalone Landing Page (No Sidebar, No Topbar) */
          <div className="w-full min-h-screen">
            {children}
          </div>
        ) : (
          /* Actual Web Application Platform (With Sidebar & Topbar) */
          <div className="min-h-screen flex bg-[#08090B]">
            {/* Sidebar */}
            <Sidebar
              mobileOpen={mobileSidebarOpen}
              onCloseMobile={() => setMobileSidebarOpen(false)}
            />

            {/* Main Content Container */}
            <div className="flex-1 flex flex-col min-w-0 min-h-screen">
              <Topbar onOpenMobileSidebar={() => setMobileSidebarOpen(true)} />
              <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1440px] w-full mx-auto overflow-x-hidden">
                {children}
              </main>
            </div>
          </div>
        )}
      </body>
    </html>
  );
}
