"use client";

import React, { useState } from "react";
import AuthGuard from "../auth-guard";
import DashboardLayout from "../components/dashboard-layout";
import { architectureApi, ApiError } from "@/lib/api";

// Zero-dependency safe Markdown parser for rendering architecture reports
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

      const isMermaid = lang.toLowerCase() === "mermaid";

      return (
        <div key={index} className="my-4">
          <div className="flex items-center justify-between px-4 py-2 bg-bg-tertiary border border-border border-b-0 rounded-t-xl shrink-0">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider flex items-center gap-1.5">
              {isMermaid ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-accent animate-pulse-glow"></span>
                  Mermaid Diagram Code
                </>
              ) : (
                `${lang || "code"} block`
              )}
            </span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(code.trim());
                alert("Copied to clipboard!");
              }}
              className="text-xs text-accent hover:text-accent-hover font-medium flex items-center gap-1"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              Copy
            </button>
          </div>
          <pre className="overflow-x-auto p-4 bg-zinc-950/80 border border-border rounded-b-xl font-mono text-xs text-text-primary">
            <code>{code.trim()}</code>
          </pre>
          {isMermaid && (
            <div className="mt-2 text-right">
              <a
                href="https://mermaid.live"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-text-muted hover:text-accent font-semibold underline underline-offset-2 inline-flex items-center gap-1"
              >
                Open in Mermaid Live Editor
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          )}
        </div>
      );
    }

    const lines = part.split("\n");
    return (
      <div key={index} className="space-y-1.5">
        {lines.map((line, lIdx) => {
          if (line.startsWith("### ")) {
            return (
              <h4 key={lIdx} className="text-sm font-bold text-text-heading mt-4 border-b border-border/40 pb-1">
                {parseInline(line.slice(4))}
              </h4>
            );
          }
          if (line.startsWith("## ")) {
            return (
              <h3 key={lIdx} className="text-base font-bold text-text-heading mt-5">
                {parseInline(line.slice(3))}
              </h3>
            );
          }
          if (line.startsWith("# ")) {
            return (
              <h2 key={lIdx} className="text-lg font-extrabold text-text-heading mt-6">
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

const DEFAULT_DESCRIPTION = "A high-performance SaaS web application deployed on AWS. It needs a client-facing Next.js frontend, an internal FastAPI backend, and a PostgreSQL database. The application expects around 10,000 active daily users and must handle file uploads securely.";

export default function ArchitecturePage() {
  const [description, setDescription] = useState(DEFAULT_DESCRIPTION);
  const [requirements, setRequirements] = useState<string[]>([
    "Highly Available (Multi-AZ)",
    "Serverless frontend hosting",
    "PostgreSQL automated backups",
    "Estimated monthly budget under $300",
  ]);
  const [reqInput, setReqInput] = useState("");
  const [provider, setProvider] = useState("gemini");
  const [adviceResult, setAdviceResult] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Add requirement tag
  const handleAddRequirement = (e: React.FormEvent) => {
    e.preventDefault();
    const val = reqInput.trim();
    if (val && !requirements.includes(val)) {
      setRequirements((prev) => [...prev, val]);
      setReqInput("");
    }
  };

  // Remove requirement tag
  const handleRemoveRequirement = (tag: string) => {
    setRequirements((prev) => prev.filter((r) => r !== tag));
  };

  // Handle Advice Generation
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim().length < 10 || isStreaming) return;

    setError(null);
    setAdviceResult("");
    setIsStreaming(true);

    try {
      const stream = architectureApi.streamAdvice({
        description: description.trim(),
        requirements,
        provider,
      });

      let accumulatedContent = "";
      for await (const chunk of stream) {
        if (chunk.event === "chunk") {
          try {
            const data = JSON.parse(chunk.data);
            accumulatedContent += data.content;
            setAdviceResult(accumulatedContent);
          } catch (e) {
            console.error("Chunk parse error:", e);
          }
        } else if (chunk.event === "error") {
          try {
            const data = JSON.parse(chunk.data);
            setError(data.error);
          } catch (e) {
            setError("Error occurred during advice generation.");
          }
        }
      }
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to connect to advisor engine.";
      setError(message);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <AuthGuard>
      <DashboardLayout title="Architecture Advisor">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-var(--header-height)-4rem)]">
          {/* Left Column: Input Form */}
          <div className="glass-card p-6 flex flex-col h-full overflow-hidden">
            <h3 className="text-md font-semibold text-text-heading mb-4">
              Describe your System
            </h3>

            <div className="flex-1 flex flex-col gap-4 overflow-hidden">
              <div className="shrink-0">
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                  AI Provider
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  disabled={isStreaming}
                  className="input-field py-2"
                >
                  <option value="gemini">Google Gemini</option>
                  <option value="claude">Anthropic Claude</option>
                  <option value="openai">OpenAI GPT</option>
                </select>
              </div>

              <div className="flex-1 flex flex-col min-h-0 shrink">
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2 shrink-0">
                  System Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={isStreaming}
                  placeholder="Detail the stack, microservices, databases, load estimates, compliance needs, etc..."
                  className="textarea-code flex-1 resize-none overflow-y-auto"
                  required
                />
              </div>

              {/* Requirements Tags */}
              <div className="shrink-0 flex flex-col gap-2">
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Specific Requirements & Constraints
                </label>
                <form onSubmit={handleAddRequirement} className="flex gap-2">
                  <input
                    type="text"
                    value={reqInput}
                    onChange={(e) => setReqInput(e.target.value)}
                    disabled={isStreaming}
                    placeholder="Type constraint and press Enter..."
                    className="input-field py-2 flex-1"
                  />
                  <button
                    type="submit"
                    disabled={isStreaming || !reqInput.trim()}
                    className="btn-secondary py-2 px-4 text-xs font-semibold shrink-0"
                  >
                    Add
                  </button>
                </form>

                {/* Tags List */}
                <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto py-1">
                  {requirements.length === 0 ? (
                    <span className="text-xs text-text-muted italic">No requirements added yet.</span>
                  ) : (
                    requirements.map((req) => (
                      <span
                        key={req}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-bg-tertiary border border-border text-xs text-text-secondary font-medium"
                      >
                        {req}
                        <button
                          type="button"
                          onClick={() => handleRemoveRequirement(req)}
                          disabled={isStreaming}
                          className="text-text-muted hover:text-error shrink-0"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </span>
                    ))
                  )}
                </div>
              </div>

              <button
                onClick={handleSubmit}
                disabled={isStreaming || description.trim().length < 10}
                className="btn-primary w-full py-3 shadow-card shrink-0"
              >
                {isStreaming ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating Architecture Advice...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                    Generate Advice & Diagrams
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Recommendations Output */}
          <div className="glass-card p-6 flex flex-col h-full overflow-hidden">
            <h3 className="text-md font-semibold text-text-heading mb-4">
              AWS Solutions Architect Advice
            </h3>

            <div className="flex-1 overflow-y-auto pr-1">
              {!adviceResult && !isStreaming && !error ? (
                <div className="h-full flex flex-col items-center justify-center text-center px-4">
                  <div className="w-16 h-16 rounded-2xl bg-bg-tertiary border border-border flex items-center justify-center text-accent mb-4 shadow-card">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <h4 className="text-md font-bold text-text-heading mb-1">
                    No Architecture Plan Generated
                  </h4>
                  <p className="text-xs text-text-secondary max-w-xs leading-relaxed">
                    Provide your system parameters and constraints on the left, and our architect AI will construct resources.
                  </p>
                </div>
              ) : (
                <div className="space-y-4 text-sm markdown-content">
                  {renderMarkdown(adviceResult)}
                  {isStreaming && adviceResult === "" && (
                    <div className="flex flex-col gap-3 py-6">
                      <div className="skeleton h-4 w-1/4"></div>
                      <div className="skeleton h-24 w-full"></div>
                      <div className="skeleton h-4 w-1/3"></div>
                    </div>
                  )}
                </div>
              )}

              {error && (
                <div className="mt-4 p-4 rounded-xl bg-error-bg border border-error/20 text-error text-xs flex items-start gap-2.5">
                  <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h5 className="font-semibold mb-1">Advisor Error</h5>
                    <p>{error}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </DashboardLayout>
    </AuthGuard>
  );
}
