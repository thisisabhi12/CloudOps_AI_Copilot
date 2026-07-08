-- ============================================================
-- CloudOps AI Copilot — Database Initialization Script
-- ============================================================
-- This runs automatically when the PostgreSQL container starts
-- for the first time. It enables the pgvector extension.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
