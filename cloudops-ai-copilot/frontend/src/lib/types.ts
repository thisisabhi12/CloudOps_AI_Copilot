/**
 * CloudOps AI Copilot — TypeScript Types
 *
 * Matches backend Pydantic schemas exactly.
 */

// ----- Auth -----

export type UserRole = "admin" | "devops" | "developer" | "readonly";

export interface User {
  id: string;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// ----- Chat -----

export type SessionType =
  | "chat"
  | "terraform_review"
  | "dockerfile_review"
  | "cloudformation_review"
  | "kubernetes_review"
  | "architecture";

export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  metadata_?: Record<string, unknown> | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  session_type: SessionType;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface ChatSessionList {
  sessions: ChatSession[];
  total: number;
}

export interface ChatRequest {
  message: string;
  session_id?: string | null;
  provider?: string | null;
}

// ----- Review -----

export type ReviewType =
  | "terraform"
  | "dockerfile"
  | "cloudformation"
  | "kubernetes";

export type Severity = "critical" | "warning" | "info" | "best_practice";

export interface ReviewRequest {
  code: string;
  filename?: string | null;
  provider?: string | null;
}

export interface ArchitectureRequest {
  description: string;
  requirements: string[];
  provider?: string | null;
}

// ----- SSE Events -----

export interface SSEChunkEvent {
  content: string;
}

export interface SSESessionEvent {
  session_id: string;
}

export interface SSEDoneEvent {
  status: string;
  review_type?: string;
}

export interface SSEErrorEvent {
  error: string;
}

// ----- Health -----

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  database: {
    connected: boolean;
  };
  ai: {
    default_provider: string;
    providers_configured: string[];
  };
}
