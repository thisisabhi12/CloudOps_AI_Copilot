/**
 * CloudOps AI Copilot — API Client
 *
 * Centralized HTTP client with JWT auth, SSE streaming support,
 * and typed request/response helpers.
 */

import type {
  TokenResponse,
  RegisterRequest,
  LoginRequest,
  ChatSessionList,
  ChatSessionDetail,
  ReviewRequest,
  ArchitectureRequest,
  HealthResponse,
  User,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

// ----- Token Management -----

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("cloudops_token");
}

function setToken(token: string): void {
  localStorage.setItem("cloudops_token", token);
}

function removeToken(): void {
  localStorage.removeItem("cloudops_token");
}

function setUser(user: User): void {
  localStorage.setItem("cloudops_user", JSON.stringify(user));
}

function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const data = localStorage.getItem("cloudops_user");
  return data ? JSON.parse(data) : null;
}

function removeUser(): void {
  localStorage.removeItem("cloudops_user");
}

// ----- Fetch Wrapper -----

async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, error.detail || "An error occurred");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ----- SSE Streaming -----

export async function* streamSSE(
  endpoint: string,
  body: object
): AsyncGenerator<{ event: string; data: string }, void, unknown> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, error.detail || "Stream request failed");
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "message";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        const data = line.slice(5).trim();
        yield { event: currentEvent, data };
        currentEvent = "message";
      }
    }
  }
}

// ----- Auth API -----

export const authApi = {
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const result = await apiFetch<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    setToken(result.access_token);
    setUser(result.user);
    return result;
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    const result = await apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    setToken(result.access_token);
    setUser(result.user);
    return result;
  },

  async getProfile(): Promise<User> {
    return apiFetch<User>("/auth/me");
  },

  logout(): void {
    removeToken();
    removeUser();
    window.location.href = "/login";
  },

  getToken,
  getUser,
  isAuthenticated(): boolean {
    return !!getToken();
  },
};

// ----- Chat API -----

export const chatApi = {
  stream(message: string, sessionId?: string | null, provider?: string | null) {
    return streamSSE("/chat", {
      message,
      session_id: sessionId,
      provider,
    });
  },

  async getSessions(limit = 50, offset = 0): Promise<ChatSessionList> {
    return apiFetch(`/chat/sessions?limit=${limit}&offset=${offset}`);
  },

  async getSession(sessionId: string): Promise<ChatSessionDetail> {
    return apiFetch(`/chat/sessions/${sessionId}`);
  },

  async deleteSession(sessionId: string): Promise<void> {
    return apiFetch(`/chat/sessions/${sessionId}`, { method: "DELETE" });
  },
};

// ----- Review API -----

export const reviewApi = {
  streamTerraform(data: ReviewRequest) {
    return streamSSE("/review/terraform", data);
  },
  streamDockerfile(data: ReviewRequest) {
    return streamSSE("/review/dockerfile", data);
  },
  streamCloudformation(data: ReviewRequest) {
    return streamSSE("/review/cloudformation", data);
  },
  streamKubernetes(data: ReviewRequest) {
    return streamSSE("/review/kubernetes", data);
  },
};

// ----- Architecture API -----

export const architectureApi = {
  streamAdvice(data: ArchitectureRequest) {
    return streamSSE("/architecture/advise", data);
  },
};

// ----- Health API -----

export const healthApi = {
  async check(): Promise<HealthResponse> {
    return apiFetch("/health");
  },
};
