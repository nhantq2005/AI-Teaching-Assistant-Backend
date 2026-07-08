import uuid

from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)