"""
CloudOps AI Copilot — Database Configuration

Async SQLAlchemy engine and session factory.
Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite).
Provides get_db dependency for FastAPI route injection.
"""

from sqlalchemy import text, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator

from app.config import settings


def _build_engine(raw_url: str):
    """
    Build the async SQLAlchemy engine from the DATABASE_URL.

    - Detects SQLite vs PostgreSQL and applies appropriate settings.
    - For PostgreSQL: rewrites scheme to postgresql+asyncpg, strips
      libpq-only query params.
    - For SQLite: uses StaticPool for aiosqlite compatibility.
    """
    url = make_url(raw_url)

    # ---- SQLite (aiosqlite) ----
    if "sqlite" in url.drivername:
        # Ensure the async driver is used
        if "aiosqlite" not in url.drivername:
            url = url.set(drivername="sqlite+aiosqlite")

        return create_async_engine(
            url.render_as_string(hide_password=False),
            echo=settings.debug,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    # ---- PostgreSQL (asyncpg) ----
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

    return create_async_engine(
        url.render_as_string(hide_password=False),
        echo=settings.debug,
        pool_size=10,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _build_engine(settings.database_url)

# Enable WAL mode and foreign keys for SQLite
if "sqlite" in settings.database_url:
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


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
