# ☁️ CloudOps AI Copilot

An AI-powered DevOps assistant that helps engineers troubleshoot cloud infrastructure, review Infrastructure as Code, analyze logs, and improve deployments using AWS and modern DevOps practices.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![Terraform](https://img.shields.io/badge/Terraform-IaC-purple?logo=terraform)
![AWS](https://img.shields.io/badge/AWS-ECS%20Fargate-orange?logo=amazon-aws)

---

## ✨ Features

- **🔍 AI Code Review** — Paste Terraform, Dockerfile, CloudFormation, or Kubernetes YAML and get instant expert-level feedback with severity ratings
- **💬 AI Chat** — Chat with an AI assistant specialized in DevOps, cloud architecture, and SRE best practices with streaming responses
- **🏗️ Architecture Advisor** — Describe your system and get AWS architecture recommendations with auto-generated Mermaid diagrams
- **📚 RAG Knowledge Base** — Powered by pgvector, the assistant retrieves relevant AWS Well-Architected Framework content for grounded answers
- **🔐 Authentication & RBAC** — JWT-based auth with role-based access control (Admin, DevOps, Developer, Read-only)
- **📊 Chat History** — Full session persistence with search and filtering
- **🤖 Multi-Provider AI** — Supports Google Gemini, Anthropic Claude, and OpenAI GPT with a pluggable adapter pattern

## 🏗️ Architecture

```text
Internet
  │
CloudFront ─→ Next.js (S3 Static)
  │
  ├─ /api/* ─→ ALB ─→ ECS Fargate (FastAPI)
  │                      │
  │                      ├── RDS PostgreSQL + pgvector
  │                      ├── S3 Uploads
  │                      ├── Secrets Manager
  │                      ├── CloudWatch
  │                      └── SNS Alerts
  │
  └─ /* ─→ S3 (Static Assets)
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- An AI API key (Gemini, Claude, or OpenAI)

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/cloudops-ai-copilot.git
cd cloudops-ai-copilot

# 2. Copy environment variables
cp backend/.env.example backend/.env
# Edit backend/.env and add your AI API key

# 3. Start everything
make dev

# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Without Docker

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🧪 Testing

```bash
make test        # Run backend tests
make lint        # Run all linters
make lint-fix    # Auto-fix lint issues
```

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16 + pgvector |
| Auth | JWT (python-jose) + bcrypt |
| AI | Google Gemini, Anthropic Claude, OpenAI GPT |
| Infrastructure | AWS ECS Fargate, RDS, S3, CloudFront, ALB |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Containers | Docker, Docker Compose |
| Monitoring | CloudWatch, Prometheus, Grafana, SNS |

## 🗂️ Project Structure

```text
cloudops-ai-copilot/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── terraform/        # Infrastructure as Code
├── docker/           # Docker Compose config
├── scripts/          # Utility scripts
├── docs/             # Documentation
├── .github/          # CI/CD workflows
└── Makefile          # Common commands
```

## 📄 License

MIT
