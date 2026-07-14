"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import AuthGuard from "./auth-guard";
import DashboardLayout from "./components/dashboard-layout";
import { chatApi, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { ChatSession, ChatMessage } from "@/lib/types";

// Safe, zero-dependency Markdown Parser for React Nodes
function parseInline(text: string) {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="text-text-heading font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={index}
          className="px-1.5 py-0.5 rounded bg-accent/10 border border-accent/15 text-blue-300 font-mono text-xs"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

function renderMarkdown(content: string) {
  const parts = content.split(/(```[\s\S]*?```)/g);
  return parts.map((part, index) => {
    if (part.startsWith("```")) {
      const match = part.match(/```(\w*)\n([\s\S]*?)```/);
      const lang = match ? match[1] : "";
      const code = match ? match[2] : part.slice(3, -3);
      return (
        <pre key={index} className="overflow-x-auto my-3 p-4 bg-zinc-950/80 border border-border rounded-xl font-mono text-xs text-text-primary">
          <code className={lang ? `language-${lang}` : ""}>{code.trim()}</code>
        </pre>
      );
    }

    const lines = part.split("\n");
    return (
      <div key={index} className="space-y-1.5">
        {lines.map((line, lIdx) => {
          if (line.startsWith("### ")) {
            return (
              <h4 key={lIdx} className="text-sm font-bold text-text-heading mt-3">
                {parseInline(line.slice(4))}
              </h4>
            );
          }
          if (line.startsWith("## ")) {
            return (
              <h3 key={lIdx} className="text-base font-bold text-text-heading mt-4">
                {parseInline(line.slice(3))}
              </h3>
            );
          }
          if (line.startsWith("# ")) {
            return (
              <h2 key={lIdx} className="text-lg font-extrabold text-text-heading mt-5">
                {parseInline(line.slice(2))}
              </h2>
            );
          }
          if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
            return (
              <ul key={lIdx} className="list-disc pl-5 my-1.5">
                <li className="text-text-primary">{parseInline(line.trim().slice(2))}</li>
              </ul>
            );
          }
          if (line.startsWith("> ")) {
            return (
              <blockquote key={lIdx} className="border-l-4 border-accent pl-3 py-1 my-2 bg-accent/5 rounded-r text-text-secondary italic">
                {parseInline(line.slice(2))}
              </blockquote>
            );
          }
          if (line.trim() === "") return <div key={lIdx} className="h-2"></div>;
          return (
            <p key={lIdx} className="leading-relaxed text-text-primary text-sm">
              {parseInline(line)}
            </p>
          );
        })}
      </div>
    );
  });
}

export default function ChatPage() {
  const { isAuthenticated } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState<string>("gemini");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch all chat sessions
  const fetchSessions = useCallback(async () => {
    try {
      const data = await chatApi.getSessions();
      setSessions(data.sessions);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  }, []);

  // Fetch messages for a specific session
  const loadSession = useCallback(async (sessionId: string) => {
    try {
      setError(null);
      setActiveSessionId(sessionId);
      const detail = await chatApi.getSession(sessionId);
      setMessages(detail.messages);
    } catch (err) {
      setError("Failed to load conversation history.");
      console.error(err);
    }
  }, []);

  // Load sessions on mount when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchSessions();
    }
  }, [fetchSessions, isAuthenticated]);

  // Scroll to bottom helper
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Start a new chat clean state
  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setError(null);
    setInput("");
  };

  // Delete a session
  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this chat session?")) return;

    try {
      await chatApi.deleteSession(sessionId);
      if (activeSessionId === sessionId) {
        handleNewChat();
      }
      fetchSessions();
    } catch {
      setError("Failed to delete chat session.");
    }
  };

  // Handle message submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    setError(null);
    const userMessageContent = input.trim();
    setInput("");

    // Create temporary user message
    const userMsg: ChatMessage = {
      id: Math.random().toString(),
      role: "user",
      content: userMessageContent,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);

    // Create temporary AI message placeholder
    const assistantMsgId = Math.random().toString();
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, assistantMsg]);

    let accumulatedContent = "";

    try {
      const stream = chatApi.stream(userMessageContent, activeSessionId, provider);

      for await (const chunk of stream) {
        // SSE Chunk events are parsed by apiFetch
        if (chunk.event === "session") {
          try {
            const data = JSON.parse(chunk.data);
            setActiveSessionId(data.session_id);
          } catch (error) {
            console.error("Session event parse error:", error);
          }
        } else if (chunk.event === "chunk") {
          try {
            const data = JSON.parse(chunk.data);
            accumulatedContent += data.content;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? { ...msg, content: accumulatedContent }
                  : msg
              )
            );
          } catch (error) {
            console.error("Chunk event parse error:", error);
          }
        } else if (chunk.event === "error") {
          try {
            const data = JSON.parse(chunk.data);
            setError(data.error);
          } catch {
            setError("Error in AI stream.");
          }
        }
      }
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "An error occurred while streaming.";
      setError(message);
      // Remove temporary assistant message if no content was yielded
      setMessages((prev) => prev.filter((msg) => msg.id !== assistantMsgId || msg.content !== ""));
    } finally {
      setIsStreaming(false);
      fetchSessions(); // Refresh sidebar list
    }
  };

  return (
    <AuthGuard>
      <DashboardLayout title="AI DevOps Chat">
        <div className="flex h-[calc(100vh-var(--header-height)-4rem)] gap-6">
          {/* Sessions Panel */}
          <div className="w-80 glass-card p-4 flex flex-col h-full shrink-0">
            <button
              onClick={handleNewChat}
              className="btn-primary w-full py-2.5 mb-4 text-sm font-semibold flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>

            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider px-2 mb-3">
              Conversations History
            </h3>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto space-y-1 pr-1">
              {sessions.length === 0 ? (
                <p className="text-xs text-text-muted text-center py-8">
                  No active chats. Start one!
                </p>
              ) : (
                sessions.map((session) => {
                  const isActive = activeSessionId === session.id;
                  return (
                    <button
                      key={session.id}
                      onClick={() => loadSession(session.id)}
                      className={`w-full flex items-center justify-between text-left px-3 py-2.5 rounded-xl transition-all ${
                        isActive
                          ? "bg-bg-tertiary text-accent font-medium shadow-card border border-border"
                          : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/40"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <span className="text-xs truncate">{session.title}</span>
                      </div>
                      <button
                        onClick={(e) => handleDeleteSession(e, session.id)}
                        className="text-text-muted hover:text-error rounded p-0.5 transition-colors"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Main Chat Feed */}
          <div className="flex-1 glass-card flex flex-col h-full overflow-hidden">
            {/* Model & Config Header */}
            <div className="px-6 py-3 border-b border-border bg-bg-secondary/40 flex items-center justify-between">
              <span className="text-xs font-semibold text-text-secondary flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-success"></span>
                Ready to assist
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-text-secondary">AI Provider:</span>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="bg-bg-input border border-border text-text-primary text-xs rounded-lg px-2.5 py-1 focus:border-accent-focus outline-none"
                >
                  <option value="gemini">Google Gemini (Default)</option>
                  <option value="claude">Anthropic Claude</option>
                  <option value="openai">OpenAI GPT</option>
                </select>
              </div>
            </div>

            {/* Message Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center px-4">
                  <div className="w-16 h-16 rounded-2xl bg-bg-tertiary border border-border flex items-center justify-center text-accent mb-4 shadow-card">
                    <svg className="w-8 h-8 animate-pulse-glow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-text-heading mb-2">
                    Start a conversation with DevOps AI
                  </h2>
                  <p className="text-xs text-text-secondary max-w-sm leading-relaxed">
                    Ask questions about AWS architectures, Kubernetes configs, CI/CD pipelines,
                    Terraform structures, or help with troubleshooting cloud issues.
                  </p>
                </div>
              ) : (
                messages.map((msg) => {
                  const isUser = msg.role === "user";
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl p-4 shadow-card ${
                          isUser
                            ? "bg-accent/15 text-text-primary border border-accent/25 rounded-tr-none"
                            : "bg-bg-tertiary border border-border rounded-tl-none"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">
                            {isUser ? "You" : `${provider.toUpperCase()} Assistant`}
                          </span>
                        </div>
                        <div className="markdown-content">
                          {isUser ? (
                            <p className="text-sm">{msg.content}</p>
                          ) : msg.content === "" ? (
                            <div className="flex items-center gap-1.5 py-1.5">
                              <span className="typing-dot"></span>
                              <span className="typing-dot"></span>
                              <span className="typing-dot"></span>
                            </div>
                          ) : (
                            renderMarkdown(msg.content)
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              {error && (
                <div className="p-4 rounded-xl bg-error-bg border border-error/20 text-error text-xs flex items-start gap-2.5">
                  <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h5 className="font-semibold mb-1">Streaming Error</h5>
                    <p>{error}</p>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="p-4 bg-bg-secondary/40 border-t border-border flex items-center gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about CloudOps, Docker configs, AWS CLI, troubleshooting..."
                disabled={isStreaming}
                className="input-field flex-1 py-3"
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="btn-primary py-3 px-5 shadow-card shrink-0"
              >
                {isStreaming ? (
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                )}
              </button>
            </form>
          </div>
        </div>
      </DashboardLayout>
    </AuthGuard>
  );
}
