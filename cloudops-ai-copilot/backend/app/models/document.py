"""
CloudOps AI Copilot — Document Model (RAG)

Stores document chunks and their vector embeddings
for retrieval-augmented generation (RAG) with pgvector.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

from app.database import Base


class DocumentChunk(Base):
    """
    A chunk of a document stored with its vector embedding.
    Used for semantic search in the RAG pipeline.
    """
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
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
        JSONB,
        nullable=True,
        default=None,
        comment="Additional metadata (section, page, tags, etc.)",
    )
    embedding = mapped_column(
        Vector(768),
        nullable=True,
        comment="768-dimensional embedding vector (Gemini text-embedding-004)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        preview = self.content[:60] + "..." if len(self.content) > 60 else self.content
        return f"<DocumentChunk {self.source}: {preview}>"
