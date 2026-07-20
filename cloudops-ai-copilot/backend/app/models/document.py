"""
CloudOps AI Copilot — Document Model (RAG)

Stores document chunks and their metadata for
retrieval-augmented generation (RAG).
Vector embeddings are stored when a compatible backend (pgvector) is available.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DocumentChunk(Base):
    """
    A chunk of a document stored with its metadata.
    Used for semantic search in the RAG pipeline.
    Note: Vector embedding support requires PostgreSQL with pgvector.
    """
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )
    source: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        comment="Source document or URL this chunk came from",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="The text content of this chunk",
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        default=None,
        comment="Additional metadata (section, page, tags, etc.)",
    )
    # Note: Vector embedding column is only available with pgvector on PostgreSQL.
    # For SQLite, embeddings can be stored as JSON arrays if needed.
    embedding_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="768-dimensional embedding vector stored as JSON array (SQLite fallback)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        preview = self.content[:60] + "..." if len(self.content) > 60 else self.content
        return f"<DocumentChunk {self.source}: {preview}>"
