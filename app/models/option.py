from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt


class Option(Base):
    __tablename__ = "options"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    quiz_attempt_id: Mapped[int] = mapped_column(ForeignKey("quiz_attempts.id"))

    question: Mapped["Question"] = relationship(back_populates="options")
    quiz_attempt: Mapped["QuizAttempt"] = relationship(back_populates="options")

    user_answers: Mapped[set["UserAnswer"]] = relationship(back_populates="option")

