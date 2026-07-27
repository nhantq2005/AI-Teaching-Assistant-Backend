from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Enum as SqlEnum, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    process_status: Mapped[ProcessingStatus] = mapped_column(SqlEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    file_url: Mapped[str] = mapped_column(String, nullable=True)
    file_type: Mapped[str] = mapped_column(String, nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    lecturer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    lecturer: Mapped["User"] = relationship(back_populates="documents")
    subject: Mapped["Subject"] = relationship(back_populates="documents")

    document_chunks: Mapped[set["DocumentChunk"]] = relationship(back_populates="document")