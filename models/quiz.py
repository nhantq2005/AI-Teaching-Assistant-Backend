import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SqlEnum, Double, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from models.base import Base


class SourceType(str, Enum):
    AI_GENERATED = "AI_GENERATED"
    TEACHER_CREATED = "TEACHER_CREATED"


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    # Thời gian tính theo phút
    time_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    source_type: Mapped[SourceType] = mapped_column(SqlEnum(SourceType), default=SourceType.TEACHER_CREATED)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(SqlEnum(DifficultyLevel))
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now())
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    subject = relationship(back_populates="quizzes")

    quiz_attempts: Mapped[set["QuizAttempt"]] = relationship(back_populates="quiz")
    questions: Mapped[set["Question"]] = relationship(back_populates="quiz")




