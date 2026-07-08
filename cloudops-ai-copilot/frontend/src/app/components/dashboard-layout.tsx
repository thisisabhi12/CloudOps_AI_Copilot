"use client";

import React from "react";
import { useAuth } from "@/hooks/useAuth";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";

interface DashboardLayoutProps {
  children: React.ReactNode;
  title: string;
}

export default function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const navItems = [
    {
      name: "AI Chat",
      path: "/",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
    },
    {
      name: "IaC Reviewer",
      path: "/review",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      ),
    },
    {
      name: "Architecture Advisor",
      path: "/architecture",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
    },
  ];

  const getRoleBadgeClass = (role: string) => {
    switch (role?.toLowerCase()) {
      case "admin":
        return "badge-critical";
      case "devops":
        return "badge-warning";
      case "developer":
        return "badge-info";
      default:
        return "badge-success";
    }
  };

  return (
    <div className="flex h-screen w-screen bg-bg-primary bg-grid-pattern text-text-primary overflow-hidden">
      {/* Sidebar */}
      <aside className="w-[var(--sidebar-width)] bg-bg-secondary border-r border-border flex flex-col shrink-0">
        {/* Brand */}
        <div className="h-[var(--header-height)] px-6 flex items-center border-b border-border">
          <Link href="/" className="flex items-center gap-2.5">
            <svg className="w-6 h-6 text-accent animate-pulse-glow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            <span className="font-bold text-lg tracking-tight">
              CloudOps <span className="gradient-text font-extrabold">Copilot</span>
            </span>
          </Link>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.path;
            return (
              <Link
                key={item.name}
                href={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-bg-tertiary text-accent border-l-2 border-accent shadow-card"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50"
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* User Card */}
        {user && (
          <div className="p-4 border-t border-border bg-bg-secondary flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-bg-tertiary border border-border flex items-center justify-center font-bold text-accent shadow-card">
                {user.username.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-text-heading truncate">
                  {user.username}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className={`badge ${getRoleBadgeClass(user.role)}`}>
                    {user.role}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={logout}
              className="btn-secondary w-full py-2 flex items-center justify-center gap-2 text-xs font-semibold"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign Out
            </button>
          </div>
        )}
      </aside>

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <header className="h-[var(--header-height)] bg-bg-secondary/30 backdrop-blur-md border-b border-border px-8 flex items-center justify-between shrink-0">
          <h2 className="text-xl font-bold text-text-heading">{title}</h2>
          <div className="flex items-center gap-4">
            <div className="text-xs text-text-muted hidden md:block">
              Connected environment: <span className="text-text-secondary font-medium">AWS Sandbox</span>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <div className="max-w-7xl mx-auto h-full flex flex-col animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
