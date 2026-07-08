"use client";

import { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-bg-primary text-text-primary">
        <div className="flex flex-col items-center gap-4">
          {/* Skeleton Spinner */}
          <div className="relative h-12 w-12 animate-pulse-glow">
            <div className="absolute inset-0 rounded-full border-4 border-border border-t-accent animate-spin"></div>
          </div>
          <p className="text-sm font-medium text-text-secondary animate-pulse-glow">
            Verifying your session...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Prevents flashing content before redirect
  }

  return <>{children}</>;
}
