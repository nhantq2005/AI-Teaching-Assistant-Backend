import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SqlEnum, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from models.base import Base
from models.question import Question


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Double, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    quiz_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    quiz:Mapped[str] = mapped_column(relationship(Question))
    option: Mapped[str] = mapped_column(relationship("Option", back_populates="question"))
