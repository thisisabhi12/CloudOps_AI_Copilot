# CloudOps AI Copilot - Getting Started Guide

## Quick Start (Recommended)

### On macOS/Linux:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### On Windows:
```batch
start-dev.bat
```

This will automatically:
- Check and install dependencies
- Start the backend server on port 8000
- Start the frontend server on port 3000
- Open API documentation

## Manual Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Step 1: Start the Backend

```bash
cd cloudops-ai-copilot/backend

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at: `http://localhost:8000`

### Step 2: Start the Frontend (in a new terminal)

```bash
cd cloudops-ai-copilot/frontend

# Install Node dependencies (first time only)
npm install

# Start the Next.js development server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Documentation**: http://localhost:8000/redoc (ReDoc)

## Troubleshooting

### "Request failed" error in frontend

**Cause**: Backend server is not running on port 8000

**Solution**: Make sure you've started the backend:
```bash
cd cloudops-ai-copilot/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Backend fails to start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install dependencies:
```bash
cd cloudops-ai-copilot/backend
pip install -r requirements.txt
```

### Frontend fails to start

**Error**: `npm: command not found`

**Solution**: Install Node.js from https://nodejs.org/

**Error**: `Port 3000 is already in use`

**Solution**: Either kill the process or use a different port:
```bash
npm run dev -- -p 3001
```

### Port already in use

**Backend (port 8000)**:
```bash
# Find and kill the process
lsof -ti :8000 | xargs kill -9
```

**Frontend (port 3000)**:
```bash
# Find and kill the process
lsof -ti :3000 | xargs kill -9
```

### Environment Variables Not Loading

If you see errors about missing API keys:

1. Verify `.env.development.local` exists in both backend and frontend directories
2. Check that the Neon database credentials are set
3. Restart the servers after adding environment variables

## Project Structure

```
cloudops-ai-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── api/              # API routes
│   ├── requirements.txt       # Python dependencies
│   └── QUICK_START.md         # Backend quick reference
│
└── frontend/
    ├── app/                  # Next.js app directory
    ├── components/           # React components
    ├── lib/                  # Utilities and helpers
    ├── package.json          # Node dependencies
    └── .env.development.local # Environment variables
```

## API Endpoints

The backend provides the following main endpoints:

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/chat/sessions` - Get chat sessions
- `POST /api/v1/chat/sessions` - Create new session
- `DELETE /api/v1/chat/sessions/{id}` - Delete session
- `POST /api/v1/chat/messages` - Send message
- `GET /api/v1/review/analyze` - Analyze code
- `GET /api/v1/health` - Health check

See `http://localhost:8000/docs` for full API documentation with examples.

## Development Commands

### Backend

```bash
cd cloudops-ai-copilot/backend

# Check syntax
python check_syntax.py

# Run tests (if available)
pytest

# Format code
black app/

# Lint code
flake8 app/
```

### Frontend

```bash
cd cloudops-ai-copilot/frontend

# Check for TypeScript errors
npm run type-check

# Lint code
npm run lint

# Build for production
npm run build

# Run production build
npm start
```

## Testing

### Backend Testing

The backend includes comprehensive testing:
```bash
cd cloudops-ai-copilot/backend

# Check all Python files for syntax errors
python check_syntax.py

# Verify startup configuration
python verify_startup.py

# Run full test suite
python test_backend.py
```

### Frontend Testing

```bash
cd cloudops-ai-copilot/frontend

# Run tests (if configured)
npm test
```

## Production Deployment

### Backend Deployment

1. Build the application:
```bash
cd cloudops-ai-copilot/backend
pip install -r requirements.txt
```

2. Set production environment variables in `.env`

3. Run with Gunicorn:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or deploy to:
- Vercel
- Railway
- Render
- AWS
- DigitalOcean
- Heroku

### Frontend Deployment

1. Build:
```bash
cd cloudops-ai-copilot/frontend
npm run build
```

2. Deploy to Vercel:
```bash
npm install -g vercel
vercel
```

Or deploy to any Node.js hosting:
- Netlify
- GitHub Pages
- AWS
- DigitalOcean

## Common Tasks

### Adding a new Python dependency

```bash
cd cloudops-ai-copilot/backend
pip install <package-name>
pip freeze > requirements.txt
```

### Adding a new Node dependency

```bash
cd cloudops-ai-copilot/frontend
npm install <package-name>
```

### Updating dependencies

```bash
# Backend
cd cloudops-ai-copilot/backend
pip install --upgrade -r requirements.txt

# Frontend
cd cloudops-ai-copilot/frontend
npm update
```

## Getting Help

- Check the backend quick start: `cloudops-ai-copilot/backend/QUICK_START.md`
- Review backend report: `BACKEND_REPORT.md`
- Check testing summary: `BACKEND_TESTING_SUMMARY.md`
- API Documentation: http://localhost:8000/docs

## Next Steps

1. Create a user account by registering at `http://localhost:3000/register`
2. Log in to the application
3. Start creating chat sessions
4. Upload infrastructure diagrams for analysis
5. Get AI-powered recommendations

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at `http://localhost:8000/docs`
3. Check the test results in `TESTING_RESULTS.md`
4. Review backend architecture in `BACKEND_REPORT.md`
