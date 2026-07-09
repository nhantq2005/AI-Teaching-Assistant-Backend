import uuid

from sqlalchemy import Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    option_id: Mapped[int] = mapped_column(ForeignKey("options.id"))
    quiz_attempt_id: Mapped[int] = mapped_column(ForeignKey("quiz_attempts.id"))

    question: Mapped["Question"] = relationship(back_populates="user_answers")
    option: Mapped["Option"] = relationship(back_populates="user_answers")
    quiz_attempt: Mapped["QuizAttempt"] = relationship(back_populates="user_answers")

