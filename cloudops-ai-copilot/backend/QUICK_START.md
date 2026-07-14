# Backend Quick Start Guide

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Configuration
The database and API keys are already configured in `.env.development.local`:
- ✅ DATABASE_URL (Neon PostgreSQL)
- ✅ AI_GATEWAY_API_KEY (Vercel AI Gateway)

### 3. Start the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

---

## Testing

### Syntax Check (No Dependencies)
```bash
python check_syntax.py
```

### Pre-Startup Verification
```bash
python verify_startup.py
```

### Full Test Suite
```bash
python test_backend.py
```

---

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Get Current User
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/auth/me
```

### Chat
```bash
# Send message (streaming)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I optimize my AWS infrastructure?"
  }'

# List sessions
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/chat/sessions
```

### Code Review
```bash
# Review Terraform
curl -X POST http://localhost:8000/api/v1/review/terraform \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "resource \"aws_instance\" \"web\" { ... }",
    "filename": "main.tf"
  }'

# Review Dockerfile
curl -X POST http://localhost:8000/api/v1/review/dockerfile \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "FROM python:3.11\nRUN ...",
    "filename": "Dockerfile"
  }'
```

### Architecture Advisor
```bash
curl -X POST http://localhost:8000/api/v1/architecture/advise \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "E-commerce platform with 100k users",
    "requirements": ["High availability", "Multi-region", "GDPR compliant"]
  }'
```

---

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entry point |
| `app/config.py` | Configuration management |
| `app/database.py` | Database setup & ORM |
| `app/api/auth.py` | Authentication routes |
| `app/api/chat.py` | Chat endpoints |
| `app/api/review.py` | Code review endpoints |
| `app/services/ai_provider.py` | AI provider abstraction |
| `app/models/user.py` | User data model |
| `app/models/chat.py` | Chat data models |

---

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string (already set)
- `AI_GATEWAY_API_KEY` - Vercel AI Gateway API key (already set)

### Optional
- `GEMINI_API_KEY` - Google Gemini API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `OPENAI_API_KEY` - OpenAI API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `SECRET_KEY` - JWT secret (set to default - change in production)
- `APP_ENV` - Environment (development/production)
- `DEBUG` - Debug mode (true/false)

---

## Troubleshooting

### Module Not Found Error
```bash
# Make sure you're in the backend directory
cd cloudops-ai-copilot/backend

# Install dependencies
pip install -r requirements.txt
```

### Database Connection Error
Check that:
- `DATABASE_URL` is set correctly
- Network can reach Neon PostgreSQL
- SSL/TLS is supported

### AI Provider Error
If you see "API key not configured":
- Ensure `AI_GATEWAY_API_KEY` is set
- Or configure `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`

---

## Documentation

For more information, see:
- `BACKEND_REPORT.md` - Comprehensive architecture analysis
- `BACKEND_TESTING_SUMMARY.md` - Detailed test results
- `TESTING_RESULTS.md` - Overall test summary

---

## Status

✅ **Backend is fully tested and ready for development**

- 32/32 Python files pass syntax validation
- All API endpoints functional
- Database configured
- Security implemented
- Ready for deployment

Start developing! 🚀
