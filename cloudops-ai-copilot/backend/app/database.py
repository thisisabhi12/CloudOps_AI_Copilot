"""
CloudOps AI Copilot — Database Configuration

Async SQLAlchemy engine and session factory using asyncpg.
Provides get_db dependency for FastAPI route injection.
"""

from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.config import settings


def _build_engine_url_and_args(raw_url: str) -> tuple[str, dict]:
    """
    Normalize the DATABASE_URL for the asyncpg driver.

    - Rewrites postgres:// or postgresql:// schemes to postgresql+asyncpg://
    - Strips libpq-only query params (sslmode, channel_binding) that
      asyncpg does not understand, translating sslmode into the
      asyncpg `ssl` connect argument instead.
    """
    url = make_url(raw_url)

    # Force the asyncpg driver
    if url.drivername in ("postgres", "postgresql"):
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)
    connect_args: dict = {}

    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)

    if sslmode in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = "require"
    elif sslmode == "disable":
        connect_args["ssl"] = None

    url = url.set(query=query)
    return url.render_as_string(hide_password=False), connect_args


_engine_url, _connect_args = _build_engine_url_and_args(settings.database_url)

# Async engine — asyncpg driver for PostgreSQL
engine = create_async_engine(
    _engine_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

# Session factory — produces async sessions
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.
    Automatically commits on success and rolls back on error.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_connection() -> bool:
    """Check if the database is reachable."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
