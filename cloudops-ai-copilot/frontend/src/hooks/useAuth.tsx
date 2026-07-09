"use client";

/**
 * CloudOps AI Copilot — Auth Hook
 *
 * Manages authentication state across the application.
 */

import { useState, useEffect, useCallback, createContext, useContext } from "react";
import type { User } from "@/lib/types";
import { authApi, ApiError } from "@/lib/api";
import { useRouter } from "next/navigation";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Initialize to a server-safe state to avoid hydration mismatches;
  // localStorage is only read after mount in the effect below.
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    if (authApi.isAuthenticated()) {
      // Optimistically restore the cached user, then verify the token
      setUser(authApi.getUser());
      authApi
        .getProfile()
        .then(setUser)
        .catch(() => {
          authApi.logout();
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      setError(null);
      setIsLoading(true);
      try {
        const result = await authApi.login({ email, password });
        setUser(result.user);
        router.push("/");
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Login failed. Please try again.";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const register = useCallback(
    async (email: string, username: string, password: string) => {
      setError(null);
      setIsLoading(true);
      try {
        const result = await authApi.register({ email, username, password });
        setUser(result.user);
        router.push("/");
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Registration failed. Please try again.";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(() => {
    setUser(null);
    authApi.logout();
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
