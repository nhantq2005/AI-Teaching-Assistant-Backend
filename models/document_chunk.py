import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SqlEnum, Double, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunk"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=True)
    slide_number: Mapped[int] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_id: Mapped[str] = mapped_column(String, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now())

    document_id = None
    course_id = None