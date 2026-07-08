import uuid
from datetime import datetime

from sqlalchemy import Double, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_score: Mapped[float] = mapped_column(Double, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    time_submitted: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="attempt_quizzes")
    quiz: Mapped["Quiz"] = relationship(back_populates="quiz_attempts")

    options: Mapped[set["Option"]] = relationship(back_populates="quiz_attempt")
    user_answers: Mapped[set["UserAnswer"]] = relationship(back_populates="quiz_attempt")