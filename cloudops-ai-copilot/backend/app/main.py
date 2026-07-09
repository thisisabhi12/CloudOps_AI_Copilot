"""
CloudOps AI Copilot — FastAPI Application Entry Point

Configures the FastAPI app with CORS, routers, and lifespan events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.review import router as review_router
from app.api.architecture import router as architecture_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"   Environment: {settings.app_env}")
    logger.info(f"   Debug: {settings.debug}")
    logger.info(f"   Default AI Provider: {settings.default_ai_provider}")
    
    # Auto-create tables on startup
    try:
        from app.database import engine, Base
        # Import models so SQLAlchemy metadata knows about them
        from app.models.user import User  # noqa: F401
        from app.models.chat import ChatSession, ChatMessage  # noqa: F401
        from app.models.document import DocumentChunk  # noqa: F401
        
        logger.info("Initializing database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

    yield
    logger.info(f"👋 Shutting down {settings.app_name}")


# ----- FastAPI Application -----
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered DevOps assistant for cloud infrastructure troubleshooting, "
        "IaC review, log analysis, and deployment optimization."
    ),
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# ----- CORS Middleware -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Routers -----
API_V1_PREFIX = "/api/v1"

app.include_router(health_router, prefix=API_V1_PREFIX)
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(chat_router, prefix=API_V1_PREFIX)
app.include_router(review_router, prefix=API_V1_PREFIX)
app.include_router(architecture_router, prefix=API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint — API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.is_development else "disabled",
        "health": f"{API_V1_PREFIX}/health",
    }
