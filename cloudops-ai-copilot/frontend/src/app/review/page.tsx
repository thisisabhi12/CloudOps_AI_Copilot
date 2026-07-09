"use client";

import React, { useState } from "react";
import AuthGuard from "../auth-guard";
import DashboardLayout from "../components/dashboard-layout";
import { reviewApi, ApiError } from "@/lib/api";
import type { ReviewType } from "@/lib/types";

// Zero-dependency safe Markdown parser for rendering findings & code
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
              <h4 key={lIdx} className="text-sm font-bold text-text-heading mt-3 border-b border-border/40 pb-1">
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

// Starter templates for users
const TEMPLATES: Record<ReviewType, string> = {
  terraform: `resource "aws_security_group" "bad_sg" {
  name        = "allow_all"
  description = "Insecure security group"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow SSH globally"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Insecure
  }
}

resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-company-secrets-bucket"
  # Missing encryption, public access block, logging
}`,
  dockerfile: `FROM ubuntu:latest
# Run as root
RUN apt-get update && apt-get install -y curl python3
COPY config.json /app/config.json
# Sensitive credentials inside
ENV DB_PASSWORD=admin_password123
CMD ["python3", "/app/server.py"]`,
  cloudformation: `AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyS3Bucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketName: 'insecure-company-data-cf'
      AccessControl: PublicRead # Insecure`,
  kubernetes: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        securityContext:
          privileged: true # Insecure
        ports:
        - containerPort: 80`,
};

export default function ReviewPage() {
  const [reviewType, setReviewType] = useState<ReviewType>("terraform");
  const [code, setCode] = useState(TEMPLATES.terraform);
  const [filename, setFilename] = useState("");
  const [provider, setProvider] = useState("gemini");
  const [reviewResult, setReviewResult] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleReviewTypeChange = (nextReviewType: ReviewType) => {
    setReviewType(nextReviewType);
    setCode(TEMPLATES[nextReviewType]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim() || isStreaming) return;

    setError(null);
    setReviewResult("");
    setIsStreaming(true);

    try {
      let stream;
      const requestData = { code, filename: filename || null, provider };

      switch (reviewType) {
        case "terraform":
          stream = reviewApi.streamTerraform(requestData);
          break;
        case "dockerfile":
          stream = reviewApi.streamDockerfile(requestData);
          break;
        case "cloudformation":
          stream = reviewApi.streamCloudformation(requestData);
          break;
        case "kubernetes":
          stream = reviewApi.streamKubernetes(requestData);
          break;
        default:
          throw new Error("Invalid review type");
      }

      let accumulatedContent = "";

      for await (const chunk of stream) {
        if (chunk.event === "chunk") {
          try {
            const data = JSON.parse(chunk.data);
            accumulatedContent += data.content;
            setReviewResult(accumulatedContent);
          } catch (error) {
            console.error("Chunk parse error:", error);
          }
        } else if (chunk.event === "error") {
          try {
            const data = JSON.parse(chunk.data);
            setError(data.error);
          } catch {
            setError("Error occurred during code review.");
          }
        }
      }
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to connect to review engine.";
      setError(message);
    } finally {
      setIsStreaming(false);
    }
  };

  // Extract score if available in review result
  const extractScore = () => {
    const scoreMatch = reviewResult.match(/Overall Score:\s*(\d+)/i);
    return scoreMatch ? parseInt(scoreMatch[1], 10) : null;
  };

  const score = extractScore();

  return (
    <AuthGuard>
      <DashboardLayout title="IaC Code Reviewer">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-var(--header-height)-4rem)]">
          {/* Left Column: Code Input */}
          <div className="glass-card p-6 flex flex-col h-full overflow-hidden">
            <h3 className="text-md font-semibold text-text-heading mb-4">
              Submit Configuration
            </h3>

            <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4 overflow-hidden">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                    IaC Type
                  </label>
                  <select
                    value={reviewType}
                    onChange={(e) => handleReviewTypeChange(e.target.value as ReviewType)}
                    disabled={isStreaming}
                    className="input-field py-2"
                  >
                    <option value="terraform">Terraform (.tf)</option>
                    <option value="dockerfile">Dockerfile</option>
                    <option value="cloudformation">CloudFormation (.yaml)</option>
                    <option value="kubernetes">Kubernetes Manifest (.yaml)</option>
                  </select>
                </div>

                <div>
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
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                  Optional Filename
                </label>
                <input
                  type="text"
                  placeholder="e.g. main.tf"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  disabled={isStreaming}
                  className="input-field py-2"
                />
              </div>

              <div className="flex-1 flex flex-col overflow-hidden">
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2 shrink-0">
                  Source Code
                </label>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  disabled={isStreaming}
                  placeholder="Paste your configuration code here..."
                  className="textarea-code flex-1 resize-none shrink overflow-y-auto"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isStreaming || !code.trim()}
                className="btn-primary w-full py-3 shadow-card shrink-0"
              >
                {isStreaming ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Reviewing Configuration...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Run AI Review
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Right Column: Review Report */}
          <div className="glass-card p-6 flex flex-col h-full overflow-hidden">
            <h3 className="text-md font-semibold text-text-heading mb-4">
              AI Analysis Report
            </h3>

            {/* Score Ring Display */}
            {score !== null && (
              <div className="flex items-center gap-5 p-4 rounded-2xl bg-bg-secondary border border-border mb-4 animate-fade-in shadow-card">
                <div className="relative w-16 h-16 flex items-center justify-center shrink-0">
                  <div className="absolute inset-0 rounded-full bg-accent/15 blur-md animate-pulse-glow"></div>
                  <svg className="w-16 h-16 transform -rotate-90">
                    <circle cx="32" cy="32" r="28" className="stroke-bg-tertiary" strokeWidth="4" fill="transparent" />
                    <circle cx="32" cy="32" r="28"
                      className={score >= 80 ? "stroke-success" : score >= 50 ? "stroke-warning" : "stroke-critical"}
                      strokeWidth="4" fill="transparent"
                      strokeDasharray={2 * Math.PI * 28}
                      strokeDashoffset={2 * Math.PI * 28 * (1 - score / 100)}
                    />
                  </svg>
                  <span className="absolute text-sm font-extrabold text-text-heading">{score}</span>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-text-heading">Security & Standard Score</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    AI-evaluated rating based on configuration vulnerabilities and design standards.
                  </p>
                </div>
              </div>
            )}

            <div className="flex-1 overflow-y-auto pr-1">
              {!reviewResult && !isStreaming && !error ? (
                <div className="h-full flex flex-col items-center justify-center text-center px-4">
                  <div className="w-16 h-16 rounded-2xl bg-bg-tertiary border border-border flex items-center justify-center text-accent mb-4 shadow-card">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h4 className="text-md font-bold text-text-heading mb-1">
                    No Review Generated Yet
                  </h4>
                  <p className="text-xs text-text-secondary max-w-xs leading-relaxed">
                    Submit your Terraform, Dockerfile, CloudFormation, or Kubernetes manifests on the left to analyze issues.
                  </p>
                </div>
              ) : (
                <div className="space-y-4 text-sm markdown-content">
                  {renderMarkdown(reviewResult)}
                  {isStreaming && reviewResult === "" && (
                    <div className="flex flex-col gap-3 py-6">
                      <div className="skeleton h-4 w-1/3"></div>
                      <div className="skeleton h-20 w-full"></div>
                      <div className="skeleton h-4 w-1/2"></div>
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
                    <h5 className="font-semibold mb-1">Analysis Stopped</h5>
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
